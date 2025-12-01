-- PostgreSQL Database Schema for Bank Reviews Analysis
-- Database: bank_reviews

-- Create database (run this separately as superuser)
-- CREATE DATABASE bank_reviews;

-- Connect to bank_reviews database before running the following

-- ============================================
-- BANKS TABLE
-- ============================================
-- Stores information about the banks
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(255) NOT NULL UNIQUE,
    app_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- REVIEWS TABLE
-- ============================================
-- Stores the scraped and processed review data
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

-- ============================================
-- INDEXES for Performance
-- ============================================
-- Index on bank_id for faster joins
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id);

-- Index on rating for faster filtering
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);

-- Index on review_date for time-based queries
CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date);

-- Index on sentiment_label for sentiment analysis queries
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label);

-- ============================================
-- COMMENTS for Documentation
-- ============================================
COMMENT ON TABLE banks IS 'Stores information about the banks being analyzed';
COMMENT ON TABLE reviews IS 'Stores scraped and processed review data with sentiment analysis';

COMMENT ON COLUMN banks.bank_id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN banks.bank_name IS 'Full name of the bank';
COMMENT ON COLUMN banks.app_name IS 'Name of the mobile banking application';

COMMENT ON COLUMN reviews.review_id IS 'Primary key, auto-incrementing';
COMMENT ON COLUMN reviews.bank_id IS 'Foreign key referencing banks table';
COMMENT ON COLUMN reviews.review_text IS 'The actual review text content';
COMMENT ON COLUMN reviews.rating IS 'Star rating from 1 to 5';
COMMENT ON COLUMN reviews.review_date IS 'Date when the review was posted';
COMMENT ON COLUMN reviews.sentiment_label IS 'Sentiment classification: positive, negative, or neutral';
COMMENT ON COLUMN reviews.sentiment_score IS 'Confidence score for sentiment (0.0 to 1.0)';
COMMENT ON COLUMN reviews.source IS 'Source of the review (e.g., Google Play Store)';

