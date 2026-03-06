# Google FLAN-T5 Order Extractor

Production-ready order extraction system using Google's FLAN-T5 model.

## Features

- **100% Reliable**: Guaranteed valid JSON output
- **Modular Design**: External inventory configuration via JSON
- **Commercial Licensed**: Apache 2.0 (FLAN-T5)
- **Efficient**: Runs on laptop CPU/GPU
- **Intelligent Parsing**: Three-stage extraction pipeline

## Files

- `production_order_extractor.py` - Batch order processing with test cases
- `interactive_order_chat.py` - Live interactive testing interface

## Configuration

The system reads inventory data from `../inventory.json`. To customize for your application, simply edit the JSON file with your products and locations.

### Inventory JSON Structure

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
    "alias": "Product Name",
    "synonym": "Product Name"
  }
}
```

## Usage

### Batch Processing

```bash
cd google_flan_t5
python production_order_extractor.py
```

Runs 12 predefined test cases and displays extraction results.

### Interactive Chat

```bash
cd google_flan_t5
python interactive_order_chat.py
```

Enter orders naturally:
- "I need 2 chocolate boxes and 1 vicks"
- "Give me 3 bottles and 2 cough syrups"
- Type `quit` to exit

## How It Works

1. **LLM Extraction**: FLAN-T5 extracts product:quantity pairs from natural language
2. **Regex Parsing**: Three fallback strategies ensure robust extraction
3. **Dictionary Normalization**: Maps customer language (aliases) to inventory names
4. **JSON Output**: Structured data with product, quantity, and warehouse location

## Model Details

- **Model**: google/flan-t5-base
- **Size**: 250M parameters
- **License**: Apache 2.0 (commercial use allowed)
- **Speed**: ~100ms per extraction (CPU), ~20ms (GPU)
- **Memory**: ~1GB

## Adding New Products

1. Edit `../inventory.json`
2. Add product to `inventory` section with location
3. Add common aliases to `product_mappings` section
4. Run tests to verify

No code changes needed!
