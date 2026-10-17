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

Input:
    - Ulta product page URL entered by the user.

Output:
    - Brand
    - Product name
    - Size in ounces
    - Shade count
    - Undertone count
    - Finish type
    - Coverage level
    - Wear claim hours
    - SPF presence
    - Non-comedogenic status
    - Skincare benefits
    - Price
    - Review count
"""
import json
import requests
from bs4 import BeautifulSoup
import re

# Request Configuration
# Defining the HTTP request headers.
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# User Input
# Collecting the Ulta product URL.
url = input("Enter Ulta product URL: ").strip()

# Page Request
# Downloading the product page HTML & confirming that the request was successful.
response = requests.get(
    url,
    headers=HEADERS,
    timeout=10
)
response.raise_for_status()
response.encoding = "utf-8"

# HTML Parsing
# Converting the downloaded HTML into a BeautifulSoup object for searching.
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

variants = product_json.get("hasVariant", [])

# Embedded Shade Data
# Locating the script block containing shade descriptions.
shade_data_script = None

for script in soup.find_all("script"):
    script_text = script.get_text()

    if '"shadeDescription"' in script_text:
        shade_data_script = script_text
        break

print("\n--- Shade Data Script Test ---")
print("Shade data script found:", shade_data_script is not None)

# Undertone Count
# Extracting unique undertone categories from embedded shade descriptions.
undertones = set()

if shade_data_script:
    script_text = shade_data_script.lower()

    if "cool" in script_text:
        undertones.add("cool")

    if "neutral" in script_text:
        undertones.add("neutral")

    if "warm" in script_text:
        undertones.add("warm")

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
# Extracting the number of product reviews.
review_link = soup.find(
    "a",
    href="#reviews"
)
review_text = review_link.get_text(strip=True)
review_count = int(
    review_text.replace("Reviews", "").replace(",", "").strip()
)

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
spf_present = None
if "spf" in page_text or "sun protection factor" in page_text:
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
# Recording whether the product explicitly includes skincare ingredients or benefits.
skincare_benefits = None

skincare_terms = [
    "niacinamide",
    "vitamin c",
    "vitamin e",
    "hyaluronic acid",
    "retinol",
    "peptide",
    "ceramide",
    "squalane",
    "salicylic acid",
    "hydrating",
    "moisturizing",
    "skincare benefits"
]
for term in skincare_terms:
    if term in page_text:
        skincare_benefits = 1
        break

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
print("Size oz:", size_oz)
print("Finish type:", finish_type)
print("Coverage level:", coverage_level)
print("Wear claim hours:", wear_claim_hours)
print("SPF present:", spf_present)
print("Non-comedogenic:", non_comedogenic)
print("Skincare benefits:", skincare_benefits)

# Request Validation Output
# Displays technical request information.
print("\n--- Request Information ---")
print("Status code:", response.status_code)
print("HTML length:", len(response.text))