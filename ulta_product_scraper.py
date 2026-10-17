"""
Filename: ulta_product_scraper.py
Author: Travisha Mills
Date: 2026-10-16
Project: Foundation Characteristics & Consumer Demand
Description:
    Web scraping script used to collect selected foundation product
    characteristics from Ulta product pages.

Main responsibilities:
    - Accept an Ulta product URL from the user.
    - Request and download the product page HTML.
    - Parse the HTML using BeautifulSoup.
    - Extract the product brand.
    - Extract the product name.
    - Count available product shades.
    - Display the extracted product information.
    - Display request status information for validation.

Dependencies:
    - Python 3.14.6 or later
    - requests
    - beautifulsoup4

Input:
    - Ulta product page URL entered by the user.

Current output:
    - Brand
    - Product name
    - Shade count
    - HTTP status code
    - HTML length
"""
import json
import requests
from bs4 import BeautifulSoup

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

# Shade Count
# Counting product variants from the embedded JSON data.
shade_count = len(variants)

# Product Information Output
# Displays the extracted foundation characteristics.
print("\n--- Product Information ---")
print("Brand:", brand)
print("Product name:", product_name)
print("Shade count:", shade_count)
print("Undertones:", sorted(undertones))
print("Undertone count:", undertone_count)

# Request Validation Output
# Displays technical request information.
print("\n--- Request Information ---")
print("Status code:", response.status_code)
print("HTML length:", len(response.text))