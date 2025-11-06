# Mem0 Improved: Enhanced Memory System

An improved version of Mem0 with research-based enhancements designed to beat the original performance on the LOCOMO benchmark. This implementation includes advanced memory retrieval, query expansion, temporal reasoning, and graph-based memory relationships.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM and embeddings)
- LOCOMO dataset (download instructions below)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/memoryful/mem0-improved.git
cd mem0-improved
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. **Download the LOCOMO dataset**:
```bash
bash download_dataset.sh
# Or manually download from:
# https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-
# Place locomo10.json in dataset/ directory
```

## 📖 Running Instructions

### Step 1: Add Memories to the System

This step processes conversations from the dataset and creates memories:

```bash
python run_experiments_improved.py \
    --method add \
    --data_path dataset/locomo10.json \
    --is_graph  # Optional: enable graph-based memory relationships
```

**What this does**:
- Processes all conversations from the dataset
- Extracts memories using hierarchical memory structure
- Stores memories in ChromaDB vector store
- Builds memory relationship graph (if `--is_graph` is enabled)

**Expected time**: ~1-2 hours depending on dataset size

### Step 2: Search and Generate Answers

This step queries the memory system and generates answers:

```bash
python run_experiments_improved.py \
    --method search \
    --data_path dataset/locomo10.json \
    --top_k 30 \
    --filter_memories \
    --is_graph  # Optional: use graph-based search
```

**Parameters**:
- `--top_k 30`: Number of memories to retrieve (default: 30)
- `--filter_memories`: Apply memory filtering and deduplication
- `--is_graph`: Use graph-based retrieval (slower but more accurate)

**What this does**:
- Processes all questions from the dataset
- Retrieves relevant memories using improved search methods
- Generates answers using enhanced prompts
- Saves results to `results/` directory

**Expected time**: ~2-4 hours depending on dataset size and parameters

### Step 3: Evaluate Results

Evaluate the generated answers against ground truth:

```bash
python evals.py \
    --input_file results/improved_mem0_results_top_30_filter_True_graph_False.json \
    --output_file evaluation_improved_metrics.json \
    --max_workers 10
```

**Parameters**:
- `--input_file`: Path to results JSON file from Step 2
- `--output_file`: Path to save evaluation metrics
- `--max_workers`: Number of parallel workers for evaluation

**Metrics computed**:
- **LLM Judge Score**: Semantic similarity score (0-1, higher is better)
- **BLEU Score**: Text similarity score (0-1, higher is better)
- **F1 Score**: Precision-recall balance (0-1, higher is better)

### Step 4: Generate Summary Scores

Generate aggregated scores across all categories:

```bash
python generate_scores.py
```

This creates a summary JSON file with average scores across all question categories.

### Step 5: Compare with Original Mem0 (Optional)

Compare results with the original Mem0 implementation:

```bash
python compare_results.py \
    --original_file ../mem0/evaluation/evaluation_metrics.json \
    --improved_file evaluation_improved_metrics.json
```

## 🧪 Testing Instructions

### Unit Tests

Run unit tests for individual components:

```bash
# Test memory addition
python -m pytest tests/test_add.py -v

# Test memory search
python -m pytest tests/test_search.py -v

# Test utility functions
python -m pytest tests/test_utils.py -v
```

### Integration Tests

Test the full pipeline with a small dataset:

```bash
# Create a test dataset with first conversation only
python -c "
import json
with open('dataset/locomo10.json') as f:
    data = json.load(f)
with open('dataset/test_locomo.json', 'w') as f:
    json.dump([data[0]], f)
"

# Run experiments on test dataset
python run_experiments_improved.py --method add --data_path dataset/test_locomo.json
python run_experiments_improved.py --method search --data_path dataset/test_locomo.json --top_k 10

# Evaluate test results
python evals.py --input_file results/improved_mem0_results_top_10_filter_False_graph_False.json
```

### Performance Benchmarks

Run performance benchmarks:

```bash
# Benchmark memory addition
time python run_experiments_improved.py --method add --data_path dataset/locomo10.json

# Benchmark memory search
time python run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30
```

### Manual Testing

Test individual components interactively:

```python
from src.improved_mem0.add import ImprovedMemoryADD
from src.improved_mem0.search import ImprovedMemorySearch

# Test memory addition
memory_add = ImprovedMemoryADD(data_path="dataset/locomo10.json")
memory_add.process_all_conversations()

# Test memory search
memory_search = ImprovedMemorySearch(top_k=10, filter_memories=True)
result = memory_search.search_memory_with_expansion(
    user_id="test_user",
    query="When did Sarah go to Hawaii?",
    top_k=10
)
print(result)
```

## 🔧 Improvements Made

### Phase 1: Core Enhancements

