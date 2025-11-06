#!/bin/bash
# Setup and run improved mem0 experiments

set -e

echo "=========================================="
echo "Improved Mem0 - Setup and Run Script"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << 'EOF'
# OpenAI API Configuration (required for LLM and embeddings)
OPENAI_API_KEY=your-openai-api-key-here

# Model Configuration
MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Note: Mem0 API keys are NOT needed - this uses local Memory class
EOF
    echo "✅ Created .env template file"
    echo "⚠️  Please edit .env file with your API keys before running experiments"
    exit 1
fi

# Check if dataset exists
if [ ! -f "dataset/locomo10.json" ]; then
    echo "⚠️  Dataset not found at dataset/locomo10.json"
    echo "📥 Please download the LOCOMO dataset from:"
    echo "   https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-"
    echo "📁 Place it in: evaluation_improved/dataset/locomo10.json"
    
    # Create dataset directory
    mkdir -p dataset
    echo "✅ Created dataset directory"
    exit 1
fi

# Create results directory
mkdir -p results

echo "✅ Setup complete!"
echo ""
echo "To run experiments:"
echo "1. Add memories:"
echo "   python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json"
echo ""
echo "2. Search and generate answers:"
echo "   python3 run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories"
echo ""
echo "3. Evaluate results:"
echo "   python3 evals.py --input_file results/improved_mem0_results_*.json"
echo ""
echo "4. Generate scores:"
echo "   python3 generate_scores.py"

