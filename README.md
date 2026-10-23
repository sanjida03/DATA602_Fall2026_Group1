
# Foundation Characteristics & Consumer Demand Analysis

**What makes one foundation a bestseller while another goes unnoticed?**

We built a Python-based data pipeline that collects and organizes cosmetic foundation characteristics and consumer demand indicators across multiple retailers.

## Project Overview

### Research Question

**Which foundation product characteristics are associated with higher consumer demand?**

We investigate whether factors such as price, shade range, coverage, finish, and skincare benefits are associated with product popularity.

### What Our Project Does

- **Collects** foundation data from Ulta, Sephora, and TikTok Shop.
- **Matches** the same products across retailers to prevent duplicate records.
- **Tracks** prices, reviews, bestseller status, and TikTok units sold over time.
- **Validates** missing values, inconsistencies, and potential data-quality issues.
- **Stores** structured data in SQLite for future statistical analysis and modeling.

### How It Works

```text
Ulta • Sephora • TikTok Shop
            ↓
     Web Scrapers
            ↓
 foundation_app.py
 Product Matching & Validation
            ↓
      foundation.db
   ┌────────┴────────┐
   ↓                 ↓
Products        Observations
   └────────┬────────┘
            ↓
      db_cleaner.py
   Data Quality Audit
            ↓
   Future Data Analysis
```

### Project Files

| Script | Purpose |
| --- | --- |
| `foundation_database.py` | Initializes the SQLite database |
| `foundation_app.py` | Manages collection, matching, and storage |
| `ulta_product_scraper.py` | Collects Ulta product data |
| `sephora_product_scraper.py` | Collects Sephora product data |
| `tiktok_product_scraper.py` | Collects TikTok Shop product data |
| `ulta_bestsellers.py` / `sephora_bestsellers.py` | Check retailer bestseller status |
| `db_cleaner.py` | Identifies potential data-quality problems |

### Expected Output

A reusable SQLite dataset containing:

- **Product characteristics:** Shade range, undertones, coverage, finish, SPF, skincare claims, and packaging.
- **Consumer demand indicators:** Price, units sold, bestseller status, and review count.
- **Source tracking:** Retailer, product URL, and collection date.

**Current stage:** Data collection and validation. The dataset will support future exploratory analysis, statistical testing, and predictive modeling.

## Getting Started

### Requirements

- Python 3.14+
- pip
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/sanjida03/DATA602_Fall2026_Group1.git
cd DATA602_Fall2026_Group1
```

**2. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file contains:

```text
pandas
requests
beautifulsoup4
```

### Run the Pipeline

Run the following commands in order:

**1. Initialize the SQLite database**

```bash
python foundation_database.py
```

**2. Collect foundation data**

```bash
python foundation_app.py
```

Select option `1` and enter an Ulta, Sephora, or TikTok Shop product URL. The application collects, matches, and saves the data.

**3. Audit the dataset**

```bash
python db_cleaner.py
```

Displays missing values, possible duplicates, standardization issues, and invalid values without modifying the database.

### Additional Documentation

A detailed **Developer & User Guide** covering application functions, data collection rules, and troubleshooting will be linked here when available.

