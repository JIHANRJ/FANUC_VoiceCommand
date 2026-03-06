"""
INTERACTIVE ORDER EXTRACTION CHAT

Live testing interface for the production order extractor.
Type your order naturally and see the extraction results instantly!
"""

import re
import json
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sys

MODEL_NAME = "google/flan-t5-base"

# =====================================================
# LOAD INVENTORY FROM EXTERNAL JSON
# =====================================================
def load_inventory(json_path: str = "../inventory.json") -> tuple:
    """
    Load inventory and product mappings from external JSON file.
    Returns: (inventory_dict, product_mapping_dict)
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)
    
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    return data['inventory'], data['product_mappings']

# Load inventory at module level
INVENTORY, PRODUCT_MAPPING = load_inventory()

# =====================================================
# EXTRACTION FUNCTIONS
# =====================================================

def build_prompt(text: str) -> str:
    """Create few-shot prompt for FLAN-T5."""
    return f"""Extract ALL ordered items from the sentence. Format: product:quantity, product:quantity

Sentence: I need two chocolate boxes and one lotion
Output: chocolate boxes:2, lotion:1

Sentence: Give me a bottle
Output: bottle:1

Sentence: Send 3 pringles and 2 coca cola
Output: pringles:3, coca cola:2

Sentence: One ponds please
Output: ponds:1

Sentence: I want nivea men
Output: nivea men:1

