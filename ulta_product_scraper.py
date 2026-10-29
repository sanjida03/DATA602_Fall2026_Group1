
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

     # Missing variant data is unknown, not zero available shades.
    shade_count = len(variants) if variants else None
    
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
    
    # Preserve unknown when no recognized undertones were extracted.
    undertone_count = len(undertones) if undertones else None

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
    
    # Extract average customer rating from the review stars.
    avg_rating = None

    review_stars = soup.select_one("div.ReviewStars")
    if review_stars:
        rating_tag = review_stars.select_one(
            "div.ReviewStars__Content span"
        )
        if rating_tag:
            try:
                rating = float(rating_tag.get_text(strip=True))
                if 0 <= rating <= 5:
                    avg_rating = rating
            except ValueError:
                pass

    # Check whether the foundation appears on Ulta's bestseller list.
    bestseller_list = bestseller_status(brand, product_name)

    
    # Extract product size in ounces.
    size_oz = None
    product_dimension = soup.find(
        "div",
        class_="ProductDimension"
    )
    if product_dimension:
        size_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:fl\.?\s*)?oz\b",
            product_dimension.get_text(" ", strip=True),
            flags=re.IGNORECASE
        )
        if size_match:
            size_oz = float(size_match.group(1))
    # Fall back to product-specific structured data.
    if size_oz is None:
        size_text = product_json.get("size", "")
        if isinstance(size_text, str):
            size_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(?:fl\.?\s*)?oz\b",
                size_text,
                flags=re.IGNORECASE
            )
            if size_match:
                size_oz = float(size_match.group(1))


    # Extract finish and coverage using controlled categories.
    page_text = soup.get_text(" ", strip=True).lower()

        # Product-specific summary used for fallback extraction.
    product_summary = soup.select_one(
        "div.ProductSummary__summary"
    )
    summary_text = (
        product_summary.get_text(" ", strip=True).lower()
        if product_summary else ""
    )

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

# Fallback: Extract missing characteristics from the product summary.

    # Coverage: Recognize descriptions such as "medium, weightless coverage".
    if coverage_level is None and summary_text:
        if re.search(r"medium[- ]to[- ]full", summary_text):
            coverage_level = "medium_to_full"
        elif re.search(r"light[- ]to[- ]medium", summary_text):
            coverage_level = "light_to_medium"
        else:
            coverage_match = re.search(
                r"\b(light|medium|full)(?:,\s*\w+)?\s+coverage\b",
                summary_text
            )
            if coverage_match:
                coverage_level = coverage_match.group(1)
    # Finish: Use only an explicitly stated finish category.
    if finish_type is None and summary_text:
        finish_match = re.search(
            r"\b(matte|natural|satin|radiant|dewy)\s+finish\b",
            summary_text
        )
        if finish_match:
            finish_type = finish_match.group(1)
    # Non-comedogenic: Look for explicit product claims.
    if non_comedogenic is None and summary_text:
        if any(term in summary_text for term in non_comedogenic_terms):
            non_comedogenic = 1
    # Skincare benefits: Check for explicit claimed improvements.
    if skincare_benefits is None and summary_text:
        benefit_terms = [
            "improves",
            "improve the look",
            "hydrates",
            "hydrating",
            "moisturizes",
            "skin barrier",
            "skin over time"
        ]
        if any(term in summary_text for term in benefit_terms):
            skincare_benefits = 1
    # Wear duration: Extract a stated number of hours.
    if wear_claim_hours is None and summary_text:
        wear_match = re.search(
            r"\b(\d+)\s*[- ]?\s*hour\s*(?:wear|longwear|longwearing)\b",
            summary_text
        )
        if wear_match:
            wear_claim_hours = int(wear_match.group(1))
    # Size: Check the summary only if the primary method failed.
    if size_oz is None and summary_text:
        size_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*(?:fl\.?\s*oz|oz)\b",
            summary_text
        )
        if size_match:
            size_oz = float(size_match.group(1))
    # Warn only after all size extraction methods have been checked.
    if size_oz is None:
        print("Warning: Product size could not be extracted.")

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
        "avg_rating": avg_rating,
        "bestseller_list": bestseller_list
    }