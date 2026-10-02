'''
Filename: foundation_app.py
Author: Travisha Mills
Date: 2026-10-01
Description: Runs the foundation data-entry application and validates user input.
'''
import sqlite3
from datetime import datetime
import pandas as pd

# Connect to the SQLite database used by the application.
connection = sqlite3.connect("foundation.db")

# Enforce fk relationships
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Reusable validation function for yes/no questions
# Returns 1 for yes and 0 for no so the value matches the SQLite table design.
def get_yes_no(prompt):
    while True:
        user_input = input(prompt).lower()
        if user_input == "y":
            return 1
        elif user_input == "n":
            return 0
        else:
            print("Please enter y or n.")

# Reusable validation function for positive whole numbers.
# Prevents text, decimals, zero, and negative values from being accepted.
def get_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            print("Value must be greater than 0.")
        except ValueError:
            print("Please enter a whole number.")

# Reusable validation function for positive decimal numbers.
def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("Value must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")

# Prevents negative numbers, decimals, and text from being accepted.
def get_nonnegative_int(prompt):
    while True:
        try:
            user_input = input(prompt).replace(",", "")
            value = int(user_input)
            if value >= 0:
                return value
            print("Value cannot be negative.")
        except ValueError:
            print("Please enter a whole number.")

# Looks up a product by name and returns its product_id.
def get_product_id_by_name():
    while True:
        product_name = input("Product name: ").strip()
        cursor.execute('''
            SELECT product_id, product_name
            FROM products
            WHERE LOWER(product_name) = LOWER(?)
        ''', (product_name,))
        product = cursor.fetchone()
        if product:
            print(f"Matched product: {product[1]} (Product ID: {product[0]})")
            return product[0]
        print("Product not found. Please enter the product name again.")

# Collects the static characteristics for new foundation product.
def add_product():
    print("\nAdd New Product")
    product_name = input("Product name: ").strip()
    brand = input("Brand: ").strip().lower()
    size_oz = get_positive_float("Size in ounces: ")
    celebrity_founded = get_yes_no("Celebrity founded? (y/n): ")
    packaging_material = input("Packaging material: ").strip().lower()
    shade_count = get_positive_int("Shade count: ")
    undertone_count = get_positive_int("Undertone count: ")
    finish_type = input("Finish type: ").strip().lower()
    coverage_level = input("Coverage level: ").strip().lower()
    non_comedogenic = get_yes_no("Non-comedogenic? (y/n): ")
    skincare_benefits = get_yes_no("Skincare benefits? (y/n): ")
    spf_present = get_yes_no("SPF present? (y/n): ")
    while True:
        wear_input = input("Wear claim in hours (leave blank if none): ")

        if wear_input == "":
            wear_claim_hours = None
            break
        try:
            wear_claim_hours = int(wear_input)
            if wear_claim_hours > 0:
                break
            print("Wear claim must be greater than 0.")
        except ValueError:
            print("Please enter a whole number or leave blank.")
    # Saves the collected product characteristic data as a new row in the products table.
    cursor.execute('''
        INSERT INTO products (
            product_name,
            brand,
            size_oz,
            celebrity_founded,
            packaging_material,
            shade_count,
            undertone_count,
            finish_type,
            coverage_level,
            non_comedogenic,
            skincare_benefits,
            spf_present,
            wear_claim_hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        product_name,
        brand,
        size_oz,
        celebrity_founded,
        packaging_material,
        shade_count,
        undertone_count,
        finish_type,
        coverage_level,
        non_comedogenic,
        skincare_benefits,
        spf_present,
        wear_claim_hours
    ))
    connection.commit()
    print("Product saved successfully.")

# Collects changing product data.
def add_observation():
    print("\nAdd Product Observation")
    product_id = get_product_id_by_name()
    source = input("Source: ").strip().lower()
    # Automatically records the date and time the observation is collected.
    collection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    price_usd = get_positive_float("Price (USD): ")
    tiktok_units_sold = get_nonnegative_int("TikTok units sold: ")
    bestseller_list = get_yes_no("On bestseller list? (y/n): ")
    while True:
        try:
            avg_rating = float(input("Average rating (0-5): "))

            if 0 <= avg_rating <= 5:
                break

            print("Rating must be between 0 and 5.")

        except ValueError:
            print("Please enter a valid number.")
    review_count = get_nonnegative_int("Review count: ")
    # Saves the collected observation data as a new row in the product_observations table.
    cursor.execute('''
        INSERT INTO product_observations (
            product_id,
            source,
            collection_date,
            price_usd,
            tiktok_units_sold,
            bestseller_list,
            avg_rating,
            review_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        product_id,
        source,
        collection_date,
        price_usd,
        tiktok_units_sold,
        bestseller_list,
        avg_rating,
        review_count
    ))
    connection.commit()
    print("Observation saved successfully.")

# Displays all saved foundation products using PANDAS.
def view_products():
    print("\nSaved Products")
    products_df = pd.read_sql_query(
        "SELECT * FROM products",
        connection
    )
    print(products_df.to_string(index=False))

# Displays all saved product observations.
def view_observations():
    print("\nProduct Observations")
    observations_df = pd.read_sql_query(
        '''
        SELECT
            po.observation_id,
            p.product_name,
            po.source,
            po.collection_date,
            po.price_usd,
            po.tiktok_units_sold,
            po.bestseller_list,
            po.avg_rating,
            po.review_count
        FROM product_observations po
        JOIN products p
            ON po.product_id = p.product_id
        ORDER BY po.collection_date DESC
        ''',
        connection
    )
    if observations_df.empty:
        print("No product observations found.")
    else:
        print(observations_df.to_string(index=False))

# Main menu display
def menu():
    print("\nFoundation Data Collection")
    print("1. Add new product")
    print("2. Add product observation")
    print("3. View products")
    print("4. View product observations")
    print("5. Exit")

menu()

# Menu choice determines which part of the program runs.
while True:
    choice = input("Choose an option(1-5): ")
    if choice == "1":
        add_product()
    elif choice == "2":
        add_observation()
    elif choice == "3":
        view_products()
    elif choice == "4":
        view_observations()
    elif choice == "5":
        print("Exiting program")
        break
    else:
        print("Invalid option")