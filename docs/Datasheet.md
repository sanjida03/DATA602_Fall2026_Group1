# Datasheet - Cosmetic Foundation Dataset

## Motivation & Purpose

### Why Was This Dataset Created?

As a beauty consumer, I've noticed that certain foundations consistently appear on bestseller lists, receive recommendations,
and maintain their place on store shelves, even as new products enter the market.
This sparked my curiosity about what sets these foundations apart.
Are certain product characteristics responsible for their continued popularity, or could factors such as marketing and retail visibility play a larger role?

This dataset was created to explore which foundation characteristics are associated with bestseller status at Ulta Beauty and Sephora.
If no clear relationships emerge, the findings may point toward other factors worth investigating.

### Who Might Benefit?

The findings may help cosmetic brands and retailers better understand the characteristics associated with popular foundations and support decisions involving:

- **Product development:** Identifying features and combinations worth exploring in future formulas.
- **Pricing:** Examining price differences between products found on bestseller lists and those not found.
- **Marketing:** Identifying product characteristics worth highlighting in product descriptions and promotions.
- **Inventory planning:** Recognizing product features worth considering when planning product selections.

### Research Scope

The study uses retailer-reported product information and captured bestseller listings from Ulta Beauty and Sephora.
Findings identify relationships rather than causes and may not represent the broader cosmetics market.

**Research Question:** Which cosmetic foundation characteristics are associated with retailer-reported bestseller status at Ulta and Sephora?


## Dataset Composition

The dataset contains cosmetic foundation information collected from Ulta Beauty and Sephora, organized into two tables.

### Dataset Structure

| Table | Information Collected |
|---|---|
| `products` | Product name, brand, size, shade range, finish, coverage, and other foundation characteristics |
| `product_observations` | Retailer, price, review count, average rating, bestseller listing status, and collection date |

### What Does Each Record Represent?

Each foundation is stored once in the `products` table and can have multiple retailer observations.

For the final analysis, each record represents **one foundation at one retailer**. A foundation sold at both Ulta and Sephora may therefore appear twice, as its price, reviews, and bestseller status can differ between retailers.

### Planned Dataset Size

| Dataset | Target |
|---|---|
| Collected candidate inventory | Approximately 200 product–retailer pairs (100 per retailer) |
| Final analytical sample | 100 product–retailer pairs |
| Ulta | 25 listed + 25 unlisted |
| Sephora | 25 listed + 25 unlisted |

The final sample size and composition will be updated after data collection and verification.

**Field definitions:** [Data Dictionary](Data_Dictionary.md)

## Data Collection & Sampling

### Data Sources

Foundation information is collected from two major beauty retailers:

- **Ulta Beauty:** https://www.ulta.com/
- **Sephora:** https://www.sephora.com/

Products are included if they appear in the foundation category of the retailer where they are collected.

### Collection Process

Python web scrapers collect foundation characteristics, prices, customer ratings, review counts, and bestseller listing status from retailer websites.
The information is stored in `foundation.db`, along with the retailer source, product URL, and collection date.
Bestseller status is determined separately for each retailer using its captured bestseller listing.

### Bestseller Classification

| Value | Meaning |
|---|---|
| `1` | Found on the captured bestseller list of its source retailer |
| `0` | Not found on the captured bestseller list |
| `NULL` | Listing status could not be determined |

Each product is classified against its own retailer's captured list. A value of `0` does not confirm that a product is commercially unsuccessful.

### Product Selection

The study uses random selection from a larger collection of foundation products.
The final sample is designed to include 100 product–retailer records:

| Retailer | Listed | Unlisted | Total |
|---|---:|---:|---:|
| Ulta | 25 | 25 | 50 |
| Sephora | 25 | 25 | 50 |
| **Total** | **50** | **50** | **100** |

Previously collected products and newly collected products have the same opportunity to be selected.
The selected records will be stored separately in `sampling.db` for verification and analysis.

**Collection dates:** Recorded for each observation; the final collection period will be added after data collection.

**Detailed procedures & Classification methods:** [Research Methodology](Research_Methodology.md)


## Data Processing & Quality

### Data Quality Standards

This is a retailer-based dataset designed to represent product information reported by Ulta Beauty and Sephora, rather than the entire cosmetic foundation market.

Data quality is evaluated based on how accurately and consistently the dataset reflects information available from these retailers.
Characteristics not reported by a retailer are recorded as missing rather than treated as collection errors.

### Verification & Cleaning

| Process | Approach |
|---|---|
| Primary variables | Verify 100% of selected records |
| Secondary characteristics | Randomly audit 20% of selected records |
| Missing information | Preserve values not reported by retailers |
| Incorrect values | Correct using available retailer evidence |
| Duplicate observations | Retain the most recent verified observation |
| Documentation | Record corrections and unresolved issues |

Any secondary characteristic included in the final analysis will undergo complete verification.

### Quality Assessment

The dataset's quality will be assessed through completeness of reported information, and documented verification results.
Information unavailable from a retailer will not automatically be considered a data-quality failure.
However, information that was available but missed or incorrectly extracted will be investigated and corrected where possible.

The dataset's reliability will be evaluated within its intended retailer-specific scope, without claiming that it represents the broader cosmetics market.

**Detailed verification procedures:** [Research Methodology](Research_Methodology.md)

## Uses & Limitations

### Intended Uses

The dataset is designed to help cosmetic brands, retailers, and researchers explore relationships between foundation characteristics and bestseller listing status.

Potential uses include:

- Comparing prices, customer ratings, and product features between listed and unlisted foundations.
- Identifying characteristics or combinations worth investigating for product development and marketing.
- Examining whether patterns differ between Ulta Beauty and Sephora.

### Research Limitations

| Limitation | What It Means |
|---|---|
| Bestseller classification | Captured retailer listings do not confirm actual sales volume |
| Sample coverage | Findings may not represent all foundations sold by Ulta, Sephora, or the broader market |
| Retailer differences | Each retailer has its own bestseller listings, product categories, and customer reviews |
| Changing information | Prices, reviews, ratings, and bestseller listings may change over time |
| Missing information | Some characteristics may be unavailable or difficult to verify |

### Appropriate Interpretation

The dataset can identify patterns and relationships, but it cannot establish why a product becomes a bestseller.
Findings should not be used alone to predict sales, measure actual consumer demand, or justify business decisions without further research.

**Additional details:** [Research Methodology](Research_Methodology.md)

## 6. Ethics & Dataset Maintenance

### Responsible Data Collection

The project collects publicly available product information from Ulta Beauty and Sephora. No customer names, personal profiles, or individual review text are collected.

Data collection is limited to information relevant to the research and should respect retailer website access requirements.

### Data Storage & Access

The original collected data are preserved separately from the verified dataset.
The dataset will be stored in a private location and made available to authorized reviewers. Access instructions will be added once the storage location is finalized.

### Dataset Maintenance

| Activity | Approach |
|---|---|
| Data updates | Record the retailer source and collection date |
| Corrections | Document changes and supporting evidence |
| Version control | Track code and documentation changes in GitHub |
| Dataset updates | Preserve original data and maintain verified versions |
| Access | Limit dataset access to authorized users |

The dataset represents retailer information collected during the study period. Future changes to retailer listings or product details will not automatically update historical records.

**Related documentation:** [Research Methodology](Research_Methodology.md) | Data Collection Protocol *(coming soon)*
