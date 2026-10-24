
"""
Filename: sephora_product_scraper.py
Author: Travisha Mills
Date: 2026-10-22
Project: Foundation Characteristics & Consumer Demand
Description: Extracts foundation product characteristics and consumer demand
data from Sephora product pages for the foundation collection application.
Dependencies:
    - requests
    - beautifulsoup4
    - sephora_bestsellers.py
"""

import json
import re
import requests

from bs4 import BeautifulSoup
from sephora_bestsellers import bestseller_status


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


# Extract product characteristics and consumer demand data from Sephora.
def scrape_sephora(url):
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

    # Extract brand and product name from structured data.
    brand_data = product_json.get("brand", {})
    brand = brand_data.get("name")
    product_name = product_json.get("name")

    # Count unique foundation shade names.
    shade_list = []
    for variant in variants:
        color = variant.get("color")
        if color:
            shade_list.append(color.strip())
    unique_shades = set(shade_list)
    shade_count = len(unique_shades)

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

    # Extract customer review count from JSON-LD.
    review_count = None
    rating_data = product_json.get("aggregateRating", {})
    if rating_data:
        review_count_value = rating_data.get("reviewCount")
        if review_count_value is not None:
            review_count = int(review_count_value)

    # Check whether the foundation appears on Sephora's bestseller list.
    product_id_match = re.search(r"P\d+", url)
    product_id = product_id_match.group() if product_id_match else None

    bestseller_list = bestseller_status(product_id)

    # Extract and normalize undertones from shade labels.
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

    # Extract labeled product characteristics from the page.
    page_text = soup.get_text(" ", strip=True)

    # Extract the foundation size in ounces.
    size_oz = None
    size_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:fl\.?\s*oz|oz)\b",
        page_text,
        flags=re.IGNORECASE
    )
    if size_match:
        size_oz = float(size_match.group(1))

    # Extract finish using the database's controlled categories.
    finish_type = None
    finish_match = re.search(
        r"\bFinish:\s*(Matte|Natural|Satin|Radiant|Dewy|Luminous)",
        page_text,
        flags=re.IGNORECASE
    )
    if finish_match:
        extracted_finish = finish_match.group(1).lower()
        if extracted_finish != "luminous":
            finish_type = extracted_finish

    # Extract coverage, preserving range categories.
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

    # Extract the stated wear duration.
    wear_claim_hours = None
    wear_match = re.search(
        r"\b(?:up to\s+)?(\d+)\s*[- ]?\s*hour\s*(?:wear|longwear)?\b",
        page_text,
        flags=re.IGNORECASE
    )
    if wear_match:
        wear_claim_hours = int(wear_match.group(1))

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
        if term in page_text.lower():
            non_comedogenic = 1
            break

    # Detect explicit SPF claims in the product description.
    spf_present = 0
    description_match = re.search(
        r"\bWhat it is:\s*(.*?)(?=\s*Coverage:|\s*Finish:|\s*Formulation:)",
        page_text,
        flags=re.IGNORECASE | re.DOTALL
    )
    # Use the structured product description as a fallback.
    description_text = (
        description_match.group(1)
        if description_match
        else product_json.get("description", "")
    )
    spf_text = f"{product_name} {description_text}"
    if re.search(
        r"\bSPF\s*[-:]?\s*\d+\b|\bsun protection factor\s*\d+\b",
        spf_text,
        flags=re.IGNORECASE
    ):
        spf_present = 1

    # Detect skincare benefits from highlighted ingredients.
    skincare_benefits = None
    ingredients_match = re.search(
        r"Highlighted Ingredients:\s*(.*?)\s*Ingredient Callouts:",
        page_text,
        flags=re.IGNORECASE | re.DOTALL
    )
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
        # Search ingredient descriptions for skincare benefit claims.
        ingredient_matches = re.findall(
            r"-\s*([^:]+):\s*(.*?)(?=\s+-\s+[^:]+:|$)",
            ingredients_text,
            flags=re.DOTALL
        )
        for ingredient, benefit in ingredient_matches:
            benefit_text = benefit.lower()
            if any(term in benefit_text for term in skincare_terms):
                skincare_benefits = 1
                break

    # Fallback: Check Sephora product highlights for missing claims.
    
    # Locate the product highlights using their text labels.
    highlights = []

    for section in soup.select('div[data-comp^="BaseComponent"]'):
        labels = [
            span.get_text(" ", strip=True).lower()
            for span in section.find_all("span", recursive=False)
        ]

        # Product highlights contain multiple short characteristic labels.
        if len(labels) >= 2 and any(
            "coverage" in label or
            "finish" in label or
            "spf" == label or
            "hydrating" == label or
            label.startswith("good for:")
            for label in labels
        ):
            highlights = labels
            break

    # Skincare benefits: Accept explicit skin-benefit highlights.
    if skincare_benefits is None or skincare_benefits == 0:
        skincare_highlights = {
            "hydrating",
            "moisturizing",
            "good for: uneven texture",
            "good for: dryness",
            "good for: pores",
            "good for: dullness",
            "good for: redness",
            "good for: dark spots",
            "good for: fine lines"
        }

        if any(
            highlight in skincare_highlights
            for highlight in highlights
        ):
            skincare_benefits = 1

    # SPF: Accept a dedicated SPF highlight.
    if spf_present is None or spf_present == 0:
        if any(
            highlight == "spf" or
            re.fullmatch(r"spf\s*\d+", highlight)
            for highlight in highlights
        ):
            spf_present = 1

    # Non-comedogenic: Require an explicit claim.
    if non_comedogenic is None or non_comedogenic == 0:
        non_comedogenic_highlights = {
            "non-comedogenic",
            "noncomedogenic",
            "won't clog pores",
            "non-pore-clogging"
        }

        if any(
            highlight in non_comedogenic_highlights
            for highlight in highlights
        ):
            non_comedogenic = 1

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