#!/usr/bin/env python3
"""
Task B: RFQ Similarity Analysis Pipeline - Simple Runner
"""

import pandas as pd
from pathlib import Path
import logging

from data_loader import load_rfq_data
from grade_normalizer import normalize_grades
from range_parser import parse_range_strings
from feature_engineering import engineer_similarity_features
from similarity_calculator import calculate_rfq_similarity

def main():
    """Run complete pipeline and save results."""
    
    logging.basicConfig(level=logging.WARNING)  # Reduce output noise
    
    print("Running RFQ similarity analysis pipeline...")
    
    # Execute pipeline
    rfq_df, reference_df = load_rfq_data()
    enriched_df, _ = normalize_grades(rfq_df, reference_df)
    parsed_df = parse_range_strings(enriched_df)
    feature_df = engineer_similarity_features(parsed_df)
    similarity_results = calculate_rfq_similarity(feature_df)
    
    # Save results
    output_path = Path("../../results/top3.csv")
    output_path.parent.mkdir(exist_ok=True)
    
    deliverable = similarity_results[['rfq_id', 'match_id', 'similarity_score']].copy()
    deliverable['similarity_score'] = deliverable['similarity_score'].round(6)
    deliverable.to_csv(output_path, index=False)
    
    print(f"Pipeline completed! Results saved to: {output_path}")
    print(f"Generated {len(deliverable)} similarity pairs")

if __name__ == "__main__":
    main()