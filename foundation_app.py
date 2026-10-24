"""
Filename: foundation_app.py
Author: Travisha Mills
Date: 2026-10-23
Project: Foundation Characteristics & Consumer Demand
Description:
    Command-line application for collecting foundation product data
    from Ulta and Sephora using product URLs.

Main responsibilities:
    - Identify retailers and run the corresponding web scraper.
    - Collect packaging material through validated manual input.
    - Match unique products using normalized names and characteristics.
    - Prevent duplicate products and warn about repeated observations.
    - Reconcile product characteristics using established priority rules.
    - Save product characteristics and retailer observations to SQLite.
    - Display saved products and observations using Pandas.

Database:
    - foundation.db
    - products
    - product_observations

Dependencies:
    - Python 3.14.6 or later
    - pandas
    - requests
    - beautifulsoup4
    - sqlite3 (Python standard library)

Run order:
    1. Run foundation_database.py to initialize the database.
    2. Run foundation_app.py to collect and review data.
    3. Run db_cleaner.py to audit data quality.
"""

import sqlite3
import re
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urlparse

import pandas as pd

from ulta_product_scraper import scrape_ulta, format_yes_no
from sephora_product_scraper import scrape_sephora

# Connect to the existing SQLite database.
connection = sqlite3.connect("foundation.db")

# Enforce relationships between database tables.
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Validate yes/no input. Blank returns None when allowed (SQLite NULL).
def get_yes_no(prompt, allow_blank=False):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "y":
            return 1
        elif user_input == "n":
            return 0
        elif allow_blank and user_input == "":
            return None
        else:
            print(
                "Enter y, n, or leave blank."
                if allow_blank else "Enter y/n."
            )

# Validate the entered product URL.
def get_url(prompt):
    while True:
        url = input(prompt).strip()
        parsed_url = urlparse(url)

        if parsed_url.scheme in ("http", "https") and parsed_url.hostname:
            return url
        else:
            print("Enter a valid URL starting with http:// or https://")

# Check for previous observations from the same product, retailer, and URL.
def check_duplicate_observation(product_id, source, source_url):
    cursor.execute('''
        SELECT observation_id, collection_date
        FROM product_observations
        WHERE product_id = ?
          AND source = ?
          AND source_url = ?
        ORDER BY collection_date DESC
        LIMIT 1
    ''', (product_id, source, source_url))
    return cursor.fetchone()

# Display a Pandas DataFrame in a readable terminal format.
def display_dataframe(df):
    if df.empty:
        print("No records found.")
        return

    with pd.option_context(
        "display.max_columns", None,
        "display.width", 140,
        "display.max_colwidth", 30
    ):
        print(df.to_string(index=False))

# Display saved foundation products using Pandas.
def view_products():
    print("\nSaved Products")

    products_df = pd.read_sql_query(
        "SELECT * FROM products",
        connection
    )

    if products_df.empty:
        print("No products found.")
        return

    print("\nProduct Information")
    product_info = products_df[
        [
            "product_id",
            "product_name",
            "brand",
            "size_oz",
            "packaging_material",
            "finish_type",
            "coverage_level"
        ]
    ]
    display_dataframe(product_info)
    print("\nProduct Characteristics")
    product_characteristics = products_df[
        [
            "product_id",
            "shade_count",
            "undertone_count",
            "non_comedogenic",
            "skincare_benefits",
            "spf_present",
            "wear_claim_hours"
        ]
    ]
    display_dataframe(product_characteristics)

# Display saved retailer observations using Pandas.
def view_observations():
    print("\nProduct Observations")

    observations_df = pd.read_sql_query('''
        SELECT
            po.observation_id,
            p.product_name,
            po.source,
            po.source_url,
            po.collection_date,
            po.price_usd,
            po.bestseller_list,
            po.review_count
        FROM product_observations po
        JOIN products p
            ON po.product_id = p.product_id
        ORDER BY po.collection_date DESC
    ''', connection)

    if observations_df.empty:
        print("No product observations found.")
    else:
        display_dataframe(observations_df)


# Collect packaging material when it is not already recorded.
def complete_missing_characteristics(data):
    if data.get("packaging_material") is None:
        options = {
            "1": "glass",
            "2": "plastic"
        }

        print("\nChoose packaging material (leave blank if unknown):")
        for number, material in options.items():
            print(f"{number}. {material}")
        while True:
            response = input("Choose an option: ").strip()

            if response == "":
                data["packaging_material"] = None
                break
            elif response in options:
                data["packaging_material"] = options[response]
                break
            else:
                print("Choose 1, 2, or leave blank.")
    return data

