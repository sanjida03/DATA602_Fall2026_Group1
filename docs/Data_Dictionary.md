# Data Dictionary: Cosmetic Foundation Dataset

## Database Overview

The database contains two tables connecting foundation characteristics with retailer-specific information.

### Database Tables

| Table | Description |
|---|---|
| `products` | Stores each foundation's identifying information and product characteristics |
| `product_observations` | Stores retailer prices, customer feedback, and bestseller listing status |

### Table Relationship

```text
products                         product_observations
┌────────────────────┐           ┌─────────────────────────┐
│ product_id (PK)    │──────────<│ product_id (FK)         │
│ product_name       │           │ observation_id (PK)     │
│ brand              │           │ source                  │
│ ...                │           │ ...                     │
└────────────────────┘           └─────────────────────────┘

           One product → Multiple retailer observations
```

| Key | Meaning |
|---|---|
| PK (Primary Key) | Unique identifier for each record |
| FK (Foreign Key) | Connects a record to another table |

### Data Types

| Type | Meaning | Example |
|---|---|---|
| `TEXT` | Text | `Estée Lauder` |
| `INTEGER` | Whole number | `57` |
| `REAL` | Number that may contain decimals | `52.00` |
| `NULL` | Missing or unknown value | `NULL` |

### Product Claim Values

Applies to `spf_present`, `non_comedogenic`, and `skincare_benefits`.

| Value | Meaning |
|---|---|
| `1` | Claim found on the corresponding retailer's product page |
| `0` | Claim not found on the corresponding retailer's product page |
| `NULL` | Unknown or could not be determined |

**Note:** `0` means the claim was not found, not necessarily that the product lacks the characteristic.

## Products Table

Stores each foundation's identifying information and product characteristics.

| Field Name | Data Type | Description | Allowed Values | Example |
|---|---|---|---|---|
| `product_id` | INTEGER | Unique product ID (PK) | Auto-generated | `1` |
| `product_name` | TEXT | Foundation product name | Required | `Double Wear Foundation` |
| `brand` | TEXT | Foundation brand | Required | `Estée Lauder` |
| `size_oz` | REAL | Product size in ounces | Greater than 0, or NULL | `1.0` |
| `packaging_material` | TEXT | Container material | glass, plastic, NULL | `glass` |
| `shade_count` | INTEGER | Number of available shades | Greater than 0, or NULL | `57` |
| `undertone_count` | INTEGER | Number of undertone categories | 0–3, or NULL | `3` |
| `finish_type` | TEXT | Advertised foundation finish | matte, natural, satin, radiant, dewy, NULL | `matte` |
| `coverage_level` | TEXT | Advertised foundation coverage | light, light_to_medium, medium, medium_to_full, full, NULL | `medium_to_full` |
| `non_comedogenic` | INTEGER | Non-comedogenic claim | 1, 0, NULL | `1` |
| `skincare_benefits` | INTEGER | Skincare benefit claim | 1, 0, NULL | `1` |
| `spf_present` | INTEGER | SPF claim | 1, 0, NULL | `0` |
| `wear_claim_hours` | INTEGER | Advertised wear duration in hours | Greater than 0, or NULL | `36` |

## Product Observations Table

Stores retailer-specific information collected for each foundation.

| Field Name | Data Type | Description | Allowed Values | Example |
|---|---|---|---|---|
| `observation_id` | INTEGER | Unique observation ID (PK) | Auto-generated | `1` |
| `product_id` | INTEGER | Links to the foundation in `products` (FK) | Required, existing product ID | `1` |
| `source` | TEXT | Retailer or website where data was collected | ulta, sephora, brand_site | `ulta` |
| `source_url` | TEXT | Product webpage address | Required | `https://www.ulta.com/...` |
| `collection_date` | TEXT | Date and time data was collected | Required, timestamp | `2026-10-22 14:30:00` |
| `price_usd` | REAL | Product price in US dollars | 0 or greater, NULL | `52.00` |
| `bestseller_list` | INTEGER | Found on retailer bestseller list | 1, 0, NULL | `1` |
| `review_count` | INTEGER | Number of customer reviews | 0 or greater, NULL | `10219` |
| `avg_rating` | REAL | Average customer rating | 0–5, NULL | `4.5` |

### Bestseller Listing Values

| Value | Meaning |
|---|---|
| `1` | Product found on the captured bestseller list of its source retailer |
| `0` | Product not found on the captured bestseller list of its source retailer |
| `NULL` | Listing status could not be determined |

**Note:** `0` does not necessarily mean the product is not a bestseller. It means the product was not found on the captured retailer list.

For details on how bestseller status is determined, see [Research Methodology](docs/Research_Methodology.md).