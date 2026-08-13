import sqlite3

from database import DB_PATH


QUERIES = {
    "1. Available books with rating 4 or higher": """
        SELECT
            title,
            price_gbp,
            rating,
            in_stock
        FROM books
        WHERE in_stock = 1
            AND rating >= 4
        ORDER BY rating DESC, price_gbp ASC;
    """,
    "2. Ten cheapest books": """
        SELECT
            title,
            price_gbp,
            price_inr,
            rating
        FROM books
        ORDER BY price_gbp ASC
        LIMIT 10;
    """,
    "3. Distinct categories": """
        SELECT DISTINCT
            category_name
        FROM categories
        ORDER BY category_name;
    """,
    "4. Books priced between 20 and 40 GBP": """
        SELECT
            title,
            price_gbp,
            rating
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp DESC;
    """,
    "5. Books from Mystery or Travel categories": """
        SELECT
            b.title,
            c.category_name,
            b.price_gbp,
            b.rating
        FROM books AS b
        JOIN categories AS c
            ON c.category_id = b.category_id
        WHERE c.category_name IN ('Mystery', 'Travel')
        ORDER BY c.category_name, b.rating DESC;
    """,
    "6. Top 10 highest-rated books with category": """
        SELECT
            b.title,
            c.category_name,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock
        FROM books AS b
        JOIN categories AS c
            ON c.category_id = b.category_id
        ORDER BY b.rating DESC, b.price_gbp ASC
        LIMIT 10;
    """,
}


def run_query(cursor, query):
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def print_result(title, columns, rows):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(" | ".join(columns))
    print("-" * 80)

    for row in rows:
        print(" | ".join(str(value) for value in row))

    print(f"\nRows returned: {len(rows)}")


def main():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for title, query in QUERIES.items():
            columns, rows = run_query(cursor, query)
            print_result(title, columns, rows)


if __name__ == "__main__":
    main()
