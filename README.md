# Cosmetic Foundation Dataset: Foundation Characteristics and Bestseller Status

## Project Overview

This project examines which cosmetic foundation characteristics are associated with bestseller status at Ulta Beauty and Sephora.
By comparing product features, prices, and customer feedback, the study aims to identify patterns that may help cosmetic brands and retailers make informed product development and marketing decisions.
The research identifies relationships rather than cause and effect. Bestseller status is based on captured retailer-reported listings.

**Research Question**

Which cosmetic foundation characteristics are associated with retailer-reported bestseller status at Ulta and Sephora?

**Detailed methodology:** [Research Methodology](docs/Research_Methodology.md)

## Data Sources

Product information is collected from two major beauty retailers:

- **Ulta Beauty:** ulta.com
- **Sephora:** sephora.com

Python web scrapers collect foundation characteristics, prices, customer review counts, average ratings, and bestseller listing status from retailer webpages.
The collected information is stored in a SQLite database `foundation.db`, which separates product characteristics from retailer-specific observations.

**Further details:** Data Collection Protocol (coming soon) and Data Dictionary (coming soon).

## Research Approach

The study randomly selects 100 foundation records from a larger collection, with equal representation from Ulta and Sephora.
Each retailer contributes 25 products found on its captured bestseller list and 25 products not found on that list.

Before analysis, the selected data are checked for accuracy, missing information, and inconsistencies.
The study then compares foundation characteristics and customer feedback to identify patterns associated with bestseller listing status.

**Further details:** [Research Methodology](docs/Research_Methodology.md)


## Project Workflow

The project follows a step-by-step process to collect, organize, verify, and analyze foundation product information.

```text
Collect Data → Store in SQLite → Select Sample → Verify & Clean → Analyze Results
```
### Repository Structure

| File | Purpose |
|---|---|
| `foundation_app.py` | Runs the data collection application |
| `foundation_database.py` | Creates the database tables |
| `ulta_product_scraper.py` | Collects product information from Ulta |
| `sephora_product_scraper.py` | Collects product information from Sephora |
| `ulta_bestsellers.py` | Checks Ulta bestseller listing membership |
| `sephora_bestsellers.py` | Checks Sephora bestseller listing membership |
| `db_cleaner.py` | Supports data-quality checks and corrections |
| `docs/Research_Methodology.md` | Explains the research design and methods |

The collected data are stored locally in `foundation.db`. The selected sample will be stored separately in `sampling.db`.

**Note:** Sample selection, final data preparation, and analysis are planned stages of the workflow and will be documented as they are completed.

## Installation & Usage

### Requirements

- Python 3.14+
- Git
- pip
- Internet connection for product data collection

### Installation

**1. Clone the repository:**

   ```powershell
   git clone https://github.com/sanjida03/DATA602_Fall2026_Group1.git
   cd DATA602_Fall2026_Group1
   ```

**2. Install the required Python libraries:**

   ```powershell
   pip install pandas numpy requests beautifulsoup4 matplotlib
   ```

**3. Run the data collection application:**

   ```powershell
   python foundation_app.py
   ```

The application allows users to collect foundation information from Ulta and Sephora, view saved records, and review collected data.

The information is stored in a local SQLite database `foundation.db`.

**Further instructions:** Data Collection Protocol *(coming soon)*.

## Limitations, Ethics & AI Disclosure

### Research Limitations

- Bestseller status reflects captured retailer listings.
- The selected sample may not represent all foundations sold at Ulta or Sephora.
- Product information and bestseller rankings may change over time.

For additional details, see the [Research Methodology](docs/Research_Methodology.md).

### Ethical Data Collection

The project collects publicly available product information from Ulta Beauty and Sephora.
No customer names, personal profiles, or individual review text are collected.
The dataset is stored separately from the public GitHub repository, with access limited to authorized users.

### AI Assistance

Generative AI was used as a support tool throughout this study. AI assistance included:

- **Research feedback:** identifying potential limitations, and suggesting improvements for the team to evaluate.
- **Project management:** Organizing tasks, and outlining development steps to optimize work flow.
- **Code development:** Assisting with Python code implementation, debugging, and troubleshooting.
- **Documentation:** Help organize project documentation.

All AI-generated feedback and suggestions were reviewed before acceptance or implementation. Final research decisions, data collection procedures, code verification, and analytical findings remain the responsibility of the research team.
