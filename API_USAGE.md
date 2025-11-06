# API Usage Analysis

## Dataset Statistics

- **Total conversations**: 10
- **Total messages**: 5,882
- **Total QA pairs**: 1,986
- **Average messages per conversation**: 588.2
- **Average QA pairs per conversation**: 198.6

## Model Configuration

### Original Mem0 Benchmark
- **Model**: `gpt-4o-mini` (from README.md)
- **Embedding Model**: `text-embedding-3-small`

### Improved Version
- **Model**: `gpt-4o-mini` (default, configurable via .env)
- **Embedding Model**: `text-embedding-3-small` (default, configurable via .env)

## API Calls for `--method add`

### Per Batch Processing
For each batch of messages (batch_size=2):
1. **Fact Extraction LLM Call**: 1 call per batch
   - Extracts facts from conversation messages
   - Uses the LLM to identify what should be remembered

2. **Memory Consolidation LLM Call**: 1 call per batch (if existing memories found)
   - Consolidates new facts with existing memories
   - Determines ADD/UPDATE/DELETE operations

3. **Embedding Calls**: Multiple calls per batch
   - 1 embedding call per extracted fact
   - 1 embedding call per existing memory (for similarity search)
   - Average: ~2-5 facts per batch, ~5 existing memories searched

### Total Calculations

**Batches to process**:
- Total messages: 5,882
- Batch size: 2
- Batches: 5,882 / 2 = **2,941 batches**
- Each conversation processed for 2 speakers (speaker_a and speaker_b)
- Total batches: **2,941 batches per conversation × 10 conversations = ~29,410 batches**

**API Calls Estimate**:
- **LLM Calls (Fact Extraction)**: ~2,941 per conversation × 10 = **~29,410 calls**
- **LLM Calls (Consolidation)**: ~2,941 per conversation × 10 = **~29,410 calls** (if memories exist)
- **Embedding Calls**: ~5-10 per batch × 29,410 = **~147,050 - 294,100 calls**

**Total LLM Calls**: ~58,820 calls (assuming all batches trigger consolidation)
**Total Embedding Calls**: ~147,050 - 294,100 calls

### Token Usage Estimate (Add Method)

**Per Fact Extraction Call**:
- Input: ~500-1000 tokens (conversation messages)
- Output: ~100-200 tokens (extracted facts)
- **Total**: ~600-1200 tokens per call
- **29,410 calls**: ~17.6M - 35.3M tokens

**Per Consolidation Call**:
- Input: ~1000-2000 tokens (existing memories + new facts)
- Output: ~200-400 tokens (consolidated memories)
- **Total**: ~1200-2400 tokens per call
- **29,410 calls**: ~35.3M - 70.6M tokens

**Embedding Calls**:
- Input: ~50-200 tokens per text
- **Total**: ~147,050 - 294,100 calls × ~50-200 tokens = **~7.4M - 58.8M tokens**

**Total Token Usage (Add Method)**:
- **LLM Tokens**: ~53M - 106M tokens
- **Embedding Tokens**: ~7.4M - 58.8M tokens
- **Grand Total**: ~60M - 165M tokens

## API Calls for `--method search`

### Per Question Processing

For each of the 1,986 QA pairs:

1. **Query Expansion LLM Call**: 1 call per question
   - Generates 2-3 expanded queries
   - Input: ~100 tokens, Output: ~50 tokens

2. **Memory Search**: 
   - Embedding calls: ~3-4 per question (for expanded queries)
   - Vector searches: ~3-4 per question

3. **Reranking LLM Call**: 1 call per question (if memories found)
   - Scores relevance of each memory
   - Input: ~500-1000 tokens, Output: ~50-100 tokens

4. **Answer Generation LLM Call**: 1 call per question
   - Generates final answer from memories
   - Input: ~1000-2000 tokens, Output: ~50-200 tokens

5. **Temporal Attention**: No additional API calls (just weighting)

### Total Calculations

**API Calls Estimate**:
- **LLM Calls (Query Expansion)**: 1,986 calls
- **LLM Calls (Reranking)**: ~1,986 calls (assuming memories found)
- **LLM Calls (Answer Generation)**: 1,986 calls
- **Embedding Calls**: ~5,958 - 7,944 calls (3-4 per question)

**Total LLM Calls**: ~5,958 calls
**Total Embedding Calls**: ~5,958 - 7,944 calls

### Token Usage Estimate (Search Method)

**Per Query Expansion Call**:
- Input: ~100 tokens, Output: ~50 tokens
- **1,986 calls**: ~150 tokens × 1,986 = **~298K tokens**

**Per Reranking Call**:
- Input: ~500-1000 tokens, Output: ~50-100 tokens
- **1,986 calls**: ~550-1100 tokens × 1,986 = **~1.1M - 2.2M tokens**

**Per Answer Generation Call**:
- Input: ~1000-2000 tokens, Output: ~50-200 tokens
- **1,986 calls**: ~1050-2200 tokens × 1,986 = **~2.1M - 4.4M tokens**

**Embedding Calls**:
- Input: ~50-200 tokens per query
- **5,958 - 7,944 calls**: ~50-200 tokens × 5,958 = **~298K - 1.2M tokens**

**Total Token Usage (Search Method)**:
- **LLM Tokens**: ~3.5M - 6.9M tokens
- **Embedding Tokens**: ~298K - 1.2M tokens
- **Grand Total**: ~3.8M - 8.1M tokens

## Total API Usage (Both Methods)

### Total API Calls
- **LLM Calls**: ~64,778 calls (58,820 + 5,958)
- **Embedding Calls**: ~153,008 - 302,044 calls (147,050-294,100 + 5,958-7,944)

### Total Token Usage
- **LLM Tokens**: ~56.5M - 112.9M tokens
- **Embedding Tokens**: ~7.7M - 60M tokens
- **Grand Total**: ~63.8M - 172.9M tokens

## Cost Estimate (Using OpenAI Pricing)

### Pricing (as of 2024):
- **gpt-4o-mini**: 
  - Input: $0.15 per 1M tokens
  - Output: $0.60 per 1M tokens
- **text-embedding-3-small**: 
  - $0.02 per 1M tokens

### Cost Breakdown:

**Add Method**:
- LLM Input: ~35M tokens × $0.15/1M = **~$5.25**
- LLM Output: ~18M tokens × $0.60/1M = **~$10.80**
- Embeddings: ~33M tokens × $0.02/1M = **~$0.66**
- **Total Add**: ~$16.71

**Search Method**:
- LLM Input: ~3.5M tokens × $0.15/1M = **~$0.53**
- LLM Output: ~3.4M tokens × $0.60/1M = **~$2.04**
- Embeddings: ~0.6M tokens × $0.02/1M = **~$0.01**
- **Total Search**: ~$2.58

**Grand Total**: ~$19.29

**Note**: These are estimates. Actual costs may vary based on:
- Actual token counts per call
- Whether consolidation is triggered for all batches
- Whether reranking is triggered for all questions
- Model pricing changes

## Improvements Over Original

The improved version adds:
- **Query Expansion**: +1,986 LLM calls (~298K tokens)
- **Reranking**: +1,986 LLM calls (~1.1M - 2.2M tokens)

**Additional Cost**: ~$0.40 - $0.80 for improved features

## Recommendations

1. **Start with a subset**: Test with 1-2 conversations first
2. **Monitor costs**: Check OpenAI usage dashboard regularly
3. **Optimize batch size**: Consider increasing batch_size to reduce API calls
4. **Cache embeddings**: Reuse embeddings when possible
5. **Use cheaper models**: Consider gpt-3.5-turbo for less critical tasks

