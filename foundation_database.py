"""
Filename: foundation_database.py
Author: Travisha Mills
Date: 2026-09-27
Project: Foundation Characteristics & Consumer Demand
Description: Initializes the SQLite database for foundation products
and retailer-specific observations.
"""

import sqlite3

# Connect to the SQLite database.
connection = sqlite3.connect("foundation.db")

# Enforce foreign-key relationships.
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Store one record per unique foundation product.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL COLLATE NOCASE,
        brand TEXT NOT NULL COLLATE NOCASE,
        size_oz REAL NOT NULL CHECK(size_oz > 0),
        packaging_material TEXT CHECK (
            packaging_material IN ('glass', 'plastic')
        ),
        shade_count INTEGER CHECK(shade_count > 0),
        undertone_count INTEGER CHECK(undertone_count BETWEEN 0 AND 3),
        finish_type TEXT CHECK (
            finish_type IN ('matte', 'natural', 'satin', 'radiant', 'dewy')
        ),
        coverage_level TEXT CHECK (
            coverage_level IN (
                'light',
                'light_to_medium',
                'medium',
                'medium_to_full',
                'full'
            )
        ),
        non_comedogenic INTEGER CHECK(non_comedogenic IN (0,1)),
        skincare_benefits INTEGER CHECK(skincare_benefits IN (0,1)),
        spf_present INTEGER CHECK(spf_present IN (0,1)),
        wear_claim_hours INTEGER CHECK(wear_claim_hours > 0),
        UNIQUE (brand, product_name, size_oz)
    )
''')

# Store multiple retailer observations per product.
cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_observations (
        observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        source TEXT NOT NULL CHECK (
            source IN ('tiktok_shop', 'ulta', 'sephora', 'brand_site')
        ),
        source_url TEXT NOT NULL,
        collection_date TEXT NOT NULL,
        price_usd REAL CHECK(price_usd >= 0),
        tiktok_units_sold INTEGER CHECK(tiktok_units_sold >= 0),
        bestseller_list INTEGER CHECK(bestseller_list IN (0,1)),
        review_count INTEGER CHECK(review_count >= 0),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
''')

connection.commit()
connection.close()