# Research Methodology

## 1. Research Design

### 1.1 Research Question

**Which cosmetic foundation characteristics are associated with retailer-reported bestseller status at Ulta and Sephora?**

This study uses an exploratory and observational approach to examine how cosmetic foundation characteristics relate to products appearing on retailer bestseller lists.
The findings aim to provide cosmetic brands and retailers with insights for product development, and marketing decisions.

### 1.2 Research Population

The research population consists of cosmetic foundation products listed within Ulta Beauty's or Sephora's foundation product category.
Product eligibility is determined by each retailer's product classification. Products listed exclusively under other product categories are excluded.
Products available at both retailers may be recorded as separate retailer-specific observations, provided they meet the eligibility criteria of each source.
Products with missing or uncertain attribute information are retained for further verification and data-quality assessment rather than automatically excluded.

**Population Limitations**

Ulta Beauty and Sephora may apply different classification criteria when assigning products to their foundation category. 
because the study draws from selected foundation products listed by these two retailers, the findings may not be generalizable to the entire cosmetic foundation market.

### 1.3 Sampling Methodology

#### Sampling Design

The study employs a structured random sampling approach to select foundation products from a compiled product list.
The target analytical sample consists of 100 product–retailer observations, evenly distributed between Ulta Beauty and Sephora, with 50 observations from each retailer.

For each retailer, the sample includes:

- 25 products appearing on the retailer's captured bestseller list.
- 25 products not appearing on the captured bestseller list.

This balanced allocation facilitates a comparative analysis between bestseller-listed and non-bestseller-listed products.
However, it does not reflect the actual proportion of bestseller-listed products within either retailer's foundation category.

#### Candidate Data Collection

The existing SQLite database, `foundation.db`, serves as the initial candidate inventory.
Previously collected pilot products are retained, while additional product data are gathered through the established Ulta Beauty and Sephora web-scraping pipeline.
The initial collection target is approximately 100 eligible product–retailer pairs per retailer, resulting in a combined candidate inventory of approximately 200 pairs.

Candidate products are identified from accessible listings within each retailer's foundation category.
The candidate pool may be expanded as needed to ensure sufficient representation across bestseller and non-bestseller groups.
All eligible products, including previously collected pilot products, are considered for random selection.

Pilot products are not automatically included in the final analytical sample.

#### Sampling Procedure

Following data collection and preliminary validation, the `products` and `product_observations` tables are joined using `product_id` to establish the eligible product–retailer records.
Where multiple observations exist for the same product and retailer, one verified observation is retained according to the selection criteria established in Section 1.5.

Eligible records are stratified by two variables:

- Retailer source (`source`)
- Bestseller listing membership (`bestseller_list`)

Using Pandas `groupby()` records are organized into four sampling groups:

1. Ulta — Listed (`1`)
2. Ulta — Unlisted (`0`)
3. Sephora — Listed (`1`)
4. Sephora — Unlisted (`0`)

A random sample of 25 product–retailer pairs is selected from each group using Pandas `sample()` with a fixed random seed of `6022026`.
Before random selection, the candidate inventory is sorted by stable product identifiers to support reproducibility.
Random selection is performed only when each group contains at least 25 eligible candidates.
If a group falls below this threshold, additional data collection is conducted where feasible. Any remaining shortfall is documented and reported.

#### Sample Storage and Verification

The selected records are exported to a separate SQLite database, `sampling.db`, for final verification and analysis.
The original `foundation.db` is preserved as the complete candidate dataset, including both selected and non-selected products.
The selected sample undergoes verification and data cleaning before Exploratory Data Analysis (EDA).

To ensure reproducibility, the sampling procedure, random seed, source dataset version, selected product identifiers, and any exclusions are documented.
If a selected product fails verification, the reason for exclusion is recorded, and a replacement is drawn from 
the remaining eligible candidates according to the original randomized order.

#### Sampling Limitations

