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
        print("\nPossible duplicate products (review only):")
        found = 0
        records = df.to_dict("records")
        for i, a in enumerate(records):
            for b in records[i + 1:]:
                if pd.isna(a["brand"]) or pd.isna(b["brand"]):
                    continue
                if normalize_name(a["brand"]) != normalize_name(b["brand"]):
                    continue
                if pd.isna(a["size_oz"]) or pd.isna(b["size_oz"]):
                    continue
                if abs(float(a["size_oz"]) - float(b["size_oz"])) > 0.02:
                    continue
                score = SequenceMatcher(None, normalize_name(a["product_name"]), normalize_name(b["product_name"])).ratio()
                if score >= 0.60:
                    print(f"  IDs {a['product_id']} and {b['product_id']} | similarity {score:.0%}")
                    print(f"    {a['product_name']} / {b['product_name']}")
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
    print("Note: TikTok sales missing from Ulta/Sephora is expected, not a scraping failure.")

    print("\nRepeated source URLs (review only; repeat collection is allowed):")
    repeated = observations.loc[observations.duplicated(subset=["product_id", "source", "source_url"], keep=False)]
    if repeated.empty:
        print("  None.")
    else:
        print(repeated[["observation_id", "product_id", "source", "collection_date"]].to_string(index=False))

    bad_source = []
    for row in observations.itertuples(index=False):
        host = urlparse(str(row.source_url)).hostname or ""
        expected = {"ulta": "ulta.com", "sephora": "sephora.com", "tiktok_shop": "shop.tiktok.com"}.get(row.source)
        if expected and not (host == expected or (row.source != "tiktok_shop" and host.endswith("." + expected))):
            bad_source.append(row.observation_id)
    print(f"Source/URL hostname mismatches: {bad_source if bad_source else 'None'}")


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
    main()
