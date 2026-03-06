# Configuration Files

This folder contains domain data (context) and output schema definitions that drive the structured extraction system.

## Quick Concept

The system works like this:
1. **Context** (JSON file like `inventory.json`) – tells the extractor about your domain
2. **Output Schema** (JSON Schema file like `output_schema_*.json`) – tells the extractor what JSON structure to produce
3. **Input** (natural language text) – what you want to extract
4. **Output** (validated JSON) – extracted data matching your schema

## Context Files

### inventory.json (Example: Order Domain)

The domain context file defines the "world" your extractor operates in.

**Format:**
```json
{
  "inventory": {
    "Product Name": {
      "rack": "Location info",
      "section": "More location info"
    }
  },
  "product_mappings": {
    "alias": "Canonical Product Name"
  }
}
```

**How to customize:**
1. Duplicate this pattern for your domain
2. Replace `inventory` with your domain key (e.g., `tickets`, `customers`, `employees`)
3. Add your data with relevant attributes
4. Include a `mappings` section for aliases/synonyms

**Example for support tickets:**
```json
{
  "departments": {
    "Engineering": {"queue": "eng-queue-1", "sla_hours": 4},
    "Support": {"queue": "sup-queue-1", "sla_hours": 24}
  },
  "component_aliases": {
    "api": "API",
    "backend": "API"
  }
}
```

## Output Schema Files

Output schemas define the **structure and validation rules** for extracted data. They're JSON Schema files that guarantee output shape.

### Built-in Template

#### output_schema_order_capture.json

**Use case:** Order processing, inventory management

**Sample output:**
```json
{
  "intent": "order_capture",
  "entities": [
    {"name": "Ponds Cream", "quantity": 2}
  ],
  "status": "success"
}
```

This is the reference schema. Copy and modify it for your own domain.

## How to Create Your Own Schema

### Step 1: Define Your Data Structure

Think about what fields you need. Example:

```
Input: "John's pizza order: one margherita, two pepperonis, extra cheese"
Output: { name: "John", items: [...], special_requests: "extra cheese" }
```

### Step 2: Write JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "customer_name": {
      "type": "string"
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "item": {"type": "string"},
          "quantity": {"type": "number"}
        },
        "required": ["item", "quantity"]
      }
    },
    "special_requests": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed"]
    }
  },
  "required": ["customer_name", "items", "status"]
}
```

### Step 3: Save and Use

```bash
# Save as config/output_schema_pizza_order.json
python3 -c "
from ollama_granite_extractor import extract_with_schema_files
import json

result = extract_with_schema_files(
    text='John wants one margherita and two pepperonis plus extra cheese',
    context_file='config/inventory.json',
    schema_file='config/output_schema_pizza_order.json'
)
print(json.dumps(result, indent=2))
"
```

## File Naming Convention

Recommend naming output schemas like:
- `output_schema_[domain]_[variant].json`

Examples:
- `output_schema_order_capture.json` – Order extraction
- `output_schema_support_ticket_bug.json` – Bug report tickets
- `output_schema_crm_contact.json` – CRM contact info
- `output_schema_survey_nps.json` – NPS survey

## Tips

1. **Keep context fresh** – Update `inventory.json` as your domain data changes
2. **Version your schemas** – Keep old schemas in version control
3. **Test with examples** – Create sample inputs and verify output matches your schema
4. **Use meaningful enums** – Instead of `type: [1,2,3]`, use `enum: ["low", "medium", "high"]`
5. **Mark required fields** – Always include a `required` array to ensure critical fields are extracted
6. **Add descriptions** – Help future maintainers understand each field's purpose

## Usage in Code

### Loading from Files

```python
from ollama_granite_extractor import extract_with_schema_files

result = extract_with_schema_files(
    text="your input",
    context_file="config/your_context.json",
    schema_file="config/output_schema_your_domain.json"
)
```

### Inline (Python Dict/List)

```python
from ollama_granite_extractor import create_generic_extractor
import json

context = json.load(open("config/inventory.json"))
schema = json.load(open("config/output_schema_order_capture.json"))

extractor = create_generic_extractor()
result = extractor.extract_structured(
    text="I want 2 ponds cream",
    context=context,
    output_schema=schema
)
```

## Next Steps

- Check `sample_scripts/generic_schema_demo.py` for a working example
- Read main `README.md` for complete installation/setup
- Refer to `ollama_granite_extractor/SETUP.md` for Ollama troubleshooting
