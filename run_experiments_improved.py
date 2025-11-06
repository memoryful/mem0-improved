"""
Run improved mem0 experiments
"""
import argparse
import os

from src.improved_mem0.add import ImprovedMemoryADD
from src.improved_mem0.search import ImprovedMemorySearch


def main():
    parser = argparse.ArgumentParser(description="Run improved memory experiments")
    parser.add_argument("--technique_type", default="improved_mem0", help="Memory technique to use")
    parser.add_argument("--method", choices=["add", "search"], default="add", help="Method to use")
    parser.add_argument("--output_folder", type=str, default="results/", help="Output path for results")
    parser.add_argument("--top_k", type=int, default=30, help="Number of top memories to retrieve")
    parser.add_argument("--filter_memories", action="store_true", default=False, help="Whether to filter memories")
    parser.add_argument("--is_graph", action="store_true", default=False, help="Whether to use graph-based search")
    parser.add_argument("--data_path", type=str, default="dataset/locomo10.json", help="Path to dataset")

    args = parser.parse_args()

    print(f"Running improved experiments with technique: {args.technique_type}, method: {args.method}")

    if args.technique_type == "improved_mem0":
        if args.method == "add":
            memory_manager = ImprovedMemoryADD(data_path=args.data_path, is_graph=args.is_graph)
            memory_manager.process_all_conversations()
        elif args.method == "search":
            output_file_path = os.path.join(
                args.output_folder,
                f"improved_mem0_results_top_{args.top_k}_filter_{args.filter_memories}_graph_{args.is_graph}.json",
            )
            memory_searcher = ImprovedMemorySearch(
                output_path=output_file_path, 
                top_k=args.top_k, 
                filter_memories=args.filter_memories, 
                is_graph=args.is_graph
            )
            memory_searcher.process_data_file(args.data_path)
    else:
        raise ValueError(f"Invalid technique type: {args.technique_type}")


if __name__ == "__main__":
    main()

