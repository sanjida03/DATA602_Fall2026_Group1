# Data Collection Protocol

## Product Eligibility & Collection Requirements

### Eligible Products

A product qualifies for collection when it meets the following requirements:

- Listed in the foundation category on Ulta Beauty or Sephora.
- Has an accessible retailer product page.
- Can be identified by its brand and product name.

Products listed exclusively outside the retailer's foundation category are excluded.

**Note:** Products are not excluded simply because some characteristics are missing.

### Collection Requirements

| Requirement | Description |
|---|---|
| Retailer | Ulta Beauty or Sephora |
| Product URL | Direct link to the retailer's product page |
| Product identity | Brand and product name |
| Collection date | Date and time the information was collected |
| Bestseller status | Automatically determined by the retailer-specific script |
| Product characteristics | Information extracted from the retailer's product page |
| Customer feedback | Available review count and average rating |

Missing or unavailable information is retained for later verification.

### Collection Rules

1. Collect products from each retailer's foundation category.
2. Use the product's direct retailer URL in `foundation_app.py`.
3. Review the extracted information before saving.
4. Check for existing products and observations to avoid unnecessary duplicates.
5. Preserve the original retailer source and collection date.

**Detailed field definitions:** [Data Dictionary](Data_Dictionary.md)

**Research eligibility rules:** [Research Methodology](Research_Methodology.md)

## Running the Data Collection Application

### Step 1: Open the Project

Open the project folder in VS Code and launch the PowerShell terminal.

### Step 2: Start the Application

```powershell
python foundation_app.py
```

### Step 3: Select a Menu Option

The application provides options to:

| Action | Purpose |
|---|---|
| Add product by URL | Collect and save foundation information |
| View products | Review saved foundation characteristics |
| View observations | Review retailer-specific information |
| View conflicts | Identify differences in collected product information |
| Exit | Close the application |

### Step 4: Collect a Foundation

1. Open an eligible foundation product page on Ulta or Sephora.
2. Copy the product's direct URL.
3. Select **Add product and observation by URL**.
4. Paste the URL when prompted.
5. Review the extracted product information.
6. Complete or correct fields when prompted.
7. Save the record.

The application stores the product information and its retailer observation in `foundation.db`.

### Step 5: Review Saved Data

Use the application's viewing options to check that:

- The product name and brand are correct.
- The retailer source matches the product URL.
- The observation contains the collection date.
- Price, review count, rating, and bestseller status are recorded when available.
- Missing information has not been replaced with guesses.

### Duplicate Handling

The application checks for previously recorded products and observations.
If a product already exists, review its information before adding another retailer observation.
Repeated observations may be retained when collecting updated information from the same retailer.

**Important:** Do not delete earlier observations simply because newer information has been collected. The approved research method preserves historical records.

### Collection Errors

If a product cannot be collected:

1. Confirm the URL is correct and accessible.
2. Check whether the product belongs to the retailer's foundation category.
3. Record any missing or incorrectly extracted information.
4. Retry collection when appropriate.
5. Report unresolved problems for review.

Do not invent values to complete a record.

## 3. Bestseller Classification & Duplicate Checks

### Bestseller Classification

Bestseller status is automatically assigned during data collection using the corresponding retailer's classification script.

| Retailer | Script | Classification Method |
|---|---|---|
| Ulta | `ulta_bestsellers.py` | Checks the product against Ulta's bestseller-sorted foundation listing |
| Sephora | `sephora_bestsellers.py` | Checks the product against a previously captured Sephora bestseller list |

### Bestseller Values

| Value | Meaning |
|---|---|
| `1` | Product found on its retailer's captured bestseller list |
| `0` | Product not found on its retailer's captured bestseller list |
| `NULL` | Listing status could not be determined |

**Important:** A value of `0` means the product was not found in the captured listing, not that it is a confirmed non-bestseller.

### Classification Checks

- Confirm the retailer source matches the product URL.
- Review the automatically assigned bestseller status.
- Flag incorrect or uncertain classifications for verification.
- Do not assign bestseller status using the other retailer's listing.

**Listing reference:** Sephora's current classification script uses a snapshot captured on October 22, 2026. Ulta retrieves its bestseller-sorted listing during classification. Record additional listing dates and coverage details when available.

### Duplicate Checks

The application checks for existing products before saving new information.

