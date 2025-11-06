"""
Multi-hop reasoning for complex queries
Chains related memories to answer questions requiring multiple steps
"""
import json
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, deque


class MultiHopReasoning:
    """Multi-hop reasoning engine for chaining related memories"""
    
    def __init__(self, max_hops: int = 2, similarity_threshold: float = 0.3):
        """
        Initialize multi-hop reasoning
        
        Args:
            max_hops: Maximum number of hops to traverse
            similarity_threshold: Minimum similarity to consider memories related
        """
        self.max_hops = max_hops
        self.similarity_threshold = similarity_threshold
    
    def extract_entities(self, text: str) -> Set[str]:
        """Extract entities (simple: capitalized words, proper nouns)"""
        import re
        # Find capitalized words (potential entities)
        entities = set(re.findall(r'\b[A-Z][a-z]+\b', text))
        # Remove common words
        common_words = {"The", "This", "That", "These", "Those", "A", "An"}
        entities = entities - common_words
        return entities
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def find_related_memories(self, current_memory: Dict[str, Any], all_memories: List[Dict[str, Any]], 
                             visited: Set[str]) -> List[Dict[str, Any]]:
        """Find memories related to the current memory"""
        current_text = current_memory.get("memory", "") or current_memory.get("text", "")
        current_entities = self.extract_entities(current_text)
        current_id = current_memory.get("id") or str(hash(current_text))
        
        related = []
        for memory in all_memories:
            memory_text = memory.get("memory", "") or memory.get("text", "")
            memory_id = memory.get("id") or str(hash(memory_text))
            
            # Skip if already visited
            if memory_id in visited:
                continue
            
            # Check entity overlap
            memory_entities = self.extract_entities(memory_text)
            entity_overlap = len(current_entities.intersection(memory_entities))
            
            # Check text similarity
            similarity = self.calculate_text_similarity(current_text, memory_text)
            
            # Consider related if entity overlap or high similarity
            if entity_overlap > 0 or similarity >= self.similarity_threshold:
                memory["relation_score"] = (entity_overlap * 0.5) + (similarity * 0.5)
                related.append(memory)
        
        # Sort by relation score
        related.sort(key=lambda x: x.get("relation_score", 0.0), reverse=True)
        return related[:5]  # Return top 5 related memories
    
    def chain_memories(self, initial_memories: List[Dict[str, Any]], 
                      all_memories: List[Dict[str, Any]], 
                      query: str) -> List[Dict[str, Any]]:
        """
        Chain memories through multiple hops to find related information
        
        Args:
            initial_memories: Starting set of memories from initial search
            all_memories: All available memories to search through
            query: Original query for context
        
        Returns:
            List of chained memories including initial and related memories
        """
        if not initial_memories:
            return []
        
        chained_memories = []
        visited = set()
        queue = deque()
        
        # Add initial memories to queue
        for memory in initial_memories:
            memory_text = memory.get("memory", "") or memory.get("text", "")
            memory_id = memory.get("id") or str(hash(memory_text))
            visited.add(memory_id)
            chained_memories.append(memory)
            queue.append((memory, 0))  # (memory, hop_level)
        
        # Traverse through hops
        while queue:
            current_memory, hop_level = queue.popleft()
            
            if hop_level >= self.max_hops:
                continue
            
            # Find related memories
            related = self.find_related_memories(current_memory, all_memories, visited)
            
            for related_memory in related:
                memory_text = related_memory.get("memory", "") or related_memory.get("text", "")
                memory_id = related_memory.get("id") or str(hash(memory_text))
                
                if memory_id not in visited:
                    visited.add(memory_id)
                    related_memory["hop_level"] = hop_level + 1
                    chained_memories.append(related_memory)
                    queue.append((related_memory, hop_level + 1))
        
        return chained_memories
    
    def answer_with_multi_hop(self, query: str, initial_memories: List[Dict[str, Any]], 
                              all_memories: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
        """
        Answer query using multi-hop reasoning
        
        Returns:
            Tuple of (chained_memories, reasoning_path)
        """
        # Determine if query needs multi-hop reasoning
        query_lower = query.lower()
        multi_hop_indicators = [
            "relationship", "between", "related", "connected", "chain",
            "because", "why", "how", "through", "via"
        ]
        
        needs_multi_hop = any(indicator in query_lower for indicator in multi_hop_indicators)
        
        if not needs_multi_hop or not initial_memories:
            return initial_memories, "Single-hop reasoning sufficient"
        
        # Chain memories
        chained_memories = self.chain_memories(initial_memories, all_memories, query)
        
        # Build reasoning path
        reasoning_path = f"Found {len(initial_memories)} initial memories, "
        reasoning_path += f"chained to {len(chained_memories) - len(initial_memories)} related memories "
        reasoning_path += f"through {self.max_hops} hops"
        
        return chained_memories, reasoning_path

