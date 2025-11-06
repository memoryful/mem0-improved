# Running Benchmarks with Local Open-Source Models

This guide explains how to run the improved mem0 benchmark using free, local open-source models instead of OpenAI API.

## Benefits

- ✅ **Free**: No API costs
- ✅ **Private**: All data stays local
- ✅ **Fast**: No network latency (if GPU available)
- ✅ **Comparable**: Can compare performance with OpenAI models

## Supported Local Models

### LLM Options

1. **Ollama** (Recommended) - Easy to install and use
   - Popular models: `llama3.1:8b`, `mistral:7b`, `qwen2.5:7b`
   - Install: `brew install ollama` (macOS) or `curl -fsSL https://ollama.com/install.sh | sh` (Linux)
   - Pull model: `ollama pull llama3.1:8b`

2. **LM Studio** - Desktop app with GUI
   - Install: https://lmstudio.ai/
   - Start local server from "Server" tab
   - Load model in GUI

### Embedding Options

1. **HuggingFace Sentence Transformers** (Recommended)
   - Models: `sentence-transformers/all-MiniLM-L6-v2` (fast), `BAAI/bge-small-en-v1.5` (better quality)
   - Runs completely locally, no API needed

## Setup

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com
```

### 2. Pull a Model

```bash
# Fast, good quality (recommended for testing)
ollama pull llama3.1:8b

# Better quality, slower
ollama pull llama3.1:70b

# Alternative fast options
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

### 3. Install Python Dependencies

```bash
pip install ollama sentence-transformers
```

### 4. Verify Setup

```bash
# Check Ollama is running
ollama list

# Test a model
ollama run llama3.1:8b "Hello, how are you?"
```

## Running Benchmarks

### Quick Start

```bash
# Run with default model (llama3.1:8b)
bash run_local_benchmark.sh

# Or specify a model
bash run_local_benchmark.sh mistral:7b
```

### Manual Run

```bash
# Step 1: Add memories
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.1:8b \
    --method add \
    --data_path dataset/locomo10.json

# Step 2: Search and generate answers
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.1:8b \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories

# Step 3: Evaluate
python3 evals.py \
    --input_file results/improved_mem0_local_ollama_llama3.1_8b_top_30_filter_True_graph_False.json

# Step 4: Generate scores
python3 generate_scores.py
```

## Model Comparison

Run benchmarks with different models and compare:

```bash
# Test with different models
python3 run_experiments_local.py --model_type ollama --model llama3.1:8b --method add
python3 run_experiments_local.py --model_type ollama --model mistral:7b --method add
python3 run_experiments_local.py --model_type ollama --model qwen2.5:7b --method add

# Compare with OpenAI
python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json
```

## Performance Considerations

### Speed
- **Local models**: Faster if you have GPU, slower on CPU
- **OpenAI API**: Consistent speed, depends on network
- **Recommendation**: Use GPU for local models if available

### Quality
- **Small models (3-8B)**: Good for testing, may have lower quality
- **Large models (70B)**: Better quality, requires more resources
- **OpenAI**: Best quality, but costs money

### Resource Requirements
- **llama3.1:8b**: ~8GB RAM, runs on CPU (slow) or GPU (fast)
- **llama3.1:70b**: ~70GB RAM, requires GPU
- **mistral:7b**: ~7GB RAM, runs on CPU or GPU

## Troubleshooting

### Ollama not found
```bash
# Check installation
which ollama

# Restart Ollama service
ollama serve
```

### Model not found
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.1:8b
```

### Out of memory
- Use smaller model (e.g., `llama3.1:8b` instead of `llama3.1:70b`)
- Use quantization (e.g., `llama3.1:8b-q4_0`)
- Close other applications

### Slow performance
- Use GPU if available (Ollama will use GPU automatically)
- Use smaller model
- Increase batch size

## Cost Comparison

### OpenAI (Original)
- **Cost**: ~$19.29 for full benchmark
- **Speed**: Fast, consistent
- **Quality**: Best

### Local Models (Ollama + HuggingFace)
- **Cost**: $0 (free)
- **Speed**: Depends on hardware (GPU faster)
- **Quality**: Good (depends on model size)

## Next Steps

1. Run benchmark with local model
2. Compare results with OpenAI version
3. Analyze performance differences
4. Optimize for your use case

## Example Results Structure

```
results/
├── improved_mem0_local_ollama_llama3.1_8b_top_30_filter_True_graph_False.json
├── improved_mem0_local_ollama_mistral_7b_top_30_filter_True_graph_False.json
└── improved_mem0_results_top_30_filter_True_graph_False.json (OpenAI)
```

You can then compare all three!