#### 1. Multi-Step Query Expansion
- **Problem**: Single query may miss relevant memories due to semantic variations
- **Solution**: Expand queries into 2-3 related queries focusing on temporal, entity, and contextual aspects
- **Expected Impact**: +5-10% improvement in recall
- **Implementation**: `src/improved_mem0/search.py::expand_query()`

#### 2. Cross-Encoder Reranking
- **Problem**: Vector similarity scores may not capture query-memory relevance accurately
- **Solution**: Use LLM to score and rerank memories by relevance to query
- **Expected Impact**: +3-7% improvement in precision
- **Implementation**: `src/improved_mem0/search.py::rerank_memories()`

#### 3. Temporal Attention Mechanisms
- **Problem**: Temporal questions need different weighting of memories with timestamps
- **Solution**: Weight memories based on temporal relevance when query involves time
- **Expected Impact**: +5-10% improvement in temporal question accuracy
- **Implementation**: `src/improved_mem0/search.py::apply_temporal_attention()`

#### 4. Hierarchical Memory Consolidation
- **Problem**: Flat memory structure doesn't capture relationships between memories
- **Solution**: Organize memories hierarchically (episodic, semantic, meta levels)
- **Expected Impact**: +3-5% improvement in consolidation quality
- **Implementation**: Enhanced custom instructions in `src/improved_mem0/add.py`

#### 5. Enhanced Answer Generation Prompts
- **Problem**: Answer generation could benefit from more structured reasoning
- **Solution**: Enhanced prompts with multi-step reasoning, temporal analysis, and evidence grounding
- **Expected Impact**: +2-5% improvement in answer accuracy
- **Implementation**: `prompts_improved.py`

### Phase 2: Advanced Enhancements

#### 6. Memory Deduplication and Consolidation
- **Problem**: Duplicate or highly similar memories waste storage and reduce retrieval efficiency
- **Solution**: Detect and merge duplicate memories using text similarity (Jaccard similarity)
- **Expected Impact**: 10-20% reduction in memory storage, faster retrieval
- **Implementation**: `src/improved_mem0/utils.py::deduplicate_memories()`

#### 7. Enhanced Temporal Reasoning
- **Problem**: Basic temporal keyword detection doesn't handle relative dates
- **Solution**: Parse temporal expressions ("3 months ago", "last week") and calculate temporal proximity
- **Expected Impact**: +10-15% improvement in temporal question accuracy
- **Implementation**: `src/improved_mem0/utils.py::parse_temporal_expression()`

#### 8. Adaptive Retrieval Parameters
- **Problem**: Fixed `top_k` and expansion count don't adapt to query complexity
- **Solution**: Dynamically adjust `top_k` and expansion count based on query complexity estimation
- **Expected Impact**: Better resource utilization, +5-10% improvement in complex queries
- **Implementation**: `src/improved_mem0/utils.py::estimate_query_complexity()`

#### 9. Batch Processing Optimizations
- **Problem**: Sequential processing is slow for large datasets
- **Solution**: Batch LLM calls and parallelize question processing
- **Expected Impact**: 2-4x faster processing, reduced API costs
- **Implementation**: Batch processing in `src/improved_mem0/search.py`

#### 10. Multi-Hop Reasoning
- **Problem**: Complex queries require chaining multiple memories together
- **Solution**: Chain related memories through entity relationships using BFS traversal
- **Expected Impact**: +15-25% improvement in complex relational queries
- **Implementation**: `src/improved_mem0/multi_hop.py`

#### 11. Memory Relationship Graph
- **Problem**: No structured representation of relationships between memories
- **Solution**: Build entity-relationship graph during memory creation, support graph traversal
- **Expected Impact**: +10-15% improvement in relational queries, foundation for graph-based retrieval
- **Implementation**: `src/improved_mem0/memory_graph.py`

## 📊 Evaluation Expected

### Performance Targets

Based on research and implementation, we expect:

- **LLM Score**: +25-35% improvement (from ~0.65 baseline to ~0.80-0.85)
- **BLEU Score**: +15-20% improvement
- **F1 Score**: +15-20% improvement
- **Temporal Questions (Category 2)**: +30-40% improvement
- **Complex/Relational Questions (Category 3)**: +25-35% improvement
- **Factual Questions (Category 1)**: +10-15% improvement
- **Processing Speed**: 2-4x faster with batch processing

### Evaluation Metrics

The evaluation uses three primary metrics:

1. **LLM Judge Score** (Primary Metric)
   - Range: 0-1
   - Measures semantic similarity between predicted and ground truth answers
   - Uses GPT-4 to judge answer quality

2. **BLEU Score**
   - Range: 0-1
   - Measures n-gram overlap between predicted and ground truth answers
   - Standard metric for text generation evaluation

