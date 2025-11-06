"""
Configuration for local open-source models
"""
from mem0.configs.base import MemoryConfig, LlmConfig, EmbedderConfig, VectorStoreConfig


def get_local_ollama_config(model_name="llama3.2:latest"):
    """
    Get configuration for Ollama (local LLM)
    
    Popular models:
    - llama3.1:8b (fast, good quality)
    - llama3.1:70b (slower, better quality)
    - mistral:7b (fast, good quality)
    - mistral-nemo:12b (fast, good quality)
    - qwen2.5:7b (fast, good quality)
    - phi3:3.8b (very fast, smaller)
    
    To install models:
    $ ollama pull llama3.1:8b
    $ ollama pull mistral:7b
    """
    config = MemoryConfig(
        llm=LlmConfig(
            provider="ollama",
            config={
                "model": model_name,
                "temperature": 0.1,
                "max_tokens": 2000,
                "ollama_base_url": "http://localhost:11434",  # Default Ollama URL
            }
        ),
        embedder=EmbedderConfig(
            provider="huggingface",
            config={
                "model": "sentence-transformers/all-MiniLM-L6-v2",  # Fast, free
                # Alternative: "BAAI/bge-small-en-v1.5" (better quality)
            }
        ),
        vector_store=VectorStoreConfig(
            provider="chroma",  # Local vector store
            config={
                "collection_name": "mem0_improved",
                "path": "./chroma_db",  # Local path for ChromaDB
            }
        ),
        custom_fact_extraction_prompt=None,  # Will use default
    )
    return config


def get_local_lmstudio_config():
    """
    Get configuration for LM Studio (local LLM server)
    
    Requires:
    1. Install LM Studio: https://lmstudio.ai/
    2. Start local server from "Server" tab
    3. Load a model (e.g., Llama 3.1 8B)
    """
    config = MemoryConfig(
        llm=LlmConfig(
            provider="lmstudio",
            config={
                "model": "lmstudio-community/Meta-Llama-3.1-70B-Instruct-GGUF/Meta-Llama-3.1-70B-Instruct-IQ2_M.gguf",
                "temperature": 0.2,
                "max_tokens": 2000,
                "lmstudio_base_url": "http://localhost:1234/v1",
            }
        ),
        embedder=EmbedderConfig(
            provider="huggingface",
            config={
                "model": "sentence-transformers/all-MiniLM-L6-v2",
            }
        ),
        vector_store=VectorStoreConfig(
            provider="chroma",
            config={
                "collection_name": "mem0_improved",
                "path": "./chroma_db_lmstudio",  # Local path for ChromaDB
            }
        ),
    )
    return config


def get_openai_config():
    """
    Get configuration for OpenAI (original benchmark)
    """
    config = MemoryConfig(
        llm=LlmConfig(
            provider="openai",
            config={
                "model": "gpt-4o-mini",
                "temperature": 0.0,
            }
        ),
        embedder=EmbedderConfig(
            provider="openai",
            config={
                "model": "text-embedding-3-small",
            }
        ),
        vector_store=VectorStoreConfig(
            provider="chroma",
            config={
                "collection_name": "mem0_openai",
                "path": "./chroma_db_openai",  # Local path for ChromaDB
            }
        ),
    )
    return config

