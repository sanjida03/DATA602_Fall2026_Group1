'''
Filename: foundation_app.py
Author: Travisha Mills
Date: 2026-10-01
Description: Runs the foundation data-entry application and validates user input.
'''
import sqlite3

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

# Collects the static characteristics for new foundation product.
def add_product():
    print("\nAdd New Product")
    product_name = input("Product name: ")
    brand = input("Brand: ")
    size_oz = get_positive_float("Size in ounces: ")
    celebrity_founded = get_yes_no("Celebrity founded? (y/n): ")
    packaging_material = input("Packaging material: ")
    shade_count = get_positive_int("Shade count: ")
    undertone_count = get_positive_int("Undertone count: ")
    finish_type = input("Finish type: ")
    coverage_level = input("Coverage level: ")
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

cursor.execute("SELECT * FROM products")
products = cursor.fetchall()
print(products)

# Main menu display
def menu():
    print("\nFoundation Data Collection")
    print("1. Add new product")
    print("2. Add product observation")
    print("3. View products")
    print("4. Exit")

menu()

# Menu choice determines which part of the program runs.
while True:
    choice = input("Choose an option(1-4): ")
    if choice == "1":
        add_product()
    elif choice == "2":
        print("Add product observation selected")
    elif choice == "3":
        print("View products selected")
    elif choice == "4":
        print("Exiting program")
        break
    else:
        print("Invalid option")