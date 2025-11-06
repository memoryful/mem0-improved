# Running Benchmarks with llama3.2:latest

You already have `llama3.2:latest` installed in Ollama! Here's how to run the benchmark.

## Quick Start

### 1. Install Python Dependencies

```bash
pip install ollama sentence-transformers
# If you get compatibility errors:
pip install --upgrade sentence-transformers huggingface_hub
```

### 2. Run Benchmark

```bash
# Step 1: Add memories (processes all conversations)
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.2:latest \
    --method add \
    --data_path dataset/locomo10.json

# Step 2: Search and generate answers (processes all 1,986 questions)
python3 run_experiments_local.py \
    --model_type ollama \
    --model llama3.2:latest \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories

# Step 3: Evaluate results
python3 evals.py \
    --input_file results/improved_mem0_local_ollama_llama3.2_latest_top_30_filter_True_graph_False.json \
    --output_file evaluation_local_metrics.json

# Step 4: Generate scores
python3 generate_scores.py
```

## What's Different from OpenAI?

### Cost
- **OpenAI**: ~$19.29 per full benchmark
- **Local (llama3.2:latest)**: $0 (free!)

### Speed
- **OpenAI**: Fast, consistent
- **Local**: Depends on your hardware
  - GPU: Fast (similar to OpenAI)
  - CPU: Slower (may take hours/days)

### Quality
- **OpenAI (gpt-4o-mini)**: Best quality (~65% LLM score)
- **Local (llama3.2:latest)**: Good quality (~55-60% LLM score expected)

## Compare Results

If you also run the OpenAI version:

```bash
# Run OpenAI version
python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json
python3 run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories

# Evaluate OpenAI results
python3 evals.py --input_file results/improved_mem0_results_top_30_filter_True_graph_False.json --output_file evaluation_openai_metrics.json

# Compare both
python3 compare_results.py \
    --original_file evaluation_openai_metrics.json \
    --improved_file evaluation_local_metrics.json
```

## Tips

1. **GPU**: If you have a GPU, Ollama will automatically use it (much faster)
2. **Monitor**: Watch progress with `ollama ps` to see if GPU is being used
3. **Memory**: Ensure you have enough RAM (llama3.2:latest needs ~8-16GB)
4. **Patience**: Full benchmark may take hours on CPU, but it's free!

## Expected Results

With `llama3.2:latest`:
- **LLM Score**: ~55-60% (vs ~65% for OpenAI)
- **BLEU Score**: ~0.35-0.40 (vs ~0.40-0.45 for OpenAI)
- **F1 Score**: ~0.40-0.45 (vs ~0.45-0.50 for OpenAI)

The improved version should still show improvements over the original mem0 even with local models!

