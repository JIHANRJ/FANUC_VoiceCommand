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
DEFAULT_OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11435/api")
DEFAULT_MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
DEFAULT_API_TIMEOUT = 60  # seconds for inference


# =====================================================
# INVENTORY LOADING
# =====================================================
def _load_inventory_file(json_path: str = "../inventory.json") -> dict:
    """Load inventory JSON payload from a file path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isabs(json_path):
        full_path = json_path
    elif os.path.exists(json_path):
        full_path = json_path
    else:
        full_path = os.path.join(script_dir, json_path)

    with open(full_path, "r") as file:
        return json.load(file)


def _parse_inventory_payload(data: dict) -> tuple[dict, dict]:
    """Validate and parse inventory payload into inventory + product mapping."""
    if not isinstance(data, dict):
        raise ValueError("inventory_json must be a dict with 'inventory' and 'product_mappings'")

    inventory = data.get("inventory")
    product_mapping = data.get("product_mappings")

    if not isinstance(inventory, dict):
        raise ValueError("inventory_json['inventory'] must be a dictionary")
    if not isinstance(product_mapping, dict):
        raise ValueError("inventory_json['product_mappings'] must be a dictionary")

    normalized_mapping = {str(key).lower().strip(): value for key, value in product_mapping.items()}
    return inventory, normalized_mapping


class OrderExtractor:
    """Reusable local order extractor using Ollama + schema-constrained JSON."""

    def __init__(
        self,
        inventory_json: Optional[dict] = None,
        inventory_path: Optional[str] = None,
        ollama_api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        api_timeout: int = DEFAULT_API_TIMEOUT,
    ):
        if inventory_json is not None:
            self.inventory, self.product_mapping = _parse_inventory_payload(inventory_json)
        else:
            payload = _load_inventory_file(inventory_path or "../inventory.json")
            self.inventory, self.product_mapping = _parse_inventory_payload(payload)

        self.ollama_api_url = ollama_api_url or DEFAULT_OLLAMA_API_URL
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.api_timeout = api_timeout

    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(
                f"{self.ollama_api_url.replace('/api', '')}/api/tags",
                timeout=2,
            )
            return response.status_code == 200
        except Exception:
            return False

    def load_model(self):
        """Verify Ollama is running and model is available (no explicit load needed)."""
        if not self.check_ollama_server():
            raise RuntimeError(
                f"❌ Ollama server not running at {self.ollama_api_url}\n"
                f"   Start it with: ollama serve\n"
                f"   Pull model: ollama pull {self.model_name}"
            )

        print(f"✅ Ollama server online at {self.ollama_api_url}")
        print(f"📦 Model: {self.model_name}")
        print(f"📋 Inventory loaded: {len(self.inventory)} products")
        print("🏻‍💼 License: Apache 2.0 (commercial use OK)")

        return None, None, "ollama"


# =====================================================
# NORMALIZATION HELPERS
# =====================================================
    def normalize_product_name(self, product_text: str) -> Optional[str]:
        """Map product text to canonical inventory name."""
        product_lower = product_text.lower().strip()

        if product_lower in self.product_mapping:
            return self.product_mapping[product_lower]

        matches = [
            (key, value)
            for key, value in self.product_mapping.items()
            if key in product_lower or product_lower in key
        ]

        if matches:
            best_match = max(matches, key=lambda item: len(item[0]))
            return best_match[1]

        return None

    def extract_quantity_from_text(self, canonical_name: str, original_text: str) -> int:
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

        product_pos = text_lower.find(product_lower)
        if product_pos == -1:
            return 1

        search_before = text_lower[:product_pos]
        for word, num in word_numbers.items():
            pattern = rf'\b{word}\b'
            if re.search(pattern, search_before):
                return num

        digits_before = re.findall(r'\b(\d+)\b', search_before)
        if digits_before:
            return int(digits_before[-1])

        search_after = text_lower[product_pos + len(product_lower):]
        for word, num in word_numbers.items():
            pattern = rf'\b{word}\b'
            if re.search(pattern, search_after):
                return num

        digits_after = re.findall(r'\b(\d+)\b', search_after)
        if digits_after:
            return int(digits_after[0])

        return 1

    @staticmethod
    def build_schema() -> dict:
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
                                "description": "Product name from inventory",
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "Quantity ordered",
                            },
                        },
                        "required": ["name", "quantity"],
                    },
                    "description": "List of ordered items with quantities",
                },
                "status": {
                    "type": "string",
                    "enum": ["success", "partial", "failed"],
                    "description": "Extraction status",
                },
            },
            "required": ["items", "status"],
        }

    def build_prompt(self, order_text: str) -> str:
        """Build instruction prompt with schema and examples."""
        canonical_products = list(self.inventory.keys())
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

    def generate_json_with_schema(self, order_text: str) -> tuple[dict, str]:
        """Call Ollama with JSON schema constraint for guaranteed valid output."""
        prompt = self.build_prompt(order_text)
        schema = self.build_schema()

        try:
            response = requests.post(
                f"{self.ollama_api_url}/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": schema,
                    "options": {
                        "temperature": 0,
                        "num_predict": 200,
                    },
                },
                timeout=self.api_timeout,
            )
            response.raise_for_status()

            result = response.json()
            raw_output = result.get("response", "").strip()

            try:
                parsed = json.loads(raw_output)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {"items": [], "status": "failed"}

            return parsed, raw_output

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"❌ Cannot connect to Ollama at {self.ollama_api_url}\n"
                f"   Start server: ollama serve\n"
                f"   Pull model: ollama pull {self.model_name}"
            )
        except Exception as error:
            raise RuntimeError(f"Ollama API error: {error}")

    def coerce_to_strict_result(self, candidate: dict, original_text: str) -> dict:
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
            canonical_name = self.normalize_product_name(raw_name)
            if not canonical_name or canonical_name not in self.inventory:
                continue

            raw_qty = entry.get("quantity", 1)
            try:
                quantity = int(raw_qty)
            except (ValueError, TypeError):
                quantity = 1

            if quantity < 1:
                quantity = 1

            if quantity == 1:
                quantity = self.extract_quantity_from_text(canonical_name, original_text)

            if canonical_name in seen:
                continue
            seen.add(canonical_name)

            items.append({
                "name": canonical_name,
                "quantity": quantity,
                "location": self.inventory[canonical_name],
            })

        return {
            "items": items,
            "status": "success" if items else "failed",
            "total_items": len(items),
        }

    def extract_order(self, order_text: str) -> tuple[dict, str]:
        """Main extraction entrypoint for reusable extractor instance."""
        raw_json, raw = self.generate_json_with_schema(order_text)
        strict_result = self.coerce_to_strict_result(raw_json, order_text)
        return strict_result, raw


def create_extractor(
    inventory_json: Optional[dict] = None,
    inventory_path: Optional[str] = None,
    ollama_api_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
) -> OrderExtractor:
    """Create a reusable extractor with configurable inventory and Ollama settings."""
    return OrderExtractor(
        inventory_json=inventory_json,
        inventory_path=inventory_path,
        ollama_api_url=ollama_api_url,
        model_name=model_name,
        api_timeout=api_timeout,
    )


DEFAULT_EXTRACTOR = create_extractor()
INVENTORY = DEFAULT_EXTRACTOR.inventory


def load_model():
    """Backward-compatible wrapper for existing callers."""
    return DEFAULT_EXTRACTOR.load_model()


def extract_order(order_text: str, tokenizer=None, model=None, device=None) -> tuple[dict, str]:
    """Backward-compatible wrapper for existing callers."""
    return DEFAULT_EXTRACTOR.extract_order(order_text)


def extract_order_with_inventory(
    order_text: str,
    inventory_json: dict,
    ollama_api_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
) -> tuple[dict, str]:
    """One-shot extraction where inventory is provided directly as JSON."""
    extractor = create_extractor(
        inventory_json=inventory_json,
        ollama_api_url=ollama_api_url,
        model_name=model_name,
        api_timeout=api_timeout,
    )
    return extractor.extract_order(order_text)


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
