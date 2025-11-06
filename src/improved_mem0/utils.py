"""
Utility functions for improved memory operations
"""
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import hashlib


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity using word overlap"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0


def deduplicate_memories(memories: List[Dict[str, Any]], similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
    """
    Deduplicate and consolidate similar memories
    
    Args:
        memories: List of memory dictionaries
        similarity_threshold: Threshold for considering memories as duplicates (0-1)
    
    Returns:
        List of deduplicated memories
    """
    if not memories:
        return memories
    
    deduplicated = []
    seen_hashes = set()
    
    for memory in memories:
        memory_text = memory.get("memory", "") or memory.get("text", "") or str(memory)
        
        # Create hash for exact duplicates
        memory_hash = hashlib.md5(memory_text.lower().encode()).hexdigest()
        if memory_hash in seen_hashes:
            continue
        
        # Check for similar memories
        is_duplicate = False
        for existing in deduplicated:
            existing_text = existing.get("memory", "") or existing.get("text", "") or str(existing)
            similarity = calculate_similarity(memory_text, existing_text)
            
            if similarity >= similarity_threshold:
                # Merge similar memories - keep the one with higher score or more metadata
                existing_score = existing.get("score", 0.0)
                memory_score = memory.get("score", 0.0)
                
                if memory_score > existing_score:
                    # Replace with better memory
                    deduplicated.remove(existing)
                    deduplicated.append(memory)
                    seen_hashes.add(memory_hash)
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduplicated.append(memory)
            seen_hashes.add(memory_hash)
    
    return deduplicated


def consolidate_memories(memories: List[Dict[str, Any]], max_consolidation: int = 3) -> List[Dict[str, Any]]:
    """
    Consolidate related memories into summaries
    
    Args:
        memories: List of memory dictionaries
        max_consolidation: Maximum number of memories to consolidate together
    
    Returns:
        List of consolidated memories
    """
    if len(memories) <= 1:
        return memories
    
    # Group memories by topic/entity (simple keyword-based grouping)
    groups = defaultdict(list)
    
    for memory in memories:
        memory_text = memory.get("memory", "") or memory.get("text", "") or str(memory)
        # Extract key entities (simple: first few words)
        key_words = memory_text.lower().split()[:3]
        group_key = " ".join(key_words)
        groups[group_key].append(memory)
    
    consolidated = []
    for group_memories in groups.values():
        if len(group_memories) <= max_consolidation:
            # Keep individual memories if small group
            consolidated.extend(group_memories)
        else:
            # For larger groups, keep top-scored memories
            sorted_memories = sorted(group_memories, key=lambda x: x.get("score", 0.0), reverse=True)
            consolidated.extend(sorted_memories[:max_consolidation])
    
    return consolidated


def parse_temporal_expression(text: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    Parse temporal expressions like "3 months ago", "last week", "yesterday"
    
    Args:
        text: Text containing temporal expression
        reference_date: Reference date (defaults to now)
    
    Returns:
        Parsed datetime or None if not found
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    text_lower = text.lower()
    
    # Patterns for relative time
    patterns = [
        (r'(\d+)\s*(?:seconds?|secs?)\s*ago', lambda m: reference_date - timedelta(seconds=int(m.group(1)))),
        (r'(\d+)\s*(?:minutes?|mins?)\s*ago', lambda m: reference_date - timedelta(minutes=int(m.group(1)))),
        (r'(\d+)\s*(?:hours?|hrs?)\s*ago', lambda m: reference_date - timedelta(hours=int(m.group(1)))),
        (r'(\d+)\s*(?:days?)\s*ago', lambda m: reference_date - timedelta(days=int(m.group(1)))),
        (r'(\d+)\s*(?:weeks?)\s*ago', lambda m: reference_date - timedelta(weeks=int(m.group(1)))),
        (r'(\d+)\s*(?:months?)\s*ago', lambda m: reference_date - timedelta(days=int(m.group(1)) * 30)),
        (r'(\d+)\s*(?:years?)\s*ago', lambda m: reference_date - timedelta(days=int(m.group(1)) * 365)),
        (r'yesterday', lambda m: reference_date - timedelta(days=1)),
        (r'today', lambda m: reference_date),
        (r'last\s+week', lambda m: reference_date - timedelta(weeks=1)),
        (r'last\s+month', lambda m: reference_date - timedelta(days=30)),
        (r'last\s+year', lambda m: reference_date - timedelta(days=365)),
    ]
    
    for pattern, func in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                return func(match)
            except:
                continue
    
    # Try to parse absolute dates
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(text, fmt)
        except:
            continue
    
    return None


def extract_temporal_info(query: str) -> Dict[str, Any]:
    """
    Extract temporal information from query
    
    Returns:
        Dictionary with temporal information
    """
    query_lower = query.lower()
    
    # Detect temporal keywords
    temporal_keywords = {
        "when": ["when", "what time", "what date"],
        "relative": ["ago", "last", "first", "before", "after", "during", "recent", "earlier", "later"],
        "absolute": ["date", "time", "year", "month", "day", "week"]
    }
    
    has_temporal = any(
        keyword in query_lower 
        for keywords in temporal_keywords.values() 
        for keyword in keywords
    )
    
    # Try to parse temporal expression
    parsed_date = parse_temporal_expression(query)
    
    return {
        "has_temporal": has_temporal,
        "parsed_date": parsed_date,
        "temporal_type": "relative" if parsed_date else ("absolute" if has_temporal else None)
    }


def calculate_temporal_proximity(memory_date: Optional[datetime], query_date: Optional[datetime]) -> float:
    """
    Calculate temporal proximity score between memory date and query date
    
    Returns:
        Score between 0 and 1 (1 = same date, 0 = very far)
    """
    if not memory_date or not query_date:
        return 0.5  # Neutral score if dates unavailable
    
    time_diff = abs((memory_date - query_date).total_seconds())
    
    # Convert to days
    days_diff = time_diff / (24 * 3600)
    
    # Score decays with time difference
    # Same day = 1.0, 1 week = 0.7, 1 month = 0.4, 1 year = 0.1
    if days_diff == 0:
        return 1.0
    elif days_diff <= 7:
        return 1.0 - (days_diff / 7) * 0.3
    elif days_diff <= 30:
        return 0.7 - ((days_diff - 7) / 23) * 0.3
    elif days_diff <= 365:
        return 0.4 - ((days_diff - 30) / 335) * 0.3
    else:
        return max(0.1, 0.1 - (days_diff - 365) / 3650)


def estimate_query_complexity(query: str) -> Dict[str, Any]:
    """
    Estimate query complexity to determine retrieval parameters
    
    Returns:
        Dictionary with complexity metrics and suggested parameters
    """
    query_lower = query.lower()
    
    # Count question words (indicates complexity)
    question_words = ["what", "when", "where", "who", "why", "how", "which", "whose"]
    question_count = sum(1 for word in question_words if word in query_lower)
    
    # Count entities (proper nouns, capitalized words)
    entities = len(re.findall(r'\b[A-Z][a-z]+\b', query))
    
    # Count temporal references
    temporal_refs = len(re.findall(r'\b(when|date|time|ago|last|first|before|after)\b', query_lower))
    
    # Count relational words
    relational_words = ["relationship", "between", "with", "and", "or", "related"]
    relational_count = sum(1 for word in relational_words if word in query_lower)
    
    # Calculate complexity score (0-1)
    complexity = min(1.0, (
        (question_count * 0.2) +
        (min(entities, 5) * 0.15) +
        (temporal_refs * 0.2) +
        (min(relational_count, 3) * 0.15) +
        (len(query.split()) / 50) * 0.3  # Length factor
    ))
    
    # Determine query type
    if temporal_refs > 0:
        query_type = "temporal"
    elif relational_count > 0 or "relationship" in query_lower:
        query_type = "relational"
    elif question_count > 1:
        query_type = "complex"
    else:
        query_type = "simple"
    
    # Suggest parameters based on complexity
    if complexity < 0.3:
        suggested_top_k = 10
        suggested_expansions = 1
    elif complexity < 0.6:
        suggested_top_k = 20
        suggested_expansions = 2
    else:
        suggested_top_k = 30
        suggested_expansions = 3
    
    return {
        "complexity": complexity,
        "query_type": query_type,
        "suggested_top_k": suggested_top_k,
        "suggested_expansions": suggested_expansions,
        "question_count": question_count,
        "entities": entities,
        "temporal_refs": temporal_refs,
        "relational_count": relational_count
    }

