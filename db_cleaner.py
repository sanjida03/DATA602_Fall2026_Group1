"""
Filename: clean_validate.py
Project: Foundation Characteristics & Consumer Demand
Description: Read-only data quality report based on DATA602 Lecture 7.
Run: py clean_validate.py
Requires: pandas; foundation.db in the same folder
"""

import re
import sqlite3
import unicodedata
from pathlib import Path
from difflib import SequenceMatcher
from urllib.parse import urlparse
import pandas as pd

DB_PATH = Path(__file__).with_name("foundation.db")
VALID_CATEGORIES = {
    "packaging_material": {"glass", "plastic"},
    "finish_type": {"matte", "natural", "satin", "radiant", "dewy"},
    "coverage_level": {"light", "light_to_medium", "medium", "medium_to_full", "full"},
    "source": {"ulta", "sephora", "brand_site"},
}
BOOLEAN_COLUMNS = {
    "products": ["non_comedogenic", "skincare_benefits", "spf_present"],
    "product_observations": ["bestseller_list"],
}
NUMERIC_COLUMNS = {
    "products": ["size_oz", "shade_count", "undertone_count", "wear_claim_hours"],
    "product_observations": ["price_usd", "review_count"],
}


def normalize_name(value):
    """Comparison only; never replace the original product name."""
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\bnew\b", " ", text)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def audit_table(df, table):
    print(f"\n{'=' * 58}\n{table.upper()} — {len(df)} rows × {len(df.columns)} columns\n{'=' * 58}")
    print("\nData types (Lecture 7: df.dtypes):")
    print(df.dtypes.to_string())

    # Blank strings and literal Unknown are examined without changing the data.
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    blank = pd.Series(0, index=df.columns, dtype=int)
    unknown = pd.Series(0, index=df.columns, dtype=int)
    for col in text_cols:
        cleaned = df[col].astype("string").str.strip()
        blank[col] = int(cleaned.eq("").fillna(False).sum())
        unknown[col] = int(cleaned.str.casefold().isin(["unknown", "n/a", "na", "none", "null"]).sum())

    missing = pd.DataFrame({
        "NULL/NaN": df.isna().sum(),
        "Blank strings": blank,
        "Unknown labels": unknown,
        "Missing % (NULL only)": (df.isna().mean() * 100).round(1),
    })
    print("\nMissing/blank/unknown by column:")
    print(missing.to_string())

    print("\nIdentifier check:")
    id_col = "product_id" if table == "products" else "observation_id"
    print(f"{id_col} unique: {df[id_col].is_unique}; repeated IDs: {df[id_col].duplicated().sum()}")

    # Do not treat a repeated product_id in observations as a duplicate.
    if table == "products":
        # Identify possible duplicate products, including unknown sizes.
        print("\nPossible duplicate products (review only):")
        found = 0
        records = df.to_dict("records")
        for i, a in enumerate(records):
            for b in records[i + 1:]:
                # Brand must match.
                if pd.isna(a["brand"]) or pd.isna(b["brand"]):
                    continue
                if normalize_name(a["brand"]) != normalize_name(b["brand"]):
                    continue
                # Compare sizes only when both are known.
                size_a = a["size_oz"]
                size_b = b["size_oz"]
                if pd.notna(size_a) and pd.notna(size_b):
                    if abs(float(size_a) - float(size_b)) > 0.02:
                        continue
                # Compare product names.
                score = SequenceMatcher(
                    None,
                    normalize_name(a["product_name"]),
                    normalize_name(b["product_name"])
                ).ratio()
                # Flag possible duplicates for review.
                if score >= 0.60:
                    print(
                        f"  IDs {a['product_id']} and {b['product_id']} "
                        f"| similarity {score:.0%}"
                    )
                    print(
                        f"    {a['product_name']} / {b['product_name']}"
                    )
                    print(
                        f"    Sizes: {size_a} oz / {size_b} oz"
                    )
                    found += 1
        if not found:
            print("  None flagged by brand + size + name similarity.")


    print("\nNonstandard categorical values:")
    any_invalid = False
    for col, allowed in VALID_CATEGORIES.items():
        if col not in df:
            continue
        # Check original values, including inconsistent capitalization or spacing.
        invalid = df[col].dropna().astype(str)
        invalid = invalid[~invalid.isin(allowed)]
        if not invalid.empty:
            print(f"  {col}: {invalid.value_counts().to_dict()}")
            any_invalid = True
    for col in BOOLEAN_COLUMNS[table]:
        invalid = df[col].dropna()
        invalid = invalid[~invalid.isin([0, 1])]
        if not invalid.empty:
            print(f"  {col}: invalid booleans {invalid.tolist()}")
            any_invalid = True
    if not any_invalid:
        print("  None detected.")

    print("\nInvalid numeric values:")
    any_invalid = False
    for col in NUMERIC_COLUMNS[table]:
        numbers = pd.to_numeric(df[col], errors="coerce")
        invalid_text = df[col].notna() & numbers.isna()
        bad_range = numbers.lt(0) if table == "product_observations" else numbers.le(0)
        if col == "undertone_count":
            bad_range = bad_range | numbers.gt(3)
        flagged = df.loc[invalid_text | bad_range, [id_col, col]]
        if not flagged.empty:
            print(f"  {col}:\n{flagged.to_string(index=False)}")
            any_invalid = True
    if not any_invalid:
        print("  None detected.")


