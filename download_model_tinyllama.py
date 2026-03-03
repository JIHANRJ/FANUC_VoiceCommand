# download_tinyllama.py

from pathlib import Path
from huggingface_hub import hf_hub_download

MODEL_REPO = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
MODEL_FILE = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

def main():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    print("Downloading TinyLlama...")

    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir=models_dir,
        local_dir_use_symlinks=False
    )

    print("Downloaded to:", model_path)

if __name__ == "__main__":
    main()