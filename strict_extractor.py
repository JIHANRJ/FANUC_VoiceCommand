import json
from pathlib import Path
from llama_cpp import Llama, LlamaGrammar

MODEL_PATH = Path("models/Phi-3-mini-4k-instruct-q4.gguf")

# ---------------------------
# STRICT JSON GRAMMAR (GBNF)
# ---------------------------

JSON_GRAMMAR = r"""
root ::= array

array ::= "[" ws item ws "]" | "[" ws item ws "," ws item ws "]" | "[" ws item ws "," ws item ws "," ws item ws "]" | "[" ws item ws "," ws item ws "," ws item ws "," ws item ws "]" | "[" ws item ws "," ws item ws "," ws item ws "," ws item ws "," ws item ws "]"

item ::= "{" ws "\"name\"" ws ":" ws name ws "," ws "\"quantity\"" ws ":" ws number ws "}"

name ::= "\"chocolate\"" | "\"nivea\"" | "\"lotion\"" | "\"vicks syrup\"" | "\"Appy juice\"" | "\"coca cola\"" | "\"soap\"" | "\"pringles\"" | "\"noodles\"" | "\"tea bags\"" | "\"ponds cream\"" | "\"dove soap\""

number ::= digit+
digit ::= [0-9]

ws ::= [ \t\n\r]*
"""

SYSTEM_PROMPT = """
Extract ordered items from the sentence.

Return ONLY a JSON array of objects with:
- name (string)
- quantity (integer)

If quantity not specified, assume 1.
"""

def main():
    print("Loading model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=False
    )

    grammar = LlamaGrammar.from_string(JSON_GRAMMAR)

    print("Model loaded.\n")

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

        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0,
            grammar=grammar,
            max_tokens=120
        )

        output = response["choices"][0]["message"]["content"]

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