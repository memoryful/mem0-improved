#!/bin/bash
# Run benchmarks with local open-source models

set -e

echo "=========================================="
echo "Local Open-Source Model Benchmark"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo ""
    echo "Install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: Download from https://ollama.com"
    echo ""
    echo "Then pull a model:"
    echo "  ollama pull llama3.1:8b"
    echo ""
    exit 1
fi

echo "✅ Ollama is installed"

# Check if model is available
MODEL=${1:-llama3.2:latest}
echo "Using model: $MODEL"

if ! ollama list | grep -q "$MODEL"; then
    echo "⚠️  Model $MODEL not found. Pulling..."
    ollama pull "$MODEL"
fi

echo "✅ Model $MODEL is available"
echo ""

# Check if Python dependencies are installed
echo "Checking dependencies..."
python3 -c "import ollama; from sentence_transformers import SentenceTransformer" 2>/dev/null || {
    echo "❌ Missing dependencies"
    echo "Install with: pip install ollama sentence-transformers"
    exit 1
}

echo "✅ Dependencies installed"
echo ""

echo "Starting benchmark with local models..."
echo "Model: $MODEL"
echo "Embeddings: sentence-transformers/all-MiniLM-L6-v2"
echo ""

# Run the benchmark
python3 run_experiments_local.py --model "$MODEL" --method add --data_path dataset/locomo10.json

