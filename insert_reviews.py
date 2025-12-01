"""
Insert Cleaned Review Data into PostgreSQL Database
Reads cleaned reviews CSV and inserts them into the database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
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


def get_or_create_bank(conn, bank_name, app_name=None):
    """
    Get bank_id for a bank, creating it if it doesn't exist.
    
    Args:
        conn: Database connection
        bank_name: Name of the bank
        app_name: Name of the app (optional)
    
    Returns:
        bank_id
    """
    cursor = conn.cursor()
    
    # Try to get existing bank
    cursor.execute("SELECT bank_id FROM banks WHERE bank_name = %s", (bank_name,))
    result = cursor.fetchone()
    
    if result:
        bank_id = result[0]
    else:
        # Create new bank
        cursor.execute(
            "INSERT INTO banks (bank_name, app_name) VALUES (%s, %s) RETURNING bank_id",
            (bank_name, app_name or bank_name)
        )
        bank_id = cursor.fetchone()[0]
        conn.commit()
        print(f"  Created bank: {bank_name} (ID: {bank_id})")
    
    cursor.close()
    return bank_id


def insert_reviews_from_csv(csv_file="data/processed/reviews_cleaned.csv", 
                           analyzed_file="data/processed/reviews_analyzed.csv"):
    """
    Insert reviews from CSV files into the database.
    
    Args:
        csv_file: Path to cleaned reviews CSV
        analyzed_file: Path to analyzed reviews CSV (with sentiment data)
    """
    print("=" * 60)
    print("Inserting Reviews into PostgreSQL Database")
    print("=" * 60)
    
    # Connect to database
    conn = get_db_connection()
    if not conn:
        print("✗ Failed to connect to database. Please run database_setup.py first.")
        return
    
    try:
        # Try to load analyzed reviews first (has sentiment data)
        if os.path.exists(analyzed_file):
            print(f"\nLoading analyzed reviews from {analyzed_file}...")
            df = pd.read_csv(analyzed_file)
            has_sentiment = True
        elif os.path.exists(csv_file):
            print(f"\nLoading cleaned reviews from {csv_file}...")
            df = pd.read_csv(csv_file)
            has_sentiment = False
            # Add empty sentiment columns if not present
            if 'sentiment_label' not in df.columns:
                df['sentiment_label'] = None
            if 'sentiment_score' not in df.columns:
                df['sentiment_score'] = None
        else:
            print(f"✗ Error: Neither {csv_file} nor {analyzed_file} found.")
            print("  Please run preprocess_reviews.py and analysis_pipeline.py first.")
            return
        
        print(f"✓ Loaded {len(df)} reviews")
        
        # Map column names
        column_mapping = {
            'review': 'review_text',
            'review_text': 'review_text',
            'date': 'review_date',
            'review_date': 'review_date',
            'bank': 'bank_name',
            'source': 'source'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_cols = ['review_text', 'rating', 'bank_name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"✗ Error: Missing required columns: {missing_cols}")
            return
        
        # Fill missing values
        df['review_date'] = df.get('review_date', pd.Series()).fillna('')
        df['sentiment_label'] = df.get('sentiment_label', pd.Series()).fillna(None)
        df['sentiment_score'] = df.get('sentiment_score', pd.Series()).fillna(None)
        df['source'] = df.get('source', 'Google Play Store')
        
        # Get or create banks and map bank names to IDs
        print("\nProcessing banks...")
        bank_id_map = {}
        for bank_name in df['bank_name'].unique():
            bank_id = get_or_create_bank(conn, bank_name)
            bank_id_map[bank_name] = bank_id
        
        # Prepare review data for insertion
        print("\nPreparing review data...")
        reviews_data = []
        
        for _, row in df.iterrows():
            bank_id = bank_id_map[row['bank_name']]
            
            # Handle date conversion
            review_date = None
            if pd.notna(row.get('review_date')) and str(row['review_date']).strip():
                try:
                    review_date = pd.to_datetime(row['review_date']).date()
                except:
                    review_date = None
            
            # Handle sentiment_score conversion
            sentiment_score = None
            if pd.notna(row.get('sentiment_score')):
                try:
                    sentiment_score = float(row['sentiment_score'])
                except:
                    sentiment_score = None
            
            reviews_data.append((
                bank_id,
                str(row['review_text'])[:10000],  # Limit text length
                int(row['rating']) if pd.notna(row['rating']) else None,
                review_date,
                str(row['sentiment_label']) if pd.notna(row['sentiment_label']) else None,
                sentiment_score,
                str(row['source']) if pd.notna(row.get('source')) else 'Google Play Store'
            ))
        
        # Insert reviews in batches
        print(f"\nInserting {len(reviews_data)} reviews...")
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO reviews 
            (bank_id, review_text, rating, review_date, sentiment_label, sentiment_score, source)
            VALUES %s
        """
        
        # Use execute_values for batch insertion
        execute_values(
            cursor,
            insert_query,
            reviews_data,
            page_size=1000
        )
        
        conn.commit()
        print(f"✓ Successfully inserted {len(reviews_data)} reviews")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Data insertion complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error inserting data: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()


def main():
    """Main function."""
    insert_reviews_from_csv()


if __name__ == "__main__":
    main()

