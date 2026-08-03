# 🌾 AgronPulse AI: Global Multi-Agent Multimodal Agricultural Diagnostics

**AgronPulse AI** is an enterprise-grade, edge-first multi-agent framework designed to decode complex, qualitative agricultural signs (such as leaf lesions, structural spotting, or soil textures) and translate them directly into quantitative, actionable agronomic insights.

The platform utilizes a decoupled, asynchronous pattern combining **LangGraph**, **FastAPI**, **ChromaDB**, and **Ollama** (`gemma4:e4b` + `nomic-embed-text`) to synthesize leaf vision analysis with live microclimatic variables and regional regulatory constraints.

---

## 🏗️ High-Level System Architecture


---

## ⚡ Functional Matrix

* **Qualitative Sign Decoding:** Interprets macroscopic leaf imagery, lesion shape profiles, and raw visual descriptions natively using `gemma4:e4b`.
* **Asynchronous Multi-Agent Graph:** Uses LangGraph to distribute specialized workflow nodes, enabling decoupled, step-by-step reasoning pipelines.
* **Isolated Vector Embedding Core:** Offloads vector storage and lookup overhead to a dedicated embedding model (`nomic-embed-text`) to preserve main model compute tokens.
* **Global Geofenced Vector Filtering:** Automatically converts latitude and longitude coordinates offline into one of the 7 continents and specific regional sub-continents, forcing ChromaDB to filter its semantic results by geo-partition.
* **Non-Blocking Background File Pruner:** Leverages FastAPI's internal `BackgroundTasks` framework to immediately return JSON diagnostics to the client, and then purges the temporary uploaded file from disk after a 5-second safety window.
* **Adaptive Robust Prompting:** Employs a fail-safe framework that guarantees actionable field prescriptions even when network tools (weather analytics, regulatory lists) experience dropouts.
* **Deterministic Cache Layers:** Prevents expensive, repetitive vision inference cycles by validating file checksum hashes on the fly.
* **Premium iOS Dark-Mode Frontend:** A modern, glassmorphic UI optimized for bright sunlight conditions, running natively on standard viewports with background-powered HTML5 Geolocation tracking.

---

## 📁 Project Directory Blueprint

Organize your project files inside your `uv` workspace to match the structure below:
```text
AgronPulseAI/
├── config.py           # Hyperparameter configs and model tag maps
├── state.py            # TypedDict state structure
├── storage.py          # Key-Value Cache and Chroma Vector DB engines
├── tools.py            # Non-blocking external agricultural APIs & offline geofencing
├── nodes.py            # Role-specific agents and decision routers
├── pipeline.py         # Asynchronous LangGraph lifecycle wiring
├── main.py             # FastAPI framework setup, lifespan hook, and file pruner
├── app_ui.py           # Streamlit iOS dark-mode user interface client
├── requirements.txt    # Frozen package environment inputs
└── setup.sh            # Automation script for environment installation
```

---

## 🛠️ System Dependencies (`requirements.txt`)

Create a `requirements.txt` file in your root workspace containing these dependencies:
```text
fastapi>=0.110.0
uvicorn>=0.30.0
langgraph>=0.0.60
langchain-community>=0.2.0
langchain-chroma>=0.1.2
pillow>=10.3.0
torch>=2.3.0
python-multipart>=0.0.9
httpx>=0.27.0
reverse_geocoder>=1.5.1
streamlit>=1.35.0
streamlit-js-eval>=0.1.7
opencv-python>=4.9.0
watchdog>=4.0.0
```

---

## 🚀 Setup and Environment Installation

### 1. Execute the Setup Script (`setup.sh`)
Your initialization shell script handles environment isolation, dependencies configuration, and local model generation maps.

