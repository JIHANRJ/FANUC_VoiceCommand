"""Generic schema-based extraction demo.

This demo shows how to:
1) pass context as JSON (inventory/catalog/domain data)
2) pass output shape as a separate JSON schema
3) run one generic extractor for non-order use cases
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_granite_extractor import create_generic_extractor


def demo() -> None:
    """Run generic schema-based extraction with separate context + schema."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    inventory_path = os.path.join(workspace_root, "config", "inventory.json")
    schema_path = os.path.join(workspace_root, "config", "output_schema_order_capture.json")

    with open(inventory_path, "r") as file:
        context_json = json.load(file)

    with open(schema_path, "r") as file:
        output_schema = json.load(file)

    input_text = "Please add two pringles and one coca cola"

    extractor = create_generic_extractor()
    extractor.load_model(verbose=False)

    structured, raw = extractor.extract_structured(
        input_text=input_text,
        context_json=context_json,
        output_schema=output_schema,
        instructions=(
            "Use product names from context inventory and map results into entities[] with quantity. "
            "Set intent to order_capture and status to success when at least one item is found."
        ),
    )

    print(
        json.dumps(
            {
                "status": "success",
                "input": input_text,
                "structured_output": structured,
                "raw_model_output": raw,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    demo()
