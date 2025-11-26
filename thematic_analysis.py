"""
Thematic Analysis Script
Extracts keywords and groups them into themes for each bank
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import warnings
warnings.filterwarnings('ignore')


class ThematicAnalyzer:
    """Extract themes from reviews using keyword extraction and clustering."""
    
    def __init__(self):
        """Initialize thematic analyzer."""
        try:
            print("Loading spaCy model...")
            self.nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model loaded")
        except OSError:
            print("⚠ spaCy model not found. Installing...")
            print("  Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def preprocess_text(self, text):
        """
        Preprocess text for keyword extraction.
        
        Args:
            text: Raw text
        
        Returns:
            Preprocessed text
        """
        if pd.isna(text) or text == '':
            return ''
        
        text = str(text).lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_keywords_tfidf(self, texts, max_features=50, ngram_range=(1, 2)):
        """
        Extract keywords using TF-IDF.
        
        Args:
            texts: List of texts
            max_features: Maximum number of features
            ngram_range: Range for n-grams
        
        Returns:
            List of keywords with scores
        """
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            min_df=2,  # Word must appear in at least 2 documents
            max_df=0.8  # Word must appear in less than 80% of documents
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get mean TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword-score pairs
            keywords = list(zip(feature_names, mean_scores))
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords
        except Exception as e:
            print(f"  Error in TF-IDF extraction: {str(e)}")
            return []
    
    def extract_keywords_spacy(self, texts, top_n=50):
        """
        Extract keywords using spaCy.
        
        Args:
            texts: List of texts
            top_n: Number of top keywords to return
        
        Returns:
            List of keywords with frequencies
        """
        if not self.nlp:
            return []
        
        all_keywords = []
        
        for text in texts:
            if pd.isna(text) or text == '':
                continue
            
            doc = self.nlp(str(text))
            
            # Extract nouns, adjectives, and verbs (excluding stop words)
            keywords = [
                token.lemma_.lower() 
                for token in doc 
                if not token.is_stop 
                and not token.is_punct 
                and token.pos_ in ['NOUN', 'ADJ', 'VERB']
                and len(token.lemma_) > 2
            ]
            
            all_keywords.extend(keywords)
        
        # Count frequencies
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(top_n)
        
        return top_keywords
    
    def identify_themes(self, keywords, bank_name):
        """
        Group keywords into themes based on banking domain knowledge.
        
        Args:
            keywords: List of (keyword, score) tuples
            bank_name: Name of the bank
        
        Returns:
            Dictionary mapping themes to keywords
        """
        # Theme patterns - keywords that indicate specific themes
        theme_patterns = {
            'Account Access Issues': [
                'login', 'access', 'password', 'authentication', 'authorization',
                'offline', 'connection', 'network', 'error', 'failed', 'blocked',
                'uninstall', 'device', 'register', 'activate'
            ],
            'Transaction Performance': [
                'transfer', 'payment', 'transaction', 'slow', 'fast', 'speed',
                'delay', 'timeout', 'processing', 'complete', 'success', 'fail',
                'wallet', 'send', 'receive', 'money'
            ],
            'User Interface & Experience': [
                'ui', 'interface', 'design', 'layout', 'user', 'friendly',
                'easy', 'simple', 'complex', 'confusing', 'navigation',
                'screen', 'button', 'feature', 'functionality'
            ],
            'App Reliability & Bugs': [
                'crash', 'bug', 'error', 'issue', 'problem', 'glitch',
                'freeze', 'hang', 'stuck', 'loading', 'spinning', 'down',
                'unreliable', 'broken', 'not work', 'doesn\'t work'
            ],
            'Customer Support': [
                'support', 'help', 'service', 'contact', 'branch', 'visit',
                'assistance', 'response', 'complaint', 'feedback'
            ],
            'Security & Privacy': [
                'security', 'safe', 'secure', 'privacy', 'data', 'protection',
                'screenshot', 'restriction', 'policy', 'authorization'
            ],
            'Feature Requests': [
                'feature', 'request', 'add', 'need', 'want', 'missing',
                'suggestion', 'improve', 'enhance', 'wish', 'would like',
                'should have', 'could have', 'multiple account'
            ]
        }
        
        # Convert keywords to lowercase for matching
        keyword_dict = {kw.lower(): score for kw, score in keywords}
        
        # Assign keywords to themes
        theme_keywords = {}
        assigned_keywords = set()
        
        for theme, patterns in theme_patterns.items():
            theme_keywords[theme] = []
            
            for pattern in patterns:
                pattern_lower = pattern.lower()
                
                # Check for exact matches
                if pattern_lower in keyword_dict:
                    if pattern_lower not in assigned_keywords:
                        theme_keywords[theme].append((pattern_lower, keyword_dict[pattern_lower]))
                        assigned_keywords.add(pattern_lower)
                
                # Check for partial matches in keywords
                for kw, score in keywords:
                    kw_lower = kw.lower()
                    if pattern_lower in kw_lower or kw_lower in pattern_lower:
                        if kw_lower not in assigned_keywords:
                            theme_keywords[theme].append((kw_lower, score))
                            assigned_keywords.add(kw_lower)
        
        # Remove empty themes
        theme_keywords = {k: v for k, v in theme_keywords.items() if v}
        
        # Sort keywords within each theme by score
        for theme in theme_keywords:
            theme_keywords[theme].sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
        
        return theme_keywords
    
    def assign_theme_to_review(self, review_text, theme_keywords):
        """
        Assign themes to a review based on keyword matching.
        
        Args:
            review_text: Review text
            theme_keywords: Dictionary of themes and their keywords
        
        Returns:
            List of theme names that match the review
        """
        if pd.isna(review_text) or review_text == '':
            return []
        
        review_lower = str(review_text).lower()
        matched_themes = []
        
        for theme, keywords in theme_keywords.items():
            for keyword, _ in keywords:
                if keyword in review_lower:
                    matched_themes.append(theme)
                    break  # Only need one keyword match per theme
        
        return matched_themes if matched_themes else ['Other']


def analyze_themes_by_bank(df):
    """
    Analyze themes for each bank.
    
    Args:
        df: DataFrame with reviews
    
    Returns:
        Dictionary with themes for each bank
    """
    analyzer = ThematicAnalyzer()
    bank_themes = {}
    
    for bank in df['bank'].unique():
        print(f"\nAnalyzing themes for {bank}...")
        bank_df = df[df['bank'] == bank]
        reviews = bank_df['review'].tolist()
        
        # Extract keywords using TF-IDF
        print(f"  Extracting keywords from {len(reviews)} reviews...")
        keywords = analyzer.extract_keywords_tfidf(reviews, max_features=100, ngram_range=(1, 2))
        
        if not keywords:
            # Fallback to spaCy if TF-IDF fails
            print("  Trying spaCy keyword extraction...")
            keywords = analyzer.extract_keywords_spacy(reviews, top_n=100)
            # Convert to (keyword, score) format
            keywords = [(kw, freq) for kw, freq in keywords]
        
        print(f"  Found {len(keywords)} keywords")
        
        # Identify themes
        print("  Identifying themes...")
        themes = analyzer.identify_themes(keywords, bank)
        
        print(f"  Identified {len(themes)} themes:")
        for theme, theme_kws in themes.items():
            top_kws = [kw for kw, _ in theme_kws[:5]]  # Top 5 keywords
            print(f"    - {theme}: {', '.join(top_kws)}")
        
        bank_themes[bank] = {
            'themes': themes,
            'analyzer': analyzer
        }
    
    return bank_themes


def assign_themes_to_reviews(df, bank_themes):
    """
    Assign themes to each review.
    
    Args:
        df: DataFrame with reviews
        bank_themes: Dictionary with themes for each bank
    
    Returns:
        DataFrame with theme assignments
    """
    df = df.copy()
    df['themes'] = ''
    
    for bank, theme_data in bank_themes.items():
        bank_df = df[df['bank'] == bank]
        analyzer = theme_data['analyzer']
        themes = theme_data['themes']
        
        print(f"\nAssigning themes to reviews for {bank}...")
        
        for idx in bank_df.index:
            review_text = df.loc[idx, 'review']
            matched_themes = analyzer.assign_theme_to_review(review_text, themes)
            df.loc[idx, 'themes'] = '; '.join(matched_themes) if matched_themes else 'Other'
    
    return df


def main():
    """Main function for testing."""
    # Load data
    df = pd.read_csv("data/processed/reviews_cleaned.csv")
    print(f"Loaded {len(df)} reviews")
    
    # Analyze themes by bank
    bank_themes = analyze_themes_by_bank(df)
    
    # Assign themes to reviews
    df_with_themes = assign_themes_to_reviews(df, bank_themes)
    
    # Save results
    df_with_themes.to_csv("data/processed/reviews_with_themes.csv", index=False)
    print(f"\n✓ Saved results to data/processed/reviews_with_themes.csv")
    
    # Save theme summary
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
    
    theme_summary_df = pd.DataFrame(theme_summary)
    theme_summary_df.to_csv("data/processed/theme_summary.csv", index=False)
    print("✓ Saved theme summary to data/processed/theme_summary.csv")


if __name__ == "__main__":
    main()

