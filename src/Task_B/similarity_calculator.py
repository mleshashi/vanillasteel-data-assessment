"""
Task B.3 Similarity calculation module for RFQ analysis.
Calculates weighted aggregate similarity scores between RFQs.
"""

import pandas as pd
import numpy as np
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def calculate_rfq_similarity(feature_df):
    """
    Calculate aggregate similarity scores between RFQs.
    
    Returns top-3 most similar RFQs for each RFQ with similarity scores.
    """
    
    print("\n=== TASK B.3: Similarity Calculation ===")
    
    # Get similarity functions
    interval_overlap_ratio = feature_df.attrs['interval_overlap_ratio']
    categorical_match = feature_df.attrs['categorical_match']
    
    # Extract available features directly from the dataframe
    # Dimension features (use the most reliable ones with good coverage)
    dimension_features = [
        ('thickness_interval_min', 'thickness_interval_max'),    # 833 values
        ('width_interval_min', 'width_interval_max'),           # 539 values  
        ('weight_interval_min', 'weight_interval_max'),         # 393 values
        ('inner_diameter_interval_min', 'inner_diameter_interval_max'), # 177 values
        ('length_interval_min', 'length_interval_max'),         # 131 values
        ('height_interval_min', 'height_interval_max')          # 132 values
    ]

    # Filter to only those that exist in dataframe
    dimension_features = [(min_col, max_col) for min_col, max_col in dimension_features 
                         if min_col in feature_df.columns and max_col in feature_df.columns]
    
    # Categorical features (exclude grade_clean as it's for matching, not similarity)
    categorical_features = [col for col in feature_df.columns if '_clean' in col and col != 'grade_clean']
    
    # Grade property features (all _mid columns that have data)
    grade_property_features = [col for col in feature_df.columns if '_mid' in col and feature_df[col].notna().sum() > 0]
    
    # Define feature weights
    weights = {
        'dimensions': 0.50,      # 50% - most discriminating
        'categorical': 0.20,     # 20% - less discriminating (many 1.0s)
        'grade_properties': 0.30 # 30% - high but less critical
    }
    
    print(f"Feature groups defined:")
    print(f"  Dimensions: {len(dimension_features)} features (weight: {weights['dimensions']})")
    print(f"  Categorical: {len(categorical_features)} features (weight: {weights['categorical']})")
    print(f"  Grade properties: {len(grade_property_features)} features (weight: {weights['grade_properties']})")
    
    # Filter valid RFQs
    valid_df = feature_df[feature_df['id'].notna()].copy().reset_index(drop=True)
    print(f"\nCalculating pairwise similarities for {len(valid_df)} RFQs...")
    
    # Calculate similarities
    similarity_results = []
    batch_size = 50
    
    print("Computing similarities...")
    
    for i in range(0, len(valid_df), batch_size):
        end_i = min(i + batch_size, len(valid_df))
        
        for idx1 in range(i, end_i):
            row1 = valid_df.iloc[idx1]
            rfq1_id = row1['id']
            
            rfq_similarities = []
            
            for idx2 in range(len(valid_df)):
                if idx1 != idx2:
                    row2 = valid_df.iloc[idx2]
                    rfq2_id = row2['id']
                    
                    # Skip exact duplicates
                    if (row1['grade'] == row2['grade'] and 
                        row1['thickness_center'] == row2['thickness_center'] and
                        row1['width_center'] == row2['width_center']):
                        continue
                    
                    # Calculate similarity components
                    dim_sim = calculate_dimension_similarity(row1, row2, dimension_features, interval_overlap_ratio)
                    cat_sim = calculate_categorical_similarity(row1, row2, categorical_features, categorical_match)
                    prop_sim = calculate_grade_property_similarity(row1, row2, grade_property_features, feature_df)
                    
                    # Calculate weighted aggregate score
                    aggregate_score = (
                        weights['dimensions'] * dim_sim +
                        weights['categorical'] * cat_sim +
                        weights['grade_properties'] * prop_sim
                    )
                    
                    rfq_similarities.append({
                        'rfq_id': rfq1_id,
                        'match_id': rfq2_id,
                        'similarity_score': aggregate_score,
                        'dimension_similarity': dim_sim,
                        'categorical_similarity': cat_sim,
                        'property_similarity': prop_sim
                    })
            
            # Get top-3 most similar for this RFQ
            if rfq_similarities:
                rfq_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
                top3 = rfq_similarities[:3]
                similarity_results.extend(top3)
        
        # Progress update
        progress = (end_i / len(valid_df)) * 100
        print(f"  Progress: {progress:.1f}% ({end_i}/{len(valid_df)} RFQs processed)")
    
    print("✓ Completed similarity calculations")
    
    # Create results dataframe
    results_df = pd.DataFrame(similarity_results)
    print(f"\nSimilarity results shape: {results_df.shape}")
    print(f"Average similarity score: {results_df['similarity_score'].mean():.3f}")
    print(f"Max similarity score: {results_df['similarity_score'].max():.3f}")
    
    # Show top results
    print(f"\nTop 10 highest similarity pairs:")
    top_results = results_df.nlargest(10, 'similarity_score')
    print(top_results[['rfq_id', 'match_id', 'similarity_score', 'dimension_similarity', 
                      'categorical_similarity', 'property_similarity']].to_string())
    
    return results_df

def calculate_dimension_similarity(row1, row2, dimension_features, interval_overlap_ratio):
    """Calculate dimensional similarity using interval overlap."""
    similarities = []
    
    for min_col, max_col in dimension_features:
        if min_col in row1.index and max_col in row1.index:
            overlap = interval_overlap_ratio(
                row1[min_col], row1[max_col],
                row2[min_col], row2[max_col]
            )
            similarities.append(overlap)
    
    return np.mean(similarities) if similarities else 0.0

def calculate_categorical_similarity(row1, row2, categorical_features, categorical_match):
    """Calculate categorical similarity using exact matches."""
    matches = []
    
    for cat_feature in categorical_features:
        if cat_feature in row1.index:
            match = categorical_match(row1[cat_feature], row2[cat_feature])
            matches.append(match)
    
    return np.mean(matches) if matches else 0.0

def calculate_grade_property_similarity(row1, row2, grade_property_features, df):
    """Calculate grade property similarity using normalized differences."""
    similarities = []
    
    for prop_feature in grade_property_features:
        if prop_feature in row1.index:
            val1, val2 = row1[prop_feature], row2[prop_feature]
            
            if pd.notna(val1) and pd.notna(val2):
                # Normalize by feature range
                feature_range = df[prop_feature].max() - df[prop_feature].min()
                if feature_range > 0:
                    normalized_diff = abs(val1 - val2) / feature_range
                    similarity = max(0, 1 - normalized_diff)
                    similarities.append(similarity)
    
    return np.mean(similarities) if similarities else 0.0

if __name__ == "__main__":
    from data_loader import load_rfq_data
    from grade_normalizer import normalize_grades
    from range_parser import parse_range_strings
    from feature_engineering import engineer_similarity_features
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test similarity calculation
    print("Starting similarity calculation test...")
    
    rfq_df, reference_df = load_rfq_data()
    enriched_df, _ = normalize_grades(rfq_df, reference_df)
    parsed_df = parse_range_strings(enriched_df)
    feature_df = engineer_similarity_features(parsed_df)
    
    # Calculate similarities
    similarity_results = calculate_rfq_similarity(feature_df)
    
    print(f"\nSimilarity calculation completed!")
    print(f"Total similarity pairs: {len(similarity_results)}")