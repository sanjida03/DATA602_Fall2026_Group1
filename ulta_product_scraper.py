
"""
Filename: ulta_product_scraper.py
Author: Travisha Mills
Date: 2026-10-16
Project: Foundation Characteristics & Consumer Demand
Description: Extracts foundation product characteristics and consumer demand
data from Ulta product pages for the foundation collection application.

Dependencies:
    - requests
    - beautifulsoup4
    - ulta_bestsellers.py
"""

import json
import re
import requests

from bs4 import BeautifulSoup
from ulta_bestsellers import bestseller_status

# Normalize retailer shade descriptions into warm, cool, or neutral.
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

# Convert stored 0/1/NULL values to readable Yes/No/Unknown labels.
def format_yes_no(value):
    if value is None:
        return "Unknown"
    return "Yes" if value == 1 else "No"

# Extract product characteristics and consumer demand data from Ulta.
def scrape_ulta(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Request and parse the product page.
    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Extract embedded product variant data.
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

    # Locate embedded shade descriptions.
    shade_data_script = None
    for script in soup.find_all("script"):
        script_text = script.get_text()
        if '"shadeDescription"' in script_text:
            shade_data_script = script_text
            break

    # Count distinct normalized undertones.
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

    # Locate the main product information section.
    product_info = soup.find(
        "div",
        class_="ProductInformation"
    )

    # Extract brand and product name.
    brand_tag = product_info.find(
        "div",
        class_="pal-c-Link__label"
    )

    brand = brand_tag.get_text(strip=True)

    product_name_tag = product_info.find(
        "span",
        class_="Text-ds--title-5"
    )
    product_name = product_name_tag.get_text(strip=True)

    # Extract current product price.
    price_tag = soup.find(
        "div",
        class_="Price"
    )
    price_text = price_tag.get_text(strip=True)
    price_usd = float(
        price_text.replace("$", "").replace(",", "")
    )

    # Extract the number of customer reviews.
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

    # Check whether the foundation appears on Ulta's bestseller list.
    bestseller_list = bestseller_status(brand, product_name)

    # Extract product size in ounces.
    product_dimension = soup.find(
        "div",
        class_="ProductDimension"
    )
    size_text = product_dimension.find_all("span")[1].get_text(strip=True)
    size_oz = float(
        size_text.lower().replace("oz", "").strip()
    )

    # Count available product shades.
    shade_count = len(variants)

    # Extract finish and coverage using controlled categories.
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

    coverage_level = None
    # Check range categories before individual coverage levels.
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

    # Extract the stated wear duration.
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

    # Detect an explicit SPF claim.
    spf_present = 0
    spf_text = (
        f"{product_name} "
        f"{product_summary.get_text(' ', strip=True) if product_summary else ''}"
    )
    if re.search(
        r"\bSPF\s*[-:]?\s*\d+\b|\bsun protection factor\s*\d+\b",
        spf_text,
        flags=re.IGNORECASE
    ):
        spf_present = 1

    # Detect explicit non-comedogenic claims.
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

    # Detect skincare benefit claims from the Key Ingredients section.
    skincare_benefits = None
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
        # Match ingredient descriptions containing skincare benefits.
        ingredient_matches = re.findall(
            r"(?:^|\.\s+)([^:.]{2,100}):\s*(.*?)(?=\.\s+[^:.]{2,100}:|$)",
            ingredients_text,
            flags=re.DOTALL
        )
        for ingredient, benefit in ingredient_matches:
            benefit_text = benefit.lower()
            if any(term in benefit_text for term in skincare_terms):
                skincare_benefits = 1
                break

    # Return values for database insertion.
    return {
        "brand": brand,
        "product_name": product_name,
        "size_oz": size_oz,
        "shade_count": shade_count,
        "undertone_count": undertone_count,
        "finish_type": finish_type,
        "coverage_level": coverage_level,
        "wear_claim_hours": wear_claim_hours,
        "non_comedogenic": non_comedogenic,
        "skincare_benefits": skincare_benefits,
        "spf_present": spf_present,
        "price_usd": price_usd,
        "review_count": review_count,
        "bestseller_list": bestseller_list
    }