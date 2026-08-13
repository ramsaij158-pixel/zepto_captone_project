import sqlite3
from pathlib import Path

from scraper import scrape_and_clean


DB_PATH = Path("books.db")
BOOKS_TABLE = "books"
CATEGORIES_TABLE = "categories"


def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {CATEGORIES_TABLE} (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BOOKS_TABLE} (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price_gbp REAL NOT NULL,
                price_inr REAL NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)),
                category_id INTEGER NOT NULL,
                scraped_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id)
                    REFERENCES categories(category_id)
            )
            """
        )
        conn.execute(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_books_title_category
            ON {BOOKS_TABLE} (title, category_id)
            """
        )
        book_columns = {
            row[1]
            for row in conn.execute(f"PRAGMA table_info({BOOKS_TABLE})")
        }

        if "scraped_at" not in book_columns:
            conn.execute(f"ALTER TABLE {BOOKS_TABLE} ADD COLUMN scraped_at TEXT")


def create_books_table(db_path=DB_PATH):
    create_tables(db_path)


def save_books(df, db_path=DB_PATH):
    required_columns = {
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category",
    }
    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    create_tables(db_path)

    rows = [
        (
            row.title,
            float(row.price_gbp),
            float(row.price_inr),
            int(row.rating),
            int(bool(row.in_stock)),
            row.category,
        )
        for row in df.itertuples(index=False)
    ]

    with get_connection(db_path) as conn:
        categories = sorted(set(df["category"]))

        conn.executemany(
            f"""
            INSERT OR IGNORE INTO {CATEGORIES_TABLE} (category_name)
            VALUES (?)
            """,
            [(category,) for category in categories],
        )

        category_rows = conn.execute(
            f"""
            SELECT category_id, category_name
            FROM {CATEGORIES_TABLE}
            """
        ).fetchall()
        category_ids = {
            category_name: category_id
            for category_id, category_name in category_rows
        }

        rows = [
            (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_ids[category],
            )
            for title, price_gbp, price_inr, rating, in_stock, category in rows
        ]

        conn.executemany(
            f"""
            INSERT INTO {BOOKS_TABLE} (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(title, category_id) DO UPDATE SET
                price_gbp = excluded.price_gbp,
                price_inr = excluded.price_inr,
                rating = excluded.rating,
                in_stock = excluded.in_stock,
                scraped_at = CURRENT_TIMESTAMP
            """,
            rows,
        )

    return len(rows)


def fetch_books(db_path=DB_PATH):
    create_tables(db_path)

    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"""
            SELECT
                b.book_id,
                b.title,
                b.price_gbp,
                b.price_inr,
                b.rating,
                b.in_stock,
                c.category_name AS category,
                b.scraped_at
            FROM {BOOKS_TABLE} AS b
            JOIN {CATEGORIES_TABLE} AS c
                ON c.category_id = b.category_id
            ORDER BY c.category_name, b.title
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def main():
    df = scrape_and_clean()
    saved_count = save_books(df)
    print(f"Saved {saved_count} books to {DB_PATH}")


if __name__ == "__main__":
    main()
