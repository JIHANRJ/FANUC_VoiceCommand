import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

model.eval()

print("Model loaded.\n")

# Prompt template
def build_prompt(text):
    return f"""
Extract ordered items from the sentence.

Return JSON array like:
[
  {{"name": "product", "quantity": 1}}
]

Rules:
- Only return JSON
- No explanation
- quantity must be integer
- If quantity missing assume 1

Sentence:
{text}
"""

def extract_items(text):
    prompt = build_prompt(text)

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.0,        # deterministic
            do_sample=False
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Clean possible trailing text
    start = decoded.find("[")
    end = decoded.rfind("]")

    if start != -1 and end != -1:
        decoded = decoded[start:end+1]

    return decoded.strip()


def main():
    test_inputs = [
        "I've got guests coming over, send me two chocolate boxes and one lotion.",
        "Give me a vicks",
        "I need 3 pringles and 2 coca cola",
        "One ponds please",
        "Add two cough syrup",
        "Give me nutties"
    ]

    for text in test_inputs:
        print("INPUT:", text)

        output = extract_items(text)

        print("RAW OUTPUT:")
        print(output)

        try:
            parsed = json.loads(output)
            print("VALID JSON ✅")
            print(json.dumps(parsed, indent=2))
        except Exception as e:
            print("INVALID JSON ❌", e)

        print("-" * 60)


if __name__ == "__main__":
    main()