import json
from pathlib import Path
from llama_cpp import Llama

MODEL_PATH = Path("models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

SYSTEM_PROMPT = """
You extract ordered items from sentences.

Return ONLY a JSON array.
No explanation.
No markdown.
No extra text.
No comments.

Format:
[
  {"name": "product name", "quantity": 1}
]

Rules:
- quantity must be integer
- if quantity missing, assume 1
- keep product wording natural from sentence

Example:

User: "Can I have two nutties and one bottle?"
Output:
[
  {"name": "nutties", "quantity": 2},
  {"name": "bottle", "quantity": 1}
]

Now extract from the next sentence.
"""

def clean_json_output(raw_output: str) -> str:
    """
    Cleans model output to isolate JSON array.
    """
    output = raw_output.strip()

    # Remove markdown if present
    output = output.replace("```json", "").replace("```", "").strip()

    # Extract only JSON array portion
    start = output.find("[")
    end = output.rfind("]")

    if start != -1 and end != -1:
        output = output[start:end+1]

    return output.strip()


def main():
    print("Loading model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=False
    )

    print("Model loaded.\n")

    test_inputs = [
        "I've got guests coming over, can you send me a couple of those chocolate boxes and maybe one lotion as well?",
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
            max_tokens=120,
            stop=["\n\n"]  # reduce trailing explanation
        )

        raw_output = response["choices"][0]["message"]["content"]

        print("RAW MODEL OUTPUT:")
        print(raw_output)

        cleaned = clean_json_output(raw_output)

        print("CLEANED OUTPUT:")
        print(cleaned)

        try:
            parsed = json.loads(cleaned)
            print("VALID JSON ✅")
            print("PARSED:", json.dumps(parsed, indent=2))
        except Exception as e:
            print("INVALID JSON ❌", e)

        print("-" * 60)


if __name__ == "__main__":
    main()