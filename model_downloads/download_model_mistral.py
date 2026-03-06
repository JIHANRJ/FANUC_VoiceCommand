"""Download Mistral-7B-Instruct model and cache it locally for offline use."""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/hub")

print(f"Downloading {MODEL_NAME}...")
print(f"Cache directory: {CACHE_DIR}")
print("This may take 10-20 minutes on a typical broadband connection.\n")

try:
    print("📥 Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    print("✅ Tokenizer downloaded.\n")
    
    print("📥 Downloading model (this is the large part, ~15 GB)...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    print("✅ Model downloaded and cached.\n")
    
    print("=" * 60)
    print("SUCCESS! Model is now cached locally.")
    print("You can now use order_parser.py offline.")
    print("=" * 60)
except Exception as e:
    print(f"❌ Error downloading model: {e}")
    exit(1)
