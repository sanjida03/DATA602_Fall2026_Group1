'''
Filename: foundation_app.py
Author: Travisha Mills
Date: 2026-10-01
Project: Foundation Characteristics & Consumer Demand
Description: Command-line application used to manually collect and review foundation
Main responsibilities:
    - Add foundation products and their static characteristics.
    - Add source-specific product observations.
    - Validate user input before saving data.
    - Standardize categorical values.
    - Preserve missing values as NULL instead of false zeros.
    - Prevent duplicate product identities.
    - Warn about likely duplicate observations.
    - Display collected products and observations using Pandas.
Database: foundation.db
Database tables:
    - products
    - product_observations
Dependencies:
    - Python Version 3.14.6 or later
    - pandas
    - sqlite3
Run order:
    1. Run foundation_database.py to initialize the database.
    2. Run foundation_app.py to enter and review data.
'''
import sqlite3
from datetime import datetime
import pandas as pd

# Connect to the SQLite database used by the application.
connection = sqlite3.connect("foundation.db")

# Enforce fk relationships
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Validates yes/no input.
# If allow_blank=True, blank input returns None so SQLite stores NULL.
def get_yes_no(prompt, allow_blank=False):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "y":
            return 1
        elif user_input == "n":
            return 0
        elif allow_blank and user_input == "":
            return None
        else:
            if allow_blank:
                print("Enter y, n, or leave blank.")
            else:
                print("Enter y/n.")

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
            print("Enter a whole number.")

# Reusable validation function for positive decimal numbers.
def get_float(prompt, allow_blank=False, allow_zero=False):
    while True:
        user_input = input(prompt).strip()
        if allow_blank and user_input == "":
            return None
        try:
            value = float(user_input)
            if allow_zero:
                if value >= 0:
                    return value
                else:
                    print("Value cannot be negative.")
            else:
                if value > 0:
                    return value
                else:
                    print("Value must be greater than 0.")
        except ValueError:
            if allow_blank:
                print("Enter a valid number or leave blank.")
            else:
                print("Enter a valid number.")

# If allow_blank=True, blank input returns None so SQLite stores NULL.
def get_nonnegative_int(prompt, allow_blank=False):
    while True:
        user_input = input(prompt).strip().replace(",", "")
        if allow_blank and user_input == "":
            return None
        try:
            value = int(user_input)
            if value >= 0:
                return value
            else:
                print("Value cannot be negative.")
        except ValueError:
            if allow_blank:
                print("Enter a whole number or leave blank.")
            else:
                print("Enter a whole number.")

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

# Displays a numbered list of valid options and returns the selected value.
def get_choice(prompt, options):
    while True:
        print(f"{prompt}")
        for number, label in options.items():
            print(f"{number}. {label}")
        choice = input("Choose an option: ").strip()
        if choice in options:
            return options[choice]
        print("Choose one of the listed options.")

# Validates that the entered source URL begins with http:// or https://
def get_url(prompt):
    while True:
        url = input(prompt).strip()
        if url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            print("Enter a valid URL starting with http:// or https://")

# Checks for an existing observation with the same product, source, and URL.
def check_duplicate_observation(product_id, source, source_url):
    cursor.execute('''
        SELECT observation_id, collection_date
        FROM product_observations
        WHERE product_id = ?
          AND source = ?
          AND source_url = ?
        ORDER BY collection_date DESC
        LIMIT 1
    ''', (product_id, source, source_url))
    return cursor.fetchone()

# Requires a non-blank text value before continuing.
def get_required_text(prompt):
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("This field cannot be blank.")

# Displays a Pandas DataFrame in a readable terminal format.
def display_dataframe(df):
    if df.empty:
        print("No records found.")
        return
    with pd.option_context(
        "display.max_columns", None,
        "display.width", 140,
        "display.max_colwidth", 30
    ):
        print(df.to_string(index=False))
        

