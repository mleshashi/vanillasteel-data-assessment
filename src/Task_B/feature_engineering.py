"""
Feature engineering module for RFQ similarity analysis.
Creates interval features, categorical features, and property features for similarity calculation.
"""

import pandas as pd
import numpy as np
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def engineer_similarity_features(enriched_df):
    """
    Create engineered features for similarity calculation.
    
    - Dimensions: Represent as intervals with overlap metrics
    - Categorical: Standardize for exact matching  
    - Grade properties: Use numeric midpoints, filter sparse features
    
    Returns:
        DataFrame with engineered features and similarity functions
    """
    
    print("\n=== TASK B.2: Feature Engineering ===")
    
    df_work = enriched_df.copy()
    
    # 1. Create dimension interval features
    df_work = create_dimension_intervals(df_work)
    
    # 2. Standardize categorical features
    df_work = standardize_categorical_features(df_work)
    
    # 3. Filter and prepare grade property features
    df_work = prepare_grade_properties(df_work)
    
    # 4. Add similarity functions
    print("\n4. Defining Overlap Metrics...")
    df_work.attrs['interval_overlap_ratio'] = interval_overlap_ratio
    df_work.attrs['categorical_match'] = categorical_match
    print("  ✓ Interval overlap ratio function defined")
    print("  ✓ Categorical match function defined")
    
    print(f"\n=== Feature Engineering Summary ===")
    print(f"Final dataset shape: {df_work.shape}")
    
    # Count feature types
    interval_features = [col for col in df_work.columns if '_interval_' in col or '_center' in col or '_width' in col]
    categorical_clean = [col for col in df_work.columns if '_clean' in col]
    property_features = [col for col in df_work.columns if '_mid' in col]
    
    print(f"Interval features created: {len(interval_features)}")
    print(f"Categorical features standardized: {len(categorical_clean)}")
    print(f"Property midpoint features available: {len(property_features)}")
    
    return df_work

def create_dimension_intervals(df):
    """Create interval features for dimensional properties."""
    
    print("\n1. Engineering Dimension Features...")
    
    dimension_pairs = [
        ('thickness_min', 'thickness_max'),
        ('width_min', 'width_max'),
        ('length_min', 'length_min'),  # length only has min in data
        ('height_min', 'height_max'),
        ('weight_min', 'weight_max'),
        ('inner_diameter_min', 'inner_diameter_max'),
        ('outer_diameter_min', 'outer_diameter_max'),
        ('yield_strength_min', 'yield_strength_max'),
        ('tensile_strength_min', 'tensile_strength_max')
    ]
    
    for min_col, max_col in dimension_pairs:
        if min_col in df.columns and max_col in df.columns:
            feature_name = min_col.replace('_min', '').replace('_max', '')
            
            df[f"{feature_name}_interval_min"] = df[min_col]
            df[f"{feature_name}_interval_max"] = df[max_col].fillna(df[min_col])
            df[f"{feature_name}_center"] = (df[f"{feature_name}_interval_min"] + df[f"{feature_name}_interval_max"]) / 2
            df[f"{feature_name}_width"] = df[f"{feature_name}_interval_max"] - df[f"{feature_name}_interval_min"]
            
            print(f"  Created interval features for {feature_name}")
    
    return df

def standardize_categorical_features(df):
    """Standardize categorical features for exact matching."""
    
    print("\n2. Engineering Categorical Features...")
    
    categorical_features = ['coating', 'finish', 'form', 'surface_type', 'surface_protection']
    
    for cat_feature in categorical_features:
        if cat_feature in df.columns:
            df[f"{cat_feature}_clean"] = df[cat_feature].fillna('Unknown').str.strip().str.upper()
            unique_count = df[f'{cat_feature}_clean'].nunique()
            print(f"  Standardized {cat_feature}: {unique_count} unique values")
    
    return df

