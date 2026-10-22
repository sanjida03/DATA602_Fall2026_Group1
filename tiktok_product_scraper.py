"""
Filename: tiktok_product_scraper.py
Author: Travisha Mills
Date: 2026-10-22
Project: Foundation Characteristics & Consumer Demand
Description:
    Collects foundation product data from TikTok Shop using
    a user-provided product URL. Extracts brand, product name,
    size (oz), price (USD), review count, and units sold.
"""

import requests
from urllib.parse import urlparse

# Request and validate the product URL.
while True:
    URL = input("Enter TikTok Shop product URL: ").strip()
    parsed_url = urlparse(URL)
    if (
        parsed_url.scheme == "https"
        and parsed_url.hostname == "shop.tiktok.com"
        and parsed_url.path.startswith("/us/pdp/")
    ):
        break
    print("Invalid URL. Please enter a valid TikTok Shop product URL.")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Request the product page.
try:
    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=15
    )

    print("\n--- TIKTOK SHOP ACCESS TEST ---")
    print("Status code:", response.status_code)
    print("HTML length:", len(response.content))
    print("Final URL:", response.url)

    # Check whether the request succeeded.
    if response.status_code == 200:
        print("Access successful. HTML inspection required.")
    else:
        print("Page access was not successful.")

except requests.RequestException as error:
    print("Request failed:", error)


# Product Data Diagnostic
# Check whether the downloaded HTML contains our required fields.

from bs4 import BeautifulSoup
import re

soup = BeautifulSoup(response.text, "html.parser")


import re
from bs4 import BeautifulSoup

# HTML Parsing
soup = BeautifulSoup(response.text, "html.parser")


def parse_count(value):
    """Convert abbreviated counts into integers."""
    value = value.strip().replace(",", "").upper()

    match = re.search(r"([\d.]+)\s*([KMB]?)", value)
    if not match:
        return None

    number = float(match.group(1))
    multiplier = {
        "": 1,
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000
    }

    return int(number * multiplier[match.group(2)])


# Product Name
name_tag = soup.find("h1")
product_name = name_tag.get_text(" ", strip=True) if name_tag else None

# Product Details
details = {}

for row in soup.select("table tr"):
    cells = row.find_all("td")
    if len(cells) == 2:
        key = cells[0].get_text(" ", strip=True).lower()
        value = cells[1].get_text(" ", strip=True)
        details[key] = value

# Brand
brand = details.get("brand")

# Product Size
size_oz = None
volume = details.get("volume")

if volume:
    match = re.search(r"([\d.]+)\s*ml\b", volume, re.I)
    if match:
        size_oz = round(float(match.group(1)) / 29.5735, 2)

# Price
price_usd = None
price_section = soup.find("h1")

if price_section:
    price_container = price_section.find_next(
        "span", class_="Headline-Semibold"
    )
    if price_container:
        parent = price_container.parent
        price_text = parent.get_text("", strip=True)
        match = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", price_text)
        if match:
            price_usd = float(match.group(1).replace(",", ""))

# Review Count
review_count = None

review_tag = soup.find(
    string=re.compile(r"[\d,]+\s+global reviews", re.I)
)

if review_tag:
    match = re.search(r"([\d,]+)\s+global reviews", str(review_tag), re.I)
    if match:
        review_count = int(match.group(1).replace(",", ""))

# Units Sold
tiktok_units_sold = None

sold_tag = soup.find(
    string=re.compile(r"[\d,.]+[KMB]?\s+sold\b", re.I)
)

if sold_tag:
    match = re.search(r"([\d,.]+[KMB]?)\s+sold\b", str(sold_tag), re.I)
    if match:
        tiktok_units_sold = parse_count(match.group(1))


# Output
print("\n--- TikTok Shop Product Data ---")
print("Brand:", brand)
print("Product name:", product_name)
print("Size (oz):", size_oz)
print("Price (USD):", price_usd)
print("Review count:", review_count)
print("TikTok units sold:", tiktok_units_sold)