# Collects the static characteristics for new foundation product.
def add_product():
    print("\nAdd New Product")
    product_name = get_required_text("Product name: ")
    brand = get_required_text("Brand: ").lower()
    size_oz = get_float("Size in ounces: ")
    celebrity_founded = get_yes_no("Celebrity founded? (y/n): ")
    packaging_options = {"1": "glass", "2": "plastic"}
    packaging_material = get_choice("Choose packaging material:", packaging_options)
    shade_count = get_positive_int("Shade count: ")
    undertone_count = get_positive_int("Undertone count: ")
    finish_options = {"1": "matte", "2": "natural", "3": "satin","4": "radiant", "5": "dewy"}
    finish_type = get_choice("Choose finish type:", finish_options)
    coverage_options = {"1": "light", "2": "light_to_medium", "3": "medium", "4": "medium_to_full", "5": "full"}
    coverage_level = get_choice( "Choose coverage level:", coverage_options)
    non_comedogenic = get_yes_no("Non-comedogenic? (y/n, leave blank if unknown): ",allow_blank=True )
    skincare_benefits = get_yes_no("Skincare benefits? (y/n, leave blank if unknown): ", allow_blank=True)
    spf_present = get_yes_no("SPF present? (y/n, leave blank if unknown): ", allow_blank=True)
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
    try:
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
    except sqlite3.IntegrityError:
        print(
            "Duplicate product detected. "
            "A product with the same brand, name, and size already exists."
        )

# Collects changing product data.
def add_observation():
    print("\nAdd Product Observation")
    product_id = get_product_id_by_name()
    # Soucre collection
    while True:
        print("\nChoose source:")
        print("1. TikTok Shop")
        print("2. Ulta")
        print("3. Sephora")
        print("4. Brand Website")
        source_choice = input("Choose an option (1-4): ").strip()
        if source_choice == "1":
            source = "tiktok_shop"
            break
        elif source_choice == "2":
            source = "ulta"
            break
        elif source_choice == "3":
            source = "sephora"
            break
        elif source_choice == "4":
            source = "brand_site"
            break
        else:
            print("Please choose 1, 2, 3, or 4.")
    source_url = get_url("Source URL: ")
    # Duplicate checking
    duplicate = check_duplicate_observation(product_id,source,source_url)
    if duplicate:
        print(
            f"\nWarning: A similar observation already exists "
            f"(Observation ID: {duplicate[0]}, "
            f"collected: {duplicate[1]}).")
        confirm = get_yes_no("Do you still want to continue? (y/n): ")
        if confirm == 0:
            print("Observation entry cancelled.")
            return    
    # Automatically records the date and time the observation is collected.
    collection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    price_usd = get_float("Price (USD) - leave blank if unavailable: ", allow_blank=True, allow_zero=True)
    tiktok_units_sold = get_nonnegative_int("TikTok units sold - leave blank if unavailable: ", allow_blank=True)
    bestseller_list = get_yes_no( "On bestseller list? (y/n, leave blank if unavailable): ", allow_blank=True)
    review_count = get_nonnegative_int("Review count - leave blank if unavailable: ", allow_blank=True)
    # Saves the collected observation data as a new row in the product_observations table.
    cursor.execute('''
        INSERT INTO product_observations (
            product_id,
            source,
            source_url,
            collection_date,
            price_usd,
            tiktok_units_sold,
            bestseller_list,
            review_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        product_id,
        source,
        source_url,
        collection_date,
        price_usd,
        tiktok_units_sold,
        bestseller_list,
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
    if products_df.empty:
        print("No products found.")
        return
    print("\nProduct Information")
    product_info = products_df[
        [
            "product_id",
            "product_name",
            "brand",
            "size_oz",
            "packaging_material",
            "finish_type",
            "coverage_level"
        ]
    ]
    display_dataframe(product_info)
    print("\nProduct Characteristics")
    product_characteristics = products_df[
        [
            "product_id",
            "shade_count",
            "undertone_count",
            "celebrity_founded",
            "non_comedogenic",
            "skincare_benefits",
            "spf_present",
            "wear_claim_hours"
        ]
    ]
    display_dataframe(product_characteristics)

# Displays all saved product observations.
def view_observations():
    print("\nProduct Observations")
    observations_df = pd.read_sql_query(
        '''
        SELECT
            po.observation_id,
            p.product_name,
            po.source,
            po.source_url,
            po.collection_date,
            po.price_usd,
            po.tiktok_units_sold,
            po.bestseller_list,
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
        display_dataframe(observations_df)

# Main menu display
def menu():
    print("\nFoundation Data Collection")
    print("1. Add new product")
    print("2. Add product observation")
    print("3. View products")
    print("4. View product observations")
    print("5. Exit")

# Menu choice determines which part of the program runs.
while True:
    menu()
    choice = input("Choose an option (1-5): ").strip()
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
        print("Invalid option. Please choose 1-5.")