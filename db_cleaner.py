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
    "source": {"ulta", "sephora", "tiktok_shop", "brand_site"},
}
BOOLEAN_COLUMNS = {
    "products": ["non_comedogenic", "skincare_benefits", "spf_present"],
    "product_observations": ["bestseller_list"],
}
NUMERIC_COLUMNS = {
    "products": ["size_oz", "shade_count", "undertone_count", "wear_claim_hours"],
    "product_observations": ["price_usd", "tiktok_units_sold", "review_count"],
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
    indicators = ["price_usd", "tiktok_units_sold", "bestseller_list", "review_count"]
    if not observations.empty:
        print((observations.groupby("source")[indicators].apply(lambda group: group.isna().mean() * 100)).round(1).to_string())
    print("Note: TikTok sales data is only available from TikTok Shop, and bestseller status is only collected from Ulta and Sephora. Missing values from unsupported sources are expected, not scraping failures.")

    # Check TikTok sales coverage by unique product instead of retailer.
    print("\n" + "=" * 58)
    print("PRODUCT-LEVEL TIKTOK SALES COVERAGE")
    print("=" * 58)
    # Find TikTok observations with recorded units sold.
    tiktok_observations = observations[
        (observations["source"] == "tiktok_shop")
        & (observations["tiktok_units_sold"].notna())
    ]
    # Identify products that already have TikTok sales data.
    products_with_sales = tiktok_observations["product_id"].unique()
    # Find products still missing TikTok units sold.
    missing_tiktok = products[
        ~products["product_id"].isin(products_with_sales)
    ]
    total_products = len(products)
    products_missing = len(missing_tiktok)
    products_collected = total_products - products_missing
    print(f"Total unique products: {total_products}")
    print(f"Products with TikTok sales: {products_collected}")
    print(f"Products missing TikTok sales: {products_missing}")
    if total_products > 0:
        coverage = products_collected / total_products * 100
        print(f"TikTok sales coverage: {coverage:.1f}%")
    print("\nProducts requiring TikTok sales collection:")
    if missing_tiktok.empty:
        print("All products have recorded TikTok sales.")
    else:
        print(
            missing_tiktok[
                ["product_id", "brand", "product_name"]
            ].to_string(index=False)
        )


# Merge duplicate products while preserving their observations.
def remove_duplicate_product():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        print("\nRemove Duplicate Product")

        # Display saved products for selection.
        products = pd.read_sql_query("""
            SELECT product_id, brand, product_name, size_oz
            FROM products
            ORDER BY product_id
        """, conn)

        if products.empty:
            print("No products found.")
            return
        print(products.to_string(index=False))

        # Select the original product and duplicate.
        try:
            keep_id = int(input("\nProduct ID to keep: "))
            delete_id = int(input("Duplicate Product ID to remove: "))
        except ValueError:
            print("Invalid product ID.")
            return
        if keep_id == delete_id:
            print("Product IDs must be different.")
            return

        # Verify both product IDs exist.
        selected = products[
            products["product_id"].isin([keep_id, delete_id])
        ]
        if len(selected) != 2:
            print("One or both product IDs do not exist.")
            return

        # Require matching normalized brands and names.
        original = selected[selected["product_id"] == keep_id].iloc[0]
        duplicate = selected[selected["product_id"] == delete_id].iloc[0]

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


# Interactive menu for database analysis and cleanup.
def cleaning_menu():
    while True:
        print("\n" + "=" * 50)
        print("FOUNDATION DATA ANALYSIS & CLEANUP")
        print("=" * 50)

        print("1. Analyze database")
        print("2. Remove duplicate product")
        print("3. Exit")

        choice = input("\nChoose an option (1-3): ").strip()

        if choice == "1":
            main()
        elif choice == "2":
            remove_duplicate_product()
        elif choice == "3":
            print("Exiting database cleanup.")
            break
        else:
            print("Invalid option. Choose 1, 2, or 3.")


def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return
    # Read-only SQLite connection; no INSERT, UPDATE, DELETE or commits.
    with sqlite3.connect(DB_PATH.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        products = pd.read_sql_query("SELECT * FROM products", conn)
        observations = pd.read_sql_query("SELECT * FROM product_observations", conn)

    print("FOUNDATION DATA QUALITY AUDIT — READ ONLY")
    audit_table(products, "products")
    audit_table(observations, "product_observations")
    audit_relationships(products, observations)
    print("\nAudit complete. No database values were changed.")


if __name__ == "__main__":
    cleaning_menu()