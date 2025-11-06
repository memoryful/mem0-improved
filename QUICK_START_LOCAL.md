# Quick Start: Local Models (llama3.2:latest)

Since you already have `llama3.2:latest` installed in Ollama, you're ready to run the benchmark!

## Verify Setup

```bash
# Check Ollama is running
ollama list

# Should see llama3.2:latest
```

## Install Python Dependencies

```bash
cd evaluation_improved
pip install ollama sentence-transformers
```

## Run Benchmark

### Step 1: Add Memories

```bash
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.2:latest \
    --method add \
    --data_path dataset/locomo10.json
```

This will process all 10 conversations and create memories using the local llama3.2 model.

### Step 2: Search and Generate Answers

```bash
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.2:latest \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories
```

This will answer all 1,986 questions using the improved search with query expansion and reranking.

### Step 3: Evaluate Results

```bash
python3 evals.py \
    --input_file results/improved_mem0_local_ollama_llama3.2_latest_top_30_filter_True_graph_False.json \
    --output_file evaluation_local_metrics.json
```

### Step 4: Generate Scores

```bash
python3 generate_scores.py
```

## Expected Performance

With `llama3.2:latest`:
- **Quality**: Good (comparable to llama3.1:8b)
- **Speed**: Depends on your hardware (GPU recommended)
- **Cost**: $0 (completely free!)

## Compare with OpenAI

If you want to compare with OpenAI results:

```bash
# Run OpenAI version first
python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json
python3 run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories

# Then compare
python3 compare_results.py \
    --original_file evaluation_openai_metrics.json \
    --improved_file evaluation_local_metrics.json
```

## Tips

1. **GPU**: If you have a GPU, Ollama will automatically use it (much faster)
2. **CPU**: Works but slower (may take hours/days for full benchmark)
3. **Monitor**: Watch Ollama usage: `ollama ps`
4. **Memory**: Ensure you have enough RAM (llama3.2:latest needs ~8-16GB)

## Troubleshooting

### Ollama not responding
```bash
# Restart Ollama
ollama serve
```

### Out of memory
- Close other applications
- Use a smaller model if needed
- Reduce batch size in code

### Slow performance
- Check if GPU is being used: `ollama ps`
- Use GPU if available
- Consider using a quantized version if available

## Next Steps

Once you have results from both:
1. Compare accuracy scores
2. Compare speed/cost
3. Analyze which performs better for your use case
4. Document findings

Good luck with your benchmark! 🚀

