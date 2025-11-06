# Quick Start Guide

## Prerequisites

Before running the experiments, you need:

1. **API Keys** - Create a `.env` file with:
   - `OPENAI_API_KEY` - Your OpenAI API key (for LLM and embeddings)
   - **Note**: Mem0 API keys are NOT needed - this uses the local `Memory` class for evaluation

2. **LOCOMO Dataset** - Download from:
   - https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-
   - Place it in `dataset/locomo10.json`

## Quick Setup

Run the setup script:
```bash
bash setup_and_run.sh
```

This will:
- Create `.env` template if missing
- Create `dataset/` directory if missing
- Check if dataset exists
- Create `results/` directory

## Running Experiments

### Step 1: Add Memories
```bash
python3 run_experiments_improved.py \
    --method add \
    --data_path dataset/locomo10.json \
    --is_graph  # Optional: use graph-based search
```

### Step 2: Search and Generate Answers
```bash
python3 run_experiments_improved.py \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories \
    --is_graph  # Optional: use graph-based search
```

### Step 3: Evaluate Results
```bash
python3 evals.py \
    --input_file results/improved_mem0_results_top_30_filter_True_graph_False.json \
    --output_file evaluation_improved_metrics.json \
    --max_workers 10
```

### Step 4: Generate Scores
```bash
python3 generate_scores.py
```

### Step 5: Compare with Original Mem0
```bash
python3 compare_results.py \
    --original_file ../mem0/evaluation/evaluation_metrics.json \
    --improved_file evaluation_improved_metrics.json
```

## Notes

- The experiments require API keys to be set in `.env`
- The LOCOMO dataset must be downloaded separately
- Each step may take significant time depending on dataset size
- Results are saved incrementally after each question

