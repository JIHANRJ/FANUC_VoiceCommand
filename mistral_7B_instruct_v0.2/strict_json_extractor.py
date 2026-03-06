"""
STRICT JSON ORDER EXTRACTOR

Purpose:
- Reliable order understanding with lightweight instruct models
- Strict JSON enforcement with schema validation and normalization
- External inventory configuration via ../inventory.json
"""

import json
import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PRESETS = {
    "phi3-mini": {
        "hf": "microsoft/Phi-3-mini-4k-instruct",
        "license": "MIT (commercial)",
        "max_new_tokens": 96,
    },
    "qwen2.5-1.5b": {
        "hf": "Qwen/Qwen2.5-1.5B-Instruct",
        "license": "Apache-2.0 (commercial)",
        "max_new_tokens": 96,
    },
    "mistral-7b": {
        "hf": "mistralai/Mistral-7B-Instruct-v0.2",
        "license": "Apache-2.0 (commercial)",
        "max_new_tokens": 96,
    },
    "tinyllama": {
        "hf": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "license": "Apache-2.0 (commercial)",
        "max_new_tokens": 96,
    },
}

DEFAULT_PRESET = "phi3-mini"
SELECTED_PRESET = os.getenv("ORDER_MODEL_PRESET", DEFAULT_PRESET).strip().lower()
if SELECTED_PRESET not in MODEL_PRESETS:
    SELECTED_PRESET = DEFAULT_PRESET

MODEL_NAME = os.getenv("ORDER_MODEL_NAME", MODEL_PRESETS[SELECTED_PRESET]["hf"]).strip()
MODEL_LICENSE = MODEL_PRESETS[SELECTED_PRESET]["license"]
MAX_NEW_TOKENS = int(os.getenv("ORDER_MAX_NEW_TOKENS", str(MODEL_PRESETS[SELECTED_PRESET]["max_new_tokens"])))


# =====================================================
# CONFIG LOADING
# =====================================================
def load_inventory(json_path: str = "../inventory.json") -> tuple:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)

    with open(full_path, "r") as file:
        data = json.load(file)

    return data["inventory"], data["product_mappings"]


INVENTORY, PRODUCT_MAPPING = load_inventory()


def load_model():
    print(f"Loading model: {MODEL_NAME}")
    print(f"Preset: {SELECTED_PRESET} | License: {MODEL_LICENSE}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

    # Detect best available device: CUDA > MPS (Metal) > CPU
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
    elif torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float16
        print("🚀 Metal Performance Shaders (MPS) detected - using GPU acceleration!")
    else:
        device = "cpu"
        dtype = torch.float32
        print("⚠️  Running on CPU - inference will be slower")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )

    model = model.to(device)
    model.eval()

    print(f"Model loaded on {device.upper()}")
    print(f"Inventory loaded: {len(INVENTORY)} products")
    return tokenizer, model, device


# =====================================================
# NORMALIZATION HELPERS
# =====================================================
def normalize_product_name(product_text: str) -> str | None:
    product_lower = product_text.lower().strip()

    if product_lower in PRODUCT_MAPPING:
        return PRODUCT_MAPPING[product_lower]

    matches = [
        (key, value)
        for key, value in PRODUCT_MAPPING.items()
        if key in product_lower or product_lower in key
    ]

    if matches:
        best_match = max(matches, key=lambda item: len(item[0]))
        return best_match[1]

    return None


def extract_quantity_from_text(canonical_name: str, original_text: str) -> int:
    if not original_text:
        return 1

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
    }

    text = original_text.lower()
    aliases = [key for key, value in PRODUCT_MAPPING.items() if value == canonical_name]
    aliases.append(canonical_name.lower())
    aliases = sorted(set(aliases), key=len, reverse=True)

    number_word_pattern = "|".join(number_words.keys())

    for alias in aliases:
        digit_before = re.search(rf"\b(\d+)\s+{re.escape(alias)}\b", text)
        if digit_before:
            return max(1, int(digit_before.group(1)))

        word_before = re.search(rf"\b({number_word_pattern})\s+{re.escape(alias)}\b", text)
        if word_before:
            return number_words[word_before.group(1)]

        digit_after = re.search(rf"\b{re.escape(alias)}\s+(\d+)\b", text)
        if digit_after:
            return max(1, int(digit_after.group(1)))

        word_after = re.search(rf"\b{re.escape(alias)}\s+({number_word_pattern})\b", text)
        if word_after:
            return number_words[word_after.group(1)]

    quantity_phrase = re.search(r"\b(\d+)\s+in\s+quantity\b", text)
    if quantity_phrase:
        return max(1, int(quantity_phrase.group(1)))

    return 1


# =====================================================
# STRICT JSON ENFORCEMENT
# =====================================================
def build_prompt(order_text: str) -> str:
    valid_products = ", ".join(INVENTORY.keys())
    return f"""
You are an order extraction engine.
Extract ordered items and quantities from user text.
Return ONLY valid JSON. No markdown. No explanation.

Required JSON schema:
{{
  "items": [
    {{"name": "<product>", "quantity": <int>}}
  ]
}}

Rules:
1) Use ONLY these canonical product names: {valid_products}
2) quantity must be integer >= 1
3) If quantity is missing, use 1
4) If no valid items, return {{"items": []}}

User text: {order_text}
""".strip()


def generate_raw_json(order_text: str, tokenizer, model, device) -> str:
    prompt = build_prompt(order_text)

    messages = [{"role": "user", "content": prompt}]
    input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )

    generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]
    result = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    if device == "mps":
        torch.mps.empty_cache()

    return result


def extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return "{}"
    return text[start:end + 1]


def coerce_to_strict_result(candidate: dict, original_text: str) -> dict:
    items = []

    raw_items = candidate.get("items", []) if isinstance(candidate, dict) else []
    if not isinstance(raw_items, list):
        raw_items = []

    seen = set()
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue

        raw_name = str(entry.get("name", "")).strip()
        canonical_name = normalize_product_name(raw_name)
        if not canonical_name or canonical_name not in INVENTORY:
            continue

        raw_qty = entry.get("quantity", 1)
        try:
            quantity = int(raw_qty)
        except Exception:
            quantity = 1

        if quantity < 1:
            quantity = 1

        if quantity == 1:
            quantity = extract_quantity_from_text(canonical_name, original_text)

        if canonical_name in seen:
            continue
        seen.add(canonical_name)

        items.append(
            {
                "name": canonical_name,
                "quantity": quantity,
                "location": INVENTORY[canonical_name],
            }
        )

    return {
        "items": items,
        "status": "success",
        "total_items": len(items),
    }


def extract_order(order_text: str, tokenizer, model, device) -> tuple[dict, str]:
    raw = generate_raw_json(order_text, tokenizer, model, device)
    json_text = extract_json_object(raw)

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError:
        parsed = {"items": []}

    strict_result = coerce_to_strict_result(parsed, order_text)
    return strict_result, raw


def run_smoke_test():
    tokenizer, model, device = load_model()
    tests = [
        "I want two ponds cream",
        "Give me 3 pringles and 2 coca cola",
        "Can I have one appy fizz and 4 soaps",
    ]

    for text in tests:
        result, raw = extract_order(text, tokenizer, model, device)
        print("-" * 80)
        print("INPUT:", text)
        print("RAW LLM:", raw)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_smoke_test()