def audit_relationships(products, observations):
    print("\n" + "=" * 58 + "\nCROSS-TABLE CHECKS\n" + "=" * 58)
    unmatched = observations.loc[~observations["product_id"].isin(products["product_id"])]
    print(f"Observations with nonexistent product_id: {len(unmatched)}")
    if not unmatched.empty:
        print(unmatched[["observation_id", "product_id"]].to_string(index=False))

    dates = pd.to_datetime(observations["collection_date"], errors="coerce", format="mixed")
    bad_dates = observations.loc[dates.isna()]
    print(f"Invalid/missing collection dates: {len(bad_dates)}")
    if not bad_dates.empty:
        print(bad_dates[["observation_id", "collection_date"]].to_string(index=False))

    print("\nMissing observation indicators by retailer (%):")
    indicators = ["price_usd", "bestseller_list", "review_count"]
    if not observations.empty:
        print((observations.groupby("source")[indicators].apply(lambda group: group.isna().mean() * 100)).round(1).to_string())
    print("Note: Bestseller status and review count are collected from Ulta and Sephora. Missing values indicate unavailable or unverified data and should be reviewed, not automatically treated as scraping failures.")

# Allow users to cancel an operation or exit the program.
def get_cleanup_input(prompt):
    value = input(prompt).strip()
    if value.lower() == "q":
        print("Exiting database cleanup.")
        raise SystemExit(0)
    if value == "0":
        print("Operation cancelled. Returning to menu.")
        return None
    return value

# Delete a product and its associated observations by product ID.
def delete_product():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        print("\nSaved Products")

        products = pd.read_sql_query("""
            SELECT product_id, brand, product_name, size_oz
            FROM products
            ORDER BY product_id
        """, conn)
        if products.empty:
            print("No products found.")
            return
        print(products.to_string(index=False))
        print("\nEnter 0 to return to menu or q to exit.")
        value = get_cleanup_input("\nProduct ID to remove: ")
        if value is None:
            return
        try:
            product_id = int(value)
        except ValueError:
            print("Invalid product ID.")
            return

        selected = products[products["product_id"] == product_id]

        if selected.empty:
            print("Product ID not found.")
            return
        product = selected.iloc[0]
        observation_count = conn.execute("""
            SELECT COUNT(*)
            FROM product_observations
            WHERE product_id = ?
        """, (product_id,)).fetchone()[0]
        print("\nProduct Selected for Deletion")
        print(f"Product ID: {product_id}")
        print(f"Brand: {product['brand']}")
        print(f"Product Name: {product['product_name']}")
        print(f"Associated Observations: {observation_count}")

        confirmation = get_cleanup_input(
            "\nDelete this product and all its observations? (y/n, 0=menu, q=exit): "
        )
        if confirmation is None:
            return
        confirmation = confirmation.lower()

        if confirmation != "y":
            print("Deletion cancelled. No changes made.")
            return

        try:
            conn.execute("BEGIN")

            # Remove observations before deleting the product.
            conn.execute("""
                DELETE FROM product_observations
                WHERE product_id = ?
            """, (product_id,))

            conn.execute("""
                DELETE FROM products
                WHERE product_id = ?
            """, (product_id,))

            conn.commit()
            print("\nProduct and associated observations deleted.")

        except sqlite3.Error as error:
            conn.rollback()
            print(f"Database error: {error}")
            print("No changes were saved.")


