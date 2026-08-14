<
## Overview

This project analyzes the Titanic dataset in two structured notebook stages:

- <font color="#1F6FEB"><b>01_eda.ipynb</b></font> focuses on data exploration, cleaning, missing value analysis, and feature understanding.
- <font color="#10B981"><b>02_modeling.ipynb</b></font> builds predictive models for survival prediction and evaluates model performance.

The workflow follows a professional machine learning pipeline:

```text
Raw Data -> Data Cleaning -> Train/Test Split -> Feature Preprocessing -> Model Training -> Evaluation -> Deployment-ready Pipeline
```

## Notebook Files

| File | Purpose |
| --- | --- |
| `analytics/01_eda.ipynb` | Explores the Titanic data, studies survival patterns, and prepares cleaned output. |
| `analytics/analytics/ 02_modeling.ipynb` | Trains classifiers, compares model performance, and saves a reusable pipeline. |

## Project Structure

```text
datapipeline/
├── analytics/
│   ├── 01_eda.ipynb
│   ├── titanic.csv
│   ├── titanic_cleaned.csv
│   └── analytics/
│       └── 02_modeling.ipynb
├── README.md
├── requirements.txt
├── scraper.py
├── database.py
├── queries.py
├── analysis.py
├── books.db
├── scraped_books.csv
└── .venv/
```

## Setup and Installation

Create a virtual environment and install dependencies:

```bash
cd /Users/ramsaijeevan001/Documents/zepto_captone_project/datapipeline
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Required Packages

The project uses the following Python libraries:

```text
pandas
numpy
matplotlib
seaborn
scikit-learn
imbalanced-learn
joblib
ipykernel
```

## Execution Flow

Run the notebooks in this order:

1. Open and execute `analytics/01_eda.ipynb`
2. Confirm the cleaned dataset is saved correctly
3. Open and execute `analytics/analytics/ 02_modeling.ipynb`
4. Review performance metrics and saved pipeline artifact

## Main Analysis Tasks

### <font color="#1F6FEB">EDA Notebook</font>

- Data overview and shape
- Missing values inspection
- Survival patterns by gender, class, and age
- Correlation and feature relationship checks
- Data cleaning and output generation

### <font color="#10B981">Modeling Notebook</font>

- Train/test split with stratification
- Preprocessing pipeline for numeric and categorical variables
- Logistic Regression, Decision Tree, and Random Forest comparison
- SMOTE and class weight comparison
- Hyperparameter tuning with GridSearchCV
- Regression task for fare prediction
- Saving the final pipeline artifact

## Model Output Highlights

The modeling notebook compares multiple classifiers using key metrics such as:

- Accuracy
- Precision
- Recall
- F1-score
- AUC

This ensures the final model is chosen based on balanced performance, not just raw accuracy.

## Results and Interpretation

The notebook focuses on a practical conclusion:

```text
The best model is selected by evaluating the trade-off between precision and recall, which is especially important in an imbalanced dataset such as Titanic survival data.
```

## Notes

- The project uses a clean split between training and test data.
- Preprocessing is fit only on training data to prevent leakage.
- The saved model pipeline can be reused on new raw inputs.
- The outputs are designed for notebook-based analysis and reproducibility.

## Final Status

<font color="#16A34A"><b>Project ready for notebook execution and model evaluation.</b></font>

---

<p align="center">
  <font color="#7C3AED"><b>Prepared for Titanic EDA and Predictive Modeling.</b></font>
</p>

This folder includes all required parts of the module:

- Live scraping with `requests` and `BeautifulSoup`
- Cleaning and type conversion with pandas
- Fixed GBP to INR conversion using `105.50`
- Normalized SQLite database with primary key and foreign key
- More than five SQL queries
- Required SQL clauses: `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT`, `IN`, `BETWEEN`, and `JOIN`
- pandas `pd.read_sql(...)`
- pandas `pd.merge(...)`
- README documentation with install steps, run steps, schema, and design decisions

## Short Summary

This data pipeline starts with live catalog data and ends with a queryable SQLite database plus pandas validation. It is small, readable, and complete enough to show the full flow of a real data-engineering task.
