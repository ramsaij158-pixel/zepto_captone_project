import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

BASE_URLS = {
    "Travel": "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "Mystery": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "Young Adult": "https://books.toscrape.com/catalogue/category/books/young-adult_21/index.html"
}

GBP_TO_INR = 105.50

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def scrape_category(category_name, category_url):

    response = requests.get(category_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    books = []

    while True:

        book_cards = soup.select("article.product_pod")

        for book in book_cards:

            title = book.h3.a.get("title", "").strip()

            price_text = book.select_one(
                ".price_color"
            ).get_text(strip=True)

            price_match = re.search(
                r"\d+(?:\.\d+)?",
                price_text
            )

            try:
                price_gbp = float(
                    price_match.group()
                )
            except (AttributeError, ValueError, TypeError):
                price_gbp = None

            rating_element = book.select_one(
                ".star-rating"
            )

            rating = None

            if rating_element:

                classes = rating_element.get("class", [])

                if len(classes) > 1:
                    rating = RATING_MAP.get(classes[1])

            availability_element = book.select_one(
                ".availability"
            )

            availability = ""

            if availability_element:
                availability = availability_element.get_text(
                    " ",
                    strip=True
                )

            in_stock = "In stock" in availability

            books.append({
                "title": title,
                "price_gbp": price_gbp,
                "rating": rating,
                "in_stock": in_stock,
                "category": category_name
            })

        next_button = soup.select_one(
            "li.next a"
        )

        if not next_button:
            break

        next_url = next_button.get("href")

        if next_url.startswith("../"):
            next_url = next_url.replace("../", "")

        elif next_url.startswith("../../../"):
            next_url = next_url.replace(
                "../../../",
                ""
            )

        else:
            # Build URL from current category path
            current_url = response.url.rsplit("/", 1)[0]
            next_url = current_url + "/" + next_url

        response = requests.get(
            next_url,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

    return books


def clean_data(books):

    df = pd.DataFrame(books)

    # Median imputation for numeric fields

    if df["price_gbp"].isna().any():
        df["price_gbp"] = df["price_gbp"].fillna(
            df["price_gbp"].median()
        )

    if df["rating"].isna().any():
        df["rating"] = df["rating"].fillna(
            df["rating"].median()
        ).round()

    # Drop rows missing essential fields

    df = df.dropna(
        subset=["title", "category"]
    )

    # Correct data types

    df["price_gbp"] = df["price_gbp"].astype(float)

    df["rating"] = df["rating"].astype(int)

    df["in_stock"] = df["in_stock"].astype(bool)

    # Required fixed conversion

    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    return df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]


def scrape_and_clean():

    all_books = []

    for category_name, category_url in BASE_URLS.items():

        print(
            f"\nScraping category: {category_name}"
        )

        books = scrape_category(
            category_name,
            category_url
        )

        print(
            f"Books found: {len(books)}"
        )

        all_books.extend(books)

    print(
        f"\nTotal books scraped: {len(all_books)}"
    )

    df = clean_data(all_books)

    return df


if __name__ == "__main__":

    df = scrape_and_clean()

    print("\n==============================")
    print("FINAL DATASET")
    print("==============================")

    print(f"Total books: {len(df)}")

    print(
        f"Total categories: "
        f"{df['category'].nunique()}"
    )

    print("\nFirst 10 rows:")
    print(df.head(10))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nCategory counts:")
    print(df["category"].value_counts())

    df.to_csv(
        "scraped_books.csv",
        index=False
    )

    print(
        "\nSaved to scraped_books.csv"
    )
    
