## Product Characteristics & Consumer Demand Analysis
A Python-based research data pipeline built to analyze the relationships between cosmetic foundation product characteristics and consumer demand. 

### Core Capabilities

- Structured Data Collection
- Multi-Source Tracking
- Input Validation
- Relational Data Storage
- Data Exploration

### Installation

**Requirements**
- Python 3.14+
- pip
- Git

**Core Dependencies**
- `pandas`
- `matplotlib`

**Install Dependencies**
```
pip install pandas matplotlib
```

**Run the Application**
- Clone the repository and navigate to the project directory:
```
git clone https://github.com/sanjida03/DATA602_Fall2026_Group1.git
cd DATA602_Fall2026_Group1
```

**Run the data collection application**
```
python foundation_app.py
```
The application will initialize and connect to the SQLite database used to store product characteristics and consumer demand observations.

### Repository Structure
- `foundation_app.py` | CLI application for product and observation data collection
- `foundation.db` | SQLite database used to store product and demand data
- `README.md` | project overview, setup, and usage instructions
- `requirements.txt` | Python package dependencies

### Data Collected

The dataset combines **product characteristics** with **consumer demand indicators** collected from multiple public sources.

https://drive.google.com/file/d/1FjLIm28nfKcOfSPkFZTapeecfGn4plPc/view?usp=sharing 

**Product Characteristics**
- Brand
- Product name
- Size
- Shade count
- Undertone count
- Finish type
- Coverage level
- Packaging material
- Celebrity founded
- Non-comedogenic
- Skincare benefits
- SPF presence
- Wear claim hours

**Consumer Demand Indicators**
- Price
- TikTok units sold
- Bestseller status
- Review count
- Collection source
- Collection source URL
- Collection date

### Data-Pipeline Structure

```text
Git Repository
↓
foundation_database.py | Creates the SQLite schema
↓
foundation_app.py | collects and stores product and observation data
↓
clean_validate.py | validates data quality
↓
Processed Data
↓
Analysis & Visualizations
```

### Data Source
Product and demand data are collected from multiple public sources, including:
- **TikTok Shop** | https://shop.tiktok.com/us
- **Ulta** | https://www.ulta.com/
- **Sephora** | https://www.sephora.com/
- **Brand websites**

### Database Structure
- `products` | stores product characteristics
- `product_observations` | stores source specific demand metrics
- `product_id` | links observations to the correct product
