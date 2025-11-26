"""
Main Analysis Pipeline
Combines sentiment analysis and thematic analysis
"""

import pandas as pd
import os
from sentiment_analysis import SentimentAnalyzer, aggregate_sentiment_by_bank_and_rating
from thematic_analysis import analyze_themes_by_bank, assign_themes_to_reviews


def run_full_pipeline(input_file="data/processed/reviews_cleaned.csv", 
                     output_file="data/processed/reviews_analyzed.csv"):
    """
    Run the complete analysis pipeline.
    
    Args:
        input_file: Path to cleaned reviews CSV
        output_file: Path to save analyzed reviews CSV
    """
    print("=" * 70)
    print("Customer Experience Analytics Pipeline")
    print("=" * 70)
    
    # Step 1: Load data
    print("\n[Step 1/4] Loading cleaned reviews...")
    try:
        df = pd.read_csv(input_file)
        print(f"✓ Loaded {len(df)} reviews")
    except FileNotFoundError:
        print(f"✗ Error: File {input_file} not found.")
        print("  Please run preprocess_reviews.py first.")
        return None
    
    # Add review_id
    df['review_id'] = range(1, len(df) + 1)
    
    # Step 2: Sentiment Analysis
    print("\n[Step 2/4] Performing sentiment analysis...")
    print("-" * 70)
    analyzer = SentimentAnalyzer(use_distilbert=True)
    sentiment_df = analyzer.analyze_batch(df['review'])
    
    # Combine sentiment results
    df = pd.concat([df.reset_index(drop=True), sentiment_df.reset_index(drop=True)], axis=1)
    
    # Check sentiment coverage
    sentiment_coverage = (df['sentiment_label'].notna().sum() / len(df)) * 100
    print(f"✓ Sentiment analysis complete: {sentiment_coverage:.1f}% coverage")
    
    if sentiment_coverage < 90:
        print(f"⚠ Warning: Sentiment coverage ({sentiment_coverage:.1f}%) is below KPI (90%)")
    else:
        print(f"✓ Sentiment coverage meets KPI requirement (≥90%)")
    
    # Step 3: Thematic Analysis
    print("\n[Step 3/4] Performing thematic analysis...")
    print("-" * 70)
    bank_themes = analyze_themes_by_bank(df)
    
    # Assign themes to reviews
    df = assign_themes_to_reviews(df, bank_themes)
    
    # Check theme coverage
    theme_coverage = (df['themes'].notna().sum() / len(df)) * 100
    print(f"✓ Thematic analysis complete: {theme_coverage:.1f}% coverage")
    
    # Step 4: Prepare final output
    print("\n[Step 4/4] Preparing final output...")
    print("-" * 70)
    
    # Select and reorder columns
    output_columns = [
        'review_id',
        'review',
        'rating',
        'date',
        'bank',
        'source',
        'sentiment_label',
        'sentiment_score',
        'themes'
    ]
    
    # Ensure all columns exist
    for col in output_columns:
        if col not in df.columns:
            df[col] = ''
    
    df_output = df[output_columns].copy()
    
    # Rename for clarity
    df_output = df_output.rename(columns={
        'review': 'review_text',
        'themes': 'identified_themes'
    })
    
    # Save final results
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_output.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Saved analyzed reviews to {output_file}")
    
    # Generate summary statistics
    print("\n" + "=" * 70)
    print("Analysis Summary")
    print("=" * 70)
    
    print(f"\nTotal Reviews Analyzed: {len(df_output)}")
    print(f"Sentiment Coverage: {sentiment_coverage:.1f}%")
    print(f"Theme Coverage: {theme_coverage:.1f}%")
    
    # Sentiment distribution
    print("\nSentiment Distribution:")
    sentiment_dist = df_output['sentiment_label'].value_counts()
    for label, count in sentiment_dist.items():
        pct = (count / len(df_output)) * 100
        print(f"  {label.capitalize()}: {count} ({pct:.1f}%)")
    
    # Themes per bank
    print("\nThemes Identified by Bank:")
    for bank in df_output['bank'].unique():
        bank_df = df_output[df_output['bank'] == bank]
        unique_themes = set()
        for themes_str in bank_df['identified_themes'].dropna():
            if themes_str:
                unique_themes.update(themes_str.split('; '))
        print(f"  {bank}: {len(unique_themes)} unique themes")
    
    # Generate aggregation reports
    print("\n" + "=" * 70)
    print("Generating Aggregation Reports...")
    print("=" * 70)
    
    # Sentiment aggregation
    agg_sentiment = aggregate_sentiment_by_bank_and_rating(df)
    if agg_sentiment is not None:
        agg_file = "data/processed/sentiment_aggregation.csv"
        agg_sentiment.to_csv(agg_file, index=False)
        print(f"✓ Saved sentiment aggregation to {agg_file}")
    
    # Theme summary
    theme_summary = []
    for bank, theme_data in bank_themes.items():
        for theme, keywords in theme_data['themes'].items():
            top_keywords = [kw for kw, _ in keywords[:10]]
            theme_summary.append({
                'bank': bank,
                'theme': theme,
                'keyword_count': len(keywords),
                'top_keywords': ', '.join(top_keywords)
            })
    
    if theme_summary:
        theme_summary_df = pd.DataFrame(theme_summary)
        theme_file = "data/processed/theme_summary.csv"
        theme_summary_df.to_csv(theme_file, index=False)
        print(f"✓ Saved theme summary to {theme_file}")
    
    print("\n" + "=" * 70)
    print("Pipeline Complete!")
    print("=" * 70)
    
    return df_output


def main():
    """Main function."""
    result_df = run_full_pipeline()
    
    if result_df is not None:
        print(f"\n✓ Analysis complete! Results saved to data/processed/reviews_analyzed.csv")
        print(f"  Total reviews analyzed: {len(result_df)}")
    else:
        print("\n✗ Pipeline failed. Please check errors above.")


if __name__ == "__main__":
    main()


