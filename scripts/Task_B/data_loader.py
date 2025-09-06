"""
Data loading module for Task B RFQ Similarity Analysis.
"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_rfq_data():

    print("\n=== Data Loading ===")
    
    task2_dir = Path("../../resources/task_2")
    rfq_path = task2_dir / "rfq.csv"
    reference_path = task2_dir / "reference_properties.tsv"
    
    # Load the datasets
    rfq_df = pd.read_csv(rfq_path)
    reference_df = pd.read_csv(reference_path, sep='\t')
    
    logger.info(f"Loaded {len(rfq_df)} RFQ records with {rfq_df.shape[1]} columns")
    logger.info(f"Loaded {len(reference_df)} reference materials with {reference_df.shape[1]} properties")
    
    # Show data overview
    rfq_grades = rfq_df['grade'].nunique()
    rfq_missing_grades = rfq_df['grade'].isnull().sum()
    ref_grades = reference_df['Grade/Material'].nunique()
    
    logger.info(f"RFQ data: {rfq_grades} unique grades, {rfq_missing_grades} missing")
    logger.info(f"Reference data: {ref_grades} material grades available")
    
    # Quick quality check
    if rfq_missing_grades > len(rfq_df) * 0.1:  # More than 10% missing
        logger.warning(f"High number of missing grades in RFQ data: {rfq_missing_grades}")
    
    return rfq_df, reference_df

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    rfq_df, reference_df = load_rfq_data()
    
    print(f"\nRFQ columns: {list(rfq_df.columns[:5])}...")  # Show first 5 columns
    print(f"Reference columns: {list(reference_df.columns[:5])}...")
    print(f"Sample RFQ grades: {rfq_df['grade'].dropna().head(5).tolist()}")