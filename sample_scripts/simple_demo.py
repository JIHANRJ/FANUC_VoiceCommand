"""
Simple demo script showing how to use the order extractor.

This is a reference for developers integrating the extractor.

Usage:
    python3 sample_scripts/simple_demo.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_granite_extractor import create_extractor


def demo():
    """Quick demo of order extraction with default inventory."""
    
    # Get absolute path to inventory (works from any directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    inventory_path = os.path.join(workspace_root, "config", "inventory.json")
    
    # Create extractor with workspace inventory
    extractor = create_extractor(inventory_path=inventory_path)
    
    # Verify Ollama server is running
    try:
        extractor.load_model(verbose=False)
    except RuntimeError as e:
        error_output = {"error": str(e), "status": "failed"}
        print(json.dumps(error_output, indent=2))
        return
    
    # Example orders to process
    test_orders = [
        "I want two ponds cream and 3 pringles",
        "Get me coca cola",
        "I need soap, instant noodles, and two vicks",
    ]
    
    # Process all orders and collect results
    results = []
    for order_text in test_orders:
        result, raw = extractor.extract_order(order_text)
        results.append({
            "input": order_text,
            "extracted": result
        })
    
    # Output as JSON
    output = {
        "status": "success",
        "model": "llama3.1:latest",
        "total_orders_processed": len(test_orders),
        "results": results
    }
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    demo()
