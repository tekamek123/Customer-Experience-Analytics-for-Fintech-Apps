# Customer Experience Analytics for Fintech Apps

## Week 2 Project: Google Play Store Review Analysis

This project analyzes customer satisfaction with mobile banking apps by collecting and processing user reviews from the Google Play Store for three Ethiopian banks:
- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

## Project Structure

```
week2/
├── data/
│   ├── raw/              # Raw scraped data
│   └── processed/        # Cleaned and processed data
├── scrape_reviews.py     # Web scraping script (Task 1)
├── preprocess_reviews.py  # Data preprocessing script (Task 1)
├── sentiment_analysis.py  # Sentiment analysis script (Task 2)
├── thematic_analysis.py   # Thematic analysis script (Task 2)
├── analysis_pipeline.py   # Main analysis pipeline (Task 2)
├── install_spacy_model.py # Helper to install spaCy model
├── database_schema.sql     # PostgreSQL database schema (Task 3)
├── database_setup.py      # Database setup script (Task 3)
├── insert_reviews.py      # Data insertion script (Task 3)
├── verify_database.py     # Database verification queries (Task 3)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Update App IDs

Before running the scraper, you need to update the app IDs in `scrape_reviews.py` with the actual Google Play Store app IDs for the three banks. You can find these by:
- Searching for the apps on Google Play Store
- Extracting the app ID from the URL (e.g., `com.cbe.mobilebanking`)

### 3. Run Data Collection

```bash
python scrape_reviews.py
```

This will:
- Scrape reviews from Google Play Store for all three banks
- Save raw data to `data/raw/` directory
- Target minimum 400 reviews per bank (1200 total)

### 4. Preprocess Data

```bash
python preprocess_reviews.py
```

This will:
- Remove duplicate reviews
- Handle missing data
- Normalize date formats to YYYY-MM-DD
- Save cleaned data to `data/processed/reviews_cleaned.csv`
- Generate data quality report

### 5. Install spaCy Model (Required for Task 2)

```bash
python install_spacy_model.py
```

Or manually:
```bash
python -m spacy download en_core_web_sm
```

### 6. Run Sentiment and Thematic Analysis (Task 2)

```bash
python analysis_pipeline.py
```

This will:
- Perform sentiment analysis using DistilBERT (with VADER fallback)
- Extract keywords and identify themes for each bank
- Assign themes to individual reviews
- Generate aggregation reports by bank and rating
- Save results to `data/processed/reviews_analyzed.csv`

The pipeline produces:
- **reviews_analyzed.csv**: Complete analysis with sentiment scores and themes
- **sentiment_aggregation.csv**: Sentiment statistics by bank and rating
- **theme_summary.csv**: Identified themes with top keywords per bank

### 7. Set Up PostgreSQL Database (Task 3)

**Prerequisites:**
- Install PostgreSQL on your system
- Create a database user with appropriate permissions

**Configuration:**
Create a `.env` file in the project root with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
```

**Setup:**
```bash
# Step 1: Create database and schema
python database_setup.py

# Step 2: Insert cleaned review data
python insert_reviews.py

# Step 3: Verify data integrity
python verify_database.py
```

This will:
- Create the `bank_reviews` database
- Create `banks` and `reviews` tables with proper schema
- Insert all cleaned review data from CSV files
- Run verification queries to check data integrity

## Database Schema

### PostgreSQL Database: `bank_reviews`

The database consists of two main tables:

#### Banks Table
Stores information about the banks being analyzed.

| Column | Type | Description |
|--------|------|-------------|
| `bank_id` | SERIAL PRIMARY KEY | Auto-incrementing unique identifier |
| `bank_name` | VARCHAR(255) | Full name of the bank (UNIQUE) |
| `app_name` | VARCHAR(255) | Name of the mobile banking application |
| `created_at` | TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | Record update timestamp |

#### Reviews Table
Stores the scraped and processed review data with sentiment analysis.

| Column | Type | Description |
|--------|------|-------------|
| `review_id` | SERIAL PRIMARY KEY | Auto-incrementing unique identifier |
| `bank_id` | INTEGER | Foreign key to `banks.bank_id` |
| `review_text` | TEXT | The actual review text content |
| `rating` | INTEGER | Star rating from 1 to 5 (CHECK constraint) |
| `review_date` | DATE | Date when the review was posted |
| `sentiment_label` | VARCHAR(20) | Sentiment: positive, negative, or neutral |
| `sentiment_score` | DECIMAL(5,4) | Confidence score (0.0 to 1.0) |
| `source` | VARCHAR(100) | Source of review (default: 'Google Play Store') |
| `created_at` | TIMESTAMP | Record creation timestamp |

**Indexes:**
- `idx_reviews_bank_id` on `bank_id` for faster joins
- `idx_reviews_rating` on `rating` for filtering
- `idx_reviews_date` on `review_date` for time-based queries
- `idx_reviews_sentiment` on `sentiment_label` for sentiment analysis

**Relationships:**
- `reviews.bank_id` → `banks.bank_id` (Foreign Key with CASCADE delete)

## Data Schema

