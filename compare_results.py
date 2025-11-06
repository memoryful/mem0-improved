"""
Compare results between original mem0 and improved version
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def load_metrics(file_path):
    """Load evaluation metrics from JSON file"""
    with open(file_path, "r") as f:
        data = json.load(f)
    
    # Flatten the data
    all_items = []
    for key in data:
        all_items.extend(data[key])
    
    # Convert to DataFrame
    df = pd.DataFrame(all_items)
    df["category"] = pd.to_numeric(df["category"])
    
    return df


def main():
    parser = argparse.ArgumentParser(description="Compare mem0 vs improved results")
    parser.add_argument(
        "--original_file", 
        type=str, 
        default="../mem0/evaluation/evaluation_metrics.json",
        help="Path to original mem0 evaluation results"
    )
    parser.add_argument(
        "--improved_file",
        type=str,
        default="evaluation_improved_metrics.json",
        help="Path to improved evaluation results"
    )
    
    args = parser.parse_args()
    
    # Load both datasets
    print("Loading original mem0 results...")
    original_df = load_metrics(args.original_file)
    
    print("Loading improved results...")
    improved_df = load_metrics(args.improved_file)
    
    # Calculate mean scores by category for both
    original_means = original_df.groupby("category").agg({
        "bleu_score": "mean", 
        "f1_score": "mean", 
        "llm_score": "mean"
    }).round(4)
    original_means["count"] = original_df.groupby("category").size()
    
    improved_means = improved_df.groupby("category").agg({
        "bleu_score": "mean",
        "f1_score": "mean",
        "llm_score": "mean"
    }).round(4)
    improved_means["count"] = improved_df.groupby("category").size()
    
    # Calculate overall means
    original_overall = original_df.agg({
        "bleu_score": "mean",
        "f1_score": "mean",
        "llm_score": "mean"
    }).round(4)
    
    improved_overall = improved_df.agg({
        "bleu_score": "mean",
        "f1_score": "mean",
        "llm_score": "mean"
    }).round(4)
    
    # Print comparison
    print("\n" + "="*80)
    print("COMPARISON: Original Mem0 vs Improved Mem0")
    print("="*80)
    
    print("\n--- Original Mem0 Scores Per Category ---")
    print(original_means)
    
    print("\n--- Improved Mem0 Scores Per Category ---")
    print(improved_means)
    
    print("\n--- Improvement by Category ---")
    improvement = improved_means[["bleu_score", "f1_score", "llm_score"]] - original_means[["bleu_score", "f1_score", "llm_score"]]
    improvement_pct = (improvement / original_means[["bleu_score", "f1_score", "llm_score"]] * 100).round(2)
    improvement.columns = [f"{col}_improvement" for col in improvement.columns]
    improvement_pct.columns = [f"{col}_pct" for col in improvement_pct.columns]
    print(improvement)
    print("\nImprovement Percentage:")
    print(improvement_pct)
    
    print("\n--- Overall Scores ---")
    print("\nOriginal Mem0 Overall:")
    print(original_overall)
    print("\nImproved Mem0 Overall:")
    print(improved_overall)
    
    print("\n--- Overall Improvement ---")
    overall_improvement = improved_overall - original_overall
    overall_improvement_pct = (overall_improvement / original_overall * 100).round(2)
    print(overall_improvement)
    print("\nOverall Improvement Percentage:")
    print(overall_improvement_pct)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"LLM Score Improvement: {overall_improvement['llm_score']:.4f} ({overall_improvement_pct['llm_score']:.2f}%)")
    print(f"BLEU Score Improvement: {overall_improvement['bleu_score']:.4f} ({overall_improvement_pct['bleu_score']:.2f}%)")
    print(f"F1 Score Improvement: {overall_improvement['f1_score']:.4f} ({overall_improvement_pct['f1_score']:.2f}%)")
    print("="*80)


if __name__ == "__main__":
    main()

