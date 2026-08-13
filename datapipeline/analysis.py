import sqlite3

import pandas as pd

from database import DB_PATH


TOP_BOOKS_QUERY = """
    SELECT
        b.title,
        c.category_name AS category,
        b.price_gbp,
        b.price_inr,
        b.rating,
        b.in_stock
    FROM books AS b
    JOIN categories AS c
        ON c.category_id = b.category_id
    ORDER BY b.rating DESC, b.price_gbp ASC
    LIMIT 10;
"""


CATEGORY_SUMMARY_QUERY = """
    SELECT
        c.category_name AS category,
        COUNT(*) AS total_books,
        ROUND(AVG(b.price_gbp), 2) AS avg_price_gbp,
        ROUND(AVG(b.price_inr), 2) AS avg_price_inr,
        ROUND(AVG(b.rating), 2) AS avg_rating
    FROM books AS b
    JOIN categories AS c
        ON c.category_id = b.category_id
    GROUP BY c.category_name
    ORDER BY total_books DESC;
"""


def show_dataframe(title, df):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(df.to_string(index=False))


def build_join_with_pandas(conn):
    books_df = pd.read_sql(
        """
        SELECT
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        FROM books;
        """,
        conn,
    )

    categories_df = pd.read_sql(
        """
        SELECT
            category_id,
            category_name
        FROM categories;
        """,
        conn,
    )

    merged_df = books_df.merge(
        categories_df,
        on="category_id",
        how="inner",
    )

    merged_df = merged_df.rename(
        columns={"category_name": "category"}
    )

    return (
        merged_df[
            [
                "title",
                "category",
                "price_gbp",
                "price_inr",
                "rating",
                "in_stock",
            ]
        ]
        .sort_values(
            by=["rating", "price_gbp"],
            ascending=[False, True],
        )
        .head(10)
        .reset_index(drop=True)
    )


def main():
    with sqlite3.connect(DB_PATH) as conn:
        sql_top_books_df = pd.read_sql(TOP_BOOKS_QUERY, conn)
        category_summary_df = pd.read_sql(CATEGORY_SUMMARY_QUERY, conn)
        pandas_top_books_df = build_join_with_pandas(conn)

    show_dataframe(
        "Top 10 books using SQL JOIN and pd.read_sql",
        sql_top_books_df,
    )

    show_dataframe(
        "Category summary using pd.read_sql",
        category_summary_df,
    )

    show_dataframe(
        "Top 10 books using pandas merge",
        pandas_top_books_df,
    )

    outputs_match = sql_top_books_df.equals(pandas_top_books_df)

    print("\n" + "=" * 80)
    print("Comparison Result")
    print("=" * 80)

    if outputs_match:
        print("SQL JOIN output and pandas merge output match.")
    else:
        print("SQL JOIN output and pandas merge output do not match.")


if __name__ == "__main__":
    main()
