
# Task A: Supplier Data Cleaning and Joining

## Overview
This task combines two supplier datasets into a unified inventory file for analysis and reporting.

## Key Steps
- **Language Translation:** German terms in supplier 1 data were translated to English.
- **Format Standardization:** Unified quality ratings (e.g., `1st/2nd/3rd` → `1/2/3`), column names, and data types.
- **Material Code Parsing:** Supplier 2 codes like `S355+Z` were split into separate grade and coating columns.
- **Missing Data Handling:** Zeros in technical properties were treated as "not tested" and converted to `NaN`.


## Data Integration Approach
- **Union Strategy:** All columns from both datasets were included; missing values filled with `NaN`.
- **Inventory_ID (`int64`):** Each inventory item is assigned a unique integer ID to ensure traceability and simplify referencing across merged data.
- **Source (`object`):** Indicates the origin of each record (e.g., Supplier 1 or Supplier 2), allowing for easy filtering and analysis by data source.
- **Supplier 1 Unique Columns:** Technical properties (`RP02`, `RM`, `AG`, `AI`), dimensions, quality ratings.
- **Supplier 2 Unique Columns:** Article ID, coating info, reservation status.
- **Common Columns:** Grade, weight, quantity, finish (standardized).

## Assumptions
- Datasets contain no duplicate inventory items.
- Zero values in technical columns (`RP02`, `RM`, `AG`, `AI`) mean "not tested".
- Supplier 2 missing thickness/width data left as `NaN`.
- Reservation status converted to boolean for analysis.

## Output
- **Records:** 100 inventory items with 17 columns.
- **File:** Saved to `../../results/inventory_dataset.csv`.