```bash
#!/bin/bash
set -e  # Exit immediately if any command fails

echo "[1/4] Checking framework prerequisites..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager via pip..."
    pip install uv
fi

if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama engine not found. Download it from https://ollama.com"
    exit 1
fi

echo "[2/4] Provisioning clean virtual workspace for AgronPulse AI..."
uv venv
source .venv/bin/activate

echo "[3/4] Installing dependencies with uv..."
uv pip install -r requirements.txt

echo "[4/4] Allocating local weights models via Ollama..."
ollama pull gemma4:e4b
ollama pull nomic-embed-text

# On macOS systems, configure structural XCode dependencies for watchdog reloader support
if [[ "\$OSTYPE" == "darwin"* ]]; then
    echo "Configuring macOS filesystem hot-reload system triggers..."
    xcode-select --install || true
fi

echo "🎉 AgronPulse AI initialization complete! Run 'source .venv/bin/activate' to start working."
```

Make the script executable and run it:
```bash
chmod +x setup.sh
./setup.sh
```

---

## 🏁 Runtime Execution Guide

### 1. Launch the Server Terminal
Activate your virtual environment and start your high-performance non-blocking Uvicorn runners:

```bash
# Activate the workspace environment
source .venv/bin/activate

# Clean out any old, mismatched cache database vectors if required
rm -rf chroma_db_storage

# Launch the FastAPI application hub on port 8080 with keeping alive sockets configurations
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --timeout-keep-alive 300 --reload
```
The server backend spins up the core multi-agent execution pipeline.

### 2. Launch the Premium iOS UI Client
In a new terminal window, activate the virtual environment and spin up the frontend client:
```bash
source .venv/bin/activate
uv run streamlit run app_ui.py
```
The interface is served locally at **`http://localhost:8501`**. 

---

## 🔬 Test Samples & Verification Metrics

### 1. UI Operational Verification
1. Open **`http://localhost:8501`** on your desktop browser or mobile emulator.
2. Grant browser **location permissions** when prompted. The high-contrast numeric input boxes under **Spatial Geolocation Parameters** will automatically fill out with your actual GPS coordinates using high-visibility dark text on light fields.
3. Keep the default **Multimedia File Upload** option active, or toggle **Switch Mode** to spin up your mobile device camera cleanly.
4. Upload or snap your crop leaf target (e.g., `data/tomato_test_leaf.jpg`), customize your descriptive notes inside the field anomalies input box, and hit **Decipher Qualitative Signs**.
5. The UI will securely stream the payload, display an async loading spinner, and return clean white results panels.

### 2. API Terminal Verification Request (`curl`)
You can bypass the UI and test raw endpoint state machine transitions directly via terminal protocols using these global sample locations:

```bash
# Test Matrix 1: Targets ASIA_APAC_SOUTH geofenced metadata sector
curl -X 'POST' \
  'http://localhost:8080/api/v1/diagnose' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'user_query=Look at these brown target spots with distinct yellow ring halos on the leaf.' \
  -F 'latitude=12.9716' \
  -F 'longitude=77.5946' \
  -F 'thread_id=zone_india_south' \
  -F 'file=@data/tomato_test_leaf.jpg'
```

### 3. Expected API JSON Output Object
```json
{
  "diagnosis": "Tomato Early Blight (Alternaria solani)",
  "confidence": "High",
  "weather_risk_factor": "CRITICAL_RISK",
  "actionable_treatments": [
    "Neem Oil Extract",
    "Copper Oxychloride (Local regulatory compliance)",
    "Trichoderma viride bio-agent"
  ]
}
```

---

## 💡 Troubleshooting Configuration Issues

* **Error: `Failed to connect to local Ollama`**
  Ensure your background Ollama engine is running. Test connectivity via browser or `curl http://localhost:11434`.
* **Error: `Model not found (404)`**
  Verify your `config.py` uses `"gemma4:e4b"` rather than legacy string references like `"gemma:e4b"`.
* **Error: `This server does not support embeddings (501)`**
  This happens when `gemma4:e4b` is mistakenly used for embedding generation. Ensure your `config.py` maps `EMBEDDING_MODEL` explicitly to `"nomic-embed-text"` and clear the old DB structure with `rm -rf chroma_db_storage`.
* **Error: `Attribute "app" not found in module "main"`**
  Ensure that the `app = FastAPI(...)` instantiation is defined globally at the zero-indentation root level of your `main.py` file, rather than being nested inside the `lifespan` function or an execution block.