3. **F1 Score**
   - Range: 0-1
   - Measures precision-recall balance
   - Good for evaluating factual accuracy

### Category Breakdown

Questions are categorized into 4 types:

- **Category 1**: Factual questions (direct memory recall)
- **Category 2**: Temporal questions (when, date, time-based)
- **Category 3**: Inferential questions (why, how, reasoning)
- **Category 4**: Complex questions (multi-hop, relationship-based)

## 🔮 Future Potential Steps

### Short-term Enhancements (1-2 months)

1. **Hybrid Search**
   - Combine dense (vector) and sparse (BM25) retrieval
   - Expected: +5-10% improvement in recall

2. **Memory Freshness Weighting**
   - Weight recent memories higher than old ones
   - Expected: Better handling of evolving information

3. **Confidence Scoring**
   - Score answer confidence based on evidence quality
   - Expected: Better uncertainty estimation

4. **Contextual Retrieval**
   - Consider conversation history in retrieval
   - Expected: Better multi-turn conversation handling

### Medium-term Enhancements (3-6 months)

5. **Graph Neural Networks (GNNs)**
   - Use GNNs for better relationship understanding
   - Expected: +10-15% improvement in relational queries

6. **Answer Verification**
   - Cross-check answers against multiple memories
   - Expected: +5-10% improvement in accuracy

7. **Multi-Modal Memory**
   - Support images, audio, and other modalities
   - Expected: Richer memory representation

8. **Federated Memory**
   - Support distributed memory across multiple agents
   - Expected: Scalable multi-agent systems

### Long-term Research (6+ months)

9. **Adaptive Learning**
   - Learn optimal retrieval parameters from data
   - Expected: Self-improving system

10. **Memory Compression**
    - Compress memories without losing information
    - Expected: Better storage efficiency

11. **Causal Reasoning**
    - Understand causal relationships between memories
    - Expected: Better "why" question answering

12. **Meta-Learning**
    - Learn to learn from past experiences
    - Expected: Faster adaptation to new domains

## 📁 Project Structure

```
evaluation_improved/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore file
├── dataset/                       # LOCOMO dataset (download separately)
│   ├── locomo10.json
│   └── locomo10_rag.json
├── results/                       # Experiment results
├── src/
│   └── improved_mem0/
│       ├── __init__.py
│       ├── add.py                 # Improved memory addition
│       ├── search.py              # Improved memory search
│       ├── memory_graph.py        # Memory relationship graph
│       ├── multi_hop.py           # Multi-hop reasoning
│       └── utils.py               # Utility functions
├── metrics/                       # Evaluation metrics
│   ├── llm_judge.py
│   └── utils.py
├── run_experiments_improved.py    # Main experiment runner
├── evals.py                       # Evaluation script
├── generate_scores.py             # Score generation script
├── compare_results.py             # Comparison script
├── prompts_improved.py            # Enhanced prompts
├── IMPROVEMENTS.md                # Detailed improvements documentation
├── IMPROVEMENTS_PHASE2.md         # Phase 2 improvements
├── COMPARISON.md                  # Comparison guide (OpenAI vs Local)
├── DATASET.md                     # Dataset download instructions
└── QUICK_START.md                 # Quick start guide
```

## 🔍 Configuration

### Environment Variables

Create a `.env` file with:

```bash
OPENAI_API_KEY=your-openai-api-key
MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

**Note**: Mem0 API keys are NOT needed - this uses the local `Memory` class for evaluation.

### Model Configuration

Default models:
- **LLM**: `gpt-4o-mini` (cost-effective, good quality)
- **Embeddings**: `text-embedding-3-small` (fast, good quality)

You can change these in `.env` or modify `config_local_models.py` for local models.

## 📝 Documentation

- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Detailed Phase 1 improvements
- [IMPROVEMENTS_PHASE2.md](IMPROVEMENTS_PHASE2.md) - Phase 2 improvements
- [COMPARISON.md](COMPARISON.md) - Comparison guide (OpenAI vs Local models)
- [DATASET.md](DATASET.md) - Dataset download instructions
- [QUICK_START.md](QUICK_START.md) - Quick start guide

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Mem0 team for the original implementation
- LOCOMO benchmark creators
- OpenAI for API access

## 📧 Contact

For questions or issues, please open an issue on GitHub.

## 📚 References

- Mem0 Paper: https://arxiv.org/abs/2504.19413
- Mem0 GitHub: https://github.com/mem0ai/mem0
- LOCOMO Dataset: https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-
- Query Expansion Research: Various RAG papers
- Cross-Encoder Reranking: Sentence-BERT paper
- Temporal Attention: Attention mechanisms in transformers
