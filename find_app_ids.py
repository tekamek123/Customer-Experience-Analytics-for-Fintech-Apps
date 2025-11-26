"""
Helper script to find Google Play Store app IDs for the three banks.
This script uses the google-play-scraper library to search for apps.
"""

from google_play_scraper import search

def find_app_id(bank_name, keywords):
    """
    Search for app ID by bank name and keywords.
    
    Args:
        bank_name: Name of the bank
        keywords: List of search keywords
    """
    print(f"\nSearching for {bank_name} app...")
    print(f"Keywords: {', '.join(keywords)}")
    print("-" * 60)
    
    for keyword in keywords:
        try:
            results = search(keyword, lang='en', country='us', n_hits=5)
            
            if results:
                print(f"\nResults for '{keyword}':")
                for i, app in enumerate(results, 1):
                    print(f"\n{i}. {app.get('title', 'N/A')}")
                    print(f"   App ID: {app.get('appId', 'N/A')}")
                    print(f"   Developer: {app.get('developer', 'N/A')}")
                    print(f"   Score: {app.get('score', 'N/A')}")
                    print(f"   Installs: {app.get('installs', 'N/A')}")
                    
                # Check if any result matches the bank name
                for app in results:
                    title = app.get('title', '').lower()
                    if any(word in title for word in bank_name.lower().split()):
                        print(f"\n✓ Potential match found!")
                        print(f"  App ID: {app.get('appId')}")
                        return app.get('appId')
        except Exception as e:
            print(f"  Error searching for '{keyword}': {str(e)}")
            continue
    
    print("\n⚠ No exact match found. Please manually verify the app ID from Google Play Store.")
    return None


def main():
    """Main function to find app IDs for all banks."""
    print("=" * 60)
    print("Google Play Store App ID Finder")
    print("=" * 60)
    print("\nThis script helps you find the correct app IDs.")
    print("Update the app IDs in scrape_reviews.py after finding them.\n")
    
    banks = {
        "Commercial Bank of Ethiopia": [
            "commercial bank ethiopia",
            "cbe mobile banking",
            "cbe mobile",
            "commercial bank ethiopia mobile"
        ],
        "Bank of Abyssinia": [
            "bank of abyssinia",
            "boa mobile banking",
            "boa mobile",
            "abyssinia bank mobile"
        ],
        "Dashen Bank": [
            "dashen bank",
            "dashen mobile banking",
            "dashen mobile",
            "dashen bank mobile"
        ]
    }
    
    app_ids = {}
    
    for bank_name, keywords in banks.items():
        app_id = find_app_id(bank_name, keywords)
        if app_id:
            app_ids[bank_name] = app_id
    
    if app_ids:
        print("\n" + "=" * 60)
        print("Recommended App IDs:")
        print("=" * 60)
        for bank, app_id in app_ids.items():
            print(f"{bank}: {app_id}")
        print("\nCopy these to scrape_reviews.py in the BANK_APPS dictionary.")
    else:
        print("\n" + "=" * 60)
        print("Manual Search Instructions:")
        print("=" * 60)
        print("1. Go to Google Play Store (play.google.com)")
        print("2. Search for each bank's mobile banking app")
        print("3. Open the app page")
        print("4. The app ID is in the URL: play.google.com/store/apps/details?id=APP_ID")
        print("5. Update scrape_reviews.py with the correct app IDs")


if __name__ == "__main__":
    main()

