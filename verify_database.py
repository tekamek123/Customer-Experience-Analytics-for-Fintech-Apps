"""
Verify Database Data Integrity
Runs SQL queries to verify data was inserted correctly
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get database connection."""
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'bank_reviews'
    }
    
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def run_verification_queries():
    """Run verification queries to check data integrity."""
    print("=" * 60)
    print("Database Verification Queries")
    print("=" * 60)
    
    conn = get_db_connection()
    if not conn:
        print("✗ Failed to connect to database.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Query 1: Total reviews count
        print("\n[Query 1] Total Reviews Count")
        print("-" * 60)
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]
        print(f"Total reviews in database: {total_reviews:,}")
        
        # Query 2: Reviews per bank
        print("\n[Query 2] Reviews Count by Bank")
        print("-" * 60)
        cursor.execute("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY review_count DESC
        """)
        print(f"{'Bank Name':<40} {'Review Count':>15}")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:<40} {row[1]:>15,}")
        
        # Query 3: Average rating per bank
        print("\n[Query 3] Average Rating by Bank")
        print("-" * 60)
        cursor.execute("""
            SELECT b.bank_name, 
                   ROUND(AVG(r.rating), 2) as avg_rating,
                   COUNT(r.review_id) as review_count
            FROM banks b
            JOIN reviews r ON b.bank_id = r.bank_id
            WHERE r.rating IS NOT NULL
            GROUP BY b.bank_id, b.bank_name
            ORDER BY avg_rating DESC
        """)
        print(f"{'Bank Name':<40} {'Avg Rating':>12} {'Count':>10}")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:<40} {row[1]:>12} {row[2]:>10,}")
        
        # Query 4: Rating distribution
        print("\n[Query 4] Rating Distribution")
        print("-" * 60)
        cursor.execute("""
            SELECT rating, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews WHERE rating IS NOT NULL), 2) as percentage
            FROM reviews
            WHERE rating IS NOT NULL
            GROUP BY rating
            ORDER BY rating
        """)
        print(f"{'Rating':<10} {'Count':>12} {'Percentage':>12}")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:<10} {row[1]:>12,} {row[2]:>11}%")
        
        # Query 5: Sentiment distribution
        print("\n[Query 5] Sentiment Distribution")
        print("-" * 60)
        cursor.execute("""
            SELECT sentiment_label, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NOT NULL), 2) as percentage
            FROM reviews
            WHERE sentiment_label IS NOT NULL
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        print(f"{'Sentiment':<15} {'Count':>12} {'Percentage':>12}")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:<15} {row[1]:>12,} {row[2]:>11}%")
        
        # Query 6: Reviews with sentiment analysis
        print("\n[Query 6] Sentiment Analysis Coverage")
        print("-" * 60)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                COUNT(sentiment_label) as reviews_with_sentiment,
                ROUND(COUNT(sentiment_label) * 100.0 / COUNT(*), 2) as coverage_percentage
            FROM reviews
        """)
        row = cursor.fetchone()
        print(f"Total reviews: {row[0]:,}")
        print(f"Reviews with sentiment: {row[1]:,}")
        print(f"Coverage: {row[2]}%")
        
        # Query 7: Date range of reviews
        print("\n[Query 7] Review Date Range")
        print("-" * 60)
        cursor.execute("""
            SELECT 
                MIN(review_date) as earliest_review,
                MAX(review_date) as latest_review,
                COUNT(*) as reviews_with_dates
            FROM reviews
            WHERE review_date IS NOT NULL
        """)
        row = cursor.fetchone()
        if row[0]:
            print(f"Earliest review: {row[0]}")
            print(f"Latest review: {row[1]}")
            print(f"Reviews with dates: {row[2]:,}")
        else:
            print("No reviews with dates found")
        
        # Query 8: Average sentiment score by bank
        print("\n[Query 8] Average Sentiment Score by Bank")
        print("-" * 60)
        cursor.execute("""
            SELECT b.bank_name,
                   ROUND(AVG(r.sentiment_score), 4) as avg_sentiment_score,
                   COUNT(r.review_id) as review_count
            FROM banks b
            JOIN reviews r ON b.bank_id = r.bank_id
            WHERE r.sentiment_score IS NOT NULL
            GROUP BY b.bank_id, b.bank_name
            ORDER BY avg_sentiment_score DESC
        """)
        print(f"{'Bank Name':<40} {'Avg Score':>12} {'Count':>10}")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:<40} {row[1]:>12} {row[2]:>10,}")
        
        # Query 9: Data quality check
        print("\n[Query 9] Data Quality Check")
        print("-" * 60)
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(review_text) as has_text,
                COUNT(rating) as has_rating,
                COUNT(review_date) as has_date,
                COUNT(sentiment_label) as has_sentiment
            FROM reviews
        """)
        row = cursor.fetchone()
        print(f"Total reviews: {row[0]:,}")
        print(f"With review text: {row[1]:,} ({row[1]*100/row[0]:.1f}%)")
        print(f"With rating: {row[2]:,} ({row[2]*100/row[0]:.1f}%)")
        print(f"With date: {row[3]:,} ({row[3]*100/row[0]:.1f}%)")
        print(f"With sentiment: {row[4]:,} ({row[4]*100/row[0]:.1f}%)")
        
        print("\n" + "=" * 60)
        print("Verification Complete!")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n✗ Error running queries: {e}")
        cursor.close()
        conn.close()


def main():
    """Main function."""
    run_verification_queries()


if __name__ == "__main__":
    main()

