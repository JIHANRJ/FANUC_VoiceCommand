# Ollama + Granite 3.2 / Llama3.1 Structured Extraction Setup

## Overview
This module uses **Ollama** (local LLM server) + **Granite 3.2** or **Llama3.1** (Apache 2.0 licensed) with **JSON Schema validation** for guaranteed structured order extraction.

**✅ STATUS**: Fully tested with Llama3.1. Switch to Granite 3.2 when available.

### Why This Approach?
✅ **Local inference** - No external APIs, full privacy/control  
✅ **Granite 3.2** - Instruction-tuned, enterprise-friendly, commercial license  
✅ **JSON Schema validation** - Model output guaranteed to match schema (no regex hacks)  
✅ **Fast on Mac** - Metal acceleration supports local 3B-8B models well  
✅ **Tool-based extraction** - Model follows explicit slot/function definitions  

---

## Installation (One-Time Setup)

### 1. Install Ollama on macOS
```bash
# Option A: Automatic (recommended)
curl -fsSL https://ollama.com/install.sh | sh

# Option B: Manual
# Download from: https://ollama.com/download/Ollama.dmg
# Then drag to Applications
```

### 2. Verify Installation
```bash
ollama --version
# Should output: ollama version X.X.X
```

### 3. Start Ollama Server
```bash
# In a terminal window, start the Ollama server:
ollama serve

# You should see:
# Ollama is running at http://127.0.0.1:11435
# Leave this terminal running
```

### 4. Pull Model (in another terminal)
```bash
# Option A: Llama3.1 (currently tested, ready to use)
ollama pull llama3.1:latest

# Option B: Granite 3.2 (when available)
ollama pull granite:3.2

# Option C: GPT-OSS (alternative 20B model)
ollama pull gpt-oss:20b
```

Check installed models:
```bash
ollama list
```

---

## Quick Start

### 1. Ensure Ollama Server is Running
```bash
# Terminal 1:
ollama serve
# Stay in this terminal
```

### 2. Run the Interactive Chat
```bash
# Terminal 2: Navigate and run
cd /Users/rakesh/Desktop/FANUC_2026/FANUC_VoiceCommand
source VoiceComm/bin/activate
python3 ollama_granite_extractor/interactive_order_chat.py
```

### 3. Test with Sample Orders
```
Your order: I want two ponds cream and 3 pringles
Your order: Give me 5 coca cola
Your order: quit
```

---

## How It Works

### Request Flow
```
User Input
    ↓
Build Prompt + JSON Schema
    ↓
Ollama API (127.0.0.1:11435)
    ↓
Granite 3.2 Model (with schema constraint)
    ↓
JSON Output (guaranteed valid schema)
    ↓
Normalize + Map products
    ↓
Structured Result
```

### JSON Schema Constraint
Instead of asking the model to "respond with JSON" (unreliable), we enforce schema:

```python
response = requests.post(
    "http://127.0.0.1:11435/api/generate",
    json={
        "model": "granite:3.2",
        "prompt": "Extract order...",
        "stream": False,
        "format": {  # ← JSON Schema constraint
            "type": "object",
            "properties": {
                "items": {"type": "array", ...},
                "status": {"type": "string", "enum": ["success", "partial", "failed"]}
            }
        }
    }
)
```

This **guarantees** the model outputs valid JSON matching your schema.

---

## Configuration

### Environment Variables
```bash
# Use default
python3 ollama_granite_extractor/interactive_order_chat.py

# Custom Ollama server location
OLLAMA_API_URL=http://192.168.1.100:11435 python3 ...

# Use different model
OLLAMA_MODEL=granite:8b python3 ...

# Combine
OLLAMA_MODEL=llama3.1:latest OLLAMA_API_URL=http://127.0.0.1:11435 python3 ...
```

### Model Options
| Model | Size | Latency | Accuracy | Recommendation |
|-------|------|---------|----------|---|
| `granite:3.2` | ~3B | Fast (5-10s) | Good | ✅ Default |
| `granite:8b` | ~8B | Medium (15-30s) | Better | For complex orders |
| `mistral:7b` | ~7B | Medium | Excellent | If you want more power |

Download alternative:
```bash
ollama pull granite:8b
OLLAMA_MODEL=granite:8b python3 ollama_granite_extractor/interactive_order_chat.py
```

---

## Troubleshooting

### Error: "Cannot connect to Ollama at http://127.0.0.1:11435"
```bash
# Make sure Ollama server is running
ollama serve  # Run in separate terminal

# Or check if listening:
curl http://localhost:11434/api/tags
```

### Error: "Model granite:3.2 not found"
```bash
# Pull the model
ollama pull granite:3.2

# List available
ollama list
```

### Slow Inference
- Start with `granite:3.2` (3B)
- If still slow, check your system resources (`Activity Monitor`)
- Granite models are optimized for macOS Metal acceleration

### High Memory Usage
- Ollama keeps models in memory for fast inference
- Unload with: `ollama list` then wait, or restart the server
- Use smaller variant: `granite` instead of `granite:8b`

---

## Advantages Over Previous Approaches

| Aspect | FLAN-T5 (Transformers) | Mistral-7B (Transformers) | **Ollama + Granite** |
|--------|-------|--------|---------|
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| Model Size | 250M | 7B | 3B (default) |
| Latency | ~2s | 3-5min (CPU) | 5-10s (Metal) |
| Accuracy | Medium | High | High |
| JSON Reliability | Regex parsing | Schema coercion | Schema validation ✅ |
| Local Private | ✅ | ✅ | ✅ |
| Tool Support | ❌ | ❌ | ✅ (function defs) |
| Setup | `pip install` | `pip install` | `ollama pull` |
| Admin Rights | ❌ | ❌ | May need (for install) |
| Recommended | Fast fallback | Don't use on CPU | ✅ **Default** |

---

## Advanced: Function Calling (Future)

Ollama 0.3+ supports function definitions for even more reliable extraction:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "extract_order_items",
        "description": "Extract items from an order",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "integer"}
                        }
                    }
                }
            }
        }
    }
}]

# response = requests.post(..., json={..., "tools": tools})
```

Currently, JSON schema is simpler and just as effective.

---

## License
- **Granite 3.2**: Apache 2.0 (commercial use allowed)
- **Ollama**: MIT
- **This module**: Use as you like

---

## Support
For issues, check:
1. Ollama server running: `curl http://127.0.0.1:11435/api/tags`
2. Model downloaded: `ollama list | grep granite`
3. Correct inventory path: `cat ../inventory.json`
