# QUICKSTART Guide


## What Is This?

Convert natural language into validated JSON. Example:

```
Input:  "I want 2 ponds cream and 3 pringles"
Output: {"items": [
  {"name": "Ponds Cream", "quantity": 2},
  {"name": "Pringles", "quantity": 3}
]}
```



---

## Prerequisites

- **Python 3.8+** (check: `python3 --version`)
- **Internet** (one-time to download model)
- **8+ GB free disk space**
- **4+ GB RAM**

---

## Step 1: Install Ollama 

The local LLM that does the extraction.

### macOS

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version
```

### Linux (Ubuntu/Debian)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

### Linux (Fedora/RHEL)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

### Windows

1. Download [OllamaSetup.exe](https://ollama.com/download/windows)
2. Run, accept defaults
3. **Restart your terminal**
4. Verify: `ollama --version`

---

## Step 2: Download the Model 

```bash
# This downloads ~8GB (one-time)
ollama pull llama3.1:latest

# Verify
ollama list
# Should show: llama3.1:latest
```

---

## Step 3: Start Ollama Server (Keep Running)

**Open a terminal and run** (leave it running):

```bash
ollama serve
# You'll see: Ollama is running at http://127.0.0.1:11434
```

**Don't close this terminal!** All extraction requires this server.

---

## Step 4: Setup Python Project (2 minutes)

**In a NEW terminal** (while step 3 runs):

```bash
# Navigate to project
cd /path/to/this/repo

# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

---

## Step 5: Run Your First Extraction (1 minute)

### Quick Demo (No Interaction)

```bash
python3 sample_scripts/simple_demo.py
```

Output: JSON of 3 test orders.

### Try It Yourself (Interactive)

```bash
python3 sample_scripts/interactive_order_chat.py
```

Then type:
```
Your order: I want 2 ponds cream and 3 pringles
```

Output: JSON with extracted items.

Type `exit` to quit.

### Generic Extraction (Any Domain)

```bash
python3 sample_scripts/generic_schema_demo.py
```

Output: Generic extraction with inventory and schema from config files.

---

## Success! What's Next?

### Using for Your Own Domain

1. Create context file: `config/my_context.json`
   ```json
   {
     "items": {
       "Widget A": {"price": 50},
       "Widget B": {"price": 75}
     }
   }
   ```

2. Create output schema: `config/my_schema.json`
   ```json
   {
     "type": "object",
     "properties": {
       "products": {
         "type": "array",
         "items": {
           "type": "object",
           "properties": {
             "name": {"type": "string"},
             "quantity": {"type": "number"}
           }
         }
       }
     }
   }
   ```

3. Extract in Python:
   ```python
   from ollama_granite_extractor import extract_with_schema_files
   
   result = extract_with_schema_files(
       text="I need 5 widget A",
       context_file="config/my_context.json",
       schema_file="config/my_schema.json"
   )
   print(result)
   ```

### Example Template

We provide a reference schema:
- `output_schema_order_capture.json` – Order extraction example

Copy and modify this for your domain. See `config/README.md` for details on creating custom schemas.

### Full Documentation

- **README.md** – Complete feature overview
- **config/README.md** – Config/schema details
- **ollama_granite_extractor/SETUP.md** – Detailed Ollama setup & troubleshooting
- **sample_scripts/README.md** – Sample code examples

---

## Troubleshooting

### Slow Performance

- **First run is slower** as model loads into memory
- For faster extraction, try smaller model:
  ```bash
  ollama pull granite:latest
  OLLAMA_MODEL=granite:latest python3 sample_scripts/interactive_order_chat.py
  ```

### Out of Memory

Use a smaller model:
```bash
ollama pull granite:latest  # Only ~3GB
OLLAMA_MODEL=granite:latest python3 sample_scripts/simple_demo.py
```

---

## Terminal Tips

### Keep Ollama Running

Don't close the Ollama terminal. To organize your workspace:

**Terminal 1 (Ollama):**
```bash
ollama serve
# Keep this open
```

**Terminal 2 (Your Work):**
```bash
cd /path/to/repo
source venv/bin/activate
python3 sample_scripts/simple_demo.py
```

### Fast Development

Define shell function for quick testing:

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
test_extract() {
  source /path/to/repo/venv/bin/activate
  cd /path/to/repo
  python3 -c "
from ollama_granite_extractor import extract_with_schema_files
import json
result = extract_with_schema_files(
    text='$1',
    context_file='config/inventory.json',
    schema_file='config/output_schema_order_capture.json'
)
print(json.dumps(result, indent=2))
"
}

# Usage:
test_extract "I want 2 cola"
```

**Windows (PowerShell):**
```powershell
# Add to $PROFILE
function test-extract {
    param($text)
    cd "C:\path\to\repo"
    .\venv\Scripts\Activate.ps1
    python3 -c "
from ollama_granite_extractor import extract_with_schema_files
import json
result = extract_with_schema_files(
    text='$text',
    context_file='config/inventory.json',
    schema_file='config/output_schema_order_capture.json'
)
print(json.dumps(result, indent=2))
"
}

# Usage:
test-extract "I want 2 cola"
```

---

## Next: Python API Reference

Once running, explore the modular API:

### Domain-Specific Extraction

```python
from ollama_granite_extractor import create_extractor

# Quick setup
extractor = create_extractor(inventory_path="config/inventory.json")
extractor.load_model()

# Extract order
result, raw = extractor.extract_order("I want 2 ponds cream")
print(result)  # Guaranteed valid JSON
```

### Generic Extraction (Any Domain)

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
print(result)  # Guaranteed matches schema
```

### Batch Processing

```python
from ollama_granite_extractor import create_extractor

extractor = create_extractor()
extractor.load_model()

orders = [
    "I want 2 coca cola",
    "Get me ponds cream",
    "3 pringles please"
]

for order_text in orders:
    result, _ = extractor.extract_order(order_text)
    print(f"Order: {result['extracted']['items']}")
```

---

## Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from ollama_granite_extractor import create_generic_extractor
import json

app = Flask(__name__)
extractor = create_generic_extractor()

@app.route("/extract", methods=["POST"])
def extract():
    data = request.json
    result = extractor.extract_structured(
        text=data["text"],
        context=json.load(open("config/inventory.json")),
        output_schema=json.load(open("config/output_schema_order_capture.json"))
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000)
```

### Command-Line Tool

```bash
# Create a script: extract.py
from ollama_granite_extractor import extract_with_schema_files
import json
import sys

text = sys.argv[1] if len(sys.argv) > 1 else "help"

result = extract_with_schema_files(
    text=text,
    context_file="config/inventory.json",
    schema_file="config/output_schema_order_capture.json"
)
print(json.dumps(result, indent=2))

# Usage:
# python3 extract.py "I want 2 ponds cream"
```

---

## Getting Help

1. **Setup issues?** Check `ollama_granite_extractor/SETUP.md`
2. **Config questions?** See `config/README.md`
3. **Sample code?** Review `sample_scripts/README.md`
4. **Features?** Read main `README.md`
5. **Still stuck?** Check Ollama server is running (step 3)

---

## Thank you !

 
