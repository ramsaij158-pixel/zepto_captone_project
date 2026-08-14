Project Overview

This project is a complete mini data pipeline built for catalog-style pricing and availability analysis. It scrapes live product data from books.toscrape.com, cleans the scraped values, converts prices from GBP to INR using a fixed project rate, stores the data in a normalized SQLite database, and then analyzes it using both SQL and pandas.

The website uses books as the product catalog, but the pipeline is similar to what a company could use for competitive pricing, product availability checks, and catalog benchmarking.

Live website -> Scraper -> Cleaned data -> SQLite database -> SQL queries -> pandas validation
Folder Contents

File	Purpose
scraper.py	Scrapes book data from the website, cleans it, converts prices, and saves scraped_books.csv.
database.py	Creates the SQLite database schema and loads cleaned book data into books.db.
queries.py	Runs the required SQL queries and prints the query results.
analysis.py	Uses pandas read_sql and merge to compare SQL JOIN output with pandas output.
requirements.txt	Lists the Python packages required to run the project.
books.db	SQLite database file created by database.py.
scraped_books.csv	CSV file created by scraper.py.
README.md	Documentation for setup, run steps, schema, and design decisions.
Install

Open a terminal in this project folder:

cd /Users/ramsaijeevan001/Documents/datapipeline
Install the required packages:

python3 -m pip install -r requirements.txt
The requirements.txt file contains:

requests
beautifulsoup4
pandas
Run The Pipeline

Run the project files in this order:

python3 scraper.py
python3 database.py
python3 queries.py
python3 analysis.py
What happens during each step:

Command	Output
python3 scraper.py	Scrapes and cleans the live book data, then creates scraped_books.csv.
python3 database.py	Creates normalized SQLite tables and saves the cleaned records into books.db.
python3 queries.py	Runs SQL queries and prints the results in the terminal.
python3 analysis.py	Reads SQL results with pandas and checks SQL JOIN output against pandas merge output.
Because books.db is already included, you can skip scraping and loading if you only want to see the query results:

python3 queries.py
python3 analysis.py
Data Source

The data is scraped from:

https://books.toscrape.com/
The scraper collects books from these three categories:

Category	Books Collected
Travel	11
Mystery	32
Young Adult	54
Total records collected:

97 books
Each scraped book contains:

title
price_gbp
rating
in_stock
category
After cleaning and conversion, the final dataset also includes:

price_inr
Cleaning And Conversion

The scraper does more than collect raw text. It prepares the data so it can be used safely in analysis.

Field	Cleaning Logic
title	Stripped and kept as text.
price_gbp	Extracted from price text and converted to float.
rating	Converted from text classes like One, Two, Three, Four, Five into integers from 1 to 5.
in_stock	Converted into a boolean value, then stored in SQLite as 1 or 0.
category	Stored separately in the categories table to keep the database normalized.
price_inr	Calculated from price_gbp using the fixed baseline conversion rate.
If a numeric value such as price or rating fails to parse, the code uses median imputation. Rows missing essential fields like title or category are dropped because they cannot be reliably used as catalog records.

Fixed Currency Rate

This project uses the required fixed baseline rate:

1 GBP = 105.50 INR
The conversion formula is:

price_inr = price_gbp * 105.50
This is not a live exchange rate. It is a project-defined constant, so no currency API or date reference is required.

SQLite Database Design

The database is normalized into two related tables:

categories
books
The categories table stores category names once. The books table stores book-level details and uses category_id as a foreign key.

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    scraped_at TEXT,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);
This design avoids repeating category names for every book and satisfies the primary key and foreign key requirement.

SQL Queries

queries.py runs six SQL queries. The assignment asks for at least five, so this project includes one extra query for stronger coverage.

Query	SQL Feature Covered
Available books with rating 4 or higher	SELECT, WHERE, ORDER BY
Ten cheapest books	ORDER BY, LIMIT
Distinct categories	DISTINCT
Books priced between 20 and 40 GBP	BETWEEN
Books from Mystery or Travel	IN, JOIN
Top 10 highest-rated books with category	JOIN, ORDER BY, LIMIT
These queries help answer practical catalog questions such as which products are highly rated, which products are cheapest, which categories exist, and how book records connect to category records.

pandas Validation

analysis.py proves that the database JOIN result can also be reproduced with pandas.

It performs three important steps:

Reads a JOIN query result using pd.read_sql(...).
Loads books and categories separately.
Recreates the JOIN using pd.merge(...).
The script then compares both outputs.

Expected result:

SQL JOIN output and pandas merge output match.
Verified Output

The pipeline was tested successfully.

Saved 97 books to books.db
Mystery: 32
Travel: 11
Young Adult: 54
SQL JOIN output and pandas merge output match.
Final Submission Checklist

This folder includes all required parts of the module:

Live scraping with requests and BeautifulSoup
Cleaning and type conversion with pandas
Fixed GBP to INR conversion using 105.50
Normalized SQLite database with primary key and foreign key
More than five SQL queries
Required SQL clauses: WHERE, ORDER BY, LIMIT, DISTINCT, IN, BETWEEN, and JOIN
pandas pd.read_sql(...)
pandas pd.merge(...)
README documentation with install steps, run steps, schema, and design decisions
Short Summary

This data pipeline starts with live catalog data and ends with a queryable SQLite database plus pandas validation. It is small, readable, and complete enough to show the full flow of a real data-engineering task.