# Delete a single observation by observation ID.
def delete_observation():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        print("\nSaved Product Observations")
        observations = pd.read_sql_query("""
            SELECT
                o.observation_id,
                o.product_id,
                p.brand,
                p.product_name,
                o.source,
                o.collection_date,
                o.price_usd,
                o.bestseller_list,
                o.review_count
            FROM product_observations AS o
            JOIN products AS p
                ON o.product_id = p.product_id
            ORDER BY o.observation_id
        """, conn)
        if observations.empty:
            print("No observations found.")
            return
        print(observations.to_string(index=False))
        print("\nEnter 0 to return to menu or q to exit.")
        value = get_cleanup_input("\nObservation ID to remove: ")
        if value is None:
            return
        try:
            observation_id = int(value)
        except ValueError:
            print("Invalid observation ID.")
            return
        selected = observations[
            observations["observation_id"] == observation_id
        ]
        if selected.empty:
            print("Observation ID not found.")
            return
        observation = selected.iloc[0]
        print("\nObservation Selected for Deletion")
        print(f"Observation ID: {observation_id}")
        print(f"Product: {observation['brand']} - {observation['product_name']}")
        print(f"Retailer: {observation['source']}")
        print(f"Collection Date: {observation['collection_date']}")
        confirmation = get_cleanup_input(
            "\nDelete this observation? (y/n, 0=menu, q=exit): "
        )
        if confirmation is None:
            return
        confirmation = confirmation.lower()
        if confirmation != "y":
            print("Deletion cancelled. No changes made.")
            return
        try:
            conn.execute("""
                DELETE FROM product_observations
                WHERE observation_id = ?
            """, (observation_id,))
            conn.commit()
            print("\nObservation deleted successfully.")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"Database error: {error}")
            print("No changes were saved.")

        def normalize(value):
            return " ".join(str(value).casefold().split())
        if (
            normalize(original["brand"]) != normalize(duplicate["brand"])
            or normalize(original["product_name"]) != normalize(duplicate["product_name"])
        ):
            print("Products have different brands or names.")
            print("Automatic merging is blocked to avoid deleting unrelated products.")
            return
        # Check for conflicting known sizes.
        original_size = original["size_oz"]
        duplicate_size = duplicate["size_oz"]
        if (
            pd.notna(original_size)
            and pd.notna(duplicate_size)
            and abs(float(original_size) - float(duplicate_size)) > 0.02
        ):
            print("Products have different known sizes.")
            print("Merge cancelled.")
            return
        # Count observations that will be transferred.
        observation_count = conn.execute("""
            SELECT COUNT(*)
            FROM product_observations
            WHERE product_id = ?
        """, (delete_id,)).fetchone()[0]
        print(f"\nKeep Product ID: {keep_id}")
        print(f"Remove Product ID: {delete_id}")
        print(f"Observations to transfer: {observation_count}")
        confirmation = input(
            "\nConfirm merge and removal? (y/n): "
        ).strip().lower()
        if confirmation != "y":
            print("No changes made.")
            return
        # Run both changes in one transaction.
        try:
            conn.execute("BEGIN")
            conn.execute("""
                UPDATE product_observations
                SET product_id = ?
                WHERE product_id = ?
            """, (keep_id, delete_id))
            conn.execute("""
                DELETE FROM products
                WHERE product_id = ?
            """, (delete_id,))
            conn.commit()
            print("\nDuplicate removed successfully.")
            print(f"All observations are linked to Product ID {keep_id}.")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"Database error: {error}")
            print("No changes were saved.")

# Delete a selected database column while preserving its records.
def delete_column():
    print("\nDelete Database Column")
    print("1. Products")
    print("2. Product Observations")
    print("0. Return to menu")
    print("q. Exit program")

    choice = get_cleanup_input("\nSelect table (1-2): ")

    if choice is None:
        return
    tables = {
        "1": "products",
        "2": "product_observations"
    }
    table_name = tables.get(choice)
    if table_name is None:
        print("Invalid table selection.")
        return
    with sqlite3.connect(DB_PATH) as conn:
        # Display available columns.
        columns = [
            row[1]
            for row in conn.execute(
                f"PRAGMA table_info({table_name})"
            )
        ]
        print(f"\nColumns in {table_name}:")
        for column in columns:
            print(f"- {column}")
        column_name = get_cleanup_input(
            "\nColumn name to remove (0=menu, q=exit): "
        )
        if column_name is None:
            return
        if column_name not in columns:
            print("Column not found.")
            return

        # Protect primary and foreign key relationships.
        protected_columns = {
            "product_id",
            "observation_id"
        }
        if column_name in protected_columns:
            print("Cannot delete an ID column.")
            return
        print("\nColumn Selected for Deletion")
        print(f"Table: {table_name}")
        print(f"Column: {column_name}")
        print("All values stored in this column will be deleted.")

        confirmation = get_cleanup_input(
            "\nConfirm column deletion? (y/n, 0=menu, q=exit): "
        )
        if confirmation is None or confirmation.lower() != "y":
            print("Deletion cancelled. No changes made.")
            return
        try:
            # SQLite requires column names in SQL rather than parameters.
            # Names are validated against the table schema above.
            conn.execute(
                f'ALTER TABLE "{table_name}" '
                f'DROP COLUMN "{column_name}"'
            )
            conn.commit()
            print(f"\nColumn '{column_name}' deleted successfully.")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"Database error: {error}")
            print("No changes were saved.")

