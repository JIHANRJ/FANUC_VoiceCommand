import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "google/flan-t5-base"

SYSTEM_PROMPT = (
    "Extract ordered items from the sentence.\n"
    "Return ONLY a JSON array of objects, each with: name (string), quantity (integer).\n"
    "Strictly follow this JSON schema: [ { \"name\": <string>, \"quantity\": <integer> } ]\n"
    "If quantity is not specified, assume 1.\n"
    "Example: [ { \"name\": \"chocolate\", \"quantity\": 2 }, { \"name\": \"lotion\", \"quantity\": 1 } ]\n"
    "Do not output anything except the JSON array.\n"
)

TEST_INPUTS = [
    "I've got guests coming over, send me two chocolate boxes and one lotion.",
    "Give me a vicks",
    "I need 3 pringles and 2 coca cola",
    "One ponds please",
    "Add two cough syrup",
    "Give me nutties"
]

def main():
    print(f"Loading model: {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print("Model loaded.\n")

    for text in TEST_INPUTS:
        prompt = SYSTEM_PROMPT + f"Sentence: {text}\nJSON: "
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        outputs = model.generate(**inputs, max_new_tokens=128)
        output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("INPUT:", text)
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