# Normalize product names for consistent matching across retailers.
def normalize_product_name(name):
    if not name:
        return ""
    name = unicodedata.normalize("NFKD", name).casefold()
    name = "".join(
        char for char in name
        if not unicodedata.combining(char)
    )
    name = name.replace("&", " and ")
    name = re.sub(r"\bnew\b", " ", name)
    name = re.sub(r"[^a-z0-9]+", " ", name)
    return " ".join(name.split())

# Compare product sizes while allowing minor rounding differences.
def sizes_match(size_a, size_b):
    if size_a is None or size_b is None:
        return False
    return abs(float(size_a) - float(size_b)) <= 0.02


# Identify the same product without treating unknown sizes as equal.
def same_product(existing_brand, existing_name, existing_size,
                 new_brand, new_name, new_size):
    # Brand and product name must match after normalization.
    if normalize_product_name(existing_brand) != normalize_product_name(new_brand):
        return False
    if normalize_product_name(existing_name) != normalize_product_name(new_name):
        return False
    # If both sizes are known, compare them normally.
    if existing_size is not None and new_size is not None:
        return sizes_match(existing_size, new_size)
    # Same brand and name with an unknown size is a possible match.
    return None


# Compare available product characteristics to identify possible duplicates.
def compare_product_characteristics(scraped, existing):
    matching_fields = []
    fields = [
        "brand",
        "size_oz",
        "shade_count",
        "undertone_count",
        "finish_type",
        "coverage_level",
        "non_comedogenic",
        "skincare_benefits",
        "spf_present",
        "wear_claim_hours",
        "packaging_material"
    ]

    for field in fields:
        new_value = scraped.get(field)
        saved_value = existing.get(field)
        # Missing characteristics do not count as matches.
        if new_value is None or saved_value is None:
            continue
        if field == "brand":
            matches = (
                normalize_product_name(new_value)
                == normalize_product_name(saved_value)
            )
        elif field == "size_oz":
            matches = sizes_match(new_value, saved_value)
        elif isinstance(new_value, str) and isinstance(saved_value, str):
            matches = (
                new_value.strip().casefold()
                == saved_value.strip().casefold()
            )
        else:
            matches = new_value == saved_value
        if matches:
            matching_fields.append(field)
    return matching_fields

# Identify existing products using brand, size, name, and characteristics.
def find_existing_product(data):
    brand = normalize_product_name(data.get("brand"))
    product_name = normalize_product_name(data.get("product_name"))
    size_oz = data.get("size_oz")

    # Brand and product name are required; size may be unknown.
    if not brand or not product_name:
        print("Cannot identify product: brand or name is missing.")
        print("Product matching stopped. No data saved.")
        return None, "incomplete"

    # Retrieve existing product characteristics.
    cursor.execute("SELECT * FROM products")
    columns = [column[0] for column in cursor.description]
    existing_products = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    possible_matches = []

    for existing in existing_products:
        saved_brand = normalize_product_name(existing["brand"])
        saved_name = normalize_product_name(existing["product_name"])
        saved_size = existing["size_oz"]

        # Brand must match.
        if brand != saved_brand:
            continue
        # Known sizes must match; unknown sizes require confirmation.
        size_unknown = size_oz is None or saved_size is None
        if not size_unknown and not sizes_match(size_oz, saved_size):
            continue
        # Exact name and brand with matching known sizes.
        if product_name == saved_name and not size_unknown:
            print(f"\nExisting product found: {existing['product_name']}")
            print(f"Product ID: {existing['product_id']}")
            return existing["product_id"], "matched"
        # Exact name and brand with an unknown size.
        if product_name == saved_name and size_unknown:
            print("\nPossible Duplicate Product Found")
            print(f"Existing Product ID: {existing['product_id']}")
            print(f"Existing Name: {existing['product_name']}")
            print(f"Existing Size: {saved_size} oz")
            print(f"Scraped Size: {size_oz} oz")
            confirmation = get_yes_no(
                "\nIs this the same foundation? (y/n): "
            )
            if confirmation == 1:
                print(f"\nUsing existing Product ID: {existing['product_id']}")
                return existing["product_id"], "matched"
            continue

        # Compare characteristics when product names differ.
        matching_fields = compare_product_characteristics(
            data, existing
        )
        similarity = SequenceMatcher(
            None, product_name, saved_name
        ).ratio()
        # Suggest possible duplicates for manual confirmation.
        if len(matching_fields) >= 5 or similarity >= 0.60:
            possible_matches.append({
                "product_id": existing["product_id"],
                "product_name": existing["product_name"],
                "size_oz": saved_size,
                "similarity": similarity,
                "matching_fields": matching_fields
            })

    # Review the strongest possible matches first.
    possible_matches.sort(
        key=lambda match: (
            len(match["matching_fields"]),
            match["similarity"]
        ),
        reverse=True
    )
    for match in possible_matches:
        print("\nPossible Duplicate Product Found")
        print(f"Existing Product ID: {match['product_id']}")
        print(f"Existing Name: {match['product_name']}")
        print(f"Scraped Name: {data['product_name']}")
        print(f"Size: {match['size_oz']} oz")
        print(f"Name similarity: {match['similarity']:.0%}")
        print(
            f"\nMatching characteristics "
            f"({len(match['matching_fields'])}):"
        )
        for field in match["matching_fields"]:
            print(f"- {field}")
        confirmation = get_yes_no(
            "\nIs this the same foundation? (y/n): "
        )
        if confirmation == 1:
            print(f"\nUsing existing Product ID: {match['product_id']}")
            return match["product_id"], "matched"

    print("\nNo matching product confirmed.")
    return None, "new"

