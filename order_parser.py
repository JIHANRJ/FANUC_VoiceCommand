import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# inventory mapping as provided, flattened for lookup
inventory = {
    "Nutties": ("Rack 1", "Section 1", "Position 1"),
    "Nivea Men": ("Rack 1", "Section 1", "Position 2"),
    "Bottle": ("Rack 1", "Section 1", "Position 3"),
    "Vicks": ("Rack 1", "Section 2", "Position 1"),
    "Cough Syrup": ("Rack 1", "Section 2", "Position 2"),
    "Coca Cola": ("Rack 1", "Section 2", "Position 3"),
    "Blue Box": ("Rack 2", "Section 1", "Position 1"),
    "Pringles": ("Rack 2", "Section 1", "Position 2"),
    "Instant Noodles": ("Rack 2", "Section 1", "Position 3"),
    "Small Medicine Box": ("Rack 2", "Section 2", "Position 1"),
    "Ponds": ("Rack 2", "Section 2", "Position 2"),
    "Dove": ("Rack 2", "Section 2", "Position 3"),
}


# Using Phi-2 (2.7B params, MIT license, commercial use allowed)
MODEL_NAME = "microsoft/phi-2"

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    # Use Metal (MPS) if available (Apple Silicon)
    if torch.backends.mps.is_available():
        print("[INFO] Using Apple Silicon Metal (MPS) backend for acceleration.")
        model = model.to("mps")
    elif torch.cuda.is_available():
        model = model.to("cuda")
    else:
        print("[INFO] Using CPU (may be slow). For best performance, use a Mac with MPS or a machine with CUDA.")
    return tokenizer, model


def parse_order(text: str, tokenizer, model, max_new_tokens: int = 128) -> dict:
    """Generate structured order JSON from a sentence using the LLM."""
    prompt = (
        "You are an order assistant.\n"
        "Given a customer request in plain English, extract each product with its quantity, "
        "and determine which rack contains the product based on this inventory (as a Python dict):\n"
        f"{json.dumps(inventory, indent=2)}\n"
        "Output ONLY valid JSON in the following format (no explanation, no markdown):\n"
        "{\n  \"items\": [\n    {\"rack\": \"Rack 1\", \"product\": \"Bottle\", \"qty\": 1}\n  ]\n}\n"
        "If a product is not recognized, set its rack to 'unknown'.\n"
        f"Request: {text}\n"
        "JSON:"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    print("[INFO] Generating response from model... (this may take up to a few minutes on CPU)")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=64,  # reduced for speed
            temperature=0.2,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
        )
    print("[INFO] Generation complete.")
    generated = tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
    print("\n--- RAW MODEL OUTPUT ---\n", generated, "\n-----------------------\n")
    # try to load the generated portion as JSON
    try:
        parsed = json.loads(generated)
        return parsed
    except json.JSONDecodeError as e:
        print("[ERROR] Could not parse JSON. Error:", e)
        print("Raw output was:\n", generated)
        return {"raw": generated.strip()}


if __name__ == "__main__":
    tokenizer, model = load_model()
    example = "Hey CRX, can I have a bottle of lotion, two chocolates and a vicks"
    result = parse_order(example, tokenizer, model)
    print(json.dumps(result, indent=2))
