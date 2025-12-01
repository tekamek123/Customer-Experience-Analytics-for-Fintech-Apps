"""
Insights Analysis Script
Identifies satisfaction drivers and pain points for each bank
"""

import pandas as pd
import numpy as np
from collections import Counter
import re


def load_data():
    """Load analyzed reviews and theme data."""
    try:
        df_reviews = pd.read_csv("data/processed/reviews_analyzed.csv")
        df_themes = pd.read_csv("data/processed/theme_summary.csv")
        return df_reviews, df_themes
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        return None, None


def extract_keywords_from_reviews(df, bank_name, sentiment_filter=None, rating_filter=None):
    """
    Extract keywords from reviews for a specific bank.
    
    Args:
        df: Reviews dataframe
        bank_name: Name of the bank
        sentiment_filter: 'positive' or 'negative' or None
        rating_filter: List of ratings [1,2,3,4,5] or None
    """
    bank_df = df[df['bank'] == bank_name].copy()
    
    if sentiment_filter:
        bank_df = bank_df[bank_df['sentiment_label'] == sentiment_filter]
    
    if rating_filter:
        bank_df = bank_df[bank_df['rating'].isin(rating_filter)]
    
    # Extract keywords from review text
    keywords = []
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                   'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                   'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
                   'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'we',
                   'app', 'bank', 'banking', 'mobile', 'application'}
    
    for review in bank_df['review_text'].dropna():
        # Simple keyword extraction
        words = re.findall(r'\b[a-z]{3,}\b', review.lower())
        keywords.extend([w for w in words if w not in common_words])
    
    return Counter(keywords)


def identify_drivers(df, bank_name):
    """
    Identify satisfaction drivers (positive aspects) for a bank.
    
    Args:
        df: Reviews dataframe
        bank_name: Name of the bank
    
    Returns:
        List of drivers with evidence
    """
    # Filter positive reviews (4-5 stars or positive sentiment)
    positive_reviews = df[
        (df['bank'] == bank_name) & 
        ((df['rating'] >= 4) | (df['sentiment_label'] == 'positive'))
    ]
    
    if len(positive_reviews) == 0:
        return []
    
    drivers = []
    
    # Analyze themes in positive reviews
    theme_counts = {}
    for themes in positive_reviews['identified_themes'].dropna():
        if themes:
            for theme in themes.split('; '):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Extract keywords from positive reviews
    positive_keywords = extract_keywords_from_reviews(df, bank_name, sentiment_filter='positive', rating_filter=[4, 5])
    
    # Identify top drivers based on themes and keywords
    # Driver 1: User Interface & Experience
    if 'User Interface & Experience' in theme_counts and theme_counts['User Interface & Experience'] > 10:
        ui_keywords = [kw for kw, count in positive_keywords.most_common(20) 
                      if kw in ['easy', 'simple', 'friendly', 'interface', 'user', 'use', 'features']]
        if ui_keywords:
            drivers.append({
                'driver': 'User-Friendly Interface',
                'evidence': f"Mentioned in {theme_counts['User Interface & Experience']} positive reviews",
                'keywords': ', '.join(ui_keywords[:5]),
                'sample_reviews': len(positive_reviews[positive_reviews['identified_themes'].str.contains('User Interface', na=False)])
            })
    
    # Driver 2: Transaction Performance
    if 'Transaction Performance' in theme_counts and theme_counts['Transaction Performance'] > 10:
        perf_keywords = [kw for kw, count in positive_keywords.most_common(20) 
                        if kw in ['fast', 'quick', 'speed', 'transfer', 'payment', 'transaction']]
        if perf_keywords:
            drivers.append({
                'driver': 'Fast Transaction Processing',
                'evidence': f"Mentioned in {theme_counts['Transaction Performance']} positive reviews",
                'keywords': ', '.join(perf_keywords[:5]),
                'sample_reviews': len(positive_reviews[positive_reviews['identified_themes'].str.contains('Transaction Performance', na=False)])
            })
    
    # Driver 3: Security & Privacy
    if 'Security & Privacy' in theme_counts:
        drivers.append({
            'driver': 'Security Features',
            'evidence': f"Mentioned in {theme_counts['Security & Privacy']} positive reviews",
            'keywords': 'security, safe, secure',
            'sample_reviews': len(positive_reviews[positive_reviews['identified_themes'].str.contains('Security', na=False)])
        })
    
    # Driver 4: Reliability (if mentioned positively)
    reliable_count = len(positive_reviews[positive_reviews['review_text'].str.contains('reliable|stable|consistent', case=False, na=False)])
    if reliable_count > 5:
        drivers.append({
            'driver': 'App Reliability',
            'evidence': f"Reliability mentioned in {reliable_count} positive reviews",
            'keywords': 'reliable, stable, consistent',
            'sample_reviews': reliable_count
        })
    
    return drivers[:3]  # Return top 3 drivers


