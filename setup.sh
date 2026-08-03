#!/bin/bash
set -e  # Stop script immediately if any command fails

echo "[1/4] Checking for uv and ollama tools..."
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env" 2>/dev/null || true
fi

if ! command -v ollama &> /dev/null; then
    echo "Error: ollama is not installed on this system."
    echo "Please download it from https://ollama.com before continuing."
    exit 1
fi

echo "[2/4] Setting up Python 3.14 environment..."
# Seed pip so PyCharm background sync won't crash with "No module named pip"
uv venv .venv --python 3.14 --seed

echo "[3/4] Installing Python packages with uv..."
# Install requirements directly into .venv
uv pip install -r requirements.txt --python .venv

echo "[4/4] Pulling Ollama models (LLM & Embeddings)..."
# Pull the generation model and the text embedding model
ollama pull gemma4:e4b
ollama pull nomic-embed-text

echo "Setup complete! To start working, run:"
echo "source .venv/bin/activate"