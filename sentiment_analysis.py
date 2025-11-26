"""
Sentiment Analysis Script
Analyzes sentiment of reviews using DistilBERT or VADER
"""

import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')


class SentimentAnalyzer:
    """Sentiment analysis using DistilBERT or VADER as fallback."""
    
    def __init__(self, use_distilbert=True):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_distilbert: If True, use DistilBERT; otherwise use VADER
        """
        self.use_distilbert = use_distilbert
        self.distilbert_pipeline = None
        self.vader_analyzer = None
        
        if use_distilbert:
            try:
                print("Loading DistilBERT model...")
                self.distilbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1  # Use CPU
                )
                print("✓ DistilBERT model loaded successfully")
            except Exception as e:
                print(f"⚠ Could not load DistilBERT: {str(e)}")
                print("Falling back to VADER...")
                self.use_distilbert = False
        
        if not self.use_distilbert:
            print("Initializing VADER sentiment analyzer...")
            self.vader_analyzer = SentimentIntensityAnalyzer()
            print("✓ VADER analyzer initialized")
    
    def analyze_text(self, text):
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment_label and sentiment_score
        """
        if not text or pd.isna(text) or str(text).strip() == '':
            return {
                'sentiment_label': 'neutral',
                'sentiment_score': 0.0
            }
        
        text = str(text).strip()
        
        if self.use_distilbert and self.distilbert_pipeline:
            try:
                result = self.distilbert_pipeline(text[:512])  # Limit to 512 tokens
                label = result[0]['label'].lower()
                score = result[0]['score']
                
                # Convert to our format
                if label == 'positive':
                    return {
                        'sentiment_label': 'positive',
                        'sentiment_score': score
                    }
                elif label == 'negative':
                    return {
                        'sentiment_label': 'negative',
                        'sentiment_score': score
                    }
                else:
                    return {
                        'sentiment_label': 'neutral',
                        'sentiment_score': 0.5
                    }
            except Exception as e:
                print(f"  Error with DistilBERT: {str(e)}, falling back to VADER")
                self.use_distilbert = False
        
        # Use VADER
        if self.vader_analyzer:
            scores = self.vader_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                label = 'positive'
                score = compound
            elif compound <= -0.05:
                label = 'negative'
                score = abs(compound)
            else:
                label = 'neutral'
                score = abs(compound)
            
            return {
                'sentiment_label': label,
                'sentiment_score': score
            }
        
        # Fallback
        return {
            'sentiment_label': 'neutral',
            'sentiment_score': 0.0
        }
    
    def analyze_batch(self, texts, batch_size=32):
        """
        Analyze sentiment for a batch of texts.
        
        Args:
            texts: List or Series of texts
            batch_size: Batch size for processing
        
        Returns:
            DataFrame with sentiment_label and sentiment_score columns
        """
        results = []
        
        print(f"Analyzing sentiment for {len(texts)} reviews...")
        
        for i, text in enumerate(texts):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(texts)} reviews...")
            
            result = self.analyze_text(text)
            results.append(result)
        
        print(f"✓ Completed sentiment analysis for {len(texts)} reviews")
        
        return pd.DataFrame(results)


def aggregate_sentiment_by_bank_and_rating(df):
    """
    Aggregate sentiment scores by bank and rating.
    
    Args:
        df: DataFrame with sentiment analysis results
    
    Returns:
        DataFrame with aggregated statistics
    """
    if 'sentiment_score' not in df.columns or 'sentiment_label' not in df.columns:
        print("⚠ Sentiment columns not found in dataframe")
        return None
    
    # Create aggregation
    agg_data = []
    
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        
        for rating in sorted(bank_df['rating'].unique()):
            rating_df = bank_df[bank_df['rating'] == rating]
            
            if len(rating_df) > 0:
                agg_data.append({
                    'bank': bank,
                    'rating': rating,
                    'review_count': len(rating_df),
                    'mean_sentiment_score': rating_df['sentiment_score'].mean(),
                    'positive_pct': (rating_df['sentiment_label'] == 'positive').sum() / len(rating_df) * 100,
                    'negative_pct': (rating_df['sentiment_label'] == 'negative').sum() / len(rating_df) * 100,
                    'neutral_pct': (rating_df['sentiment_label'] == 'neutral').sum() / len(rating_df) * 100
                })
    
    return pd.DataFrame(agg_data)


def main():
    """Main function for testing."""
    # Load data
    df = pd.read_csv("data/processed/reviews_cleaned.csv")
    print(f"Loaded {len(df)} reviews")
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer(use_distilbert=True)
    
    # Analyze sentiment
    sentiment_df = analyzer.analyze_batch(df['review'])
    
    # Combine with original data
    result_df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)
    
    # Save results
    result_df.to_csv("data/processed/reviews_with_sentiment.csv", index=False)
    print("✓ Saved results to data/processed/reviews_with_sentiment.csv")
    
    # Aggregate by bank and rating
    agg_df = aggregate_sentiment_by_bank_and_rating(result_df)
    if agg_df is not None:
        print("\nSentiment Aggregation by Bank and Rating:")
        print(agg_df.to_string(index=False))
        agg_df.to_csv("data/processed/sentiment_aggregation.csv", index=False)
        print("\n✓ Saved aggregation to data/processed/sentiment_aggregation.csv")


if __name__ == "__main__":
    main()

