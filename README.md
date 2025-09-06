
# Vanilla Steel Data Assessment

This repository contains solutions for the Vanilla Steel Data Assessment, focusing on data cleaning, dataset merging, and RFQ similarity analysis.

---

## 📁 Project Structure

```
├── notebooks/
│ └── TaskA-data exploration
│ └── TaskB-data exploration
├── resources/ # Raw & updated input data
├── results/ # Final outputs (Task A & Task B)
├── src/ # Modular Python code for Task A & B
│ └── TaskA
│ └── TaskB
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## 🛠 Features

### Task A: Supplier Data Cleaning & Joining
- Implemented in Jupyter Notebook (`src/Task_A.ipynb`)
- Cleans and merges two supplier datasets into a unified inventory.

### Task B: RFQ Similarity Analysis
- Implemented as a modular Python pipeline (`src/Task_B/`)
- Finds top-3 similar RFQs for each request.

**Modules:**
- `data_loader.py`
- `grade_normalizer.py`
- `range_parser.py`
- `feature_engineering.py`
- `similarity_calculator.py`
- `run.py`

---

## 🚀 Getting Started

### 1. Clone and Set Up

```bash
git clone https://github.com/mleshashi/vanillasteel-data-assessment.git
cd vanillasteel-data-assessment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Task A (Jupyter Notebook)

```bash
cd src/Task_A/
jupyter notebook Task_A.ipynb
```
Run all cells to generate the cleaned inventory dataset.

### 3. Run Task B (Python Pipeline)

```bash
cd src/Task_B/
python run.py
```
This will execute the similarity analysis and save results to `results/top3.csv`.

---

## 📦 Output Files

- **Task A:** `results/inventory_dataset.csv` — Unified supplier data
- **Task B:** `results/top3.csv` — Top-3 similar RFQs for each request

---

## 📄 License

This project is licensed under the terms of the LICENSE file.