# Correct verified product characteristics without deleting records.
def edit_product_characteristics():
    fields = {
        "1": ("size_oz", "float"),
        "2": ("packaging_material", "choice"),
        "3": ("shade_count", "integer"),
        "4": ("undertone_count", "integer"),
        "5": ("finish_type", "choice"),
        "6": ("coverage_level", "choice"),
        "7": ("non_comedogenic", "boolean"),
        "8": ("skincare_benefits", "boolean"),
        "9": ("spf_present", "boolean"),
        "10": ("wear_claim_hours", "integer")
    }
    choices = {
        "packaging_material": {"glass", "plastic"},
        "finish_type": {
            "matte", "natural", "satin", "radiant", "dewy"
        },
        "coverage_level": {
            "light", "light_to_medium", "medium",
            "medium_to_full", "full"
        }
    }
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        # Display products to identify the record.
        products = pd.read_sql_query("""
            SELECT product_id, brand, product_name, size_oz
            FROM products
            ORDER BY product_id
        """, conn)
        if products.empty:
            print("No products found.")
            return

        print("\nSaved Products")
        print(products.to_string(index=False))
        print("\nEnter 0 to return to menu or q to exit.")

        value = get_cleanup_input("\nProduct ID to edit: ")
        if value is None:
            return
        try:
            product_id = int(value)
        except ValueError:
            print("Invalid product ID.")
            return
        product = conn.execute(
            "SELECT * FROM products WHERE product_id = ?",
            (product_id,)
        ).fetchone()
        if product is None:
            print("Product ID not found.")
            return

        print(f"\nEditing Product ID: {product_id}")
        print(f"Brand: {product['brand']}")
        print(f"Product: {product['product_name']}")

        # Display current product characteristics.
        print("\nCurrent Product Characteristics")

        for number, (field, data_type) in fields.items():
            current = product[field]
            display = "Unknown" if current is None else current
            print(f"{number}. {field}: {display}")

        print("0. Return to menu")
        print("q. Exit program")
        selection = get_cleanup_input(
            "\nChoose a characteristic to edit: "
        )
        if selection is None:
            return
        if selection not in fields:
            print("Invalid characteristic selection.")
            return
        field, data_type = fields[selection]
        old_value = product[field]

        # Display controlled categorical options.
        if field in choices:
            print("\nAllowed values:")
            print(", ".join(sorted(choices[field])))

        elif data_type == "boolean":
            print("\nAllowed values: yes, no, 1, 0")

        print("\nEnter NULL if the value is unknown.")
        print("Enter 'back' to cancel or q to exit.")

        entered = input(
            f"\nNew value for {field}: "
        ).strip()
        if entered.lower() == "q":
            raise SystemExit(0)
        if entered.lower() == "back":
            print("Edit cancelled.")
            return

        # Validate the corrected value.
        try:
            if entered.lower() in ("null", "unknown"):
                new_value = None
            elif data_type == "boolean":
                values = {
                    "yes": 1,
                    "y": 1,
                    "1": 1,
                    "no": 0,
                    "n": 0,
                    "0": 0
                }
                if entered.lower() not in values:
                    raise ValueError("Enter yes, no, 1, or 0.")
                new_value = values[entered.lower()]
            elif data_type == "choice":
                new_value = entered.lower()
                if new_value not in choices[field]:
                    raise ValueError("Invalid category.")
            elif data_type == "integer":
                new_value = int(entered)
                if new_value < 0:
                    raise ValueError("Value cannot be negative.")
                if field == "undertone_count" and new_value > 3:
                    raise ValueError(
                        "Undertone count must be between 0 and 3."
                    )
                if field == "shade_count" and new_value == 0:
                    raise ValueError(
                        "Shade count must be positive."
                    )
                if field == "wear_claim_hours" and new_value == 0:
                    raise ValueError(
                        "Wear duration must be positive."
                    )
            elif data_type == "float":
                new_value = float(entered)

                if not 0 < new_value < float("inf"):
                    raise ValueError(
                        "Size must be a positive finite number."
                    )
        except ValueError as error:
            print(f"Invalid value: {error}")
            print("No changes made.")
            return

        # Show the proposed correction.
        print("\nConfirm Product Correction")
        print(f"Product ID: {product_id}")
        print(f"Characteristic: {field}")
        print(f"Previous value: {old_value}")
        print(f"New value: {new_value}")

        confirmation = get_cleanup_input(
            "\nSave this correction? (y/n, 0=menu, q=exit): "
        )
        if confirmation is None or confirmation.lower() != "y":
            print("Edit cancelled. No changes made.")
            return
        # Update only the selected characteristic.
        try:
            conn.execute(
                f'UPDATE products SET "{field}" = ? '
                'WHERE product_id = ?',
                (new_value, product_id)
            )
            conn.commit()
            print("\nProduct characteristic updated successfully.")
        except sqlite3.Error as error:
            conn.rollback()
            print(f"Database error: {error}")
            print("No changes were saved.")


