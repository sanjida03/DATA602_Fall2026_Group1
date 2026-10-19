import json
import requests
from bs4 import BeautifulSoup
import re


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
# Extracting structured foundation variant data from Sephora's JSON-LD.
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
# Counting unique shade/color names from product variants.
shades = set()
for variant in variants:
    color = variant.get("color")
    if color:
        shades.add(color.strip())
shade_count = len(shades)

# Price
price_usd = None
if variants:
    offers = variants[0].get("offers", {})
    price = offers.get("price")
    if price is not None:
        price_usd = float(price)

# Page Test
print("\n--- PAGE TEST ---")
print("Status:", response.status_code)
print("HTML length:", len(response.text))
print("Title:", soup.title)

print("\n--- Product Information ---")
print("Brand:", brand)
print("Product name:", product_name)
print("Shade count:", shade_count)
print("Price USD:", price_usd)