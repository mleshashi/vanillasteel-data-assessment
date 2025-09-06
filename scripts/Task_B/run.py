#!/usr/bin/env python3
"""
Task B: RFQ Similarity Analysis Pipeline
"""

import sys
from pathlib import Path
import logging

# Import pipeline modules
from data_loader import load_rfq_data
from grade_normalizer import normalize_grades
from range_parser import parse_range_strings
from feature_engineering import engineer_similarity_features
from similarity_calculator import calculate_rfq_similarity
#from deliverable_creator import create_final_deliverable, create_summary_report

def main():
    """Run the complete RFQ similarity analysis pipeline."""
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("Starting RFQ similarity analysis...")
    
    # Load data
    rfq_df, reference_df = load_rfq_data()
    
    # Process and enrich data
    enriched_rfq, grade_mapping = normalize_grades(rfq_df, reference_df)
    
    # Parse range strings
    enriched_with_ranges = parse_range_strings(enriched_rfq)

    # Feature engineering
    feature_engineered_df = engineer_similarity_features(enriched_with_ranges)

    print("\n=== TASK B.3: Similarity Calculation ===")
    # Calculate similarities
    similarity_results = calculate_rfq_similarity(feature_engineered_df)
    
    # Create deliverables
    create_final_deliverable(similarity_results)
    create_summary_report(similarity_results, feature_engineered_df)
    
    logger.info("Pipeline completed! Results saved to ../../results/top3.csv")

if __name__ == "__main__":
    main()