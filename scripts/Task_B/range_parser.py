"""
Range string parsing module for RFQ similarity analysis.
Converts string ranges like "≤0.17", "360-510 MPa" into numeric min/max/mid values.
"""

import pandas as pd
import re
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def parse_range_strings(enriched_df):
    """
    Parse range strings into numeric min/max/mid values.
    
    Args:
        enriched_df: DataFrame with reference properties as strings
        
    Returns:
        DataFrame with additional numeric columns for each property
    """
    
    print("\n=== TASK B.1: Range String Parsing ===")

    df_work = enriched_df.copy()
    
    # Define properties to parse
    chemical_props = [
        'Carbon (C)', 'Manganese (Mn)', 'Silicon (Si)', 'Sulfur (S)', 
        'Phosphorus (P)', 'Chromium (Cr)', 'Nickel (Ni)', 'Molybdenum (Mo)',
        'Vanadium (V)', 'Copper (Cu)', 'Aluminum (Al)', 'Titanium (Ti)',
        'Niobium (Nb)', 'Boron (B)', 'Nitrogen (N)'
    ]
    
    mechanical_props = [
        'Tensile strength (Rm)', 'Yield strength (Re or Rp0.2)', 'Elongation (A%)'
    ]
    
    properties_to_parse = chemical_props + mechanical_props
    parsed_count = 0
    
    # Parse each property
    for prop in properties_to_parse:
        if prop in df_work.columns:
            print(f"Parsing {prop}...")
            
            # Create column names
            prop_clean = prop.replace('(', '').replace(')', '').replace(' ', '_').replace('/', '_')
            min_col = f"{prop_clean}_min"
            max_col = f"{prop_clean}_max"
            mid_col = f"{prop_clean}_mid"
            
            # Parse values
            parsed_values = df_work[prop].apply(parse_single_range)
            
            df_work[min_col] = [x[0] for x in parsed_values]
            df_work[max_col] = [x[1] for x in parsed_values]
            df_work[mid_col] = [x[2] for x in parsed_values]
            
            # Report success rate
            successful = df_work[mid_col].notna().sum()
            total_available = df_work[prop].notna().sum()
            print(f"  Successfully parsed {successful}/{total_available} values")
            
            parsed_count += 1
    
    print(f"Total properties parsed: {parsed_count}")
    print(f"Final dataset shape: {df_work.shape}")

    return df_work

def parse_single_range(value_str):
    """
    Parse a single range string into (min_val, max_val, mid_val).
    
    Handles formats like:
    - "≤0.17" -> (None, 0.17, 0.085)
    - "360-510 MPa" -> (360, 510, 435)
    - "≥235 MPa" -> (235, None, None)
    - "0.17" -> (None, None, 0.17)
    
    Returns:
        tuple: (min_val, max_val, mid_val) or (None, None, None) if unparseable
    """
    
    if pd.isna(value_str) or value_str == '':
        return None, None, None
    
    # Clean the string
    value_str = str(value_str).strip()
    clean_str = re.sub(r'[A-Za-z%°]', '', value_str)  # Remove units
    clean_str = re.sub(r'\s+', ' ', clean_str).strip()
    
    try:
        # Pattern 1: ≤X or <=X (upper bound only)
        if '≤' in value_str or '<=' in value_str:
            max_val = float(re.findall(r'[\d.]+', clean_str)[0])
            mid_val = max_val / 2
            return None, max_val, mid_val
        
        # Pattern 2: ≥X or >=X (lower bound only)
        elif '≥' in value_str or '>=' in value_str:
            min_val = float(re.findall(r'[\d.]+', clean_str)[0])
            return min_val, None, None
        
        # Pattern 3: X-Y or X–Y (range)
        elif '-' in clean_str or '–' in clean_str:
            numbers = re.findall(r'[\d.]+', clean_str)
            if len(numbers) >= 2:
                min_val = float(numbers[0])
                max_val = float(numbers[1])
                mid_val = (min_val + max_val) / 2
                return min_val, max_val, mid_val
        
        # Pattern 4: Single number
        else:
            numbers = re.findall(r'[\d.]+', clean_str)
            if numbers:
                val = float(numbers[0])
                return None, None, val
    
    except (ValueError, IndexError):
        pass
    
    return None, None, None

if __name__ == "__main__":
    from data_loader import load_rfq_data
    from grade_normalizer import normalize_grades
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test range parsing
    rfq_df, reference_df = load_rfq_data()
    enriched_df, _ = normalize_grades(rfq_df, reference_df)
    parsed_df = parse_range_strings(enriched_df)
    
    print(f"\nFinal dataset shape: {parsed_df.shape}")
    
    # Show some parsed examples
    carbon_cols = [col for col in parsed_df.columns if 'Carbon_C' in col]
    if carbon_cols:
        sample = parsed_df[['Carbon (C)'] + carbon_cols].dropna().head(3)
        print(f"\nSample Carbon parsing:")
        print(sample.to_string())