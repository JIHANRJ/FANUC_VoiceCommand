# Structured Data Extractor

A professional-grade **local LLM-powered JSON extractor** that converts natural language input into validated JSON output. Works with any domain—order processing, ticket creation, data collection, etc. All processing happens on your machine; no external APIs.

## What This Does

Given:
- **Context** (a JSON dictionary of your domain data, e.g., product inventory)
- **Input** (natural language text)
- **Output Schema** (JSON Schema defining your desired output structure)

This system returns **validated JSON** matching your schema, using a local LLM with schema-constrained generation.

## Key Features

✓ **Local processing** – No external APIs; all inference on your machine  
✓ **Guaranteed valid JSON** – Schema validation built into model generation  
✓ **Domain agnostic** – Works for orders, tickets, surveys, CRM data, anything  
✓ **Easy setup** – One-command installation, works on Windows/Mac/Linux  
✓ **Modular & reusable** – Python API and CLI tools included  

## Installation

### 1. Install Ollama (One-Time)

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Or download [Ollama.dmg](https://ollama.com/download) and drag to Applications.

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux (Fedora/RHEL):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
1. Download [OllamaSetup.exe](https://ollama.com/download/windows)
2. Run installer
3. Restart your terminal after installation

Verify:
```bash
ollama --version
```

### 2. Clone/Setup Project

```bash
# Navigate to project directory
cd /path/to/this/repo

# Create virtual environment (optional but recommended)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Ollama Server

**In a separate terminal window** (keep this running):

```bash
ollama serve
# You should see: Ollama is running at http://127.0.0.1:11434
```

### 4. Pull Model (in another terminal)

```bash
# Download the model (one-time, ~4GB)
ollama pull llama3.1:latest
```

Done! Now you can run extraction.

## Quick Start

### Use the Interactive Chat (Order Example)

```bash
python3 sample_scripts/interactive_order_chat.py
```

Then type your orders:
```
Your order: I want 2 ponds cream and 3 pringles
```

Output (JSON):
```json
{
  "status": "success",
  "input": "I want 2 ponds cream and 3 pringles",
  "structured_output": {
    "intent": "order_capture",
    "entities": [
      {"name": "Ponds Cream", "quantity": 2},
      {"name": "Pringles", "quantity": 3}
    ],
    "status": "success"
  }
}
```

### Run Simple Demo

```bash
python3 sample_scripts/simple_demo.py
```

### Use for Your Own Domain

Create your context (`inventory.json`) and schema (`output_schema.json`), then:

```python
from ollama_granite_extractor import create_generic_extractor

# 1. Load your context and schema
context = {
  "products": {
    "Widget A": {"price": 50, "stock": 100},
    "Widget B": {"price": 75, "stock": 60}
  }
}

schema = {
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "product": {"type": "string"},
          "quantity": {"type": "number"}
        }
      }
    }
  }
}

# 2. Extract
extractor = create_generic_extractor()
result = extractor.extract_structured(
    text="I need 5 widget A and 2 widget B",
    context=context,
    output_schema=schema
)

print(result)
# Output: {"items": [{"product": "Widget A", "quantity": 5}, ...]}
```

## File Structure

```
.
├── README.md                                    # This file
├── QUICKSTART.md                                # Step-by-step guide
├── requirements.txt                             # Python dependencies
├── ollama_granite_extractor/                    # Core extraction module
│   ├── __init__.py
│   ├── strict_json_extractor.py                 # OrderExtractor class
│   ├── generic_schema_extractor.py              # GenericSchemaExtractor class
│   ├── README.md
│   └── SETUP.md                                 # Detailed Ollama setup
├── sample_scripts/
│   ├── README.md
│   ├── simple_demo.py                           # Basic order extraction demo
│   ├── interactive_order_chat.py                # Interactive order chat
│   └── generic_schema_demo.py                   # Generic extraction (any domain)
├── config/
│   ├── inventory.json                           # Example context (product data)
│   ├── output_schema_order_capture.json         # Example output schema
│   └── README.md                                # Configuration guide
└── models/                                      # Pre-downloaded GGUF models
```

## Configuration

### Define Your Context (Domain Data)

Create a JSON file with your domain data. Example: `config/inventory.json`

```json
{
  "inventory": {
    "Ponds Cream": {
      "rack": "Rack 2",
      "section": "Section 2",
      "position": "Position 2"
    },
    "Pringles": {
      "rack": "Rack 2",
      "section": "Section 1",
      "position": "Position 2"
    }
  },
  "product_mappings": {
    "ponds": "Ponds Cream",
    "cream": "Ponds Cream",
    "chips": "Pringles"
  }
}
```

### Define Your Output Schema

Create a JSON Schema file. Example: `config/output_schema_order_capture.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "description": "Classification of the request"
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "quantity": {"type": "number"}
        },
        "required": ["name", "quantity"]
      }
    },
    "status": {
      "type": "string",
      "enum": ["success", "partial"]
    }
  },
  "required": ["intent", "entities", "status"]
}
```

See `config/README.md` for more templates.

## Architecture: Two Extractors

This system provides two extraction approaches:

### 1. OrderExtractor (Domain-Specific)

**Use when:** You're building an order/inventory system with location tracking.

**Features:**
- Pre-built order capture logic
- Product normalization and mapping
- Warehouse location tracking (rack/section/position)
- Quantity extraction with fallback parsing
- Optimized prompts for order domain

**Code:**
```python
from ollama_granite_extractor import create_extractor

