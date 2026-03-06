# Sample Scripts

This folder contains example scripts for using the Ollama order extractor.

## Files

- **simple_demo.py** - Quick demo showing basic extraction usage
- **interactive_order_chat.py** - Full interactive chat interface

## Usage

### Run the simple demo
```bash
python3 simple_demo.py
```

Output:
```
Input: I want two ponds cream and 3 pringles
   2 item(s) found:
      • Ponds Cream x2 @ Rack 2
      • Pringles x3 @ Rack 2
```

### Run the interactive chat
```bash
python3 interactive_order_chat.py
```

Then type your orders:
```
Your order: I want two ponds cream and 3 pringles
SUCCESS: Extracted 2 item(s):
   1. Ponds Cream x 2
      Location: Rack 2 -> Section 2 -> Position 2
   2. Pringles x 3
      Location: Rack 2 -> Section 1 -> Position 2
```

## Integration

Both scripts use the modular extractor:

```python
from ollama_granite_extractor import create_extractor

extractor = create_extractor(inventory_path="config/inventory.json")
extractor.load_model()
result, raw = extractor.extract_order("your order")
```

See the scripts for detailed examples.