### Cleaned Reviews (reviews_cleaned.csv)
- **review**: Review text content
- **rating**: Star rating (1-5)
- **date**: Review date in YYYY-MM-DD format
- **bank**: Bank name (Commercial Bank of Ethiopia, Bank of Abyssinia, or Dashen Bank)
- **source**: Data source (Google Play Store)

### Analyzed Reviews (reviews_analyzed.csv)
- **review_id**: Unique identifier for each review
- **review_text**: Review text content
- **rating**: Star rating (1-5)
- **date**: Review date in YYYY-MM-DD format
- **bank**: Bank name
- **source**: Data source
- **sentiment_label**: Sentiment classification (positive/negative/neutral)
- **sentiment_score**: Sentiment confidence score (0-1)
- **identified_themes**: Semicolon-separated list of themes (e.g., "Account Access Issues; Transaction Performance")

## Key Performance Indicators (KPIs)

### Task 1: Data Collection and Preprocessing
- ✅ **Data Collection**: 1,200+ reviews collected
- ✅ **Data Quality**: <5% missing data
- ✅ **Per Bank**: Minimum 400 reviews per bank
- ✅ **Clean Dataset**: Properly formatted CSV with all required columns

### Task 2: Sentiment and Thematic Analysis
- ✅ **Sentiment Coverage**: 90%+ reviews with sentiment scores
- ✅ **Theme Identification**: 3+ themes per bank with examples
- ✅ **Modular Pipeline**: Separate scripts for sentiment and thematic analysis
- ✅ **Aggregation Reports**: Sentiment and theme statistics by bank and rating

### Task 3: Database Design and Implementation
- ✅ **Database Setup**: PostgreSQL database `bank_reviews` created
- ✅ **Schema Design**: Two-table relational schema with proper indexes
- ✅ **Data Insertion**: Python script successfully inserts 1,200+ reviews
- ✅ **Data Verification**: SQL queries verify data integrity and quality
- ✅ **Documentation**: Schema documented in README and SQL comments

## Methodology

### Web Scraping
- Uses `google-play-scraper` library to collect reviews
- Sorts by newest reviews first
- Implements rate limiting to avoid being blocked
- Handles errors gracefully with retry logic

### Data Preprocessing
1. **Duplicate Removal**: Removes duplicate reviews based on review text and bank
2. **Missing Data Handling**: 
   - Removes rows with empty review text
   - Validates ratings (must be 1-5)
   - Handles missing dates gracefully
3. **Date Normalization**: Converts various date formats to YYYY-MM-DD
4. **Data Quality Checks**: Calculates and reports data quality metrics

### Sentiment Analysis
- **Primary Method**: DistilBERT-base-uncased-finetuned-sst-2-english (transformer model)
- **Fallback Method**: VADER (rule-based sentiment analyzer)
- **Output**: Sentiment label (positive/negative/neutral) and confidence score
- **Aggregation**: Mean sentiment scores by bank and rating

### Thematic Analysis
- **Keyword Extraction**: 
  - TF-IDF vectorization for n-grams (1-2 words)
  - spaCy for POS tagging and lemmatization
- **Theme Identification**: Rule-based clustering into 3-5 themes per bank:
  - Account Access Issues
  - Transaction Performance
  - User Interface & Experience
  - App Reliability & Bugs
  - Customer Support
  - Security & Privacy
  - Feature Requests
- **Theme Assignment**: Keywords matched to review text to assign themes

## Git Workflow

This project uses separate branches for each task:

### Task 1 Branch
```bash
# Create and switch to task-1 branch
git checkout -b task-1

# Add files
git add .

# Commit with meaningful messages
git commit -m "Add initial project structure and scraping scripts"

# Push to remote
git push origin task-1
```

### Task 2 Branch
```bash
# Create and switch to task-2 branch
git checkout -b task-2

# Add analysis scripts
git add sentiment_analysis.py thematic_analysis.py analysis_pipeline.py

# Commit
git commit -m "Add sentiment and thematic analysis pipeline"

# Push to remote
git push origin task-2
```

### Task 3 Branch
```bash
# Create and switch to task-3 branch
git checkout -b task-3

# Add database files
git add database_schema.sql database_setup.py insert_reviews.py verify_database.py

# Commit
git commit -m "Add PostgreSQL database schema and data insertion scripts"

# Push to remote
git push origin task-3
```

## Notes

- The scraper includes rate limiting to respect Google Play Store's terms of service
- If scraping fails, check the app IDs and ensure they are correct
- The preprocessing script will report data quality metrics to ensure KPIs are met
- All data files are saved in UTF-8 encoding to handle special characters

## Task Status

- ✅ **Task 1**: Data Collection and Preprocessing - Complete
- ✅ **Task 2**: Sentiment and Thematic Analysis - Complete
- ✅ **Task 3**: Database Design and Implementation - Complete
- ⏳ **Task 4**: Data Visualization and Reporting - Pending

## Contact

For questions or issues, please contact the facilitators:
- Kerod
- Mahbubah
- Filimon

Or visit the Slack channel: #all-week-2

