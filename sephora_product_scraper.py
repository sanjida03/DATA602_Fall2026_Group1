"""
Filename: sephora_product_scraper.py
Author: Travisha Mills
Date: 2026-10-22
Project: Foundation Characteristics & Consumer Demand
Description:
    Web scraping script used to collect foundation product
    characteristics and consumer demand information from Sephora
    product pages.
Main responsibilities:
    - Accept a Sephora product URL from the user.
    - Request and download the product page HTML.
    - Parse the page using BeautifulSoup.
    - Extract product data from embedded JSON-LD and HTML.
    - Extract the product brand and product name.
    - Extract product size and price.
    - Count unique available foundation shades.
    - Identify and standardize undertones into warm, cool, and neutral.
    - Extract finish type and coverage level.
    - Extract stated wear duration.
    - Identify explicit SPF claims.
    - Identify explicit non-comedogenic claims.
    - Extract highlighted skincare ingredients and benefit claims.
    - Display boolean characteristics as Yes/No.
    - Display the collected product information.
Dependencies:
    - Python 3.14.6 or later
    - requests
    - beautifulsoup4
"""

import json
import requests
from bs4 import BeautifulSoup
import re
from sephora_bestsellers import bestseller_status

# Undertone Normalization
# Standardize retailer shade descriptions into three categories.
def normalize_undertone(description):
    description = description.lower()
    # Prioritize explicitly stated primary undertones.
    primary = re.search(
        r"\b(warm|cool|neutral)\b",
        description
    )
    if primary:
        return primary.group(1)
    # Map alternative descriptions to standard categories.
    undertone_mapping = {
        "warm": ["golden", "yellow", "peach", "peachy"],
        "cool": ["rosy", "pink", "red", "blue"],
        "neutral": ["balanced", "olive"]
    }
    for category, keywords in undertone_mapping.items():
        for keyword in keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", description):
                return category
    return None

# Convert stored values to Yes/No output.
def format_yes_no(value):
    if value is None:
        return "Unknown"
    return "Yes" if value == 1 else "No"

# Request Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# User Input
url = input("Enter Sephora product URL: ").strip()

# Page Request
response = requests.get(
    url,
    headers=HEADERS,
    timeout=10
)
response.raise_for_status()
response.encoding = "utf-8"

# HTML Parsing
soup = BeautifulSoup(
    response.text,
    "html.parser"
)

# Embedded Product Data
# Extract structured foundation variant data from Sephora's JSON-LD.
product_json = None
script_tags = soup.find_all(
    "script",
    type="application/ld+json"
)
for script in script_tags:
    script_text = script.get_text(strip=True)
    try:
        data = json.loads(script_text)
        if (
            isinstance(data, dict)
            and data.get("@type") == "ProductGroup"
        ):
            product_json = data
            break
    except json.JSONDecodeError:
        continue
if product_json is None:
    raise ValueError("ProductGroup JSON-LD data was not found.")
variants = product_json.get("hasVariant", [])

# Brand
brand_data = product_json.get("brand", {})
brand = brand_data.get("name")

# Product Name
product_name = product_json.get("name")

# Shade Count
# Extract shade names from Sephora product variants.
shade_list = []
for variant in variants:
    color = variant.get("color")
    if color:
        shade_list.append(color.strip())
unique_shades = set(shade_list)
shade_count = len(unique_shades)

# Price
# Extract the product price from structured variant data.
price_usd = None
if variants:
    offers = variants[0].get("offers") or {}
    if isinstance(offers, dict):
        price = offers.get("price")
        if price is not None:
            try:
                price_usd = float(price)
            except (ValueError, TypeError):
                pass


# Review Count
# Extract the number of customer reviews from Sephora's JSON-LD.
review_count = None

rating_data = product_json.get("aggregateRating", {})
if rating_data:
    review_count_value = rating_data.get("reviewCount")
    if review_count_value is not None:
        review_count = int(review_count_value)

# Bestseller Classification
product_id_match = re.search(r"P\d+", url )
product_id = product_id_match.group() if product_id_match else None
bestseller_list = bestseller_status(product_id)


# Undertone Count
# Extract and normalize undertones from Sephora shade labels.
undertones = set()

swatch_buttons = soup.find_all(
    "button",
    attrs={"data-at": ["swatch", "selected_swatch"]}
)
for button in swatch_buttons:
    shade_label = button.get("aria-label", "").lower()
    match = re.search(
        r"\bwith\s+(.+?)\s+undertones?\b",
        shade_label
    )
    if match:
        category = normalize_undertone(match.group(1))
        if category:
            undertones.add(category)

undertone_count = len(undertones) if undertones else None


# Product Characteristics
# Extracting labeled coverage and finish values from Sephora.
page_text = soup.get_text(" ", strip=True)