def identify_pain_points(df, bank_name):
    """
    Identify pain points (negative aspects) for a bank.
    
    Args:
        df: Reviews dataframe
        bank_name: Name of the bank
    
    Returns:
        List of pain points with evidence
    """
    # Filter negative reviews (1-2 stars or negative sentiment)
    negative_reviews = df[
        (df['bank'] == bank_name) & 
        ((df['rating'] <= 2) | (df['sentiment_label'] == 'negative'))
    ]
    
    if len(negative_reviews) == 0:
        return []
    
    pain_points = []
    
    # Analyze themes in negative reviews
    theme_counts = {}
    for themes in negative_reviews['identified_themes'].dropna():
        if themes:
            for theme in themes.split('; '):
                theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Extract keywords from negative reviews
    negative_keywords = extract_keywords_from_reviews(df, bank_name, sentiment_filter='negative', rating_filter=[1, 2])
    
    # Pain Point 1: App Reliability & Bugs
    if 'App Reliability & Bugs' in theme_counts and theme_counts['App Reliability & Bugs'] > 10:
        bug_keywords = [kw for kw, count in negative_keywords.most_common(20) 
                       if kw in ['crash', 'error', 'bug', 'issue', 'problem', 'freeze', 'loading', 'down']]
        if bug_keywords:
            pain_points.append({
                'pain_point': 'App Crashes and Bugs',
                'evidence': f"Mentioned in {theme_counts['App Reliability & Bugs']} negative reviews",
                'keywords': ', '.join(bug_keywords[:5]),
                'sample_reviews': len(negative_reviews[negative_reviews['identified_themes'].str.contains('App Reliability', na=False)]),
                'severity': 'High' if theme_counts['App Reliability & Bugs'] > 50 else 'Medium'
            })
    
    # Pain Point 2: Account Access Issues
    if 'Account Access Issues' in theme_counts and theme_counts['Account Access Issues'] > 10:
        access_keywords = [kw for kw, count in negative_keywords.most_common(20) 
                          if kw in ['login', 'access', 'password', 'connection', 'offline', 'error']]
        if access_keywords:
            pain_points.append({
                'pain_point': 'Login and Access Problems',
                'evidence': f"Mentioned in {theme_counts['Account Access Issues']} negative reviews",
                'keywords': ', '.join(access_keywords[:5]),
                'sample_reviews': len(negative_reviews[negative_reviews['identified_themes'].str.contains('Account Access', na=False)]),
                'severity': 'High' if theme_counts['Account Access Issues'] > 50 else 'Medium'
            })
    
    # Pain Point 3: Transaction Performance (slow)
    if 'Transaction Performance' in theme_counts:
        slow_count = len(negative_reviews[negative_reviews['review_text'].str.contains('slow|delay|timeout|wait', case=False, na=False)])
        if slow_count > 10:
            pain_points.append({
                'pain_point': 'Slow Transaction Processing',
                'evidence': f"Slow performance mentioned in {slow_count} negative reviews",
                'keywords': 'slow, delay, timeout, wait',
                'sample_reviews': slow_count,
                'severity': 'Medium'
            })
    
    # Pain Point 4: Customer Support
    if 'Customer Support' in theme_counts and theme_counts['Customer Support'] > 5:
        pain_points.append({
            'pain_point': 'Customer Support Issues',
            'evidence': f"Mentioned in {theme_counts['Customer Support']} negative reviews",
            'keywords': 'support, service, branch, help',
            'sample_reviews': len(negative_reviews[negative_reviews['identified_themes'].str.contains('Customer Support', na=False)]),
            'severity': 'Medium'
        })
    
    return pain_points[:3]  # Return top 3 pain points


