# Model Downloads

Scripts to download various language models for testing and experimentation.

## 📥 Available Models

### 1. FLAN-T5 Base (Default - Recommended)
```bash
python3 download_model_flan_T5.py
```
- **License**: Apache 2.0 ✅ Commercial use OK
- **Size**: ~1GB
- **Parameters**: 250M
- **Used by**: `production_order_extractor.py` (default)
- **Performance**: Excellent for instruction following
- **Speed**: Fast on CPU and GPU

### 2. Phi-3 Mini (4K Context)
```bash
python3 download_model_Phi-3.py
```
- **License**: MIT ✅ Commercial use OK
- **Size**: ~2.4GB (GGUF format, quantized)
- **Parameters**: 3.8B
- **Context**: 4K tokens
- **Performance**: Good reasoning, larger than default
- **Speed**: Slower on CPU, good on GPU

### 3. Phi-2
```bash
python3 download_model_phi-2.py
```
- **License**: MIT ✅ Commercial use OK
- **Size**: ~5GB
- **Parameters**: 2.7B
- **Performance**: Strong instruction-following
- **Speed**: Medium on CPU, fast on GPU

### 4. TinyLlama
```bash
python3 download_model_tinyllama.py
```
- **License**: Apache 2.0 ✅ Commercial use OK
- **Size**: ~1.1GB (GGUF format, quantized)
- **Parameters**: 1.1B
- **Performance**: Lightweight, fast
- **Speed**: Very fast on CPU
- **Use Case**: Embedded systems, real-time

### 5. Mistral 7B
```bash
python3 download_model_mistral.py
```
- **License**: Apache 2.0 ✅ Commercial use OK
- **Size**: ~13GB
- **Parameters**: 7B
- **Context**: 8K tokens
- **Performance**: Very strong reasoning
- **Speed**: GPU recommended

## 🚀 Installation

Each script will:
1. Download the model from HuggingFace
2. Save to the `../models/` directory
3. Show download progress
4. Display model info when complete

Example:
```bash
python3 download_model_flan_T5.py
```

Output:
```
Downloading FLAN-T5 Base model...
Downloading: 100%|████████████| 1.0GB/1.0GB
✅ Model downloaded and cached
```

## 📊 Model Comparison

| Model | Size | Params | License | Speed | Quality | Recommended |
|---|---|---|---|---|---|---|
| FLAN-T5 Base | 1GB | 250M | Apache 2.0 | Very Fast | Excellent | ✅ YES |
| TinyLlama | 1.1GB | 1.1B | Apache 2.0 | Very Fast | Good | Embedded |
| Phi-2 | 5GB | 2.7B | MIT | Fast | Very Good | GPU |
| Phi-3 | 2.4GB | 3.8B | MIT | Medium | Excellent | GPU |
| Mistral 7B | 13GB | 7B | Apache 2.0 | Slow | Excellent | GPU Only |

## 💾 Storage Requirements

- FLAN-T5: 1GB
- TinyLlama: 1.1GB  
- Phi-2: 5GB
- Phi-3: 2.4GB
- Mistral: 13GB
- **Total available disk needed**: 25GB

## 🔧 Using Downloaded Models

After downloading, you can modify `production_order_extractor.py` to use different models:

```python
# For Phi-3 (GGUF):
from llama_cpp import Llama
llm = Llama(
    model_path="models/Phi-3-mini-4k-instruct-q4.gguf",
    n_ctx=2048,
    n_gpu_layers=-1
)

# For FLAN-T5 (default):
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
```

## 📝 Notes

- All models are loaded from HuggingFace Hub
- Models are cached after first download
- GGUF format models are pre-quantized for efficiency
- Commercial use is allowed for all models listed
- GPU recommended for anything larger than FLAN-T5

## 🎯 Recommendation

**For the order extraction system**: Use **FLAN-T5 Base** (default)
- Works great on CPU
- Fast inference
- Perfect for this task
- Commercial license
- Lowest resource usage

Only download larger models if you need:
- Better reasoning for complex orders
- Support for other languages
- More context (larger order lists)
- GPU acceleration available

---

Made for FANUC Voice Command System
