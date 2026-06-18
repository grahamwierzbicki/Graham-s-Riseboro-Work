# Riseboro Data Analysis Project

This repository contains data analysis, ETL pipelines, and scripts to support the **Riseboro** organization.

## Project Context
* **Team:** 5-person data analysis team.
* **Cadence:** Weekly milestones.
* **Overall Goal:** Help Riseboro identify trends, prioritize preventative repairs, and improve overall operational effectiveness.

---

## Repository Structure
```
├── data/
│   ├── raw/          # Original, unmodified Excel/CSV data sheets (ignored by Git)
│   └── processed/    # Cleaned outputs, summaries, and final sheets (ignored by Git)
├── src/              # Python scripts for data ETL, analysis, and modeling
└── README.md         # Project description, goals, and task tracker
```

---

## Project Tasks & Progress

### Week 1 (Data Prep & Initial Enrichment)
- [x] **Data Loading & Cleaning**: Loaded and normalized raw Yardi exports into a single combined dataset.
- [x] **Row Cleaning**: Cleaned empty/unreasonable rows in Python, re-exported to CSV.
- [x] **Fuzzy String Matching / Anchors**: Grouped Plumbing and Extermination descriptions into granular subcategories (e.g., `Leak`, `Clog/Drain`, `Bedbugs`, `Rodents`) using pattern matching.

### Week 2 (Spatial Analysis, Trends & Modeling)
- [ ] **Address Matching**: Pull NYC property bounds data and match to the "Master Property Code Sheet" addresses.
- [ ] **311 Dataset Integration**: Pull 311 dataset and match to the Master Property List on addresses.
- [ ] **Seasonal & Long-Term Trends**: Show work orders by month (seasonal trends) and by year (long-term trends) for **Rheingold** and **Gates Plaza** locations.
- [ ] **HPD Fee Analysis**:
  - [ ] Pull HPD Fee data and show monthly/yearly trends.
  - [ ] Identify high-cost buildings for fees.
  - [ ] Create a map visualization of high-cost fee buildings.
- [ ] **HPD Fee Dashboard**: Pull HPD Fee data and create a basic dashboard showing City & Brooklyn level highlights (unfiltered).
- [ ] **Portfolio Mapping**: Map the portfolio buildings and display on a map in PowerBI.
- [ ] **Predictive Modeling**: Test 3 prediction models for issue rates at Rheingold (for a specific issue type or overall) and summarize the drawbacks and benefits of each.
- [ ] **PowerBI Integration**: Intro to PowerBI dashboard creation.

---

## How to Run

### Setup
Ensure you have the required Python packages installed:
```bash
pip install pandas openpyxl requests
```

### ETL Pipeline (Week 1)
To run the category normalization and subcategorization pipeline:
```bash
python3 src/week1.py
```
This loads raw data from `data/raw/` and outputs the final enriched dataset to `data/processed/work_orders_enriched_final.xlsx`.
