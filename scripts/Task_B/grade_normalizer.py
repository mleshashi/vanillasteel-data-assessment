"""
Normalize grade keys and handle grade matching between RFQ and reference data.
    
Task B.1: Normalize grade keys (case, suffixes, aliases) and join RFQs with reference.

"""

import pandas as pd
import re
import logging
import warnings
from difflib import get_close_matches

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def normalize_grades(rfq_df, reference_df):
    """
    Normalize grade names and join RFQ data with reference properties.
    
    Returns:
        tuple: (enriched_rfq_df, grade_mapping_dict)
    """
    
    print("\n=== TASK B.1: Grade Normalization and Reference Join ===")

    # Work with copies
    rfq_work = rfq_df.copy()
    ref_work = reference_df.copy()
    
    # Clean and normalize grade strings
    rfq_work['grade_clean'] = rfq_work['grade'].apply(clean_grade_string)
    ref_work['grade_clean'] = ref_work['Grade/Material'].apply(clean_grade_string)
    
    # Remove duplicate reference entries (keep best match per grade)
    ref_clean = deduplicate_reference_data(ref_work)
    
    # Grade Analysis
    rfq_grades = set(rfq_work['grade_clean'].dropna())
    ref_grades = set(ref_clean['grade_clean'].dropna())
    
    common_grades = rfq_grades.intersection(ref_grades)
    rfq_missing_in_ref = rfq_grades - ref_grades
    ref_not_in_rfq = ref_grades - rfq_grades
    
    print(f"\nGrade Analysis:")
    print(f"Unique normalized grades in RFQ: {len(rfq_grades)}")
    print(f"Unique normalized grades in Reference: {len(ref_grades)}")
    print(f"Grades found in both datasets: {len(common_grades)}")
    print(f"RFQ grades missing in reference: {len(rfq_missing_in_ref)}")
    print(f"Reference grades not in RFQ: {len(ref_not_in_rfq)}")
    
    # Create grade mapping
    grade_mapping = create_grade_mapping(rfq_work, ref_clean)
    
    # Join datasets
    enriched_df = join_with_reference(rfq_work, ref_clean, grade_mapping)
    
    # Join Results
    total_rfq = len(rfq_work)
    matched = enriched_df['Grade/Material'].notna().sum()
    missing = enriched_df['Grade/Material'].isna().sum()
    
    print(f"\nJoin Results:")
    print(f"Total RFQ records: {total_rfq}")
    print(f"Records with reference data: {matched}")
    print(f"Records missing reference data: {missing}")
    # print the shape of the enriched dataframe
    print(f"Enriched RFQ shape: {enriched_df.shape}")
    print("No duplicate rows created!")
    
    return enriched_df, grade_mapping

def clean_grade_string(grade):
    """Clean and normalize a grade string."""
    if pd.isna(grade):
        return None
    
    grade = str(grade).strip().upper()
    
    # Remove delivery condition suffixes (+N, +QT, +C, etc.)
    grade = re.sub(r'\+.*$', '', grade)
    
    # Remove spaces and dashes
    grade = grade.replace(' ', '').replace('-', '')
    
    # Handle common DX grade patterns (DX51 → DX51D)
    if re.match(r'^DX\d{2}$', grade):
        grade = grade + 'D'
    
    return grade

def deduplicate_reference_data(ref_df):
    """Remove duplicate reference entries, keeping the best one per grade."""
    
    def select_best_entry(group):
        if len(group) == 1:
            return group.iloc[0]
        
        # Prefer entries with exact grade match to cleaned version
        original_clean = group['Grade/Material'].str.upper().str.replace(' ', '').str.replace('-', '')
        exact_matches = group[original_clean == group['grade_clean']]
        
        if len(exact_matches) > 0:
            return exact_matches.iloc[0]
        
        # Otherwise pick shortest name (fewer suffixes)
        return group.loc[group['Grade/Material'].str.len().idxmin()]
    
    return ref_df.groupby('grade_clean', group_keys=False).apply(select_best_entry).reset_index(drop=True)

def create_grade_mapping(rfq_df, ref_df):
    """Create mapping from RFQ grades to reference grades."""
    
    rfq_grades = set(rfq_df['grade_clean'].dropna())
    ref_grades = set(ref_df['grade_clean'].dropna())
    
    mapping = {}
    
    # Direct matches first
    for grade in rfq_grades:
        if grade in ref_grades:
            mapping[grade] = grade
    
    # Fuzzy matching for remaining grades
    unmatched = rfq_grades - set(mapping.keys())
    for grade in unmatched:
        # Try close string matches
        matches = get_close_matches(grade, ref_grades, n=1, cutoff=0.8)
        if matches:
            mapping[grade] = matches[0]
            continue
        
        # Try substring matching for known patterns
        for ref_grade in ref_grades:
            if len(grade) >= 4 and (grade in ref_grade or ref_grade in grade):
                mapping[grade] = ref_grade
                break
    
    logger.info(f"Created {len(mapping)} grade mappings from {len(rfq_grades)} unique RFQ grades")
    return mapping

def join_with_reference(rfq_df, ref_df, grade_mapping):
    """Join RFQ data with reference data using grade mapping."""
    
    # Apply mapping
    rfq_df['grade_mapped'] = rfq_df['grade_clean'].map(grade_mapping)
    
    # Join datasets
    enriched = rfq_df.merge(
        ref_df,
        left_on='grade_mapped',
        right_on='grade_clean',
        how='left',
        suffixes=('', '_ref')
    )
    
    # Clean up redundant columns
    cols_to_drop = [col for col in enriched.columns if col.endswith('_ref')]
    enriched = enriched.drop(columns=cols_to_drop)
    
    return enriched

if __name__ == "__main__":
    from data_loader import load_rfq_data
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test grade normalization
    rfq_df, reference_df = load_rfq_data()
    enriched_df, mapping = normalize_grades(rfq_df, reference_df)
    
    print(f"\nEnriched dataset shape: {enriched_df.shape}")
    print(f"Sample mappings: {dict(list(mapping.items())[:3])}")
    print(f"RFQs with reference data: {enriched_df['Grade/Material'].notna().sum()}")
    