def prepare_grade_properties(df):
    """Filter and prepare grade property features based on data coverage."""
    
    print("\n3. Engineering Grade Property Features...")
    
    # All possible property features (include Copper that was missed)
    all_property_features = [
        'Carbon_C_mid', 'Manganese_Mn_mid', 'Silicon_Si_mid', 
        'Sulfur_S_mid', 'Phosphorus_P_mid', 'Chromium_Cr_mid',
        'Nickel_Ni_mid', 'Molybdenum_Mo_mid', 'Vanadium_V_mid',
        'Copper_Cu_mid', 'Aluminum_Al_mid', 'Titanium_Ti_mid',
        'Niobium_Nb_mid', 'Boron_B_mid', 'Nitrogen_N_mid', 
        'Tensile_strength_Rm_mid', 'Yield_strength_Re_or_Rp0.2_mid', 
        'Elongation_A%_mid'
    ]
    
    # Filter features with sufficient data coverage (5% minimum)
    min_coverage = 10
    kept_features = []
    total_with_ref = df['Grade/Material'].notna().sum()
    
    print(f"\n  Grade Properties Availability and Filtering (min {min_coverage}% coverage):")
    
    for feature in all_property_features:
        if feature in df.columns:
            non_null_count = df[feature].notna().sum()
            coverage = non_null_count / total_with_ref * 100 if total_with_ref > 0 else 0
            
            if coverage >= min_coverage:
                kept_features.append(feature)
                status = "kept"
            else:
                df.drop(columns=[feature], inplace=True)
                status = "dropped"
            
            print(f"    {feature}: {non_null_count}/{total_with_ref} ({coverage:.1f}%) {status}")
    
    return df

def interval_overlap_ratio(min1, max1, min2, max2):
    """Calculate overlap ratio between two intervals."""
    if pd.isna(min1) or pd.isna(max1) or pd.isna(min2) or pd.isna(max2):
        return 0.0
    
    # Ensure min <= max for both intervals
    min1, max1 = min(min1, max1), max(min1, max1)
    min2, max2 = min(min2, max2), max(min2, max2)
    
    # Calculate overlap
    overlap = max(0, min(max1, max2) - max(min1, min2))
    union = max(max1, max2) - min(min1, min2)
    
    return overlap / union if union > 0 else 0.0

def categorical_match(val1, val2):
    """Check if two categorical values match exactly."""
    if pd.isna(val1) or pd.isna(val2):
        return 0.0
    return 1.0 if val1 == val2 else 0.0

if __name__ == "__main__":
    from data_loader import load_rfq_data
    from grade_normalizer import normalize_grades
    from range_parser import parse_range_strings
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test feature engineering
    rfq_df, reference_df = load_rfq_data()
    enriched_df, _ = normalize_grades(rfq_df, reference_df)
    parsed_df = parse_range_strings(enriched_df)
    feature_df = engineer_similarity_features(parsed_df)
    
    print(f"\nFeature engineering completed!")
    print(f"Final dataset shape: {feature_df.shape}")
    
    # Debug: Show exactly which categorical features were created
    categorical_clean_cols = [col for col in feature_df.columns if '_clean' in col]
    print(f"\nDEBUG - The {len(categorical_clean_cols)} categorical '_clean' features are:")
    for i, col in enumerate(categorical_clean_cols, 1):
        count = feature_df[col].notna().sum()
        print(f"  {i}. {col}: {count} values")
    
    # Debug: Show exactly which _mid features are being counted
    mid_cols = [col for col in feature_df.columns if '_mid' in col]
    print(f"\nDEBUG - The {len(mid_cols)} '_mid' features are:")
    for i, col in enumerate(mid_cols, 1):
        count = feature_df[col].notna().sum()
        print(f"  {i}. {col}: {count} values")
    
    # Debug: Show dimensional features and their counts
    dimension_cols = [col for col in feature_df.columns if '_interval_' in col or '_center' in col or '_width' in col]
    print(f"\nDEBUG - Dimensional features ({len(dimension_cols)} total):")
    for i, col in enumerate(dimension_cols, 1):
        count = feature_df[col].notna().sum()
        print(f"  {i}. {col}: {count} values")
