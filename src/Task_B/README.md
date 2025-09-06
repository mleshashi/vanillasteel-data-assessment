
# Task B: RFQ Similarity Analysis

## Overview
This pipeline finds the 3 most similar RFQs for each of 1000 requests by matching material properties, dimensions, and categorical features.

---

## Main Steps

### 1. Grade Matching & Reference Join (B.1)
- **Grade normalization:** Cleaned case, removed suffixes (+N, +QT), handled aliases (DX51 → DX51D).
- **Reference join:** Left join on normalized grades; kept all 1000 RFQs, enriched 941 with properties.
- **Missing grades:** 59 RFQs had no reference match, kept as-is with null properties.
- **Range parsing:** Converted values like "≤0.17", "360-510 MPa" to min/max/mid numeric values.
- **Missing value strategy:** Kept nulls rather than imputing; used available data only.

### 2. Feature Engineering (B.2)
- **Dimensions:** Created interval features (min/max/center/width) for 6 dimension types.
	- Used overlap ratio as similarity metric: overlap_length / union_length.
	- Handled singletons by setting min=max.
- **Categories:** Exact match (1/0) for coating, finish, form, surface_type, surface_protection.
- **Properties:** Used midpoint values from parsed ranges, filtered sparse features (<10% coverage).
- **Final features:** 36 interval, 5 categorical, 12 property features.

### 3. Similarity Calculation (B.3)
- **Aggregate score:** Weighted average - Dimensions 50%, Properties 30%, Categories 20%.
- **Exclusions:** Removed self-matches and exact duplicates (same grade + dimensions).
- **Top-3 selection:** Ranked by similarity score, kept best 3 per RFQ.

---

## Key Decisions
- **Join strategy:** Left join to preserve all RFQs, even without reference data.
- **Sparse properties:** Dropped Copper (0%), Boron (0.7%), others with <10% coverage.
- **Weight rationale:** Dimensions most discriminating, categories often perfect matches.
- **Missing handling:** No imputation; similarity calculation adapts to available features.

---

## Results & Important Findings

### Data Coverage After Join
- 941/1000 RFQs successfully matched to reference properties.
- Chemical composition: Carbon 99.9%, Manganese 99.9%, specialty elements much lower.
- Mechanical properties: Tensile strength 99.9%, yield strength 37%, elongation 0.2%.

### Similarity Distribution
- 3000 total pairs generated (3 matches × 1000 RFQs).
- Average similarity: 0.485 (moderate - good separation).
- Top similarity: 0.666 (perfect categorical + property match, decent dimension overlap).
- Score breakdown: Most high scores had perfect categorical matches (1.0) + good property alignment.

### Feature Performance
- Dimensions: Most discriminating - thickness (833 values), width (539 values) had best coverage.
- Categories: High exact match rates led to many 1.0 scores.
- Properties: Carbon/Manganese drove most chemical similarity, specialty elements rarely available.

---

## Summary
The pipeline successfully handled real-world messiness—such as inconsistent formats, missing data, and sparse properties—while producing reasonable similarity rankings for RFQs.
