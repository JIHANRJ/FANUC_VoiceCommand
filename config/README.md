# Configuration Files

This folder contains configuration files for the order extraction system.

## inventory.json

The main configuration file that defines:

- **inventory**: Product catalog with warehouse locations
  - Each product has `rack`, `section`, and `position`
  - Edit these to match your actual warehouse layout

- **product_mappings**: Aliases and synonyms
  - Maps customer language (e.g., "ponds") to canonical product names (e.g., "Ponds Cream")
  - Add more mappings as needed for your product names

### Example format:

```json
{
  "inventory": {
    "Ponds Cream": {
      "rack": "Rack 2",
      "section": "Section 2",
      "position": "Position 2"
    }
  },
  "product_mappings": {
    "ponds cream": "Ponds Cream",
    "ponds": "Ponds Cream",
    "cream": "Ponds Cream"
  }
}
```

### To customize:

1. Edit `inventory.json` directly
2. Add your products under `inventory`
3. Add aliases under `product_mappings`
4. No code changes needed—extractor reads config on startup

All sample scripts automatically load from this location.
