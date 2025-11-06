"""
Memory Relationship Graph
Builds and maintains an entity-relationship graph from memories
"""
import json
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import hashlib


class MemoryGraph:
    """Entity-relationship graph for memories"""
    
    def __init__(self):
        """Initialize empty graph"""
        self.entities = {}  # entity_id -> entity_info
        self.relationships = defaultdict(list)  # entity_id -> [(related_entity_id, relationship_type, strength)]
        self.memory_entities = defaultdict(set)  # memory_id -> set of entity_ids
        self.entity_memories = defaultdict(set)  # entity_id -> set of memory_ids
    
    def extract_entities(self, text: str) -> Set[str]:
        """Extract entities from text (simple: capitalized words, proper nouns)"""
        # Find capitalized words (potential entities)
        entities = set(re.findall(r'\b[A-Z][a-z]+\b', text))
        
        # Remove common words
        common_words = {
            "The", "This", "That", "These", "Those", "A", "An", "I", "You", "He", "She",
            "It", "We", "They", "When", "Where", "What", "Who", "Why", "How", "Which"
        }
        entities = entities - common_words
        
        # Also extract quoted strings (often names)
        quoted = set(re.findall(r'"([^"]+)"', text))
        entities.update(quoted)
        
        return entities
    
    def extract_relationships(self, text: str, entities: Set[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships between entities
        
        Returns:
            List of (entity1, entity2, relationship_type) tuples
        """
        relationships = []
        text_lower = text.lower()
        
        # Relationship patterns
        relationship_patterns = [
            (r'(\w+)\s+(?:is|was|are|were)\s+(?:a|an|the)?\s*(\w+)', 'is_a'),
            (r'(\w+)\s+(?:has|had|have)\s+(\w+)', 'has'),
            (r'(\w+)\s+(?:works?|worked)\s+(?:at|for)\s+(\w+)', 'works_at'),
            (r'(\w+)\s+(?:lives?|lived)\s+(?:in|at)\s+(\w+)', 'lives_in'),
            (r'(\w+)\s+(?:loves?|likes?|enjoys?)\s+(\w+)', 'likes'),
            (r'(\w+)\s+(?:went|goes|going)\s+to\s+(\w+)', 'went_to'),
            (r'(\w+)\s+(?:met|meets?)\s+(\w+)', 'met'),
            (r'(\w+)\s+(?:with|and)\s+(\w+)', 'with'),
        ]
        
        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    entity1 = match.group(1).capitalize()
                    entity2 = match.group(2).capitalize()
                    
                    # Check if entities are in our entity set
                    if entity1 in entities and entity2 in entities:
                        relationships.append((entity1, entity2, rel_type))
                except (IndexError, AttributeError):
                    continue
        
        return relationships
    
    def add_memory(self, memory_id: str, memory_text: str, metadata: Optional[Dict] = None):
        """Add a memory to the graph and extract entities/relationships"""
        # Extract entities
        entities = self.extract_entities(memory_text)
        
        # Store memory-entity mappings
        self.memory_entities[memory_id] = entities
        for entity in entities:
            self.entity_memories[entity].add(memory_id)
            
            # Initialize entity if not exists
            if entity not in self.entities:
                self.entities[entity] = {
                    "id": entity,
                    "name": entity,
                    "first_seen": metadata.get("timestamp", "") if metadata else "",
                    "memory_count": 0
                }
            
            self.entities[entity]["memory_count"] += 1
        
        # Extract relationships
        relationships = self.extract_relationships(memory_text, entities)
        
        for entity1, entity2, rel_type in relationships:
            # Ensure both entities exist
            if entity1 not in self.entities:
                self.entities[entity1] = {
                    "id": entity1,
                    "name": entity1,
                    "first_seen": metadata.get("timestamp", "") if metadata else "",
                    "memory_count": 0
                }
            if entity2 not in self.entities:
                self.entities[entity2] = {
                    "id": entity2,
                    "name": entity2,
                    "first_seen": metadata.get("timestamp", "") if metadata else "",
                    "memory_count": 0
                }
            
            # Add relationship (bidirectional)
            self.relationships[entity1].append((entity2, rel_type, 1.0))
            self.relationships[entity2].append((entity1, rel_type, 1.0))
    
    def get_related_entities(self, entity: str, max_depth: int = 2) -> Set[str]:
        """Get entities related to the given entity through graph traversal"""
        if entity not in self.entities:
            return set()
        
        related = set()
        visited = set()
        queue = [(entity, 0)]  # (entity, depth)
        
        while queue:
            current_entity, depth = queue.pop(0)
            
            if depth >= max_depth or current_entity in visited:
                continue
            
            visited.add(current_entity)
            related.add(current_entity)
            
            # Get directly related entities
            for related_entity, rel_type, strength in self.relationships.get(current_entity, []):
                if related_entity not in visited:
                    queue.append((related_entity, depth + 1))
        
        related.discard(entity)  # Remove self
        return related
    
    def get_related_memories(self, entity: str, max_depth: int = 2) -> Set[str]:
        """Get memories related to an entity through the graph"""
        related_entities = self.get_related_entities(entity, max_depth)
        related_memories = set()
        
        # Get memories for all related entities
        for related_entity in related_entities:
            related_memories.update(self.entity_memories.get(related_entity, set()))
        
        return related_memories
    
    def find_memory_path(self, entity1: str, entity2: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find a path between two entities through the graph"""
        if entity1 not in self.entities or entity2 not in self.entities:
            return None
        
        if entity1 == entity2:
            return [entity1]
        
        # BFS to find path
        queue = [(entity1, [entity1])]
        visited = {entity1}
        
        while queue:
            current_entity, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_entity == entity2:
                return path
            
            # Explore neighbors
            for related_entity, rel_type, strength in self.relationships.get(current_entity, []):
                if related_entity not in visited:
                    visited.add(related_entity)
                    queue.append((related_entity, path + [related_entity]))
        
        return None
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        total_relationships = sum(len(rels) for rels in self.relationships.values()) // 2  # Divide by 2 for bidirectional
        
        return {
            "num_entities": len(self.entities),
            "num_relationships": total_relationships,
            "num_memories": len(self.memory_entities),
            "avg_entities_per_memory": sum(len(entities) for entities in self.memory_entities.values()) / len(self.memory_entities) if self.memory_entities else 0,
            "avg_memories_per_entity": sum(len(memories) for memories in self.entity_memories.values()) / len(self.entity_memories) if self.entity_memories else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization"""
        return {
            "entities": self.entities,
            "relationships": {k: v for k, v in self.relationships.items()},
            "memory_entities": {k: list(v) for k, v in self.memory_entities.items()},
            "entity_memories": {k: list(v) for k, v in self.entity_memories.items()}
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load graph from dictionary"""
        self.entities = data.get("entities", {})
        self.relationships = defaultdict(list, data.get("relationships", {}))
        self.memory_entities = defaultdict(set, {k: set(v) for k, v in data.get("memory_entities", {}).items()})
        self.entity_memories = defaultdict(set, {k: set(v) for k, v in data.get("entity_memories", {}).items()})

