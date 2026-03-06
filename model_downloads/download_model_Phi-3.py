from pathlib import Path
from huggingface_hub import hf_hub_download

MODEL_REPO = "microsoft/Phi-3-mini-4k-instruct-gguf"
MODEL_FILE = "Phi-3-mini-4k-instruct-q4.gguf"

def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    print("Downloading model...")

    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir=models_dir,
        local_dir_use_symlinks=False
    )

    print("\nModel downloaded successfully.")
    print("Saved to:", model_path)

if __name__ == "__main__":
    main()