extractor = create_extractor(inventory_path="config/inventory.json")
extractor.load_model()

# Extract a single order
result, raw_output = extractor.extract_order("I want 2 ponds cream and 3 pringles")
print(result)  # Guaranteed valid JSON with location data
```

### 2. GenericSchemaExtractor (Domain-Agnostic)

**Use when:** You need extraction for ANY domain (tickets, feedback, CRM, etc.).

**Features:**
- Accepts arbitrary context JSON (your domain data)
- Accepts arbitrary output schema JSON (your desired structure)
- No hardcoded logic - fully configurable
- Works with any business domain
- Schema-constrained generation guarantees valid output

**Code:**
```python
from ollama_granite_extractor import create_generic_extractor
import json

# Load your domain context and output schema
context = json.load(open("config/inventory.json"))
schema = json.load(open("config/output_schema_order_capture.json"))

extractor = create_generic_extractor()
result = extractor.extract_structured(
    text="I want 2 ponds cream",
    context=context,
    output_schema=schema
)
print(result)  # Guaranteed matches your schema
```

**Or use the convenience function:**
```python
from ollama_granite_extractor import extract_with_schema_files

# Direct file loading
result = extract_with_schema_files(
    text="user input",
    context_file="config/my_context.json",
    schema_file="config/my_schema.json"
)
```

### Which Should You Use?

| Use Case | Recommended Extractor |
|----------|----------------------|
| Order processing with inventory | **OrderExtractor** |
| Any other domain (tickets, CRM, surveys) | **GenericSchemaExtractor** |
| Custom business logic needed | Start with **GenericSchemaExtractor** |
| Need location tracking | **OrderExtractor** |

## Examples

See `sample_scripts/README.md` for detailed examples.

- `simple_demo.py` – Hardcoded order examples (no interaction)
- `interactive_order_chat.py` – Interactive chat for orders
- `generic_schema_demo.py` – Generic extraction with any domain

## Performance Notes

- **First run:** Model download ~4GB (one-time)
- **Extraction speed:** 2-5 seconds per request (depending on input length)
- **Hardware:** Works best with Metal acceleration (macOS/AMD) or CUDA (NVIDIA GPU)
- **CPU-only:** Supported on all platforms; slower but functional

## Troubleshooting

### "Connection refused" Error
```
Make sure Ollama server is running in a separate terminal:
  ollama serve
```

### "Model not found" Error
```
Download the model:
  ollama pull llama3.1:latest
```

### Slow Performance
- CPU extraction is slower; GPU acceleration (Metal/CUDA) recommended
- First run may be slower as model loads into memory
- Reduce input length for faster extraction

### Custom Models
To use a different model:
```python
from ollama_granite_extractor import create_extractor

extractor = create_extractor(
  inventory_path="config/inventory.json",
  model_name="mistral:latest"  # or granite:latest when available
)
extractor.load_model()
result, raw = extractor.extract_order("your text")
```

## License

Apache 2.0 – Safe for commercial use.

## Support

For issues or questions:
1. Check `QUICKSTART.md` for setup help
2. See `ollama_granite_extractor/SETUP.md` for detailed Ollama setup
3. Review `config/README.md` for configuration examples
4. Check sample scripts in `sample_scripts/README.md`
