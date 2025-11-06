#!/usr/bin/env python3
"""
Simple test script for personal memory experiments
Test adding and searching memories with your own data
Uses Ollama with llama3.2:latest for local testing
"""
import json
from dotenv import load_dotenv
from mem0 import Memory
from config_local_models import get_local_ollama_config

load_dotenv()

# Enhanced custom instructions for personal memories
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


def test_add_memory():
    """Test adding memories"""
    print("=" * 60)
    print("Testing Memory Addition")
    print("=" * 60)
    
    # Initialize Memory with Ollama configuration
    print("Using Ollama with llama3.2:latest")
    config = get_local_ollama_config(model_name="llama3.2:latest")
    config.custom_fact_extraction_prompt = custom_instructions
    memory = Memory(config=config)
    
    user_id = "test_user_1"
    
    # Test messages - replace with your own personal data
    test_messages = [
        {
            "role": "user",
            "content": "Hi, I'm Sarah. I'm a software engineer working at a tech startup. I love hiking and recently went on a trip to the mountains last weekend."
        },
        {
            "role": "user",
            "content": "I'm planning to learn Spanish this year and have signed up for classes starting next month. I'm also thinking about moving to a new apartment."
        },
        {
            "role": "user",
            "content": "My favorite food is Italian cuisine, especially pasta. I don't like spicy food much."
        }
    ]
    
    print(f"\nAdding memories for user: {user_id}")
    print(f"Number of messages: {len(test_messages)}\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Adding message {i}/{len(test_messages)}: {message['content'][:60]}...")
        try:
            result = memory.add(
                message["content"],
                user_id=user_id,
                metadata={"source": "test", "message_id": i}
            )
            print(f"✅ Memory added successfully!")
            if result:
                if isinstance(result, dict):
                    print(f"   Memory ID: {result.get('id', 'N/A')}")
                    print(f"   Memory: {str(result)[:100]}...")
                else:
                    print(f"   Result: {str(result)[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 60)
    return memory, user_id


def test_search_memory(memory, user_id):
    """Test searching memories"""
    print("=" * 60)
    print("Testing Memory Search")
    print("=" * 60)
    
    # Test queries - replace with your own questions
    test_queries = [
        "What does Sarah do for work?",
        "What are Sarah's hobbies?",
                "What are Sarah's food preferences?",
        "What is Sarah planning to learn?",
    ]
    
    print(f"\nSearching memories for user: {user_id}")
    print(f"Number of queries: {len(test_queries)}\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}/{len(test_queries)}: {query}")
        try:
            results = memory.search(query, user_id=user_id, limit=5)
            print(f"✅ Found {len(results)} memories:")
            for j, result in enumerate(results, 1):
                # Handle different result formats
                if isinstance(result, str):
                    memory_text = result
                    score = "N/A"
                elif isinstance(result, dict):
                    memory_text = result.get('memory', result.get('facts', result.get('content', str(result))))
                    score = result.get('score', result.get('similarity', 'N/A'))
                else:
                    memory_text = str(result)
                    score = "N/A"
                
                print(f"   {j}. Score: {score:.4f if isinstance(score, float) else score}")
                if isinstance(memory_text, str):
                    print(f"      Memory: {memory_text[:150]}...")
                else:
                    print(f"      Memory: {str(memory_text)[:150]}...")
                print()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        print("-" * 60)
        print()


def test_get_all_memories(memory, user_id):
    """Test getting all memories"""
    print("=" * 60)
    print("Getting All Memories")
    print("=" * 60)
    
    try:
        all_memories = memory.get_all(user_id=user_id)
        print(f"\n✅ Retrieved {len(all_memories)} total memories for {user_id}:\n")
        
        for i, mem in enumerate(all_memories, 1):
            # Handle different memory formats
            if isinstance(mem, str):
                print(f"{i}. Memory: {mem}")
            elif isinstance(mem, dict):
                memory_text = mem.get('memory', mem.get('facts', mem.get('content', str(mem))))
                metadata = mem.get('metadata', {})
                print(f"{i}. Memory ID: {mem.get('id', 'N/A')}")
                print(f"   Content: {memory_text}")
                if metadata:
                    print(f"   Metadata: {metadata}")
            else:
                print(f"{i}. Memory: {mem}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Personal Memory Test Script")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Add test memories")
    print("2. Search those memories")
    print("3. Display all memories")
    print("\n" + "=" * 60 + "\n")
    
    try:
        # Step 1: Add memories
        memory, user_id = test_add_memory()
        
        # Step 2: Search memories
        test_search_memory(memory, user_id)
        
        # Step 3: Get all memories
        test_get_all_memories(memory, user_id)
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
