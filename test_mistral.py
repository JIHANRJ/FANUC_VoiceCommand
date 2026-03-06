#!/usr/bin/env python3
"""Test script for Mistral strict JSON extractor."""
import sys
sys.path.insert(0, '/Users/rakesh/Desktop/FANUC_2026/FANUC_VoiceCommand')

from mistral_7B_instruct_v0.2.strict_json_extractor import (
    load_model, 
    parse_to_structured_json,
    extract_quantity_from_text
)
import json

# Load model
print("Loading Mistral model...")
model, tokenizer = load_model()
print("✓ Model loaded\n")

# Test cases
test_cases = [
    "I want two ponds cream",
    "Give me 3 pringles and 2 coca cola",
    "appy fizz 4 in quantity",
    "I need one chocolates"
]

for test_input in test_cases:
    print(f"INPUT: {test_input}")
    result = parse_to_structured_json(model, tokenizer, test_input)
    print(f"OUTPUT:\n{json.dumps(result, indent=2)}\n")
    print("-" * 80)
