"""
Filename: ulta_product_scraper.py
Author: Travisha Mills
Date: 2026-10-16
Project: Foundation Characteristics & Consumer Demand
Description:
    Web scraping script used to collect foundation product
    characteristics and consumer demand information from Ulta
    product pages.

Main responsibilities:
    - Accept an Ulta product URL from the user.
    - Request and download the product page HTML.
    - Parse the page using BeautifulSoup.
    - Extract the product brand and product name.
    - Extract product size and price.
    - Count available foundation shades.
    - Identify available undertone categories.
    - Extract finish type and coverage level.
    - Extract stated wear duration.
    - Identify explicit SPF claims.
    - Identify explicit non-comedogenic claims.
    - Identify skincare ingredients or benefit claims.
    - Extract the product review count.
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
from ulta_bestsellers import bestseller_status

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
url = input("Enter Ulta product URL: ").strip()

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
# Extracting structured foundation variant data from Ulta's JSON-LD script.
product_json = None
script_tags = soup.find_all(
    "script",
    type="application/ld+json"
)
for script in script_tags:
    script_text = script.get_text(strip=True)
    if '"ProductGroup"' in script_text:
        product_json = json.loads(script_text)
        break

if product_json is None:
    raise ValueError("ProductGroup JSON-LD data was not found.")
variants = product_json.get("hasVariant", [])

# Embedded Shade Data
# Locating the script block containing shade descriptions.
shade_data_script = None
for script in soup.find_all("script"):
    script_text = script.get_text()
    if '"shadeDescription"' in script_text:
        shade_data_script = script_text
        break

# Undertone Count
# Extract and normalize undertones from Ulta shade descriptions.
undertones = set()
shade_descriptions = re.findall(
    r'"shadeDescription"\s*:\s*"([^"]*)"',
    shade_data_script or "",
    flags=re.IGNORECASE
)
for description in shade_descriptions:
    category = normalize_undertone(description)
    if category:
        undertones.add(category)
undertone_count = len(undertones)

# Product Information Section
# Locating the main product information container.
product_info = soup.find(
    "div",
    class_="ProductInformation"
)

# Brand
# Extracting the foundation brand.
brand_tag = product_info.find(
    "div",
    class_="pal-c-Link__label"
)

brand = brand_tag.get_text(strip=True)

# Product Name
# Extracting the foundation product name.
product_name_tag = product_info.find(
    "span",
    class_="Text-ds--title-5"
)

product_name = product_name_tag.get_text(strip=True)

# Price
# Extracting the current product price.
price_tag = soup.find(
    "div",
    class_="Price"
)
price_text = price_tag.get_text(strip=True)

price_usd = float(
    price_text.replace("$", "").replace(",", "")
)

# Review Count
# Extract the number of customer reviews from Ulta.
review_count = None

review_link = soup.find("a", href="#reviews")
if review_link:
    review_text = review_link.get("aria-label", "")
    match = re.search(
        r"([\d,]+)\s+reviews?\b",
        review_text,
        flags=re.IGNORECASE
    )
    # Fall back to visible review text if needed.
    if not match:
        review_text = review_link.get_text(" ", strip=True)
        match = re.search(
            r"([\d,]+)\s+reviews?\b",
            review_text,
            flags=re.IGNORECASE
        )
    if match:
        review_count = int(match.group(1).replace(",", ""))

# Bestseller Classification
bestseller_list = bestseller_status(brand, product_name)

# Size
# Extracting the product size in ounces.
product_dimension = soup.find(
    "div",
    class_="ProductDimension"
)
size_text = product_dimension.find_all("span")[1].get_text(strip=True)
size_oz = float(
    size_text.lower().replace("oz", "").strip())

# Shade Count
# Counting product variants from the embedded JSON data.
shade_count = len(variants)

# Finish Type
# Extracting the product finish from the page text.
page_text = soup.get_text(" ", strip=True).lower()
finish_type = None
if "matte" in page_text:
    finish_type = "matte"
elif "natural finish" in page_text:
    finish_type = "natural"
elif "satin" in page_text:
    finish_type = "satin"
elif "radiant" in page_text:
    finish_type = "radiant"
elif "dewy" in page_text:
    finish_type = "dewy"

# Coverage Level
# Extracting and standardizing the product coverage level.
coverage_level = None
if "medium-to-full" in page_text or "medium to full" in page_text:
    coverage_level = "medium_to_full"
elif "light-to-medium" in page_text or "light to medium" in page_text:
    coverage_level = "light_to_medium"
elif "full coverage" in page_text:
    coverage_level = "full"
elif "medium coverage" in page_text:
    coverage_level = "medium"
elif "light coverage" in page_text:
    coverage_level = "light"

# Wear Claim Hours
# Extracting the stated wear duration from the product summary.
product_summary = soup.find(
    "div",
    class_="ProductSummary__summary"
)
wear_claim_hours = None
if product_summary:
    summary_text = product_summary.get_text(" ", strip=True).lower()
    wear_match = re.search(
        r"(\d+)\s*[- ]?hour",
        summary_text
    )
    if wear_match:
        wear_claim_hours = int(wear_match.group(1))

# SPF Present
# Recording SPF only when explicitly stated on the product page.
# SPF Presence
# Detect explicit SPF claims in product information.
spf_present = 0
spf_text = f"{product_name} {product_summary.get_text(' ', strip=True) if product_summary else ''}"
if re.search(
    r"\bSPF\s*[-:]?\s*\d+\b|\bsun protection factor\s*\d+\b",
    spf_text,
    flags=re.IGNORECASE
):
    spf_present = 1

# Non-Comedogenic
# Recording whether the product explicitly states that it is non-comedogenic.
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
    if term in page_text:
        non_comedogenic = 1
        break

# Skincare Benefits
# Extracting skincare ingredients from Ulta's Key Ingredients section.
highlighted_ingredients = []
skincare_benefits = None

# Locate product-specific key ingredients.
ingredients_match = re.search(
    r"\bKey Ingredients\s+(.*?)(?=\s+(?:How To Use|How to Use|Ingredients)\b)",
    page_text,
    flags=re.IGNORECASE | re.DOTALL
)
skincare_terms = [
    "hydrat",
    "moistur",
    "sebum",
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
    # Extract ingredient names and their associated descriptions.
    ingredient_matches = re.findall(
        r"(?:^|\.\s+)([^:.]{2,100}):\s*(.*?)(?=\.\s+[^:.]{2,100}:|$)",
        ingredients_text,
        flags=re.DOTALL
    )
    for ingredient, benefit in ingredient_matches:
        benefit_text = benefit.lower()
        if any(term in benefit_text for term in skincare_terms):
            names = re.split(
                r"\s+and\s+|,\s*",
                ingredient.strip(),
                flags=re.IGNORECASE
            )
            for name in names:
                name = name.strip()
                if name and name not in highlighted_ingredients:
                    highlighted_ingredients.append(name)
            skincare_benefits = 1


# Product Information Output
# Displays the extracted foundation characteristics.
print("\n--- Product Information ---")
print("Brand:", brand)
print("Product name:", product_name)
print("Shade count:", shade_count)
print("Undertones:", sorted(undertones))
print("Undertone count:", undertone_count)
print("Price USD:", price_usd)
print("Review count:", review_count)
print("Bestseller list:", format_yes_no(bestseller_list))
print("Size oz:", size_oz)
print("Finish type:", finish_type)
print("Coverage level:", coverage_level)
print("Wear claim hours:", wear_claim_hours)
print("Non-comedogenic:", format_yes_no(non_comedogenic))
print("SPF present:", format_yes_no(spf_present))
print("Skincare benefits:", format_yes_no(skincare_benefits))
print("Highlighted ingredients:",", ".join(highlighted_ingredients) if highlighted_ingredients else "Unknown")