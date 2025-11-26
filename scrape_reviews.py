"""
Web Scraping Script for Google Play Store Reviews
Scrapes reviews for three Ethiopian banks: CBE, BOA, and Dashen Bank
"""

import json
from google_play_scraper import app, reviews, Sort
import pandas as pd
from datetime import datetime
import time

# Bank app information
# Note: These are placeholder app IDs - you may need to update with actual app IDs
BANK_APPS = {
    "Commercial Bank of Ethiopia": {
        "app_id": "com.cbe.mobilebanking",  # Update with actual app ID
        "target_reviews": 400
    },
    "Bank of Abyssinia": {
        "app_id": "com.bankofabyssinia.mobilebanking",  # Update with actual app ID
        "target_reviews": 400
    },
    "Dashen Bank": {
        "app_id": "com.dashen.mobilebanking",  # Update with actual app ID
        "target_reviews": 400
    }
}


def scrape_app_reviews(app_id, app_name, target_count=400):
    """
    Scrape reviews from Google Play Store for a given app.
    
    Args:
        app_id: Google Play Store app ID
        app_name: Name of the bank/app
        target_count: Target number of reviews to scrape
    
    Returns:
        List of review dictionaries
    """
    print(f"\nScraping reviews for {app_name} (App ID: {app_id})...")
    
    all_reviews = []
    continuation_token = None
    attempts = 0
    max_attempts = 10
    
    try:
        while len(all_reviews) < target_count and attempts < max_attempts:
            try:
                if continuation_token:
                    result, continuation_token = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort=Sort.NEWEST,
                        count=200,
                        continuation_token=continuation_token
                    )
                else:
                    result, continuation_token = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort=Sort.NEWEST,
                        count=200
                    )
                
                all_reviews.extend(result)
                print(f"  Collected {len(all_reviews)} reviews so far...")
                
                if not continuation_token:
                    print(f"  No more reviews available. Collected {len(all_reviews)} reviews.")
                    break
                
                # Rate limiting to avoid being blocked
                time.sleep(2)
                attempts += 1
                
            except Exception as e:
                print(f"  Error during scraping: {str(e)}")
                attempts += 1
                time.sleep(5)
        
        print(f"✓ Successfully collected {len(all_reviews)} reviews for {app_name}")
        return all_reviews[:target_count]  # Return only the target count
        
    except Exception as e:
        print(f"✗ Failed to scrape reviews for {app_name}: {str(e)}")
        return []


def format_reviews(reviews_list, bank_name):
    """
    Format scraped reviews into a standardized structure.
    
    Args:
        reviews_list: List of review dictionaries from scraper
        bank_name: Name of the bank
    
    Returns:
        List of formatted review dictionaries
    """
    formatted = []
    
    for review in reviews_list:
        formatted_review = {
            'review': review.get('content', ''),
            'rating': review.get('score', 0),
            'date': review.get('at', '').strftime('%Y-%m-%d') if review.get('at') else '',
            'bank': bank_name,
            'source': 'Google Play Store'
        }
        formatted.append(formatted_review)
    
    return formatted


def main():
    """Main function to scrape reviews for all banks."""
    print("=" * 60)
    print("Google Play Store Review Scraper")
    print("=" * 60)
    
    all_reviews = []
    
    for bank_name, app_info in BANK_APPS.items():
        app_id = app_info['app_id']
        target = app_info['target_reviews']
        
        # Scrape reviews
        raw_reviews = scrape_app_reviews(app_id, bank_name, target)
        
        # Format reviews
        formatted_reviews = format_reviews(raw_reviews, bank_name)
        all_reviews.extend(formatted_reviews)
        
        # Save raw data for each bank (optional backup)
        if formatted_reviews:
            df_bank = pd.DataFrame(formatted_reviews)
            output_file = f"data/raw/reviews_{bank_name.replace(' ', '_')}_raw.csv"
            df_bank.to_csv(output_file, index=False, encoding='utf-8')
            print(f"  Saved raw data to {output_file}")
    
    # Save all reviews to a single CSV
    if all_reviews:
        df_all = pd.DataFrame(all_reviews)
        output_file = "data/raw/all_reviews_raw.csv"
        df_all.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ Total reviews collected: {len(all_reviews)}")
        print(f"✓ Saved all reviews to {output_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Collection Summary:")
        print("=" * 60)
        for bank_name in BANK_APPS.keys():
            bank_count = len([r for r in all_reviews if r['bank'] == bank_name])
            print(f"  {bank_name}: {bank_count} reviews")
        print("=" * 60)
    else:
        print("\n✗ No reviews were collected. Please check app IDs and try again.")


if __name__ == "__main__":
    import os
    
    # Create data directory if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    
    main()

