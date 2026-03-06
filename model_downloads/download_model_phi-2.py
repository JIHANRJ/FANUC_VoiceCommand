from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "microsoft/phi-2"

print("Downloading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="cpu"
)

print("Model downloaded and cached.")