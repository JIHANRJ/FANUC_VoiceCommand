"""
Interactive chat for order extraction using Ollama.
Returns JSON output for each order.

Usage from sample_scripts/:
    python3 interactive_order_chat.py
    
Usage from project root (after activating venv):
    python3 sample_scripts/interactive_order_chat.py
"""

import json
import sys
import os
from typing import NoReturn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_granite_extractor import create_extractor


def main() -> None:
    """Interactive order extraction chat interface."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    inventory_path = os.path.join(workspace_root, "config", "inventory.json")
    
    extractor = create_extractor(inventory_path=inventory_path)
    
    try:
        extractor.load_model()
    except RuntimeError as error:
        print(f"ERROR: {error}")
        return

    print(f"\nReady! Model: {extractor.model_name} | Products: {len(extractor.inventory)}")
    print("Type your order and get JSON output. Type 'exit' to quit.\n")

    order_count = 0

    while True:
        try:
            user_input = input("Your order: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print(f"\nProcessed {order_count} orders. Goodbye!")
                break

            order_count += 1
            result, raw = extractor.extract_order(user_input) # JSON output 
            
            print(json.dumps(result, indent=2))

        except KeyboardInterrupt:
            print(f"\n\nProcessed {order_count} orders. Goodbye!")
            break
        except Exception as error:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
