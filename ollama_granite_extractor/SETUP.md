# Ollama + Llama3.1 / Granite 3.2 Structured Extraction Setup

## Overview

This module uses **Ollama** (local LLM server) + **Llama3.1** or **Granite 3.2** (both open-source) with **JSON Schema validation** for guaranteed structured data extraction.

**Current Status**: Fully tested with Llama3.1 on macOS, Linux, and Windows. Granite 3.2 ready when released.

### Why This Approach?

- **Local inference** – No external APIs, full privacy and control
- **Open-source models** – Apache 2.0 licensed (commercial use allowed)
- **JSON Schema validation** – Model output guaranteed to match your schema
- **Fast on all platforms** – Metal acceleration (Mac), CUDA (NVIDIA GPU), or CPU
- **Modular & reusable** – Python API works identically across all OSes

---

## Installation by Platform

### macOS

#### Step 1: Install Ollama

Option A (Automatic, recommended):
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Option B (Manual):
1. Download [Ollama.dmg](https://ollama.com/download/Ollama-darwin.zip)
2. Unzip and run installer
3. Or download [Ollama.dmg](https://ollama.com/download) and drag to Applications

#### Step 2: Verify Installation

```bash
ollama --version
# Should output: ollama version X.X.X
```

#### Step 3: Start Ollama Server

Open a terminal and run (keep this terminal open):
```bash
ollama serve
# You should see: Ollama is running at http://127.0.0.1:11434
```

#### Step 4: Pull Model (in another terminal)

```bash
# Download Llama3.1 (currently recommended, ~8GB)
ollama pull llama3.1:latest

# Or Granite 3.2 (when available)
ollama pull granite:latest
```

Check installation:
```bash
ollama list
```

---

### Linux (Ubuntu/Debian)

#### Step 1: Install Ollama

```bash
# Download and install
curl -fsSL https://ollama.com/install.sh | sh

# Or manual installation
# Download from: https://ollama.com/download/linux
# Follow the installer
```

#### Step 2: Verify Installation

```bash
ollama --version
```

#### Step 3: Start Ollama Server

Option A (foreground, for testing):
```bash
ollama serve
# You should see: Ollama is running at http://127.0.0.1:11434
```

Option B (background, as service via systemd):
```bash
# Ollama installs as a service automatically
sudo systemctl start ollama
sudo systemctl enable ollama  # Start on boot

# Check status
sudo systemctl status ollama

# View logs
journalctl -u ollama
```

#### Step 4: Pull Model (in another terminal)

```bash
ollama pull llama3.1:latest
ollama list
```

#### Step 5: Set Proper Permissions (if needed)

If you get permission errors:
```bash
# Add your user to ollama group
sudo usermod -a -G ollama $USER
newgrp ollama

# Or allow ollama socket access
sudo chmod 777 /run/ollama/ollama.sock
```

---

### Linux (Fedora/RHEL/CentOS)

#### Step 1: Install Ollama

```bash
# Option A: Using curl
curl -fsSL https://ollama.com/install.sh | sh

# Option B: Using dnf/yum (if Ollama is in repos)
sudo dnf install ollama
# or
sudo yum install ollama
```

#### Step 2: Verify Installation

```bash
ollama --version
```

#### Step 3: Enable and Start Service

```bash
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

#### Step 4: Pull Model

```bash
ollama pull llama3.1:latest
ollama list
```

---

### Windows 10/11

#### Step 1: Install Ollama

1. Download [OllamaSetup.exe](https://ollama.com/download/windows)
2. Run the installer
3. Accept default installation (typically `C:\Users\{YourUsername}\AppData\Local\Ollama\`)
4. **Restart your terminal/PowerShell after installation**

#### Step 2: Verify Installation

Open PowerShell or Command Prompt:
```powershell
ollama --version
# Should output: ollama version X.X.X
```

#### Step 3: Start Ollama Server

```powershell
# Keep this terminal open while you work
ollama serve
# You should see: Ollama is running at http://127.0.0.1:11434
```

#### Step 4: Pull Model (in another PowerShell/CMD)

```powershell
ollama pull llama3.1:latest
ollama list
```

#### Step 5: (Optional) Run as Windows Service

For persistent background service:
```powershell
# This is handled automatically by Ollama installer
# Service may already be running

# Check if running:
Get-Service | grep ollama
```

---

## Quick Start (All Platforms)

### 1. Clone/Setup Project

```bash
# Navigate to project
cd /path/to/this/repo

# Create virtual environment
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

### 2. Ensure Ollama Server Running

**Terminal 1** (keep running):
```bash
ollama serve
```

### 3. Run Interactive Chat

**Terminal 2:**
```bash
# Activate venv first (if not already)
python3 sample_scripts/interactive_order_chat.py
```

### 4. Test with Sample Orders

```
Your order: I want two ponds cream and 3 pringles
Your order: Give me 5 coca cola
Your order: quit
```

---

## How It Works

### Request Flow

```
User Input (natural language)
    ↓
Build Prompt + JSON Schema
    ↓
Ollama API (127.0.0.1:11434)
    ↓
Llama3.1 Model (with schema constraint)
    ↓
JSON Output (guaranteed valid per schema)
    ↓
Normalize & Map products (if order domain)
    ↓
Structured Result (to Python/JSON)
```

### Schema Validation

Instead of asking the model to "respond with JSON" (unreliable), we enforce schema during generation:

```python
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "llama3.1:latest",
        "prompt": "Extract: I want 2 ponds cream",
        "stream": False,
        "format": {  # ← JSON Schema constraint
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "items": {"type": "array"},
                "status": {"type": "string", "enum": ["success", "partial"]}
            }
        }
    }
)
```

This **guarantees** valid JSON output matching your schema.

---

## Configuration

### Environment Variables

```bash
# All platforms - set model/server location

# macOS/Linux:
export OLLAMA_MODEL=llama3.1:latest
export OLLAMA_API_URL=http://127.0.0.1:11434
python3 sample_scripts/interactive_order_chat.py

# Windows (PowerShell):
$env:OLLAMA_MODEL="llama3.1:latest"
$env:OLLAMA_API_URL="http://127.0.0.1:11434"
python3 sample_scripts/interactive_order_chat.py

# Windows (Command Prompt):
set OLLAMA_MODEL=llama3.1:latest
set OLLAMA_API_URL=http://127.0.0.1:11434
python3 sample_scripts/interactive_order_chat.py
```

### Model Options

| Model | Download Size | RAM Usage | Latency | Quality | Notes |
|-------|---|---|---|---|---|
| `llama3.1:latest` | ~8GB | ~8GB | 3-8s | Excellent | **Recommended** |
| `llama3.1:8b` | ~8GB | ~8GB | 3-8s | Excellent | Same as latest |
| `llama3.1:70b` | ~40GB | ~40GB | 30-60s | Superior | For complex tasks, needs 64GB RAM |
| `granite:latest` | ~3GB | ~3GB | 1-3s | Good | Faster, good for simple extraction |
| `mistral:latest` | ~5GB | ~5GB | 2-5s | Excellent | Alternative, very fast |

Download and use alternative:
```bash
ollama pull granite:latest
ollama run granite:latest "test prompt"

# Use in code
export OLLAMA_MODEL=granite:latest
python3 sample_scripts/interactive_order_chat.py
```

---

## Troubleshooting

### macOS

**Issue: "Cannot connect to Ollama"**
```bash
# Make sure Ollama is running:
ollama serve  # Run in separate terminal
# Then try again
```

**Issue: "Model not found"**
```bash
ollama pull llama3.1:latest
ollama list  # Verify
```

**Issue: Slow performance**
- Check Activity Monitor: confirm Metal acceleration is working
- First run is slower (model loads into memory)
- Restart Ollama server if memory is stuck

---

### Linux

**Issue: "Permission denied" when running ollama**
```bash
# Add user to ollama group
sudo usermod -a -G ollama $USER
newgrp ollama
# Logout and login, or restart terminal
```

**Issue: "Connection refused"**
```bash
# Check if service is running
sudo systemctl status ollama

# Start service if not running
sudo systemctl start ollama

# View logs
journalctl -u ollama -f
```

**Issue: Out of memory**
```bash
# Check available RAM
free -h

# For systems with limited RAM, use smaller model
ollama pull granite:latest  # ~3GB instead of ~8GB
OLLAMA_MODEL=granite:latest python3 sample_scripts/interactive_order_chat.py
```

**Issue: GPU not detected (NVIDIA)**
```bash
# Verify CUDA
nvidia-smi

# If no CUDA, Ollama falls back to CPU (slower but functional)
```

---

### Windows

**Issue: "ollama is not recognized as an internal or external command"**
```powershell
# Restart PowerShell/CMD after installation
# Close and reopen terminal window
```

**Issue: "Connection refused" on port 11434**
```powershell
# Make sure Ollama server is running (separate cmd/PowerShell window)
ollama serve

# Check if running on different port
netstat -ano | findstr :11434
```

**Issue: Firewall blocking connection**
```powershell
# Allow Ollama through firewall
# Right-click PowerShell as Admin, then:
New-NetFirewallRule -DisplayName "Ollama" -Direction Inbound -Program "C:\Users\$env:USERNAME\AppData\Local\Ollama\ollama.exe" -Action Allow
```

**Issue: Out of memory**
```powershell
# Use smaller model
ollama pull granite:latest
set OLLAMA_MODEL=granite:latest
python3 sample_scripts/interactive_order_chat.py
```

---

## Performance Comparison

### macOS (Apple Silicon M1/M2)

| Model | Download | First Run | Subsequent | Memory |
|-------|----------|-----------|-----------|--------|
| Granite 3.2 | ~3GB | 3-5s | 1-2s | 4GB |
| Llama3.1 | ~8GB | 8-12s | 3-5s | 8GB |
| Llama3.1 70B | ~40GB | 30-60s | 20-40s | 40GB |

### Linux (CPU)

| Model | Download | Time | Memory | Notes |
|-------|----------|------|--------|-------|
| Granite | ~3GB | 10-20s | 4GB | Acceptable |
| Llama3.1 | ~8GB | 30-60s | 8GB | Slow but works |
| NVIDIA GPU | Varies | 3-8s | 6-10GB | Much faster |

### Windows 10/11

| Model | OS Version | Time | Memory | GPU Support |
|-------|-----------|------|--------|---|
| Granite | Any | 5-10s | 4GB | CPU only |
| Llama3.1 | Any | 5-10s | 8GB | CUDA (NVIDIA) |

---

## Cross-Platform API (All the Same!)

The Python API works identically across macOS, Linux, and Windows:

```python
from ollama_granite_extractor import create_generic_extractor

# Works identically on Mac, Linux, Windows
extractor = create_generic_extractor()
result = extractor.extract_structured(
    text="I want 2 ponds cream",
    context={...},
    output_schema={...}
)
print(result)  # JSON dict, same on all platforms
```

No OS-specific code needed in your application!

---

## Advanced: Custom Ollama Server

Run Ollama on a different machine/port:

```bash
# On server machine (e.g., 192.168.1.100):
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# On client machine:
export OLLAMA_API_URL=http://192.168.1.100:11434
python3 sample_scripts/interactive_order_chat.py
```

Works across networks, useful for:
- Shared team model server
- Powerful machine handles inference
- Lightweight client machines

---

## License

- **Llama3.1**: Meta (Community License)
- **Granite**: IBM (Apache 2.0 – commercial use OK)
- **Ollama**: MIT
- **This module**: Use freely

---

## Resources

- Ollama docs: https://ollama.com
- Model library: https://ollama.com/library
- Llama3.1: https://llama.meta.com
- Granite: https://github.com/ibm-granite

## Support

Stuck? Check:
1. Ollama running: `ollama serve` in separate terminal
2. Model downloaded: `ollama list`
3. Correct port: `curl http://127.0.0.1:11434/api/tags`
4. Dependencies: `pip list | grep requests`
