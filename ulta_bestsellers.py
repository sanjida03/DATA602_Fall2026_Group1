
"""
Filename: ulta_bestsellers.py
Author: Travisha Mills
Date: 2026-10-16
Project: Foundation Characteristics & Consumer Demand
Description: Collects Ulta's bestselling foundations and checks product status.
"""

import requests
from bs4 import BeautifulSoup

# Ulta's foundation page sorted by bestselling products.
URL = "https://www.ulta.com/shop/makeup/face/foundation?sort=best_sellers"

# Identify the request as coming from a web browser.
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_bestseller_products():
    """Collect product names from Ulta's bestselling foundation list."""
    # Request the webpage and check for HTTP errors.
    response = requests.get(URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    # Convert the HTML into a searchable document.
    soup = BeautifulSoup(response.text, "html.parser")
    # Locate the section containing foundation products.
    product_list = soup.find(
        "ul",
        attrs={"data-test": "products-list"}
    )

    # Return None if the product list cannot be located.
    if product_list is None:
        return None
    # Find all individual product entries.
    products = product_list.find_all(
        "li",
        attrs={"data-test": "products-list-item"}
    )
    product_names = []

    # Extract each product's name from its HTML element.
    for product in products:
        name_tag = product.find(
            "span",
            class_="pal-c-Text__isScreenReader"
        )
        if name_tag:
            product_names.append(name_tag.get_text(strip=True))
    # Return the collected names or None if no names were found.
    return product_names if product_names else None

def bestseller_status(brand, product_name):
    """Return 1 if listed, 0 if not listed, or None if unavailable."""
    # Retrieve the bestseller list without printing it.
    try:
        product_names = get_bestseller_products()
    except requests.RequestException:
        return None
    # Unknown status if the list could not be collected.
    if product_names is None:
        return None
    # Combine brand and name for case-insensitive comparison.
    full_name = f"{brand} {product_name}".casefold().strip()
    # Check whether the product appears in the bestseller list.
    for bestseller in product_names:
        if full_name == bestseller.casefold().strip():
            return 1
    # Product was not found in the collected list.
    return 0

# Display the full list only when this file is run directly.
if __name__ == "__main__":
    product_names = get_bestseller_products()
    # Display a message if the list is unavailable.
    if product_names is None:
        print("Bestseller list unavailable.")
    else:
        # Display the total number of products collected.
        print("\n--- Ulta Bestselling Foundations ---")
        print("Products found:", len(product_names))

        # Print each product with its position in the list.
        for number, name in enumerate(product_names, start=1):
            print(f"{number}. {name}")
