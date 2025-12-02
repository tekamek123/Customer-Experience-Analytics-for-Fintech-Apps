"""
Create Visualizations for Bank Reviews Analysis
Generates 3-5 plots for insights and recommendations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
import os
from collections import Counter
import re

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Create output directory
os.makedirs("visualizations", exist_ok=True)


def load_data():
    """Load analyzed reviews data."""
    try:
        df = pd.read_csv("data/processed/reviews_analyzed.csv")
        return df
    except FileNotFoundError:
        print("[ERROR] reviews_analyzed.csv not found. Run analysis_pipeline.py first.")
        return None


def plot_1_sentiment_by_bank(df):
    """Plot 1: Sentiment Distribution by Bank"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sentiment_by_bank = df.groupby(['bank', 'sentiment_label']).size().unstack(fill_value=0)
    sentiment_by_bank_pct = sentiment_by_bank.div(sentiment_by_bank.sum(axis=1), axis=0) * 100
    
    x = np.arange(len(sentiment_by_bank_pct.index))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, sentiment_by_bank_pct['positive'], width, 
                   label='Positive', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar(x + width/2, sentiment_by_bank_pct['negative'], width, 
                   label='Negative', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Bank', fontweight='bold', fontsize=12)
    ax.set_ylabel('Percentage (%)', fontweight='bold', fontsize=12)
    ax.set_title('Sentiment Distribution by Bank', fontweight='bold', fontsize=14, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(sentiment_by_bank_pct.index, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 100)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('visualizations/1_sentiment_by_bank.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: visualizations/1_sentiment_by_bank.png")
    plt.close()


def plot_2_rating_distribution(df):
    """Plot 2: Rating Distribution Comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    banks = df['bank'].unique()
    colors = ['#3498db', '#9b59b6', '#f39c12']
    
    for idx, bank in enumerate(banks):
        bank_df = df[df['bank'] == bank]
        rating_counts = bank_df['rating'].value_counts().sort_index()
        
        axes[idx].bar(rating_counts.index, rating_counts.values, 
                     color=colors[idx], alpha=0.7, edgecolor='black', linewidth=1.5)
        axes[idx].set_xlabel('Rating (Stars)', fontweight='bold')
        axes[idx].set_ylabel('Number of Reviews', fontweight='bold')
        axes[idx].set_title(f'{bank}\nAvg: {bank_df["rating"].mean():.2f}', 
                          fontweight='bold', fontsize=11)
        axes[idx].set_xticks([1, 2, 3, 4, 5])
        axes[idx].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels
        for rating, count in rating_counts.items():
            axes[idx].text(rating, count + 5, str(count), 
                          ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle('Rating Distribution by Bank', fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('visualizations/2_rating_distribution.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: visualizations/2_rating_distribution.png")
    plt.close()


def plot_3_average_metrics_comparison(df):
    """Plot 3: Average Metrics Comparison (Rating, Sentiment Score)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Calculate metrics
    metrics = []
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        metrics.append({
            'bank': bank,
            'avg_rating': bank_df['rating'].mean(),
            'avg_sentiment_score': bank_df['sentiment_score'].mean()
        })
    metrics_df = pd.DataFrame(metrics)
    
    # Plot 1: Average Rating
    bars1 = ax1.barh(metrics_df['bank'], metrics_df['avg_rating'], 
                     color=['#3498db', '#9b59b6', '#f39c12'], alpha=0.8, edgecolor='black')
    ax1.set_xlabel('Average Rating', fontweight='bold', fontsize=11)
    ax1.set_title('Average Rating by Bank', fontweight='bold', fontsize=12)
    ax1.set_xlim(0, 5)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bank, rating) in enumerate(zip(metrics_df['bank'], metrics_df['avg_rating'])):
        ax1.text(rating + 0.1, i, f'{rating:.2f}', va='center', fontweight='bold')
    
    # Plot 2: Average Sentiment Score
    bars2 = ax2.barh(metrics_df['bank'], metrics_df['avg_sentiment_score'], 
                     color=['#3498db', '#9b59b6', '#f39c12'], alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Average Sentiment Score', fontweight='bold', fontsize=11)
    ax2.set_title('Average Sentiment Score by Bank', fontweight='bold', fontsize=12)
    ax2.set_xlim(0, 1)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (bank, score) in enumerate(zip(metrics_df['bank'], metrics_df['avg_sentiment_score'])):
        ax2.text(score + 0.01, i, f'{score:.3f}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('visualizations/3_average_metrics_comparison.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: visualizations/3_average_metrics_comparison.png")
    plt.close()


def plot_4_theme_frequency(df):
    """Plot 4: Theme Frequency by Bank"""
    theme_data = []
    
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        theme_counts = Counter()
        
        for themes in bank_df['identified_themes'].dropna():
            if themes:
                for theme in themes.split('; '):
                    theme_counts[theme] += 1
        
        for theme, count in theme_counts.items():
            theme_data.append({
                'bank': bank,
                'theme': theme,
                'count': count
            })
    
    theme_df = pd.DataFrame(theme_data)
    
    # Pivot for heatmap
    theme_pivot = theme_df.pivot(index='theme', columns='bank', values='count').fillna(0)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(theme_pivot, annot=True, fmt='.0f', cmap='YlOrRd', 
                cbar_kws={'label': 'Frequency'}, linewidths=0.5, ax=ax)
    
    ax.set_xlabel('Bank', fontweight='bold', fontsize=12)
    ax.set_ylabel('Theme', fontweight='bold', fontsize=12)
    ax.set_title('Theme Frequency Heatmap by Bank', fontweight='bold', fontsize=14, pad=15)
    plt.xticks(rotation=15, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig('visualizations/4_theme_frequency_heatmap.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: visualizations/4_theme_frequency_heatmap.png")
    plt.close()


def plot_5_keyword_wordcloud(df, bank_name):
    """Plot 5: Keyword Word Cloud for each bank"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    banks = df['bank'].unique()
    
    for idx, bank in enumerate(banks):
        bank_df = df[df['bank'] == bank]
        
        # Extract keywords from reviews
        text = ' '.join(bank_df['review_text'].dropna().astype(str))
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                       'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                       'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
                       'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'we',
                       'app', 'bank', 'banking', 'mobile', 'application', 'use', 'using'}
        
        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, 
                             background_color='white',
                             max_words=100,
                             colormap='viridis',
                             stopwords=common_words,
                             relative_scaling=0.5).generate(text)
        
        axes[idx].imshow(wordcloud, interpolation='bilinear')
        axes[idx].axis('off')
        axes[idx].set_title(bank, fontweight='bold', fontsize=12, pad=10)
    
    plt.suptitle('Keyword Word Clouds by Bank', fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('visualizations/5_keyword_wordclouds.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: visualizations/5_keyword_wordclouds.png")
    plt.close()


def create_all_visualizations():
    """Create all visualizations."""
    print("=" * 70)
    print("Creating Visualizations")
    print("=" * 70)
    
    df = load_data()
    if df is None:
        return
    
    print("\nGenerating 5 visualizations...")
    
    # Plot 1: Sentiment by Bank
    print("\n[1/5] Creating sentiment distribution plot...")
    plot_1_sentiment_by_bank(df)
    
    # Plot 2: Rating Distribution
    print("\n[2/5] Creating rating distribution plot...")
    plot_2_rating_distribution(df)
    
    # Plot 3: Average Metrics
    print("\n[3/5] Creating average metrics comparison...")
    plot_3_average_metrics_comparison(df)
    
    # Plot 4: Theme Frequency
    print("\n[4/5] Creating theme frequency heatmap...")
    plot_4_theme_frequency(df)
    
    # Plot 5: Word Clouds
    print("\n[5/5] Creating keyword word clouds...")
    plot_5_keyword_wordcloud(df, None)
    
    print("\n" + "=" * 70)
    print("All visualizations created successfully!")
    print("=" * 70)
    print("\nVisualizations saved in: visualizations/")
    print("  - 1_sentiment_by_bank.png")
    print("  - 2_rating_distribution.png")
    print("  - 3_average_metrics_comparison.png")
    print("  - 4_theme_frequency_heatmap.png")
    print("  - 5_keyword_wordclouds.png")


if __name__ == "__main__":
    create_all_visualizations()

