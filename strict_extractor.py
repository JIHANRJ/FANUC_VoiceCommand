import json
from pathlib import Path
from llama_cpp import Llama, LlamaGrammar

MODEL_PATH = Path("models/Phi-3-mini-4k-instruct-q4.gguf")

# Complete product catalog from inventory
CATALOG = [
    "Nutties", "Nivea Men", "Bottle", "Vicks", "Cough Syrup", 
    "Coca Cola", "Blue Box", "Pringles", "Instant Noodles",
    "Small Medicine Box", "Ponds", "Dove"
]

# ---------------------------
# STRICT JSON GRAMMAR (GBNF)
# ---------------------------
# Simplified grammar - focuses on structure, lets model choose from catalog

JSON_GRAMMAR = r"""
root ::= array
array ::= "[" ws "]" | "[" ws item (ws "," ws item)* ws "]"
item ::= "{" ws "\"name\"" ws ":" ws string ws "," ws "\"quantity\"" ws ":" ws number ws "}"
string ::= "\"" [^"]+ "\""
number ::= [1-9] [0-9]?
ws ::= [ \t\n]*
"""

SYSTEM_PROMPT = f"""You are an order extraction assistant. Extract items from customer requests.

AVAILABLE PRODUCTS:
{', '.join(CATALOG)}

Return ONLY a JSON array with this exact format:
[{{"name": "Product Name", "quantity": 1}}]

Rules:
- Match customer words to closest product name
- If quantity not mentioned, use 1
- Use exact product names from the list above
- chocolate/chocolate box → Blue Box
- lotion → Bottle or Nivea Men
- soap → Dove
- medicine → Small Medicine Box
- noodles → Instant Noodles

Examples:
"I need 2 nutties and 1 vicks" → [{{"name": "Nutties", "quantity": 2}}, {{"name": "Vicks", "quantity": 1}}]
"Give me a bottle" → [{{"name": "Bottle", "quantity": 1}}]
"""

def main():
    print("Loading model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=False,
        n_threads=4
    )

    grammar = LlamaGrammar.from_string(JSON_GRAMMAR, verbose=False)

    print("Model loaded.\n")

    test_inputs = [
        "I need 2 Nutties and 1 Vicks",
        "Give me a bottle",
        "Send 3 Pringles and 2 Coca Cola",
        "One Ponds please",
        "Add two Cough Syrup and one Dove",
        "I want Nivea Men",
        "Get me 5 Instant Noodles",
        "Send a Blue Box and 3 bottles",
        "I need a Small Medicine Box",
        "Give me 2 chocolate boxes, 1 lotion, and 3 vicks",  # Common names test
    ]

    for text in test_inputs:
        print("INPUT:", text)

        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            grammar=grammar,
            max_tokens=300,
            top_p=0.95,
            repeat_penalty=1.1
        )

        output = response["choices"][0]["message"]["content"]

        print("OUTPUT:", output)

        try:
            parsed = json.loads(output)
            print("✅ VALID JSON")
            print(json.dumps(parsed, indent=2))
        except Exception as e:
            print("❌ INVALID JSON:", e)

        print("-" * 60)


if __name__ == "__main__":
    main()