# help me edit the entire
# Vanilla Steel Data Assessment

This repository contains my solutions for the **Vanilla Steel Assessment**, focusing on **data cleaning, dataset merging, and RFQ similarity analysis**.

---

## 📂 Project Structure

├── notebooks/ # Jupyter notebooks for Task A & B exploration
├── resources/ # Raw & updated input data
├── results/ # Final outputs (Task A & Task B)
├── src/ # Python code for Task A & B
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt


---

## 🛠 What's Inside

### **Task A: Supplier Data Cleaning & Joining**
- Implemented in **Jupyter Notebook** (`src/ Task_A`)  
- Cleans and merges two supplier datasets into a unified inventory.   


---

### **Task B: RFQ Similarity Analysis**
- Implemented as a **modular Python pipeline** (`scr/ Task_B`)
- `README.md`  

**Modules:**
- `data_loader.py`
- `grade_normalizer.py`
- `range_parser.py`  
- `feature_engineering.py`  
- `similarity_calculator.py`
- `run.py`
- `README.md`

---

## ▶️ How to Run

### **Install Dependencies**
```bash
pip install -r requirements.txt


### Task A (Jupyter Notebook)
```bash
cd src/Task_A/
jupyter notebook Task_A.ipynb
```
Run all cells to generate the cleaned inventory dataset.


### Task B (Python Pipeline)
```bash
cd scripts/Task_B/
python run.py
```
This will execute the complete similarity analysis and save results to ../../results/top3.csv.


## Output
Task A: Creates results/inventory_dataset.csv with unified supplier data
Task B: Creates results/top3.csv with top-3 similar RFQs for each request