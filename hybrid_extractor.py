import re
import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model.eval()
print("Model loaded.\n")

# ---- Allowed catalog ----
CATALOG = [
    "chocolate boxes",
    "lotion",
    "vicks",
    "cough syrup",
    "coca cola",
    "pringles",
    "ponds",
    "nutties"
]

# ---- Prompt ----
def build_prompt(text):
    return f"""
Convert the sentence into ordered items.

Example:
Sentence: Can I have two chocolate boxes and one lotion?
Output:
chocolate boxes:2
lotion:1

Sentence: {text}
Output:
"""

# ---- LLM Extraction ----
def extract_raw(text):
    prompt = build_prompt(text)

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            do_sample=False,
            num_beams=4,
            early_stopping=True
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.strip()

# ---- Deterministic Parser ----
def parse_to_json(raw_output):
    items = []

    lines = raw_output.split("\n")

    for line in lines:
        line = line.strip().lower()

        if ":" not in line:
            continue

        product, qty = line.split(":", 1)

        product = product.strip()
        qty = qty.strip()

        if not qty.isdigit():
            continue

        qty = int(qty)

        # Catalog validation
        if product in CATALOG:
            items.append({
                "name": product,
                "quantity": qty
            })

    return {"items": items}

# ---- Main Test ----
def main():
    test_inputs = [
        "I've got guests coming over, send me two chocolate boxes and one lotion.",
        "Give me a vicks",
        "I need 3 pringles and 2 coca cola",
        "One ponds please",
        "Add two cough syrup",
        "Give me nutties"
    ]

    for text in test_inputs:
        print("INPUT:", text)

        raw = extract_raw(text)
        print("LLM RAW:")
        print(raw)

        structured = parse_to_json(raw)
        print("FINAL JSON:")
        print(json.dumps(structured, indent=2))

        print("-" * 60)

if __name__ == "__main__":
    main()