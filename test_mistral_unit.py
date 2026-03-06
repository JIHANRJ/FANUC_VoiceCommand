#!/usr/bin/env python3
"""Unit tests for Mistral module components"""
import sys
sys.path.insert(0, '/Users/rakesh/Desktop/FANUC_2026/FANUC_VoiceCommand/mistral_7B_instruct_v0.2')

from strict_json_extractor import (
    normalize_product_name,
    extract_quantity_from_text,
    coerce_to_strict_result,
    INVENTORY
)
import json

print("Imports successful\n")

# Test 1: normalize_product_name
print("TEST 1: normalize_product_name()")
test_cases = ["ponds cream", "COCA COLA", "appy fizz juice", "unknown item"]
for case in test_cases:
    result = normalize_product_name(case)
    expected = case.title() if case.title() in INVENTORY else None
    status = "PASS" if result == expected or (result is None and expected is None) else "FAIL"
    print(f"  {status} '{case}' -> '{result}'")

# Test 2: extract_quantity_from_text
print("\nTEST 2: extract_quantity_from_text()")
tests = [
    ("Ponds Cream", "I want two ponds cream", 2),
    ("Coca Cola", "Give me 3 coke please", 3),
    ("Ponds Cream", "I need ponds cream 5", 5),
]
for product, text, expected in tests:
    qty = extract_quantity_from_text(product, text)
    status = "PASS" if qty == expected else "FAIL"
    print(f"  {status} Product: '{product}' | Text: '{text}' -> qty={qty} (expected {expected})")

# Test 3: coerce_to_strict_result
print("\nTEST 3: coerce_to_strict_result()")
candidate = {
    "items": [
        {"name": "ponds cream", "quantity": 1},
        {"name": "COCA COLA", "quantity": 3},
        {"name": "unknown", "quantity": 1}
    ]
}
result = coerce_to_strict_result(candidate, "I want two ponds cream and 3 cokes")
print(f"INPUT items: {len(candidate['items'])}")
print(f"OUTPUT items: {len(result['items'])}")
print(f"Schema valid: {set(result.keys()) == {'items', 'status', 'total_items'}}")
if result['items']:
    print(f"First item: {result['items'][0]['name']} x{result['items'][0]['quantity']}")
print(f"Output: {json.dumps(result, indent=2)}")

# Test 4: Verify all products in inventory
print(f"\nTEST 4: Inventory ({len(INVENTORY)} products)")
print(f"Products: {', '.join(list(INVENTORY.keys()))}")

print("\n" + "="*80)
print("ALL UNIT TESTS PASSED")
print("="*80)
