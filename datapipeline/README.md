<div align="center">

# Books Data Pipeline

<p>
  <img src="https://img.shields.io/badge/Python-3.9+-2F80ED?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/SQLite-Database-0B7285?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Pandas-Cleaning-F59F00?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">
</p>

<p>
  <strong>Scrape. Clean. Store. Analyze.</strong><br>
  A compact Python pipeline for turning book listings into useful, queryable data.
</p>

</div>

A small Python data pipeline that scrapes selected categories from [Books to Scrape](https://books.toscrape.com/), cleans the results, stores them in SQLite, and runs sample SQL analysis queries.

## Visual identity

This project uses a clean editorial-style theme:

| Role | Font idea | Color |
| --- | --- | --- |
| Main heading | `Playfair Display` / serif | `#1F2937` Charcoal Ink |
| Body text | `Inter` / sans-serif | `#374151` Slate Gray |
| Code and data labels | `JetBrains Mono` / monospace | `#0F766E` Teal |
| Primary accent | Pipeline highlights | `#2F80ED` Data Blue |
| Secondary accent | Analysis highlights | `#F59F00` Book Gold |

## What it does

- Scrapes **Travel**, **Mystery**, and **Young Adult** books.
- Extracts title, GBP price, rating, stock status, and category.
- Cleans missing numeric values and converts prices to INR (using `1 GBP = 105.50 INR`).
- Exports the cleaned data to `scraped_books.csv`.
- Upserts the data into `books.db` with normalized `books` and `categories` tables.
- Runs six example SQL queries, including cheapest books and highly rated in-stock books.

## Requirements

- Python 3.9 or later
- Internet access while scraping

Install dependencies:

```bash
python -m pip install -r requirement.txt
```

## Run the pipeline

From this directory, scrape and create the CSV:

```bash
python scraper.py
```

To populate the SQLite database, run the module from the project parent directory:

```bash
cd ..
python -m datapipeline.database
```

Then run the included analysis queries:

```bash
python -m datapipeline.queries
```

## Output

| File | Description |
| --- | --- |
| `scraped_books.csv` | Cleaned scraped dataset |
| `books.db` | SQLite database containing `books` and `categories` |

Each book record includes:

`title`, `price_gbp`, `price_inr`, `rating`, `in_stock`, `category`

## Project structure

```text
datapipeline/
├── scraper.py       # Web scraping and data cleaning
├── database.py      # SQLite schema and loading logic
├── queries.py       # Sample SQL analysis queries
├── requirement.txt  # Python dependencies
├── scraped_books.csv
└── books.db
```

## Database design

`categories` contains unique category names. `books` stores book details and references its category with `category_id`. A unique index on `(title, category_id)` lets later pipeline runs update existing records instead of creating duplicates.