The sampling design intentionally balances retailer representation and bestseller listing membership.
As a result, the sample proportions do not reflect the actual distribution of bestseller-listed products within either retailer.
Additionally, random selection is restricted to the collected candidate inventory, which may not capture the full range of foundation products available through Ulta Beauty and Sephora.
Consequently, findings are interpreted as exploratory associations within the selected sample rather than estimates representative of the broader cosmetic foundation market.

### 1.4 Bestseller Status Definition

#### Definition

The variable `bestseller_list` serves as the operational measure of bestseller status, indicating whether a foundation product appears on the captured bestseller listing of its correlated retailer.
Because Ulta Beauty and Sephora maintain separate bestseller listings, classification is determined independently using the product's corresponding retailer source.

#### Bestseller Classification Process

Bestseller classification is performed through two retailer-specific Python scripts:

**Ulta — `ulta_bestsellers.py`**

Retrieves foundation products ranked by bestseller status and identifies listing membership by matching product brand and name against the captured retailer listing.

**Sephora — `sephora_bestsellers.py`**

Uses a previously captured bestseller listing containing 45 foundation products, collected on October 22, 2026. Product identifiers are used to determine listing membership.
During data collection, each retailer's product scraper invokes its corresponding bestseller classification function.
The resulting classification is automatically recorded in the `bestseller_list` column of the `product_observations` table, alongside the retailer source and collection date.

#### Reason for This Approach

Retailer specific bestseller status were selected as an indicator of product popularity because they identify products recognized by retailers 
as top performing within their respective categories.
These listings provide an observable basis for examining product characteristics associated with bestseller status.
They can also be refreshed through additional data collection when necessary.
Separate classification scripts were implemented to accommodate retailer-specific data retrieval methods while maintaining consistent classification procedures.
The two implementations differ in their data retrieval approaches: Sephora uses a fixed, previously captured reference listing,
 while Ulta retrieves its bestseller-sorted product listing at the time of classification.

#### Variable Interpretation

| Value | Meaning |
|---|---|
| `1` | Product appears in the captured bestseller listing of its source retailer |
| `0` | Product does not appear in the captured bestseller listing of its source retailer |
| `NULL` | Bestseller listing membership could not be determined |

#### Assumptions and Limitations

- Bestseller status represents captured listing membership rather than independently verified sales volume.
- A value of `0` indicates absence from the collected listing and does not establish that a product is commercially unsuccessful.
- Captured bestseller listings may not represent the complete set of bestselling products offered by a retailer.
- Bestseller rankings and product availability may change over time.
- Ulta and Sephora use different listing sources and classification procedures, which may affect cross-retailer comparability.
- Observed relationships between foundation characteristics and bestseller listing membership are interpreted as associations, not evidence of causation.

Throughout the analysis, products are consistently classified as `listed` or `unlisted` within their respective captured retailer bestseller listings.
The dataset supports exploratory comparisons of foundation characteristics and customer feedback across these listing categories.
Available listing dates and coverage information are documented to establish the reference period and scope of classification.

### 1.5 Unit of Analysis

The primary unit of analysis is a **product–retailer pair**, representing one cosmetic foundation product observed within either Ulta Beauty or Sephora.

The database contains two relational tables:

- `products`: Stores unique foundation products and their recorded characteristics.
- `product_observations`: Stores retailer-specific measurements, including price, review count, average customer rating, bestseller listing membership, source URL, and collection date.

A foundation available at both retailers may contribute one analytical record per retailer, as its pricing, customer feedback metrics, and bestseller listing membership may differ between sources.

#### Repeated Observations

The collection system permits multiple observations of the same foundation at the same retailer over time.
To prevent repeatedly collected products from receiving disproportionate representation in the primary analytical sample, one verified observation is retained per product–retailer pair.
When multiple observations exist, the most recent verified observation is selected based on `collection_date`.
If multiple verified observations share the same timestamp, the observation with the highest `observation_id` is retained.
All observations are verified before this selection rule is applied. Earlier observations remain preserved in `foundation.db` for traceability and potential sensitivity analysis.

