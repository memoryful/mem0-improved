# Mem0 Improved: Research-Based Enhancements

This document describes the improvements made to mem0 to beat its performance on the LOCOMO benchmark.

## Key Improvements Implemented

### 1. Multi-Step Query Expansion

**Problem**: Single query may miss relevant memories due to semantic variations.

**Solution**: Expand queries into multiple related queries focusing on:
- Temporal aspects (when, what date, time period)
- Entity relationships (who, what relationships)
- Contextual variations (synonyms, related concepts)

**Implementation**: 
- Uses LLM to generate 2-3 related queries per original query
- Searches with all queries and combines unique results
- Improves recall by covering semantic variations

**Expected Impact**: +5-10% improvement in recall

### 2. Cross-Encoder Reranking

**Problem**: Vector similarity scores may not capture query-memory relevance accurately.

**Solution**: Use cross-encoder style scoring to rerank memories by relevance to query.

**Implementation**:
- After retrieving memories, use LLM to score each memory's relevance to query
- Resort memories by relevance score
- Select top-k after reranking

**Expected Impact**: +3-7% improvement in precision

### 3. Temporal Attention Mechanisms

**Problem**: Temporal questions need different weighting of memories with timestamps.

**Solution**: Weight memories based on temporal relevance when query involves time.

**Implementation**:
- Detect temporal keywords in query (when, date, time, last, first, ago, before, after)
- Apply higher weight (1.5x) to memories with timestamps for temporal queries
- Resort memories by combined score (similarity × temporal weight)

**Expected Impact**: +5-10% improvement in temporal question accuracy

### 4. Hierarchical Memory Consolidation

**Problem**: Flat memory structure doesn't capture relationships between memories.

**Solution**: Organize memories hierarchically:
- **Episodic Level**: Specific events with time and context
- **Semantic Level**: General facts and knowledge
- **Meta Level**: Patterns, preferences, and relationships

**Implementation**:
- Enhanced custom instructions for hierarchical memory extraction
- Memory consolidation considers hierarchical relationships
- Better understanding of memory relationships

**Expected Impact**: +3-5% improvement in consolidation quality

### 5. Enhanced Answer Generation Prompts

**Problem**: Answer generation could benefit from more structured reasoning.

**Solution**: Enhanced prompts with:
- Multi-step reasoning instructions
- Temporal analysis guidelines
- Evidence-based answering requirements
- Precision requirements

**Implementation**:
- Improved prompts with step-by-step reasoning approach
- Better temporal calculation instructions
- Evidence grounding requirements

**Expected Impact**: +2-5% improvement in answer accuracy

## Expected Overall Improvement

Based on research and these improvements:

- **LLM Score**: +15-25% improvement (from ~0.65 to ~0.75-0.80)
- **BLEU Score**: +10-15% improvement
- **F1 Score**: +10-15% improvement
- **Temporal Questions**: +20-30% improvement (Category 2 questions)

## Technical Details

### Query Expansion Algorithm
```
1. Original query: "When did Sarah go to Hawaii?"
2. Generate expanded queries:
   - "What date did Sarah visit Hawaii?"
   - "When was Sarah's trip to Hawaii?"
   - "Sarah Hawaii trip date"
3. Search with all queries
4. Combine unique results
5. Rerank by relevance
```

### Reranking Algorithm
```
1. Retrieve memories with vector search
2. For each memory, score relevance to query:
   - Score = LLM(query, memory)
   - Range: 0-1
3. Sort by relevance score
4. Select top-k
```

### Temporal Attention
```
1. Detect temporal keywords in query
2. If temporal:
   - Weight memories with timestamps: 1.5x
   - Weight memories without timestamps: 1.0x
3. Sort by: score × temporal_weight
```

## Evaluation Methodology

1. **Setup**: Use same LOCOMO dataset as mem0
2. **Metrics**: 
   - LLM Judge Score (primary metric)
   - BLEU Score
   - F1 Score
3. **Comparison**: Compare against original mem0 results
4. **Categories**: Evaluate across all question categories (1-4)

## Running Experiments

See README.md for instructions on running experiments and comparing results.

## Future Improvements

1. **Graph Neural Networks**: Use GNNs for better relationship understanding
2. **Adaptive Retrieval**: Dynamically adjust retrieval parameters based on query complexity
3. **Memory Importance Scoring**: Assign importance scores during memory creation
4. **Multi-Modal Memory**: Support images and other modalities
5. **Federated Memory**: Support distributed memory across multiple agents

## References

- Mem0 Paper: https://arxiv.org/abs/2504.19413
- LOCOMO Benchmark: https://github.com/mem0ai/mem0
- Query Expansion Research: Various RAG papers
- Cross-Encoder Reranking: Sentence-BERT paper
- Temporal Attention: Attention mechanisms in transformers