| Situation | Action |
|---|---|
| New foundation product | Save the product and its retailer observation |
| Existing product, new retailer | Add the retailer observation to the existing product |
| Existing product, same retailer | Check whether the observation is already recorded |
| New observation collected on a later date | Preserve it as an additional observation |
| Duplicate entry or conflicting product information | Flag for review before correction |

Do not delete historical observations during routine collection.
For the final analysis, the most recent verified observation will represent each product–retailer pair.

### Collection Records

Each saved retailer observation should include:

- Product identifier (`product_id`)
- Retailer source (`source`)
- Product URL (`source_url`)
- Collection date (`collection_date`)
- Bestseller classification (`bestseller_list`)

These fields allow the team to trace each observation back to its retailer source.

**Detailed classification rules:** [Research Methodology](Research_Methodology.md)

## 4. Data Verification & Manual Corrections

### Verification Requirements

After selecting the final sample, verify the collected information against the corresponding retailer's product page and available collection records.

| Verification Level | Variables | Requirement |
|---|---|---|
| Primary | Bestseller status, price, review count, average rating, shade count | Verify all selected records |
| Secondary | Finish, coverage, SPF, skincare benefits, non-comedogenic claims, size, packaging, undertones, wear duration | Audit 20% of selected records |

The secondary audit will include 20 records: five randomly selected from each retailer–bestseller group.

**Note:** Any secondary characteristic used in the final analysis must be verified for every applicable selected record.

### Verification Steps

1. Open the saved product URL (`source_url`).
2. Confirm the product name, brand, and retailer.
3. Compare the recorded values with available retailer information.
4. Check bestseller classification against the appropriate retailer listing evidence.
5. Identify missing, incorrect, or uncertain values.
6. Document corrections and unresolved issues.

### Handling Missing Information

| Situation | Action |
|---|---|
| Information available but missed by scraper | Correct the value |
| Incorrect value extracted | Replace with verified value |
| Information not reported by retailer | Retain `NULL` where appropriate |
| Information cannot be verified | Flag as uncertain |
| Product claim not found | Record `0` according to the documented claim rules |

For product claims, `0` means the claim was not found on the corresponding retailer's product page. It does not prove that the product lacks the characteristic.

### Manual Correction Log

Record each correction using the following format:

| Field | Description |
|---|---|
| Product ID | `product_id` |
| Observation ID | `observation_id` |
| Variable | Field being corrected |
| Original value | Value before correction |
| Corrected value | Verified replacement |
| Source | Retailer webpage or supporting evidence |
| Verification date | Date the information was checked |
| Reason | Explanation for the correction |

### Correction Rules

- Correct values only when reliable evidence is available.
- Do not guess missing information.
- Document changes before applying them to the selected dataset.
- Preserve the original collected records in `foundation.db`.
- Investigate suspicious values even when they fall outside the random audit.

### Final Verification Check

Before analysis, confirm that:

- Required variables have been verified.
- The secondary audit is complete.
- Corrections and unresolved issues are documented.
- Each selected product–retailer pair has one verified observation.
- The final sample contains no unintended duplicate pairs.

**Detailed verification standards:** [Research Methodology](Research_Methodology.md)

## 5. Sampling, Collection Failures & Final Checks

### Final Sample Selection

Once the candidate inventory has been collected, the team will randomly select 100 product–retailer pairs.

| Retailer | Listed | Unlisted | Total |
|---|---:|---:|---:|
| Ulta | 25 | 25 | 50 |
| Sephora | 25 | 25 | 50 |
| **Total** | **50** | **50** | **100** |

### Sampling Procedure

1. Confirm products meet their retailer's foundation-category requirements.
2. Check product identities and retailer-specific bestseller labels.
3. Retain the most recent verified observation for each product–retailer pair.
4. Group eligible records by retailer and bestseller status.
5. Randomly select 25 records from each group using seed `6022026`.
6. Save selected records in `sampling.db`.
7. Record selected IDs, exclusions, and the random selection procedure.

### Collection & Verification Failures

| Issue | Action |
|---|---|
| Product URL unavailable | Record the problem and retry when appropriate |
| Scraper fails | Record the error and investigate |
| Required information cannot be verified | Flag for review |
| Incorrect retailer or ineligible product | Exclude from the eligible candidate pool |
| Duplicate product–retailer pair | Apply the approved observation selection rule |
| Selected record fails verification | Document the reason and use the next eligible candidate in the original randomized order |
| Insufficient candidates in a group | Expand collection where possible and document any shortfall |

Do not invent missing values or change bestseller labels to meet sampling targets.