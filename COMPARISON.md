# Benchmark Comparison: OpenAI vs Local Models

This guide explains how to run benchmarks with both OpenAI and local open-source models and compare the results.

## Quick Comparison

| Feature | OpenAI (gpt-4o-mini) | Local (Ollama + HuggingFace) |
|---------|----------------------|------------------------------|
| **Cost** | ~$19.29 per full benchmark | $0 (free) |
| **Speed** | Fast, consistent | Depends on hardware (GPU faster) |
| **Quality** | Best | Good (depends on model) |
| **Privacy** | Data sent to OpenAI | Completely local |
| **Setup** | API key only | Install Ollama + pull model |

## Running Both Benchmarks

### 1. OpenAI Benchmark (Original)

```bash
# Step 1: Add memories
python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json

# Step 2: Search and generate answers
python3 run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories

# Step 3: Evaluate
python3 evals.py --input_file results/improved_mem0_results_top_30_filter_True_graph_False.json --output_file evaluation_openai_metrics.json

# Step 4: Generate scores
python3 generate_scores.py
```

### 2. Local Model Benchmark (Ollama)

```bash
# Install Ollama and pull model first
ollama pull llama3.1:8b

# Step 1: Add memories
python3 run_experiments_local.py --model_type ollama --model llama3.1:8b --method add --data_path dataset/locomo10.json

# Step 2: Search and generate answers
python3 run_experiments_local.py --model_type ollama --model llama3.1:8b --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories

# Step 3: Evaluate
python3 evals.py --input_file results/improved_mem0_local_ollama_llama3.1_8b_top_30_filter_True_graph_False.json --output_file evaluation_local_metrics.json

# Step 4: Generate scores
python3 generate_scores.py
```

## Comparing Results

Use the comparison script to compare results:

```bash
python3 compare_results.py \
    --original_file evaluation_openai_metrics.json \
    --improved_file evaluation_local_metrics.json
```

## Expected Differences

### Accuracy
- **OpenAI**: Best accuracy (~65% LLM score baseline)
- **Local (llama3.1:8b)**: Good accuracy (~55-60% LLM score)
- **Local (llama3.1:70b)**: Better accuracy (~60-65% LLM score)

### Speed
- **OpenAI**: Fast, consistent (~few hours for full benchmark)
- **Local (CPU)**: Slow (~days for full benchmark)
- **Local (GPU)**: Fast (~few hours, similar to OpenAI)

### Cost
- **OpenAI**: ~$19.29 per full benchmark
- **Local**: $0 (free)

## Recommendations

### For Testing
- Use **local models** (free, good enough for testing)
- Start with `llama3.1:8b` (fast, good quality)

### For Production
- Use **OpenAI** (best quality, consistent)
- Or use **local models** with GPU (free, good quality)

### For Research
- Run **both** and compare results
- Analyze performance differences
- Document findings

## Model Recommendations

### Small Models (8B parameters)
- **llama3.1:8b**: Good quality, fast
- **mistral:7b**: Good quality, fast
- **qwen2.5:7b**: Good quality, fast

### Large Models (70B parameters)
- **llama3.1:70b**: Best quality, slower
- Requires GPU for reasonable speed

### Embeddings
- **sentence-transformers/all-MiniLM-L6-v2**: Fast, good quality
- **BAAI/bge-small-en-v1.5**: Better quality, slightly slower

## Example Workflow

1. **Test with local model first** (free, validates setup)
2. **Compare with OpenAI** (if budget allows)
3. **Analyze differences** (understand trade-offs)
4. **Choose best option** (based on needs)

## Cost Savings

Running full benchmark with local models saves:
- **~$19.29 per run** (vs OpenAI)
- **Unlimited runs** (no API costs)
- **Faster iteration** (no rate limits)

Perfect for:
- Development and testing
- Research and experimentation
- Iterating on improvements

