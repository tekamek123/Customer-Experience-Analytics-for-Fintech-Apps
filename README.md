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
├── scrape_reviews.py     # Web scraping script
├── preprocess_reviews.py  # Data preprocessing script
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

## Data Schema

The cleaned CSV file contains the following columns:

- **review**: Review text content
- **rating**: Star rating (1-5)
- **date**: Review date in YYYY-MM-DD format
- **bank**: Bank name (Commercial Bank of Ethiopia, Bank of Abyssinia, or Dashen Bank)
- **source**: Data source (Google Play Store)

## Key Performance Indicators (KPIs)

- ✅ **Data Collection**: 1,200+ reviews collected
- ✅ **Data Quality**: <5% missing data
- ✅ **Per Bank**: Minimum 400 reviews per bank
- ✅ **Clean Dataset**: Properly formatted CSV with all required columns

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

## Git Workflow

This project uses the `task-1` branch for Task 1 deliverables:

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

## Notes

- The scraper includes rate limiting to respect Google Play Store's terms of service
- If scraping fails, check the app IDs and ensure they are correct
- The preprocessing script will report data quality metrics to ensure KPIs are met
- All data files are saved in UTF-8 encoding to handle special characters

## Next Steps (Future Tasks)

- Task 2: Sentiment Analysis and Theme Extraction
- Task 3: Database Design and Implementation
- Task 4: Data Visualization and Reporting

## Contact

For questions or issues, please contact the facilitators:
- Kerod
- Mahbubah
- Filimon

Or visit the Slack channel: #all-week-2

