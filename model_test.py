# python3 model_test.py
# should get a output of "Hello! How can I assist you today?" or similar, demonstrating the model is working.
from llama_cpp import Llama
from pathlib import Path

MODEL_PATH = Path("models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

def main():
    print("Loading model...")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=False
    )

    print("Model loaded successfully.\n")

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        temperature=0
    )

    output = response["choices"][0]["message"]["content"]

    print("Output:")
    print(output)

if __name__ == "__main__":
    main()