Sentence: {text}
Output:"""

def extract_with_llm(text: str, model, tokenizer, device) -> str:
    """Use FLAN-T5 to extract structured product:quantity pairs."""
    prompt = build_prompt(text)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            num_beams=5,
            early_stopping=True,
            temperature=1.0
        )
    
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.strip()

def normalize_product_name(product_text: str) -> str:
    """Map customer product name to canonical inventory name."""
    product_lower = product_text.lower().strip()
    
    if product_lower in PRODUCT_MAPPING:
        return PRODUCT_MAPPING[product_lower]
    
    matches = [
        (key, value) 
        for key, value in PRODUCT_MAPPING.items() 
        if key in product_lower or product_lower in key
    ]
    
    if matches:
        best_match = max(matches, key=lambda x: len(x[0]))
        return best_match[1]
    
    return None

def extract_quantity_from_text(canonical_name: str, original_text: str) -> int:
    """Recover quantity from original user text for a canonical product."""
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
    }

    text = original_text.lower()
    aliases = [k for k, v in PRODUCT_MAPPING.items() if v == canonical_name]
    aliases.append(canonical_name.lower())
    aliases = sorted(set(aliases), key=len, reverse=True)

    for alias in aliases:
        # e.g. "2 ponds cream" or "two ponds cream"
        digit_before = re.search(rf'\b(\d+)\s+{re.escape(alias)}\b', text)
        if digit_before:
            return max(1, int(digit_before.group(1)))

        word_before = re.search(
            rf'\b({"|".join(number_words.keys())})\s+{re.escape(alias)}\b',
            text
        )
        if word_before:
            return number_words[word_before.group(1)]

        # e.g. "ponds cream 2" or "ponds cream two"
        digit_after = re.search(rf'\b{re.escape(alias)}\s+(\d+)\b', text)
        if digit_after:
            return max(1, int(digit_after.group(1)))

        word_after = re.search(
            rf'\b{re.escape(alias)}\s+({"|".join(number_words.keys())})\b',
            text
        )
        if word_after:
            return number_words[word_after.group(1)]

    # fallback for phrases like "4 in quantity" when only one item is present
    quantity_phrase = re.search(r'\b(\d+)\s+in\s+quantity\b', text)
    if quantity_phrase:
        return max(1, int(quantity_phrase.group(1)))

    return 1

def parse_to_structured_json(raw_llm_output: str, original_text: str = "") -> dict:
    """Parse LLM output into structured JSON with inventory mapping."""
    items = []
    
    raw_llm_output = raw_llm_output.lower()
    
    # Strategy 1: product:quantity patterns
    matches = re.findall(r'([a-z][a-z\s\-]+?)\s*:\s*(\d+)', raw_llm_output)
    
    # Strategy 2: quantity + product patterns
    if not matches:
        alt_matches = re.findall(r'(\d+)\s+([a-z][a-z\s\-]+?)(?:\s|,|and|$)', raw_llm_output)
        matches = [(prod.strip(), qty) for qty, prod in alt_matches]
    
    # Strategy 3: product names without quantities (assume 1)
    if not matches:
        for product_key in PRODUCT_MAPPING.keys():
            if product_key in raw_llm_output:
                matches.append((product_key, "1"))
    
    for product_text, qty_text in matches:
        product_text = product_text.strip()
        canonical_name = normalize_product_name(product_text)
        
        if canonical_name:
            try:
                qty = int(qty_text)
                if qty < 1:
                    qty = 1
            except:
                qty = 1

            if qty == 1 and original_text:
                qty = extract_quantity_from_text(canonical_name, original_text)
            
            if not any(item["name"] == canonical_name for item in items):
                items.append({
                    "name": canonical_name,
                    "quantity": qty,
                    "location": INVENTORY[canonical_name]
                })
    
    return {
        "items": items,
        "status": "success",
        "total_items": len(items)
    }

def extract_order(text: str, model, tokenizer, device) -> dict:
    """Complete extraction pipeline."""
    raw = extract_with_llm(text, model, tokenizer, device)
    structured = parse_to_structured_json(raw, text)
    return structured, raw

# =====================================================
# INTERACTIVE CHAT INTERFACE
# =====================================================

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*80)
    print("INTERACTIVE ORDER EXTRACTION CHAT")
    print("="*80)
    print(f"\nAvailable Products ({len(INVENTORY)} items):")
    # Print products dynamically from inventory
    product_names = list(INVENTORY.keys())
    for i in range(0, len(product_names), 6):
        chunk = product_names[i:i+6]
        print("   " + ", ".join(chunk))
    print("\nTips:")
    print("   - Speak naturally: 'I need 2 chocolate boxes and 1 vicks'")
    print("   - Type 'quit' or 'exit' to stop")
    print("   - Type 'help' to see this info again")
    print("="*80 + "\n")

def print_result(result: dict, raw: str):
    """Pretty print extraction results."""
    print("\n" + "-"*80)
    print(f"Raw LLM: {raw}")
    print("-"*80)
    
    if result["total_items"] == 0:
        print("WARNING: No items extracted. Please try rephrasing your order.")
    else:
        print(f"SUCCESS: Extracted {result['total_items']} item(s):\n")
        for i, item in enumerate(result["items"], 1):
            loc = item["location"]
            print(f"   {i}. {item['name']} x {item['quantity']}")
            print(f"      Location: {loc['rack']} -> {loc['section']} -> {loc['position']}")
    
    print("\nFull JSON:")
    print(json.dumps(result, indent=2))
    print("-"*80 + "\n")

def main():
    """Run interactive chat interface."""
    print_banner()
    
    # Load model once
    print("Loading FLAN-T5 model... (this takes a moment)")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    
    print(f"Model loaded on {device.upper()}")
    print(f"Inventory loaded: {len(INVENTORY)} products\n")
    print("Ready! Type your order below:\n")
    
    order_count = 0
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("Your order: ").strip()
            
            # Handle special commands
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\nProcessed {order_count} orders. Goodbye!")
                break
            
            if user_input.lower() in ['help', 'h', '?']:
                print_banner()
                continue
            
            # Process order
            order_count += 1
            result, raw = extract_order(user_input, model, tokenizer, device)
            print_result(result, raw)
            
        except KeyboardInterrupt:
            print(f"\n\nInterrupted. Processed {order_count} orders. Goodbye!")
            break
        except Exception as e:
            print(f"\nERROR: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()
