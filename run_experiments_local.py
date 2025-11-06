"""
Run improved mem0 experiments with local open-source models
"""
import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_local_models import get_local_ollama_config, get_local_lmstudio_config, get_openai_config
from src.improved_mem0.add_local import ImprovedMemoryADD
from src.improved_mem0.search import ImprovedMemorySearch


def main():
    parser = argparse.ArgumentParser(description="Run improved memory experiments with local models")
    parser.add_argument("--technique_type", default="improved_mem0", help="Memory technique to use")
    parser.add_argument("--method", choices=["add", "search"], default="add", help="Method to use")
    parser.add_argument("--output_folder", type=str, default="results/", help="Output path for results")
    parser.add_argument("--top_k", type=int, default=30, help="Number of top memories to retrieve")
    parser.add_argument("--filter_memories", action="store_true", default=False, help="Whether to filter memories")
    parser.add_argument("--is_graph", action="store_true", default=False, help="Whether to use graph-based search")
    parser.add_argument("--data_path", type=str, default="dataset/locomo10.json", help="Path to dataset")
    parser.add_argument("--model", type=str, default="llama3.2:latest", help="Ollama model name (e.g., llama3.2:latest, llama3.1:8b, mistral:7b)")
    parser.add_argument("--model_type", choices=["ollama", "lmstudio", "openai"], default="ollama", help="Model provider type")
    
    args = parser.parse_args()

    print(f"Running improved experiments with technique: {args.technique_type}, method: {args.method}")
    print(f"Model type: {args.model_type}")
    if args.model_type == "ollama":
        print(f"Ollama model: {args.model}")

    # Get configuration based on model type
    if args.model_type == "ollama":
        config = get_local_ollama_config(model_name=args.model)
    elif args.model_type == "lmstudio":
        config = get_local_lmstudio_config()
    elif args.model_type == "openai":
        config = get_openai_config()
    else:
        raise ValueError(f"Invalid model type: {args.model_type}")

    if args.technique_type == "improved_mem0":
        if args.method == "add":
            memory_manager = ImprovedMemoryADD(data_path=args.data_path, is_graph=args.is_graph, config=config)
            memory_manager.process_all_conversations()
        elif args.method == "search":
            output_file_path = os.path.join(
                args.output_folder,
                f"improved_mem0_local_{args.model_type}_{args.model.replace(':', '_')}_top_{args.top_k}_filter_{args.filter_memories}_graph_{args.is_graph}.json",
            )
            from src.improved_mem0.search import ImprovedMemorySearch
            memory_searcher = ImprovedMemorySearch(
                output_path=output_file_path, 
                top_k=args.top_k, 
                filter_memories=args.filter_memories, 
                is_graph=args.is_graph,
                config=config
            )
            memory_searcher.process_data_file(args.data_path)
    else:
        raise ValueError(f"Invalid technique type: {args.technique_type}")


if __name__ == "__main__":
    main()

