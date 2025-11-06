"""
Improved Mem0 Memory Search with Multi-Step Query Expansion and Cross-Encoder Reranking
"""
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Template
from openai import OpenAI
from tqdm import tqdm

from mem0 import Memory
from mem0.configs.base import MemoryConfig

# Add parent directory to path to import prompts_improved
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from prompts_improved import ANSWER_PROMPT_IMPROVED, ANSWER_PROMPT_IMPROVED_GRAPH
from src.improved_mem0.utils import (
    deduplicate_memories,
    consolidate_memories,
    extract_temporal_info,
    calculate_temporal_proximity,
    parse_temporal_expression,
    estimate_query_complexity
)
from src.improved_mem0.multi_hop import MultiHopReasoning
from src.improved_mem0.memory_graph import MemoryGraph

load_dotenv()


class ImprovedMemorySearch:
    """Enhanced memory search with multi-step query expansion and cross-encoder reranking"""
    
    def __init__(self, output_path="results.json", top_k=10, filter_memories=False, is_graph=False, config=None, 
                 enable_deduplication=True, enable_adaptive_params=True, batch_size=5, enable_multi_hop=True):
        # Use local Memory class instead of API client for local evaluation
        if config is None:
            config = MemoryConfig()
        self.memory = Memory(config=config)
        self.base_top_k = top_k  # Base top_k, can be adjusted adaptively
        self.top_k = top_k
        # Use the LLM from config instead of OpenAI client
        self.llm = self.memory.llm
        self.results = defaultdict(list)
        self.output_path = output_path
        self.filter_memories = filter_memories
        self.is_graph = is_graph
        self.enable_deduplication = enable_deduplication
        self.enable_adaptive_params = enable_adaptive_params
        self.batch_size = batch_size  # For batch processing
        self.enable_multi_hop = enable_multi_hop
        self.multi_hop_reasoner = MultiHopReasoning(max_hops=2) if enable_multi_hop else None

        if self.is_graph:
            self.ANSWER_PROMPT = ANSWER_PROMPT_IMPROVED_GRAPH
        else:
            self.ANSWER_PROMPT = ANSWER_PROMPT_IMPROVED

    def expand_query(self, query, max_expansions=None, max_retries=3):
        """Expand query into multiple related queries for better retrieval coverage"""
        # Adaptive expansion count based on query complexity
        if self.enable_adaptive_params and max_expansions is None:
            complexity_info = estimate_query_complexity(query)
            max_expansions = complexity_info["suggested_expansions"]
        else:
            max_expansions = max_expansions or 2
        
        expansion_prompt = f"""
        Given the following question, generate {max_expansions} related queries that could help retrieve relevant information.
        Focus on:
        1. Temporal aspects (when, what date, time period)
        2. Entity relationships (who, what relationships)
        3. Contextual variations (synonyms, related concepts)
        
        Original question: {query}
        
        Return a JSON object with a "queries" key containing an array of query strings:
        {{"queries": ["query1", "query2", "query3"]}}
        """
        
        for attempt in range(max_retries):
            try:
                # Use the LLM from memory config
                response = self.llm.generate_response(
                    messages=[{"role": "user", "content": expansion_prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                # Handle different response formats
                if isinstance(response, str):
                    expanded = json.loads(response)
                else:
                    expanded = json.loads(response.choices[0].message.content)
                queries = expanded.get("queries", [])
                if not queries:
                    queries = [query]
                # Always include original query
                if query not in queries:
                    queries = [query] + queries
                # Limit to max_expansions + 1 (original + expansions)
                queries = queries[:max_expansions + 1]
                return queries
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return [query]

    def search_memory_with_expansion(self, user_id, query, max_retries=3, retry_delay=1):
        """Search memory with query expansion, deduplication, and enhanced temporal reasoning"""
        start_time = time.time()
        
        # Adaptive parameters based on query complexity
        if self.enable_adaptive_params:
            complexity_info = estimate_query_complexity(query)
            self.top_k = complexity_info["suggested_top_k"]
            max_expansions = complexity_info["suggested_expansions"]
        else:
            self.top_k = self.base_top_k
            max_expansions = None
        
        # Extract temporal information from query
        temporal_info = extract_temporal_info(query)
        query_date = temporal_info.get("parsed_date")
        
        # Expand query
        expanded_queries = self.expand_query(query, max_expansions=max_expansions)
        
        # Search with all queries (can be parallelized)
        all_memories = []
        seen_memory_ids = set()
        graph_relations = []  # Store graph relations if available
        
        for expanded_query in expanded_queries:
            retries = 0
            while retries < max_retries:
                try:
                    memories = self.memory.search(
                        expanded_query, 
                        user_id=user_id, 
                        limit=self.top_k * 2,  # Get more for deduplication
                        filters={"user_id": user_id} if self.filter_memories else None
                    )
                    # Convert to dict format for consistency
                    if isinstance(memories, dict):
                        memories = memories.get("results", [])
                    break
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    time.sleep(retry_delay)
            
            # Collect unique memories
            # Handle both list and dict formats from Memory class
            if isinstance(memories, dict):
                memory_list = memories.get("results", [])
            else:
                memory_list = memories if isinstance(memories, list) else []
            
            for memory in memory_list:
                if not isinstance(memory, dict):
                    continue
                # Get memory ID - handle different formats
                mem_id = memory.get("id") or memory.get("memory_id") or str(hash(memory.get("memory", "")))
                if mem_id not in seen_memory_ids:
                    seen_memory_ids.add(mem_id)
                    all_memories.append(memory)
            
            # Graph relations not supported in local Memory class for now
            # graph_relations.extend(relations)
        
        # Deduplicate memories
        if self.enable_deduplication:
            all_memories = deduplicate_memories(all_memories, similarity_threshold=0.75)
            all_memories = consolidate_memories(all_memories, max_consolidation=3)
        
        # Enhanced temporal reasoning - calculate temporal proximity scores
        if temporal_info["has_temporal"] and query_date:
            for memory in all_memories:
                metadata = memory.get("metadata", {})
                if not isinstance(metadata, dict):
                    metadata = {}
                memory_timestamp = metadata.get("timestamp", "")
                
                if memory_timestamp:
                    # Try to parse memory timestamp
                    memory_date = parse_temporal_expression(memory_timestamp)
                    if memory_date:
                        temporal_proximity = calculate_temporal_proximity(memory_date, query_date)
                        # Boost score with temporal proximity
                        current_score = memory.get("score", 0.0)
                        memory["temporal_proximity"] = temporal_proximity
                        memory["score"] = current_score * (1 + temporal_proximity * 0.5)
        
        # Rerank memories by relevance (simple scoring based on query match)
        all_memories = self.rerank_memories(query, all_memories)
        
        # Multi-hop reasoning if enabled
        if self.enable_multi_hop and self.multi_hop_reasoner:
            try:
                # Get all memories for multi-hop reasoning
                all_available_memories = self.memory.get_all(user_id=user_id) if hasattr(self.memory, 'get_all') else all_memories
                
                # Convert to format expected by multi-hop reasoner
                formatted_memories = []
                for mem in all_available_memories:
                    if isinstance(mem, dict):
                        formatted_memories.append(mem)
                    else:
                        formatted_memories.append({"memory": str(mem), "text": str(mem)})
                
                # Perform multi-hop reasoning
                chained_memories, reasoning_path = self.multi_hop_reasoner.answer_with_multi_hop(
                    query, all_memories[:self.top_k], formatted_memories
                )
                
                # Merge chained memories with original (deduplicate)
                seen_ids = {mem.get("id") or str(hash(mem.get("memory", ""))) for mem in all_memories[:self.top_k]}
                for chained_mem in chained_memories:
                    chained_id = chained_mem.get("id") or str(hash(chained_mem.get("memory", "")))
                    if chained_id not in seen_ids:
                        all_memories.append(chained_mem)
                        seen_ids.add(chained_id)
                
                # Re-sort by score
                all_memories.sort(key=lambda x: x.get("score", x.get("rerank_score", 0.0)), reverse=True)
            except Exception as e:
                print(f"Multi-hop reasoning failed: {e}, using original memories")
        
        # Take top_k after reranking and multi-hop
        all_memories = all_memories[:self.top_k]
        
        end_time = time.time()
        
        # Format semantic memories
        semantic_memories = []
        for memory in all_memories:
            # Handle different memory formats
            memory_text = memory.get("memory", "") or memory.get("text", "") or memory.get("data", "")
            metadata = memory.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            timestamp = metadata.get("timestamp", "")
            score = memory.get("score", memory.get("rerank_score", 0.0))
            hop_level = memory.get("hop_level", 0)
            
            semantic_memories.append({
                "memory": memory_text,
                "timestamp": timestamp,
                "score": round(score, 2),
                "hop_level": hop_level,
            })
        
        # Graph-based memory retrieval if available
        graph_memories = None
        if self.is_graph:
            # Try to get graph from memory instance if available
            # For now, we'll use entity-based search from graph
            try:
                # Extract entities from query
                query_entities = set()
                for memory in semantic_memories[:5]:  # Use top memories to find entities
                    memory_text = memory.get("memory", "")
                    # Simple entity extraction
                    import re
                    entities = set(re.findall(r'\b[A-Z][a-z]+\b', memory_text))
                    query_entities.update(entities)
                
                # If we have a memory graph, use it to find related memories
                # This would require passing the graph from add.py
                # For now, graph_memories remains None
                graph_memories = []
            except Exception as e:
                print(f"Graph memory retrieval failed: {e}")
                graph_memories = None
        
        return semantic_memories, graph_memories, end_time - start_time

    def rerank_memories(self, query, memories, batch_size=None):
        """Rerank memories using cross-encoder style scoring with batch processing"""
        if not memories:
            return memories
        
        batch_size = batch_size or self.batch_size
        
        # If memories fit in one batch, process all at once
        if len(memories) <= batch_size:
            return self._rerank_batch(query, memories)
        
        # Process in batches and merge results
        reranked_memories = []
        for i in range(0, len(memories), batch_size):
            batch = memories[i:i + batch_size]
            reranked_batch = self._rerank_batch(query, batch)
            reranked_memories.extend(reranked_batch)
        
        # Final sort across all batches
        reranked_memories.sort(key=lambda x: x.get("rerank_score", x.get("score", 0.0)), reverse=True)
        return reranked_memories
    
    def _rerank_batch(self, query, memories):
        """Rerank a batch of memories"""
        if not memories:
            return memories
        
        # Use LLM to score relevance
        scoring_prompt = f"""
        Given the query and a list of memories, score each memory's relevance to the query.
        Query: {query}
        
        Memories:
        {json.dumps([{"id": i, "memory": m.get("memory", "") or m.get("text", "")} for i, m in enumerate(memories)], indent=2)}
        
        Return a JSON object with memory IDs as keys and relevance scores (0-1) as values:
        {{"0": 0.9, "1": 0.7, ...}}
        """
        
        try:
            # Use the LLM from memory config
            response = self.llm.generate_response(
                messages=[{"role": "user", "content": scoring_prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            # Handle different response formats
            if isinstance(response, str):
                scores = json.loads(response)
            else:
                scores = json.loads(response.choices[0].message.content)
            
            # Update memory scores and sort
            for i, memory in enumerate(memories):
                memory["rerank_score"] = scores.get(str(i), memory.get("score", 0.0))
            
            memories.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        except Exception as e:
            print(f"Reranking failed: {e}, using original scores")
            # Fallback to original scores
            memories.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        return memories

    def apply_temporal_attention(self, memories, query):
        """Apply enhanced temporal attention weighting to memories"""
        # Extract temporal information
        temporal_info = extract_temporal_info(query)
        query_date = temporal_info.get("parsed_date")
        
        if not temporal_info["has_temporal"]:
            return memories
        
        # Enhanced temporal weighting with proximity calculation
        for memory in memories:
            timestamp = memory.get("timestamp", "")
            if timestamp and query_date:
                # Parse memory timestamp
                memory_date = parse_temporal_expression(timestamp)
                if memory_date:
                    # Calculate temporal proximity
                    proximity = calculate_temporal_proximity(memory_date, query_date)
                    memory["temporal_weight"] = 1.0 + (proximity * 0.5)  # 1.0 to 1.5
                else:
                    memory["temporal_weight"] = 1.3  # Default boost for temporal queries
            elif timestamp:
                # Has timestamp but no query date - still boost
                memory["temporal_weight"] = 1.3
            else:
                memory["temporal_weight"] = 1.0
        
        # Re-sort with temporal weighting
        memories.sort(
            key=lambda x: x.get("score", 0.0) * x.get("temporal_weight", 1.0), 
            reverse=True
        )
        
        return memories

    def answer_question(self, speaker_1_user_id, speaker_2_user_id, question, answer, category):
        """Answer question using improved search"""
        speaker_1_memories, speaker_1_graph_memories, speaker_1_memory_time = self.search_memory_with_expansion(
            speaker_1_user_id, question
        )
        speaker_2_memories, speaker_2_graph_memories, speaker_2_memory_time = self.search_memory_with_expansion(
            speaker_2_user_id, question
        )
        
        # Apply temporal attention
        speaker_1_memories = self.apply_temporal_attention(speaker_1_memories, question)
        speaker_2_memories = self.apply_temporal_attention(speaker_2_memories, question)

        search_1_memory = [f"{item['timestamp']}: {item['memory']}" for item in speaker_1_memories]
        search_2_memory = [f"{item['timestamp']}: {item['memory']}" for item in speaker_2_memories]

        template = Template(self.ANSWER_PROMPT)
        answer_prompt = template.render(
            speaker_1_user_id=speaker_1_user_id.split("_")[0],
            speaker_2_user_id=speaker_2_user_id.split("_")[0],
            speaker_1_memories=json.dumps(search_1_memory, indent=4),
            speaker_2_memories=json.dumps(search_2_memory, indent=4),
            speaker_1_graph_memories=json.dumps(speaker_1_graph_memories, indent=4) if speaker_1_graph_memories else "[]",
            speaker_2_graph_memories=json.dumps(speaker_2_graph_memories, indent=4) if speaker_2_graph_memories else "[]",
            question=question,
        )

        t1 = time.time()
        # Use the LLM from memory config
        response = self.llm.generate_response(
            messages=[{"role": "system", "content": answer_prompt}], 
            temperature=0.0
        )
        t2 = time.time()
        response_time = t2 - t1
        
        # Handle different response formats
        if isinstance(response, str):
            response_content = response
        else:
            response_content = response.choices[0].message.content
        
        return (
            response_content,
            speaker_1_memories,
            speaker_2_memories,
            speaker_1_memory_time,
            speaker_2_memory_time,
            speaker_1_graph_memories,
            speaker_2_graph_memories,
            response_time,
        )

    def process_question(self, val, speaker_a_user_id, speaker_b_user_id):
        """Process a single question"""
        question = val.get("question", "")
        answer = val.get("answer", "")
        category = val.get("category", -1)
        evidence = val.get("evidence", [])
        adversarial_answer = val.get("adversarial_answer", "")

        (
            response,
            speaker_1_memories,
            speaker_2_memories,
            speaker_1_memory_time,
            speaker_2_memory_time,
            speaker_1_graph_memories,
            speaker_2_graph_memories,
            response_time,
        ) = self.answer_question(speaker_a_user_id, speaker_b_user_id, question, answer, category)

        result = {
            "question": question,
            "answer": answer,
            "category": category,
            "evidence": evidence,
            "response": response,
            "adversarial_answer": adversarial_answer,
            "speaker_1_memories": speaker_1_memories,
            "speaker_2_memories": speaker_2_memories,
            "num_speaker_1_memories": len(speaker_1_memories),
            "num_speaker_2_memories": len(speaker_2_memories),
            "speaker_1_memory_time": speaker_1_memory_time,
            "speaker_2_memory_time": speaker_2_memory_time,
            "speaker_1_graph_memories": speaker_1_graph_memories,
            "speaker_2_graph_memories": speaker_2_graph_memories,
            "response_time": response_time,
        }

        # Save results after each question
        with open(self.output_path, "w") as f:
            json.dump(self.results, f, indent=4)

        return result

    def process_data_file(self, file_path, max_workers=4):
        """Process all questions in the dataset with batch processing optimizations"""
        with open(file_path, "r") as f:
            data = json.load(f)

        # Collect all questions for batch processing
        all_questions = []
        for idx, item in enumerate(data):
            qa = item["qa"]
            conversation = item["conversation"]
            speaker_a = conversation["speaker_a"]
            speaker_b = conversation["speaker_b"]

            speaker_a_user_id = f"{speaker_a}_{idx}"
            speaker_b_user_id = f"{speaker_b}_{idx}"

            for question_item in qa:
                all_questions.append({
                    "idx": idx,
                    "question_item": question_item,
                    "speaker_a_user_id": speaker_a_user_id,
                    "speaker_b_user_id": speaker_b_user_id
                })

        # Process questions in batches with parallel execution
        def process_single_question(item):
            try:
                result = self.process_question(
                    item["question_item"],
                    item["speaker_a_user_id"],
                    item["speaker_b_user_id"]
                )
                return (item["idx"], result)
            except Exception as e:
                print(f"Error processing question: {e}")
                return None

        # Process in batches
        for i in tqdm(range(0, len(all_questions), self.batch_size), desc="Processing question batches"):
            batch = all_questions[i:i + self.batch_size]
            
            # Use ThreadPoolExecutor for parallel processing within batch
            with ThreadPoolExecutor(max_workers=min(max_workers, len(batch))) as executor:
                batch_results = list(executor.map(process_single_question, batch))
            
            # Collect results and save
            for result in batch_results:
                if result is not None:
                    idx, question_result = result
                    if idx not in self.results:
                        self.results[idx] = []
                    self.results[idx].append(question_result)
            
            # Save results after each batch
            with open(self.output_path, "w") as f:
                json.dump(self.results, f, indent=4)

        # Final save
        with open(self.output_path, "w") as f:
            json.dump(self.results, f, indent=4)