# Interactive menu for database analysis and cleanup.
def cleaning_menu():
    while True:
        print("\n" + "=" * 50)
        print("FOUNDATION DATABASE ANALYSIS & CLEANUP")
        print("=" * 50)

        print("1. Analyze database")
        print("2. Edit product characteristics")
        print("3. Delete product")
        print("4. Delete observation")
        print("5. Delete column")
        print("6. Exit")

        choice = input(
            "\nChoose an option (1-6, q=exit): "
        ).strip().lower()

        if choice == "1":
            main()
        elif choice == "2":
            edit_product_characteristics()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            delete_observation()
        elif choice == "5":
            delete_column()
        elif choice in ("6", "q"):
            print("Exiting database cleanup.")
            break
        else:
            print("Invalid option. Choose 1-6 or q.")


# Identify missing fields for each product and observation.
def report_missing_records(products, observations):
    print("\n" + "=" * 58)
    print("MISSING DATA BY RECORD")
    print("=" * 58)

    # Product fields that should be checked for missing values.
    product_fields = [
        "size_oz",
        "packaging_material",
        "shade_count",
        "undertone_count",
        "finish_type",
        "coverage_level",
        "non_comedogenic",
        "skincare_benefits",
        "spf_present",
        "wear_claim_hours"
    ]
    print("\nPRODUCTS REQUIRING REVIEW")
    product_count = 0
    for _, product in products.iterrows():
        missing = []
        for field in product_fields:
            if field not in products.columns:
                continue
            value = product[field]
            if pd.isna(value) or (
                isinstance(value, str)
                and value.strip().lower() in ("", "unknown", "n/a")
            ):
                missing.append(field)
        if missing:
            product_count += 1
            print(
                f"\nProduct ID {product['product_id']} — "
                f"{product['brand']}: {product['product_name']}"
            )
            print(f"  Missing: {', '.join(missing)}")
    if product_count == 0:
        print("No missing product characteristics found.")
    else:
        print(f"\nProducts requiring review: {product_count}")

    # Observation fields relevant to Ulta and Sephora.
    observation_fields = [
        "price_usd",
        "bestseller_list",
        "review_count",
        "source_url",
        "collection_date"
    ]
    print("\nOBSERVATIONS REQUIRING REVIEW")
    observation_count = 0
    for _, observation in observations.iterrows():
        missing = []
        for field in observation_fields:
            if field not in observations.columns:
                continue
            value = observation[field]
            if pd.isna(value) or (
                isinstance(value, str)
                and value.strip().lower() in ("", "unknown", "n/a")
            ):
                missing.append(field)
        if missing:
            observation_count += 1
            print(
                f"\nObservation ID {observation['observation_id']} "
                f"— Product ID {observation['product_id']} "
                f"({observation['source']})"
            )
            print(f"  Missing: {', '.join(missing)}")
    if observation_count == 0:
        print("No missing observation fields found.")
    else:
        print(f"\nObservations requiring review: {observation_count}")

def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return
    # Read-only SQLite connection; no INSERT, UPDATE, DELETE or commits.
    with sqlite3.connect(DB_PATH.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        products = pd.read_sql_query("SELECT * FROM products", conn)
        observations = pd.read_sql_query("SELECT * FROM product_observations", conn)

    print("FOUNDATION DATA QUALITY AUDIT *READ ONLY*")
    audit_table(products, "products")
    audit_table(observations, "product_observations")
    audit_relationships(products, observations)
    # Identify exactly which records contain missing values.
    report_missing_records(products, observations)
    print("\nAudit complete. No database values were changed.")

if __name__ == "__main__":
    cleaning_menu()