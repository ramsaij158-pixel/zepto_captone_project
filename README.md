# Zepto Capstone

This repository is organized into three main folders:

- [datapipeline](datapipeline) — data collection, scraping, cleaning, and SQL analysis
- [analytics](analytics) — exploratory data analysis and model building
- [support_assistant](support_assistant) — Zepto policy FAQ assistant using RAG, LangGraph, ChromaDB, and FastAPI

## Project overview

This capstone combines three parts of a real product workflow:

1. Data collection and preparation
2. Data analysis and predictive modeling
3. GenAI-powered support assistant for policy queries

## Folder structure

```text
zepto_project/
├── datapipeline/
│   ├── README.md
│   ├── scraper.py
│   ├── database.py
│   ├── queries.py
│   └── requirement.txt
├── analytics/
│   ├── README.md
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   ├── model_pipeline.joblib
│   └── charts/
├── support_assistant/
│   ├── README.md
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docs/
├── README.md
└── .gitignore
```

## How to use

### Data pipeline
```bash
cd datapipeline
python -m pip install -r requirement.txt
python scraper.py
```

### Analytics
```bash
cd analytics
python -m pip install -r requirements.txt
jupyter notebook
```

### Support assistant
```bash
cd support_assistant
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860
```

## Documentation

- [datapipeline/README.md](datapipeline/README.md)
- [analytics/README.md](analytics/README.md)
- [support_assistant/README.md](support_assistant/README.md)

This README is based directly on the three project folders in the repository and shows how they work together as one end-to-end Zepto capstone project.
