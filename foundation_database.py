'''
Filename: foundation_database.py
Author: Travisha Mills
Data: 2026-09-27
Description: Set up the initial SQLite database structure with products and product_observations tables
'''
import sqlite3

# SQLite database connection
connection = sqlite3.connect("foundation.db")

# Enforce relationships between database tables
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()
            
# PRODUCTS TABLE: Stores each foundation product and its static characteristics.
cursor.execute('''
     CREATE TABLE IF NOT EXISTS products (
     product_id INTEGER PRIMARY KEY AUTOINCREMENT,
     product_name TEXT NOT NULL,
     brand TEXT NOT NULL,
     size_oz REAL CHECK(size_oz > 0),
     celebrity_founded INTEGER CHECK (celebrity_founded IN (0,1)),
     packaging_material TEXT,
     shade_count INTEGER CHECK(shade_count > 0),
     undertone_count INTEGER CHECK(undertone_count > 0),
     finish_type TEXT,
     coverage_level TEXT,
     non_comedogenic INTEGER CHECK (non_comedogenic IN (0,1)),
     skincare_benefits INTEGER CHECK (skincare_benefits IN (0,1)),
     spf_present INTEGER CHECK (spf_present IN (0,1)),
     wear_claim_hours INTEGER CHECK(wear_claim_hours > 0)
     )
''')

cursor.execute('''
    PRAGMA table_info(products);
''')

columns_products = cursor.fetchall()


# Observation Table to store changing value
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    collection_date TEXT NOT NULL,
    price_usd REAL CHECK (price_usd >= 0),
    tiktok_units_sold INTEGER CHECK (tiktok_units_sold >= 0),
    bestseller_list INTEGER CHECK (bestseller_list IN (0,1)),
    avg_rating REAL CHECK (avg_rating BETWEEN 0 AND 5),
    review_count INTEGER CHECK (review_count >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
''')

cursor.execute('''
    PRAGMA table_info(product_observations);
''')

columns = cursor.fetchall()

for column in columns_products:
    print(column)

for column in columns:
    print(column)

connection.commit()

connection.close()