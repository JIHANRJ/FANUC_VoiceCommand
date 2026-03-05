"""
INTERACTIVE ORDER EXTRACTION CHAT

Live testing interface for the production order extractor.
Type your order naturally and see the extraction results instantly!
"""

import re
import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sys

MODEL_NAME = "google/flan-t5-base"

# =====================================================
# INVENTORY DATABASE
# =====================================================
INVENTORY = {
    "Nutties": {"rack": "Rack 1", "section": "Section 1", "position": "Position 1"},
    "Nivea Men": {"rack": "Rack 1", "section": "Section 1", "position": "Position 2"},
    "Bottle": {"rack": "Rack 1", "section": "Section 1", "position": "Position 3"},
    "Vicks": {"rack": "Rack 1", "section": "Section 2", "position": "Position 1"},
    "Cough Syrup": {"rack": "Rack 1", "section": "Section 2", "position": "Position 2"},
    "Coca Cola": {"rack": "Rack 1", "section": "Section 2", "position": "Position 3"},
    "Blue Box": {"rack": "Rack 2", "section": "Section 1", "position": "Position 1"},
    "Pringles": {"rack": "Rack 2", "section": "Section 1", "position": "Position 2"},
    "Instant Noodles": {"rack": "Rack 2", "section": "Section 1", "position": "Position 3"},
    "Small Medicine Box": {"rack": "Rack 2", "section": "Section 2", "position": "Position 1"},
    "Ponds": {"rack": "Rack 2", "section": "Section 2", "position": "Position 2"},
    "Dove": {"rack": "Rack 2", "section": "Section 2", "position": "Position 3"},
}

# Product name normalization
PRODUCT_MAPPING = {
    "nutties": "Nutties",
    "nivea men": "Nivea Men",
    "nivea": "Nivea Men",
    "bottle": "Bottle",
    "lotion": "Bottle",
    "vicks": "Vicks",
    "vicks syrup": "Vicks",
    "cough syrup": "Cough Syrup",
    "cough": "Cough Syrup",
    "coca cola": "Coca Cola",
    "coca-cola": "Coca Cola",
    "cola": "Coca Cola",
    "coke": "Coca Cola",
    "blue box": "Blue Box",
    "chocolate": "Blue Box",
    "chocolate box": "Blue Box",
    "chocolate boxes": "Blue Box",
    "chocolates": "Blue Box",
    "pringles": "Pringles",
    "pringle": "Pringles",
    "chips": "Pringles",
    "instant noodles": "Instant Noodles",
    "noodles": "Instant Noodles",
    "ramen": "Instant Noodles",
    "small medicine box": "Small Medicine Box",
    "medicine box": "Small Medicine Box",
    "medicine": "Small Medicine Box",
    "ponds": "Ponds",
    "ponds cream": "Ponds",
    "pond": "Ponds",
    "dove": "Dove",
    "dove soap": "Dove",
    "soap": "Dove",
}

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

def parse_to_structured_json(raw_llm_output: str) -> dict:
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
    structured = parse_to_structured_json(raw)
    return structured, raw

# =====================================================
# INTERACTIVE CHAT INTERFACE
# =====================================================

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*80)
    print("🤖 INTERACTIVE ORDER EXTRACTION CHAT")
    print("="*80)
    print("\n📦 Available Products:")
    print("   Nutties, Nivea Men, Bottle, Vicks, Cough Syrup, Coca Cola,")
    print("   Blue Box, Pringles, Instant Noodles, Small Medicine Box, Ponds, Dove")
    print("\n💡 Tips:")
    print("   - Speak naturally: 'I need 2 chocolate boxes and 1 vicks'")
    print("   - Type 'quit' or 'exit' to stop")
    print("   - Type 'help' to see this info again")
    print("="*80 + "\n")

def print_result(result: dict, raw: str):
    """Pretty print extraction results."""
    print("\n" + "-"*80)
    print(f"🤖 Raw LLM: {raw}")
    print("-"*80)
    
    if result["total_items"] == 0:
        print("⚠️  No items extracted. Please try rephrasing your order.")
    else:
        print(f"✅ Extracted {result['total_items']} item(s):\n")
        for i, item in enumerate(result["items"], 1):
            loc = item["location"]
            print(f"   {i}. {item['name']} × {item['quantity']}")
            print(f"      📍 {loc['rack']} → {loc['section']} → {loc['position']}")
    
    print("\n📄 Full JSON:")
    print(json.dumps(result, indent=2))
    print("-"*80 + "\n")

def main():
    """Run interactive chat interface."""
    print_banner()
    
    # Load model once
    print("⏳ Loading FLAN-T5 model... (this takes a moment)")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    
    print(f"✅ Model loaded on {device.upper()}\n")
    print("Ready! Type your order below:\n")
    
    order_count = 0
    
    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = input("🛒 Your order: ").strip()
            
            # Handle special commands
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n👋 Processed {order_count} orders. Goodbye!")
                break
            
            if user_input.lower() in ['help', 'h', '?']:
                print_banner()
                continue
            
            # Process order
            order_count += 1
            result, raw = extract_order(user_input, model, tokenizer, device)
            print_result(result, raw)
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Interrupted. Processed {order_count} orders. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()
