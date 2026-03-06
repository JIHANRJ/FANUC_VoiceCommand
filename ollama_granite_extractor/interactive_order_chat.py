"""
INTERACTIVE CHAT FOR OLLAMA GRANITE 3.2 STRICT JSON EXTRACTOR
"""

import json
from strict_json_extractor import load_model, extract_order, INVENTORY


def print_banner():
    print("\n" + "=" * 80)
    print("OLLAMA GRANITE 3.2 STRICT JSON ORDER CHAT")
    print("=" * 80)
    print(f"\nAvailable Products ({len(INVENTORY)} items):")

    product_names = list(INVENTORY.keys())
    for index in range(0, len(product_names), 6):
        chunk = product_names[index:index + 6]
        print("   " + ", ".join(chunk))

    print("\nTips:")
    print("   - Example: 'I want two ponds cream and 3 pringles'")
    print("   - Type 'quit' or 'exit' to stop")
    print("=" * 80 + "\n")


def print_result(result: dict, raw: str):
    print("\n" + "-" * 80)

    if result["total_items"] == 0:
        print("⚠️  WARNING: No valid items extracted.")
    else:
        print(f"✅ SUCCESS: Extracted {result['total_items']} item(s):\n")
        for idx, item in enumerate(result["items"], 1):
            loc = item["location"]
            print(f"   {idx}. {item['name']} x {item['quantity']}")
            print(f"      Location: {loc['rack']} -> {loc['section']} -> {loc['position']}")

    print("\nStrict JSON:")
    print(json.dumps(result, indent=2))
    print("-" * 80 + "\n")


def main():
    print_banner()
    
    try:
        load_model()
    except RuntimeError as error:
        print(f"\n❌ Error: {error}")
        return

    print("\nReady! Type your order below:\n")
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
            result, raw = extract_order(user_input)
            print_result(result, raw)

        except KeyboardInterrupt:
            print(f"\n\nInterrupted. Processed {order_count} orders. Goodbye!")
            break
        except Exception as error:
            print(f"\n❌ ERROR: {error}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()
