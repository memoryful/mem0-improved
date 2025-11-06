"""
Improved Mem0 Memory Addition with Enhanced Consolidation
"""
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from tqdm import tqdm

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from src.improved_mem0.memory_graph import MemoryGraph

load_dotenv()


# Enhanced custom instructions with hierarchical memory focus
custom_instructions = """
Generate personal memories that follow these guidelines:

1. **Hierarchical Memory Structure**: Organize memories in a hierarchical fashion:
   - **Episodic Level**: Specific events with time and context
   - **Semantic Level**: General facts and knowledge
   - **Meta Level**: Patterns, preferences, and relationships

2. **Memory Richness**: Each memory should be self-contained with complete context:
   - The person's name (do not use "user")
   - Personal details (career aspirations, hobbies, life circumstances)
   - Emotional states and reactions
   - Ongoing journeys or future plans
   - Specific dates when events occurred
   - Relationships between entities

3. **Importance Scoring**: Assign importance scores (1-10) to memories:
   - High importance (8-10): Life-changing events, strong preferences, critical facts
   - Medium importance (5-7): Regular activities, moderate preferences
   - Low importance (1-4): Casual mentions, minor details

4. **Temporal Context**: Include temporal markers:
   - Absolute dates when available
   - Relative time references with context
   - Temporal relationships (before, after, during)

5. **Meaningful Personal Narratives**: Focus on:
   - Identity and self-acceptance journeys
   - Family planning and parenting
   - Creative outlets and hobbies
   - Mental health and self-care activities
   - Career aspirations and education goals
   - Important life events and milestones
   - Interpersonal relationships

6. **Memory Format**: Structure as a paragraph with clear narrative structure that captures:
   - The person's experience
   - Challenges and aspirations
   - Temporal and relational context
   - Importance level

7. **Extract memories only from user messages**, not incorporating assistant responses
"""


class ImprovedMemoryADD:
    """Enhanced memory addition with hierarchical consolidation and importance scoring"""
    
    def __init__(self, data_path=None, batch_size=2, is_graph=False, enable_memory_graph=True):
        # Use local Memory class instead of API client for local evaluation
        config = MemoryConfig()
        config.custom_fact_extraction_prompt = custom_instructions
        self.memory = Memory(config=config)
        self.batch_size = batch_size
        self.data_path = data_path
        self.data = None
        self.is_graph = is_graph
        self.enable_memory_graph = enable_memory_graph
        self.memory_graph = MemoryGraph() if enable_memory_graph else None
        if data_path:
            self.load_data()

    def load_data(self):
        with open(self.data_path, "r") as f:
            self.data = json.load(f)
        return self.data

    def add_memory(self, user_id, message, metadata, retries=3):
        """Add memory with retry logic and graph building"""
        for attempt in range(retries):
            try:
                result = self.memory.add(
                    message, 
                    user_id=user_id, 
                    metadata=metadata
                )
                
                # Add to memory graph if enabled
                if self.enable_memory_graph and self.memory_graph:
                    # Extract memory text from result or message
                    if isinstance(result, dict):
                        memory_text = result.get("memory", "") or result.get("facts", "") or message
                        memory_id = result.get("id") or str(hash(memory_text))
                    else:
                        memory_text = message if isinstance(message, str) else str(message)
                        memory_id = str(hash(memory_text))
                    
                    # Add to graph
                    self.memory_graph.add_memory(memory_id, memory_text, metadata)
                
                return result
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise e

    def add_memories_for_speaker(self, speaker, messages, timestamp, desc):
        """Add memories for a speaker with batching"""
        for i in tqdm(range(0, len(messages), self.batch_size), desc=desc):
            batch_messages = messages[i : i + self.batch_size]
            self.add_memory(speaker, batch_messages, metadata={"timestamp": timestamp})

    def process_conversation(self, item, idx):
        """Process a single conversation"""
        conversation = item["conversation"]
        speaker_a = conversation["speaker_a"]
        speaker_b = conversation["speaker_b"]

        speaker_a_user_id = f"{speaker_a}_{idx}"
        speaker_b_user_id = f"{speaker_b}_{idx}"

        # Delete all memories for the two users
        # Note: delete_all doesn't exist in Memory class, we'll skip this for now
        # Memory will overwrite/replace memories as needed

        for key in conversation.keys():
            if key in ["speaker_a", "speaker_b"] or "date" in key or "timestamp" in key:
                continue

            date_time_key = key + "_date_time"
            timestamp = conversation[date_time_key]
            chats = conversation[key]

            messages = []
            messages_reverse = []
            for chat in chats:
                if chat["speaker"] == speaker_a:
                    messages.append({"role": "user", "content": f"{speaker_a}: {chat['text']}"})
                    messages_reverse.append({"role": "assistant", "content": f"{speaker_a}: {chat['text']}"})
                elif chat["speaker"] == speaker_b:
                    messages.append({"role": "assistant", "content": f"{speaker_b}: {chat['text']}"})
                    messages_reverse.append({"role": "user", "content": f"{speaker_b}: {chat['text']}"})
                else:
                    raise ValueError(f"Unknown speaker: {chat['speaker']}")

            # Add memories for the two users on different threads
            thread_a = threading.Thread(
                target=self.add_memories_for_speaker,
                args=(speaker_a_user_id, messages, timestamp, "Adding Memories for Speaker A"),
            )
            thread_b = threading.Thread(
                target=self.add_memories_for_speaker,
                args=(speaker_b_user_id, messages_reverse, timestamp, "Adding Memories for Speaker B"),
            )

            thread_a.start()
            thread_b.start()
            thread_a.join()
            thread_b.join()

        print("Messages added successfully")

    def process_all_conversations(self, max_workers=10):
        """Process all conversations in parallel"""
        if not self.data:
            raise ValueError("No data loaded. Please set data_path and call load_data() first.")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_conversation, item, idx) for idx, item in enumerate(self.data)]

            for future in futures:
                future.result()

