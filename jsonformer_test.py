import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from jsonformer import Jsonformer

# JSONFormer needs a HuggingFace transformers model (not GGUF).
# TinyLlama is small (1.1B) and fast on CPU/MPS.
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="auto"
)

print("Model loaded.\n")

# Schema for JSONFormer — guarantees valid JSON output
schema = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "number"}
                }
            }
        }
    }
}

def extract(text):
    prompt = (
        "You are an order assistant. Extract the ordered items from the sentence below.\n"
        "Each item has a name and a quantity (integer). If quantity is not stated, assume 1.\n\n"
        "Example:\n"
        'Sentence: "I want two chocolate boxes and one lotion"\n'
        'Result: {"items": [{"name": "chocolate boxes", "quantity": 2}, {"name": "lotion", "quantity": 1}]}\n\n'
        f'Sentence: "{text}"\n'
        "Result:"
    )

    jsonformer = Jsonformer(
        model=model,
        tokenizer=tokenizer,
        json_schema=schema,
        prompt=prompt,
        max_array_length=5,
        max_string_token_length=20,
        temperature=0.1,
        debug=True,
    )

    return jsonformer()

def main():
    tests = [
        "Send me two chocolate boxes and one lotion",
        "Give me a vicks",
        "I need 3 pringles and 2 coca cola",
        "One ponds please",
        "Add two cough syrup",
        "Give me nutties",
    ]

    for t in tests:
        print("INPUT:", t)
        result = extract(t)
        print("OUTPUT:", json.dumps(result, indent=2))
        print("-" * 60)

if __name__ == "__main__":
    main()