"""
Filename: tiktok_product_scraper.py
Author: Travisha Mills
Date: 2026-10-22
Project: Foundation Characteristics & Consumer Demand
Description: Extracts foundation product information and consumer demand
data from TikTok Shop product URLs for the foundation collection application.
Dependencies:
    - requests
    - beautifulsoup4
"""
import re
import requests

from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Convert abbreviated counts (K, M, B) into integers.
def parse_count(value):
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


# Extract product characteristics and demand data from TikTok Shop.
def scrape_tiktok(url):

    # Validate the TikTok Shop product URL.
    parsed_url = urlparse(url)

    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "shop.tiktok.com"
        or not parsed_url.path.startswith("/us/pdp/")
    ):
        raise ValueError("Invalid TikTok Shop product URL.")

    # Request and parse the product page.
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )
    response.raise_for_status()
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the product name.
    name_tag = soup.find("h1")
    product_name = (
        name_tag.get_text(" ", strip=True)
        if name_tag else None
    )

    # Extract structured product details.
    details = {}
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].get_text(" ", strip=True).lower()
            value = cells[1].get_text(" ", strip=True)
            details[key] = value

    # Extract the brand.
    brand = details.get("brand")

    # Convert product volume from milliliters to ounces.
    size_oz = None
    volume = details.get("volume")
    if volume:
        match = re.search(r"([\d.]+)\s*ml\b", volume, re.I)
        if match:
            size_oz = round(
                float(match.group(1)) / 29.5735, 2
            )

    # Extract the current product price.
    price_usd = None
    price_section = soup.find("h1")
    if price_section:
        price_container = price_section.find_next(
            "span", class_="Headline-Semibold"
        )
        if price_container:
            parent = price_container.parent
            price_text = parent.get_text("", strip=True)
            match = re.search(
                r"\$\s*([\d,]+(?:\.\d{2})?)",
                price_text
            )
            if match:
                price_usd = float(
                    match.group(1).replace(",", "")
                )

    # Extract the global review count.
    review_count = None
    review_tag = soup.find(
        string=re.compile(r"[\d,]+\s+global reviews", re.I)
    )
    if review_tag:
        match = re.search(
            r"([\d,]+)\s+global reviews",
            str(review_tag),
            re.I
        )
        if match:
            review_count = int(
                match.group(1).replace(",", "")
            )

    # Extract the reported number of units sold.
    tiktok_units_sold = None
    sold_tag = soup.find(
        string=re.compile(r"[\d,.]+[KMB]?\s+sold\b", re.I)
    )
    if sold_tag:
        match = re.search(
            r"([\d,.]+[KMB]?)\s+sold\b",
            str(sold_tag),
            re.I
        )
        if match:
            tiktok_units_sold = parse_count(match.group(1))

    # Return only fields collected from TikTok Shop.
    return {
        "brand": brand,
        "product_name": product_name,
        "size_oz": size_oz,
        "price_usd": price_usd,
        "review_count": review_count,
        "tiktok_units_sold": tiktok_units_sold
    }