# Reconcile existing characteristics using the established priority rules.
def reconcile_characteristics(product_id, data, source, url):
    boolean_fields = {
        "spf_present",
        "non_comedogenic",
        "skincare_benefits"
    }
    review_fields = [
        "spf_present",
        "non_comedogenic",
        "skincare_benefits",
        "coverage_level"
    ]
    # Retrieve the saved product information.
    cursor.execute(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        raise ValueError("Existing product not found.")

    columns = [column[0] for column in cursor.description]
    existing = dict(zip(columns, product))
    # Fill missing non-conflict characteristics when new values are available.
    fill_fields = [
        "packaging_material",
        "shade_count",
        "undertone_count",
        "finish_type",
        "wear_claim_hours"
    ]
    for field in fill_fields:
        new_value = data.get(field)
        saved_value = existing.get(field)
        if saved_value is None and new_value is not None:
            cursor.execute(
                f"UPDATE products SET {field} = ? WHERE product_id = ?",
                (new_value, product_id)
            )
            existing[field] = new_value
            print(f"Filled missing characteristic: {field} = {new_value}")

    # Review only the agreed boolean and coverage characteristics.
    for field in review_fields:
        new_value = data.get(field)
        saved_value = existing.get(field)
        if new_value is None:
            continue
        # Fill missing values automatically.
        if saved_value is None:
            cursor.execute(
                f"UPDATE products SET {field} = ? WHERE product_id = ?",
                (new_value, product_id)
            )
            existing[field] = new_value
            print(f"Filled missing characteristic: {field} = {new_value}")
            continue

        # Keep matching values unchanged.
        if saved_value == new_value:
            continue
        # Boolean characteristics: review only No (0) to Yes (1).
        if field in boolean_fields:
            if not (saved_value == 0 and new_value == 1):
                continue
        # Coverage ranges have higher priority than single coverage levels.
        elif field == "coverage_level":
            coverage_priority = {
                "light": 1,
                "medium": 1,
                "full": 1,
                "light_to_medium": 2,
                "medium_to_full": 2
            }
            saved_priority = coverage_priority.get(saved_value, 0)
            new_priority = coverage_priority.get(new_value, 0)
            # Do not downgrade from a range to a single coverage level.
            if saved_priority > new_priority:
                continue

        # Ask for authorization before replacing an existing value.
        print("\nCharacteristic Conflict Detected")
        print(f"Product ID: {product_id}")
        print(f"Product: {existing['product_name']}")
        print(f"Field: {field}")

        if field in boolean_fields:
            print(f"Existing value: {format_yes_no(saved_value)}")
            print(f"New scraped value: {format_yes_no(new_value)}")
        else:
            print(f"Existing value: {saved_value}")
            print(f"New scraped value: {new_value}")

        print(f"Source: {source}")
        confirm = get_yes_no(
            "Update the existing product characteristic? (y/n): "
        )
        if confirm == 1:
            cursor.execute(
                f"UPDATE products SET {field} = ? WHERE product_id = ?",
                (new_value, product_id)
            )
            existing[field] = new_value
            print(f"Updated {field}.")
        else:
            print(f"Kept existing {field}: {saved_value}")


# Save one unique product and its source-specific observation.
def save_product_and_observation(data, product_id, source, url):
    # Warn when an observation was previously collected from the same URL.
    if product_id is not None:
        duplicate = check_duplicate_observation(
            product_id, source, url
        )
        if duplicate:
            print(
                f"\nPrevious observation found: ID {duplicate[0]}"
                f" | Collected: {duplicate[1]}"
            )
            confirm = get_yes_no(
                "Save another observation? (y/n): "
            )
            if confirm == 0:
                print("Collection cancelled.")
                return

    # Record the observation collection date and time.
    collection_date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    try:
        # Create a product record only when no existing product matches.
        if product_id is None:
            cursor.execute('''
                INSERT INTO products (
                    product_name,
                    brand,
                    size_oz,
                    packaging_material,
                    shade_count,
                    undertone_count,
                    finish_type,
                    coverage_level,
                    non_comedogenic,
                    skincare_benefits,
                    spf_present,
                    wear_claim_hours
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("product_name"),
                data.get("brand"),
                data.get("size_oz"),
                data.get("packaging_material"),
                data.get("shade_count"),
                data.get("undertone_count"),
                data.get("finish_type"),
                data.get("coverage_level"),
                data.get("non_comedogenic"),
                data.get("skincare_benefits"),
                data.get("spf_present"),
                data.get("wear_claim_hours")
            ))
            product_id = cursor.lastrowid
            print(f"\nNew product created. Product ID: {product_id}")
        else:
            print(f"\nUsing existing Product ID: {product_id}")
            # Reconcile new retailer data with existing characteristics.
            reconcile_characteristics(
                product_id,
                data,
                source,
                url
            )

        # Create a new observation for each authorized collection.
        cursor.execute('''
            INSERT INTO product_observations (
                product_id,
                source,
                source_url,
                collection_date,
                price_usd,
                bestseller_list,
                review_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            source,
            url,
            collection_date,
            data.get("price_usd"),
            data.get("bestseller_list"),
            data.get("review_count")
        ))
        observation_id = cursor.lastrowid
        # Save characteristic updates and observation together.
        connection.commit()
        print("\nObservation saved successfully.")
        print(f"Observation ID: {observation_id}")
        print(f"Linked Product ID: {product_id}")
        print(f"Retailer: {source}")
        print(f"Collection Date: {collection_date}")

    except sqlite3.Error as error:
        connection.rollback()
        print(f"\nDatabase error: {error}")
        print("Changes were not saved.")

# Accept a product URL and call the matching retailer scraper.
def add_product_by_url():
    print("\nAdd Product and Observation by URL")

    url = get_url("Enter product URL: ")

    # Identify the retailer using the URL hostname.
    hostname = (urlparse(url).hostname or "").lower()
    if hostname == "ulta.com" or hostname.endswith(".ulta.com"):
        source = "ulta"
        data = scrape_ulta(url)
    elif hostname == "sephora.com" or hostname.endswith(".sephora.com"):
        source = "sephora"
        data = scrape_sephora(url)
    else:
        print("Unsupported retailer URL.")
        return
    # Display the extracted data using readable boolean labels.
    print(f"\nRetailer: {source}")
    boolean_fields = {
        "non_comedogenic",
        "skincare_benefits",
        "spf_present",
        "bestseller_list"
    }

    print("\nScraped Product Information")
    for field, value in data.items():
        if field in boolean_fields:
            value = format_yes_no(value)
        print(f"{field}: {value}")

    # Check for an existing unique foundation.
    product_id, match_status = find_existing_product(data)
    if match_status == "incomplete":
        print("Product matching stopped. No data saved.")
        return

    if product_id is not None:
        # Reuse packaging information from the existing product.
        existing = cursor.execute('''
            SELECT packaging_material
            FROM products
            WHERE product_id = ?
        ''', (product_id,)).fetchone()
        data["packaging_material"] = existing[0]

        # Request packaging only when the saved value is missing.
        if data["packaging_material"] is None:
            print("\nAdditional Product Characteristics")
            data = complete_missing_characteristics(data)
        print(f"\nExisting Product ID: {product_id}")
    else:
        # Collect packaging for a new unique product.
        print("\nAdditional Product Characteristics")
        data = complete_missing_characteristics(data)

        print("\nNew product identified.")
    print("Packaging material:", data["packaging_material"])
    print("Match status:", match_status)
    # Save the product and its retailer observation.
    save_product_and_observation(
        data,
        product_id,
        source,
        url
    )

# Display application menu.
def menu():
    print("\nFoundation Data Collection")
    print("1. Add product and observation by URL")
    print("2. View products")
    print("3. View product observations")
    print("4. Exit")

# Main application loop.
def main():
    try:
        while True:
            menu()
            choice = input("Choose an option (1-4): ").strip()
            if choice == "1":
                add_product_by_url()
            elif choice == "2":
                view_products()
            elif choice == "3":
                view_observations()
            elif choice == "4":
                print("Exiting program.")
                break
            else:
                print("Invalid option. Please choose 1-4.")
    finally:
        connection.close()

if __name__ == "__main__":
    main()