#### Final Analytical Sample

The target sample consists of 100 product–retailer pairs, evenly distributed across four sampling groups:

- 25 Ulta listed foundations.
- 25 Ulta unlisted foundations.
- 25 Sephora listed foundations.
- 25 Sephora unlisted foundations.

Each selected product–retailer pair contributes one record to the primary exploratory data analysis (EDA).
The analytical dataset is constructed by joining product-level characteristics with the selected retailer-specific observations using `product_id`.

#### Analytical Focus

The analysis examines differences in product characteristics between bestseller-listed and non-bestseller-listed foundations.
Primary comparison variables include price, review count, and average customer rating. Additional foundation characteristics are examined to identify potential patterns and associations with bestseller listing membership.
Comparisons are conducted across the two retailer sources to explore whether observed patterns are consistent between Ulta and Sephora.

**Any statistically significant differences are interpreted as associations within the selected sample rather than evidence of causation.**

### 1.6 Data Verification Rules

#### Verification Approach

The project follows a two-stage data collection and verification process to assess dataset accuracy, consistency, and reliability.

#### Stage 1 — Automated Data Collection

Ulta and Sephora web-scraping pipelines extract foundation characteristics and retailer-specific measurements, which are stored in `foundation.db`.
Multiple extraction methods are used to accommodate differences in retailer webpage structures and product formatting, supporting more complete data capture across both sources.

#### Stage 2 — Manual Verification and Data Quality Assessment

After random selection, all variables included in the primary Exploratory Data Analysis (EDA) undergo 100% manual verification against available retailer evidence and collection records.

The following variables require complete verification across the selected analytical sample:

| Variable | Description |
|---|---|
| `bestseller_list` | Captured retailer bestseller listing membership |
| `price_usd` | Foundation price |
| `review_count` | Number of customer reviews |
| `avg_rating` | Average customer rating |
| `shade_count` | Number of available shades |

Product identifiers, retailer source, source URL, and collection dates are also validated for every selected observation.

#### Secondary Characteristic Audit

Additional recorded characteristics not included in the primary EDA undergo a random 20% verification audit.

These characteristics include:

- `size_oz`
- `packaging_material`
- `undertone_count`
- `wear_claim_hours`
- `finish_type` 
- `coverage_level`
- `spf_present`
- `skincare_benefits`
- `non_comedogenic`

The audit uses a reproducible random selection procedure, with five observations selected from each retailer–bestseller membership group.
This produces 20 audited observations from the planned 100-record analytical sample.
Additional investigation is conducted whenever suspicious or potentially invalid values are identified outside the random audit.
If a secondary characteristic is subsequently incorporated into the EDA, it must undergo complete verification across all applicable analytical observations.

#### Missing and Incorrect Values

Missing values are investigated to determine whether they reflect information not reported by the retailer, extraction failures, or information that cannot be independently verified.
Values missed during automated extraction are corrected when reliable supporting evidence is available. Incorrect nonmissing values are also corrected following verification.
The absence of a reported product claim is not automatically interpreted as confirmation that the characteristic is absent.
Values that cannot be verified remain missing or are flagged as uncertain rather than replaced with unsupported assumptions.

#### Correction Documentation

All manual corrections are recorded in a verification log containing:

- Product and observation identifiers
- Variable examined
- Original value
- Corrected value
- Verification source
- Verification date
- Reason for correction

Verified values, unresolved discrepancies, and missing information are documented to maintain data traceability.

#### Verification Limitations

Product prices, customer review counts, average ratings, and retailer bestseller listings may change over time.
When historical values cannot be independently recovered, the team documents the available verification evidence and
 any differences between the original collection and subsequent verification rather than assuming that current retailer information represents historical values.

**Although this verification process strengthens the quality and reliability of the curated dataset, it does not guarantee the elimination of all extraction,
 classification, or measurement errors.**
