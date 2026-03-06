"""
OLLAMA GRANITE 3.2 STRICT JSON EXTRACTION

Purpose:
- Local LLM inference with Ollama (no external APIs)
- Granite 3.2 instruction-tuned model (Apache 2.0 licensed)
- JSON Schema validation for guaranteed structured output
- Tool-based approach for reliable slot extraction
"""

import json
import os
import re
import requests
from typing import Optional

# Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11435/api")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1:latest")  # Default to llama3.1 (granite:3.2 not yet available)
API_TIMEOUT = 60  # seconds for inference


# =====================================================
# INVENTORY LOADING
# =====================================================
def load_inventory(json_path: str = "../inventory.json") -> tuple:
    """Load inventory and product mappings from external JSON."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)

    with open(full_path, "r") as file:
        data = json.load(file)

    return data["inventory"], data["product_mappings"]


INVENTORY, PRODUCT_MAPPING = load_inventory()


def check_ollama_server() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get(
            f"{OLLAMA_API_URL.replace('/api', '')}/api/tags",
            timeout=2
        )
        return response.status_code == 200
    except Exception:
        return False


def load_model():
    """Verify Ollama is running and model is available (no explicit load needed)."""
    if not check_ollama_server():
        raise RuntimeError(
            f"❌ Ollama server not running at {OLLAMA_API_URL}\n"
            f"   Start it with: ollama serve\n"
            f"   Pull Granite model: ollama pull granite:3.2"
        )

    print(f"✅ Ollama server online at {OLLAMA_API_URL}")
    print(f"📦 Model: {MODEL_NAME}")
    print(f"📋 Inventory loaded: {len(INVENTORY)} products")
    print(f"🏻‍💼 License: Apache 2.0 (commercial use OK)")
    
    # Return dummy tokenizer/model/device for compatibility
    return None, None, "ollama"


# =====================================================
# NORMALIZATION HELPERS
# =====================================================
def normalize_product_name(product_text: str) -> Optional[str]:
    """Map product text to canonical inventory name."""
    product_lower = product_text.lower().strip()

    # Direct mapping
    if product_lower in PRODUCT_MAPPING:
        return PRODUCT_MAPPING[product_lower]

    # Fuzzy match
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
    """Fallback quantity extraction from original text (word + digit patterns)."""
    if not original_text:
        return 1

    word_numbers = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "dozen": 12, "hundred": 100,
    }

    product_lower = canonical_name.lower()
    text_lower = original_text.lower()

    # Find product position
    product_pos = text_lower.find(product_lower)
    if product_pos == -1:
        return 1

    # Look for numbers before product
    search_before = text_lower[:product_pos]
    for word, num in word_numbers.items():
        pattern = rf'\b{word}\b'
        if re.search(pattern, search_before):
            return num

    # Look for digits before product
    digits_before = re.findall(r'\b(\d+)\b', search_before)
    if digits_before:
        return int(digits_before[-1])

    # Look for numbers after product
    search_after = text_lower[product_pos + len(product_lower):]
    for word, num in word_numbers.items():
        pattern = rf'\b{word}\b'
        if re.search(pattern, search_after):
            return num

    digits_after = re.findall(r'\b(\d+)\b', search_after)
    if digits_after:
        return int(digits_after[0])

    return 1


def build_schema():
    """Define JSON schema for order extraction."""
    return {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Product name from inventory"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity ordered"
                        }
                    },
                    "required": ["name", "quantity"]
                },
                "description": "List of ordered items with quantities"
            },
            "status": {
                "type": "string",
                "enum": ["success", "partial", "failed"],
                "description": "Extraction status"
            }
        },
        "required": ["items", "status"]
    }


def build_prompt(order_text: str) -> str:
    """Build instruction prompt with schema and examples."""
    canonical_products = list(INVENTORY.keys())
    products_str = ", ".join(canonical_products)

    prompt = f"""You are an expert order extraction assistant. Extract product orders and quantities.

CANONICAL PRODUCTS (use these exact names):
{products_str}

RULES:
1. Extract each product name and quantity mentioned
2. Use ONLY canonical product names from the list above
3. If a product is not in the list, skip it
4. Always extract quantities (default to 1 if not specified)
5. Return VALID JSON matching the exact schema

USER ORDER: {order_text}

EXAMPLES:
- "I want two ponds cream" → {{"items": [{{"name": "Ponds Cream", "quantity": 2}}], "status": "success"}}
- "Give me 3 cokes and 2 pringles" → {{"items": [{{"name": "Coca Cola", "quantity": 3}}, {{"name": "Pringles", "quantity": 2}}], "status": "success"}}
- "Unknown item xyz" → {{"items": [], "status": "failed"}}

Now extract the order above and respond with ONLY valid JSON (no extra text):
"""
    return prompt


def generate_json_with_schema(order_text: str) -> tuple[dict, str]:
    """Call Ollama with JSON schema constraint for guaranteed valid output."""
    prompt = build_prompt(order_text)
    schema = build_schema()

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": schema,
                "options": {
                    "temperature": 0,  # Deterministic for consistency
                    "num_predict": 200,  # Limit tokens
                },
            },
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()

        result = response.json()
        raw_output = result.get("response", "").strip()

        # Parse JSON from response
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON block
            json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = {"items": [], "status": "failed"}

        return parsed, raw_output

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}\n"
            f"   Start server: ollama serve\n"
            f"   Pull model: ollama pull {MODEL_NAME}"
        )
    except Exception as error:
        raise RuntimeError(f"Ollama API error: {error}")


def coerce_to_strict_result(candidate: dict, original_text: str) -> dict:
    """Validate and normalize extracted items to strict schema."""
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
        
        # Skip unknown products
        if not canonical_name or canonical_name not in INVENTORY:
            continue

        # Get quantity
        raw_qty = entry.get("quantity", 1)
        try:
            quantity = int(raw_qty)
        except (ValueError, TypeError):
            quantity = 1

        # Enforce minimum quantity
        if quantity < 1:
            quantity = 1

        # Fallback: if quantity is 1, try to recover from original text
        if quantity == 1:
            quantity = extract_quantity_from_text(canonical_name, original_text)

        # Avoid duplicates
        if canonical_name in seen:
            continue
        seen.add(canonical_name)

        items.append({
            "name": canonical_name,
            "quantity": quantity,
            "location": INVENTORY[canonical_name],
        })

    return {
        "items": items,
        "status": "success" if items else "failed",
        "total_items": len(items),
    }


def extract_order(order_text: str, tokenizer=None, model=None, device=None) -> tuple[dict, str]:
    """Main extraction function (tokenizer/model/device for compatibility)."""
    raw_json, raw = generate_json_with_schema(order_text)
    strict_result = coerce_to_strict_result(raw_json, order_text)
    return strict_result, raw


if __name__ == "__main__":
    # Quick test
    load_model()
    tests = [
        "I want two ponds cream",
        "Give me 3 cokes and 2 pringles",
        "Can I have one appy fizz and 4 soaps",
    ]

    for text in tests:
        print("\n" + "=" * 80)
        print(f"INPUT: {text}")
        result, raw = extract_order(text)
        print(f"RAW: {raw}")
        print(f"OUTPUT: {json.dumps(result, indent=2)}")
