"""
Data Preprocessing Script
Cleans and normalizes scraped review data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os


def load_raw_data(input_file="data/raw/all_reviews_raw.csv"):
    """
    Load raw review data from CSV.
    
    Args:
        input_file: Path to raw CSV file
    
    Returns:
        DataFrame with raw review data
    """
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"✓ Loaded {len(df)} reviews from {input_file}")
        return df
    except FileNotFoundError:
        print(f"✗ Error: File {input_file} not found. Please run scrape_reviews.py first.")
        return None
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return None


def remove_duplicates(df):
    """
    Remove duplicate reviews based on review text and bank.
    
    Args:
        df: DataFrame with review data
    
    Returns:
        DataFrame with duplicates removed
    """
    initial_count = len(df)
    df = df.drop_duplicates(subset=['review', 'bank'], keep='first')
    removed = initial_count - len(df)
    
    if removed > 0:
        print(f"✓ Removed {removed} duplicate reviews")
    
    return df


def handle_missing_data(df):
    """
    Handle missing data in the dataset.
    
    Args:
        df: DataFrame with review data
    
    Returns:
        DataFrame with missing data handled
    """
    initial_count = len(df)
    
    # Remove rows where review text is completely missing
    df = df[df['review'].notna() & (df['review'].str.strip() != '')]
    
    # Fill missing ratings with 0 (will be marked for removal if needed)
    df['rating'] = df['rating'].fillna(0)
    
    # Remove rows with invalid ratings (should be 1-5)
    df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
    
    # Handle missing dates - set to empty string or current date
    df['date'] = df['date'].fillna('')
    
    # Fill missing bank names (shouldn't happen, but just in case)
    df['bank'] = df['bank'].fillna('Unknown')
    df['source'] = df['source'].fillna('Google Play Store')
    
    removed = initial_count - len(df)
    if removed > 0:
        print(f"✓ Removed {removed} rows with missing/invalid data")
    
    return df


def normalize_dates(df):
    """
    Normalize date formats to YYYY-MM-DD.
    
    Args:
        df: DataFrame with review data
    
    Returns:
        DataFrame with normalized dates
    """
    def parse_date(date_str):
        """Parse various date formats to YYYY-MM-DD."""
        if pd.isna(date_str) or date_str == '':
            return ''
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y'
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        # If all formats fail, try pandas parser
        try:
            dt = pd.to_datetime(date_str)
            return dt.strftime('%Y-%m-%d')
        except:
            return ''
    
    df['date'] = df['date'].apply(parse_date)
    
    # Count successfully parsed dates
    parsed_count = len(df[df['date'] != ''])
    print(f"✓ Normalized dates: {parsed_count}/{len(df)} reviews have valid dates")
    
    return df


def calculate_data_quality_metrics(df):
    """
    Calculate data quality metrics.
    
    Args:
        df: DataFrame with review data
    
    Returns:
        Dictionary with quality metrics
    """
    total = len(df)
    
    metrics = {
        'total_reviews': total,
        'missing_review_text': len(df[df['review'].isna() | (df['review'].str.strip() == '')]),
        'missing_rating': len(df[df['rating'].isna() | (df['rating'] == 0)]),
        'missing_date': len(df[df['date'].isna() | (df['date'] == '')]),
        'missing_bank': len(df[df['bank'].isna()]),
    }
    
    metrics['missing_data_percentage'] = (
        (metrics['missing_review_text'] + 
         metrics['missing_rating'] + 
         metrics['missing_date'] + 
         metrics['missing_bank']) / (total * 4) * 100
        if total > 0 else 0
    )
    
    return metrics


def main():
    """Main preprocessing function."""
    print("=" * 60)
    print("Review Data Preprocessing")
    print("=" * 60)
    
    # Load raw data
    df = load_raw_data()
    
    if df is None or len(df) == 0:
        print("✗ No data to process. Exiting.")
        return
    
    print(f"\nInitial dataset: {len(df)} reviews")
    
    # Remove duplicates
    df = remove_duplicates(df)
    
    # Handle missing data
    df = handle_missing_data(df)
    
    # Normalize dates
    df = normalize_dates(df)
    
    # Ensure correct column order
    df = df[['review', 'rating', 'date', 'bank', 'source']]
    
    # Calculate quality metrics
    metrics = calculate_data_quality_metrics(df)
    
    # Print quality report
    print("\n" + "=" * 60)
    print("Data Quality Report:")
    print("=" * 60)
    print(f"Total reviews: {metrics['total_reviews']}")
    print(f"Missing review text: {metrics['missing_review_text']}")
    print(f"Missing ratings: {metrics['missing_rating']}")
    print(f"Missing dates: {metrics['missing_date']}")
    print(f"Missing bank names: {metrics['missing_bank']}")
    print(f"Overall missing data: {metrics['missing_data_percentage']:.2f}%")
    print("=" * 60)
    
    # Check if quality meets KPI (<5% missing data)
    if metrics['missing_data_percentage'] < 5:
        print("✓ Data quality meets KPI requirement (<5% missing data)")
    else:
        print("⚠ Warning: Data quality is below KPI requirement (<5% missing data)")
    
    # Check if we have enough reviews (1200+)
    if metrics['total_reviews'] >= 1200:
        print(f"✓ Review count meets requirement (1200+ reviews)")
    else:
        print(f"⚠ Warning: Review count ({metrics['total_reviews']}) is below requirement (1200+)")
    
    # Save processed data
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/reviews_cleaned.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Saved cleaned data to {output_file}")
    
    # Print summary by bank
    print("\n" + "=" * 60)
    print("Summary by Bank:")
    print("=" * 60)
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        print(f"  {bank}: {len(bank_df)} reviews")
    print("=" * 60)


if __name__ == "__main__":
    main()

