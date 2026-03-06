# FANUC Voice Command - Order Extraction System

This repository currently supports two active extraction implementations:
- `google_flan_t5` (kept as-is)
- `ollama_granite_extractor` (local Ollama, schema-constrained JSON)

## Active Project Structure

```
FANUC_VoiceCommand/
├── config/
│   └── inventory.json
├── sample_scripts/
│   ├── simple_demo.py
│   ├── interactive_order_chat.py
│   └── README.md
├── google_flan_t5/
│   ├── production_order_extractor.py
│   └── interactive_order_chat.py
├── ollama_granite_extractor/
│   ├── __init__.py
│   ├── strict_json_extractor.py
│   ├── README.md
│   └── SETUP.md
├── transcribe.py
└── requirements.txt
```

## Quick Start (Ollama Path)

```bash
cd /Users/rakesh/Desktop/FANUC_2026/FANUC_VoiceCommand
source VoiceComm/bin/activate
ollama serve
python3 sample_scripts/interactive_order_chat.py
```

Or run the simple demo:
```bash
python3 sample_scripts/simple_demo.py
```

## Programmatic Use (Modular)

```python
from ollama_granite_extractor import create_extractor

extractor = create_extractor(inventory_path="config/inventory.json")
extractor.load_model()
result, raw = extractor.extract_order("I want two ponds cream and 3 pringles")
print(result)
```

## Inventory Contract

The extractor expects this JSON shape at `config/inventory.json`:

```json
{
  "inventory": {
    "Product Name": {
      "rack": "Rack 1",
      "section": "Section 1",
      "position": "Position 1"
    }
  },
  "product_mappings": {
    "alias": "Product Name"
  }
}
```

## Notes

- All extraction runs locally on your machine with Ollama.
- `google_flan_t5` remains unchanged.
- For detailed Ollama setup, see `ollama_granite_extractor/SETUP.md`.
