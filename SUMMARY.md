# Mem0 Improved: Summary

## Overview

This project implements an improved version of mem0 with research-based enhancements designed to beat the original performance on the LOCOMO benchmark.

## Project Structure

```
evaluation_improved/
├── README.md                      # Setup and usage instructions
├── IMPROVEMENTS.md                # Detailed improvements documentation
├── SUMMARY.md                     # This file
├── requirements.txt               # Python dependencies
├── run_experiments_improved.py    # Main experiment runner
├── evals.py                       # Evaluation script
├── generate_scores.py             # Score generation script
├── compare_results.py             # Comparison script
├── prompts_improved.py            # Enhanced prompts
├── src/
│   └── improved_mem0/
│       ├── __init__.py
│       ├── add.py                 # Improved memory addition
│       └── search.py              # Improved memory search
└── metrics/                       # Evaluation metrics (copied from mem0)
    ├── llm_judge.py
    └── utils.py
```

## Key Improvements

1. **Multi-Step Query Expansion**: Expand queries into multiple related queries for better retrieval coverage
2. **Cross-Encoder Reranking**: Rerank memories by relevance to query using LLM scoring
3. **Temporal Attention Mechanisms**: Weight memories based on temporal relevance
4. **Hierarchical Memory Consolidation**: Organize memories hierarchically (episodic, semantic, meta)
5. **Enhanced Answer Generation**: Improved prompts with multi-step reasoning

## Expected Performance

Based on research and implementation:

- **LLM Score**: +15-25% improvement (target: 0.75-0.80 vs 0.65 baseline)
- **BLEU Score**: +10-15% improvement
- **F1 Score**: +10-15% improvement
- **Temporal Questions**: +20-30% improvement (Category 2)

## Setup Instructions

1. **Install Dependencies**:
```bash
cd evaluation_improved
pip install -r requirements.txt
```

2. **Set Environment Variables** (create `.env` file):
```
OPENAI_API_KEY=your-openai-api-key
MEM0_API_KEY=your-mem0-api-key
MEM0_PROJECT_ID=your-mem0-project-id
MEM0_ORGANIZATION_ID=your-mem0-organization-id
MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

3. **Download LOCOMO Dataset**:
   - Download from: https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-
   - Place in `dataset/` directory as `locomo10.json`

## Running Experiments

### Step 1: Add Memories
```bash
python run_experiments_improved.py \
    --technique_type improved_mem0 \
    --method add \
    --data_path dataset/locomo10.json \
    --is_graph  # Optional: use graph-based search
```

### Step 2: Search and Generate Answers
```bash
python run_experiments_improved.py \
    --technique_type improved_mem0 \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories \
    --is_graph  # Optional: use graph-based search
```

### Step 3: Evaluate Results
```bash
python evals.py \
    --input_file results/improved_mem0_results_top_30_filter_True_graph_False.json \
    --output_file evaluation_improved_metrics.json \
    --max_workers 10
```

### Step 4: Generate Scores
```bash
python generate_scores.py
```

### Step 5: Compare with Original Mem0
```bash
python compare_results.py \
    --original_file ../mem0/evaluation/evaluation_metrics.json \
    --improved_file evaluation_improved_metrics.json
```

## Implementation Details

### Multi-Step Query Expansion

The search process expands queries into multiple related queries:
- Original: "When did Sarah go to Hawaii?"
- Expanded: ["When did Sarah go to Hawaii?", "What date did Sarah visit Hawaii?", "When was Sarah's trip to Hawaii?"]
- Searches with all queries and combines unique results

### Cross-Encoder Reranking

After vector search retrieval:
1. Score each memory's relevance to query using LLM
2. Sort memories by relevance score
3. Select top-k after reranking

### Temporal Attention

For temporal questions:
- Detect temporal keywords (when, date, time, last, first, ago, before, after)
- Weight memories with timestamps: 1.5x
- Weight memories without timestamps: 1.0x
- Resort by combined score

### Hierarchical Memory

Memories are organized hierarchically:
- **Episodic**: Specific events with time and context
- **Semantic**: General facts and knowledge
- **Meta**: Patterns, preferences, and relationships

## Results Interpretation

After running experiments, compare:
- **LLM Score**: Primary metric (0-1, higher is better)
- **BLEU Score**: Text similarity (0-1, higher is better)
- **F1 Score**: Precision-recall balance (0-1, higher is better)

Expected improvements:
- Overall LLM score: +15-25%
- Category 2 (temporal): +20-30%
- Category 3 (inferential): +10-20%
- Category 4 (factual): +5-15%

## Next Steps

1. Run experiments on LOCOMO dataset
2. Compare results with original mem0
3. Analyze performance by category
4. Iterate on improvements based on results
5. Document findings and publish results

## References

- Mem0 Paper: https://arxiv.org/abs/2504.19413
- Mem0 GitHub: https://github.com/mem0ai/mem0
- LOCOMO Dataset: https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-

