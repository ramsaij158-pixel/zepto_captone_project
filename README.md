# Zepto Capstone — Data, Analytics & GenAI Pipeline

A concise, local-focused overview of the three project modules: Data Pipeline, Analytics, and Support Assistant.

## Summary

- Module 1 — Data Pipeline: scraping, cleaning, conversion (GBP→INR), SQLite warehousing, and SQL queries.
- Module 2 — Analytics: EDA and predictive modeling on the Titanic dataset; notebooks with visualizations and a saved modeling pipeline.
- Module 3 — Support Assistant: a retrieval-augmented generation (RAG) service over policy docs with local embeddings and a FastAPI endpoint.

<!-- Colored subheadings with font fallbacks. If GitHub strips styles, tell me and I'll use a different approach. -->
<h2><span style="color:#1E90FF; font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">Module 1 — Data Pipeline</span></h2>

Scraping · cleaning · SQLite warehousing · SQL queries.

<h2><span style="color:#FF6F61; font-family: 'Georgia', 'Times New Roman', Times, serif;">Module 2 — Analytics</span></h2>

EDA · visualizations · modeling · saved pipeline.

<h2><span style="color:#34C759; font-family: 'Courier New', Courier, monospace;">Module 3 — Support Assistant</span></h2>

RAG service · embeddings · ChromaDB · FastAPI.

## Repository layout

```
zepto_project/
├── data_pipeline/         Module 1 — scrape → clean → SQLite → queries
├── analytics/             Module 2 — EDA notebooks + modeling
├── support_assistant/     Module 3 — RAG service (FastAPI + ChromaDB)
└── README.md              this file (overview for all modules)
```

## Quickstart (local)

Clone the repo and run the module you need:

```bash
git clone <this-repo-url>
cd zepto_project
```

Module 1 — Data Pipeline
```bash
cd data_pipeline
pip install -r requirements.txt
python scraper.py
python clean_and_load.py
python run_queries.py
cd ..
```

Module 2 — Analytics Pipeline
```bash
cd analytics
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace 01_eda.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_modeling.ipynb
cd ..
```

Module 3 — Support Assistant
```bash
cd support_assistant
pip install -r requirements.txt
python -m app.ingest
uvicorn app.main:app --port 7860
```

---

I removed external badges, camouflaged links, and HTML artifacts to keep this README local and easy to read. If you want a decorative README (badges, images, or colored subheadings), tell me which elements to add and I will update it.
