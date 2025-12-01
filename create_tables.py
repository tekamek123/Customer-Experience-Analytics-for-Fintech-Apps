"""
Simple script to create tables directly
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres'),
    database='bank_reviews'
)

cur = conn.cursor()

# Create banks table
cur.execute("""
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(255) NOT NULL UNIQUE,
    app_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create reviews table
cur.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label VARCHAR(20),
    sentiment_score DECIMAL(5, 4),
    source VARCHAR(100) DEFAULT 'Google Play Store',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES banks(bank_id) ON DELETE CASCADE
);
""")

# Create indexes
cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label);")

conn.commit()
print("[OK] Tables created successfully!")

cur.close()
conn.close()