def compare_banks(df):
    """Compare banks across key metrics."""
    comparison = []
    
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        
        comparison.append({
            'bank': bank,
            'total_reviews': len(bank_df),
            'avg_rating': bank_df['rating'].mean(),
            'positive_sentiment_pct': (bank_df['sentiment_label'] == 'positive').sum() / len(bank_df) * 100,
            'negative_sentiment_pct': (bank_df['sentiment_label'] == 'negative').sum() / len(bank_df) * 100,
            '5_star_pct': (bank_df['rating'] == 5).sum() / len(bank_df) * 100,
            '1_star_pct': (bank_df['rating'] == 1).sum() / len(bank_df) * 100,
        })
    
    return pd.DataFrame(comparison)


def generate_insights_report():
    """Generate comprehensive insights report."""
    print("=" * 70)
    print("Insights Analysis: Satisfaction Drivers and Pain Points")
    print("=" * 70)
    
    df_reviews, df_themes = load_data()
    if df_reviews is None:
        return None
    
    insights = {}
    
    for bank in df_reviews['bank'].unique():
        print(f"\n{'='*70}")
        print(f"Analyzing: {bank}")
        print(f"{'='*70}")
        
        drivers = identify_drivers(df_reviews, bank)
        pain_points = identify_pain_points(df_reviews, bank)
        
        insights[bank] = {
            'drivers': drivers,
            'pain_points': pain_points
        }
        
        print(f"\n[DRIVERS] ({len(drivers)} identified):")
        for i, driver in enumerate(drivers, 1):
            print(f"\n  {i}. {driver['driver']}")
            print(f"     Evidence: {driver['evidence']}")
            print(f"     Keywords: {driver['keywords']}")
            print(f"     Sample reviews: {driver['sample_reviews']}")
        
        print(f"\n[PAIN POINTS] ({len(pain_points)} identified):")
        for i, pp in enumerate(pain_points, 1):
            print(f"\n  {i}. {pp['pain_point']} [{pp.get('severity', 'N/A')} Severity]")
            print(f"     Evidence: {pp['evidence']}")
            print(f"     Keywords: {pp['keywords']}")
            print(f"     Sample reviews: {pp['sample_reviews']}")
    
    # Bank comparison
    print(f"\n{'='*70}")
    print("Bank Comparison")
    print(f"{'='*70}")
    comparison = compare_banks(df_reviews)
    print(comparison.to_string(index=False))
    
    # Save insights to CSV
    insights_data = []
    for bank, data in insights.items():
        for driver in data['drivers']:
            insights_data.append({
                'bank': bank,
                'type': 'Driver',
                'item': driver['driver'],
                'evidence': driver['evidence'],
                'keywords': driver['keywords']
            })
        for pp in data['pain_points']:
            insights_data.append({
                'bank': bank,
                'type': 'Pain Point',
                'item': pp['pain_point'],
                'evidence': pp['evidence'],
                'keywords': pp['keywords']
            })
    
    insights_df = pd.DataFrame(insights_data)
    insights_df.to_csv("data/processed/insights_summary.csv", index=False)
    print(f"\n[OK] Insights saved to data/processed/insights_summary.csv")
    
    return insights, comparison


if __name__ == "__main__":
    generate_insights_report()