# Product Size
# Extract the foundation size in ounces.
size_oz = None
size_match = re.search(
    r"\b(\d+(?:\.\d+)?)\s*(?:fl\.?\s*oz|oz)\b",
    page_text,
    flags=re.IGNORECASE
)
if size_match:
    size_oz = float(size_match.group(1))

# Finish Type
finish_type = None
finish_match = re.search(
    r"\bFinish:\s*(Matte|Natural|Satin|Radiant|Dewy|Luminous)",
    page_text,
    flags=re.IGNORECASE
)
if finish_match:
    finish_type = finish_match.group(1).lower()

# Coverage Level
coverage_level = None
coverage_match = re.search(
    r"\bCoverage:\s*(Light to Medium|Medium to Full|Light|Medium|Full)",
    page_text,
    flags=re.IGNORECASE
)
if coverage_match:
    coverage_level = (
        coverage_match.group(1)
        .lower()
        .replace(" to ", "_to_")
    )

# Wear Claim Hours
wear_claim_hours = None
wear_match = re.search(
    r"\b(?:up to\s+)?(\d+)\s*[- ]?\s*hour\s*(?:wear|longwear)?\b",
    page_text,
    flags=re.IGNORECASE
)
if wear_match:
    wear_claim_hours = int(wear_match.group(1))

# Non-Comedogenic
non_comedogenic = None
non_comedogenic_terms = [
    "non-comedogenic",
    "noncomedogenic",
    "non pore clogging",
    "non-pore-clogging",
    "won't clog pores",
    "will not clog pores"
]
for term in non_comedogenic_terms:
    if term in page_text.lower():
        non_comedogenic = 1
        break

# SPF Presence
# Detecting explicit SPF claims in product information.
spf_present = 0
# Extract the product-specific description.
description_match = re.search(
    r"\bWhat it is:\s*(.*?)(?=\s*Coverage:|\s*Finish:|\s*Formulation:)",
    page_text,
    flags=re.IGNORECASE | re.DOTALL
)
# Use the product's structured description as a fallback.
description_text = (
    description_match.group(1)
    if description_match
    else product_json.get("description", "")
)
# Combine product name and description.
spf_text = f"{product_name} {description_text}"
# Check for explicit SPF claims.
if re.search(
    r"\bSPF\s*[-:]?\s*\d+\b|\bsun protection factor\s*\d+\b",
    spf_text,
    flags=re.IGNORECASE
):
    spf_present = 1

# Skincare Benefits
# Extract highlighted ingredients and identifying skincare claims.
skincare_benefits = None
highlighted_ingredients = []
# Locate the highlighted ingredients section.
ingredients_match = re.search(
    r"Highlighted Ingredients:\s*(.*?)\s*Ingredient Callouts:",
    page_text,
    flags=re.IGNORECASE | re.DOTALL
)
# Terms associated with skincare benefits.
skincare_terms = [
    "hydrat",
    "moisturiz",
    "oil production",
    "skin barrier",
    "dark spots",
    "fine lines",
    "wrinkles",
    "acne",
    "skin texture"
]
if ingredients_match:
    ingredients_text = ingredients_match.group(1)
    # Extract highlighted ingredients and their benefit descriptions.
    ingredient_matches = re.findall(
        r"-\s*([^:]+):\s*(.*?)(?=\s+-\s+[^:]+:|$)",
        ingredients_text,
        flags=re.DOTALL
    )
    for ingredient, benefit in ingredient_matches:
        # Split combined ingredient names.
        names = re.split(
            r"\s+and\s+|,\s*",
            ingredient.strip()
        )
        for name in names:
            name = name.strip()
            if name and name not in highlighted_ingredients:
                highlighted_ingredients.append(name)

        # Check whether an explicit skincare benefit is claimed.
        benefit_text = benefit.lower()
        if any(term in benefit_text for term in skincare_terms):
            skincare_benefits = 1

# Bestseller Diagnostic
# Check product structured data for ranking information.

print("\n--- BESTSELLER TEST ---")

print("Product ID:", product_json.get("productGroupID"))

for key, value in product_json.items():
    if any(
        term in key.lower()
        for term in ["best", "rank", "sort", "position"]
    ):
        print(f"{key}: {value}")

print("\n--- Product Information ---")
print("Brand:", brand)
print("Product name:", product_name)
print("Shade count:", shade_count)
print("Price USD:", price_usd)
print("Review count:", review_count)
print("Bestseller list:", format_yes_no(bestseller_list))
print("Undertones:", sorted(undertones))
print("Undertone count:", undertone_count)
print("Size oz:", size_oz)
print("Finish type:", finish_type)
print("Coverage level:", coverage_level)
print("Wear claim hours:", wear_claim_hours)
print("Non-comedogenic:", format_yes_no(non_comedogenic))
print("SPF present:", format_yes_no(spf_present))
print("Skincare benefits:", format_yes_no(skincare_benefits))
print("Highlighted ingredients:", ", ".join(highlighted_ingredients) if highlighted_ingredients else "Unknown")