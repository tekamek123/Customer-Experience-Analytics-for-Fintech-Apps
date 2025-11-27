"""
Generate Interim Report as PDF
Creates a 4-page report covering scraping and early analysis
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import os
import io


def load_data():
    """Load all necessary data files."""
    data = {}
    
    # Load cleaned reviews
    try:
        df_cleaned = pd.read_csv("data/processed/reviews_cleaned.csv")
        data['cleaned'] = df_cleaned
    except:
        data['cleaned'] = None
    
    # Load sentiment aggregation
    try:
        df_sentiment = pd.read_csv("data/processed/sentiment_aggregation.csv")
        data['sentiment'] = df_sentiment
    except:
        data['sentiment'] = None
    
    # Load theme summary
    try:
        df_themes = pd.read_csv("data/processed/theme_summary.csv")
        data['themes'] = df_themes
    except:
        data['themes'] = None
    
    return data


def create_report_pdf(output_file="Interim_Report.pdf"):
    """Create the interim report PDF."""
    
    # Load data
    data = load_data()
    df_cleaned = data['cleaned']
    df_sentiment = data['sentiment']
    df_themes = data['themes']
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#3949ab'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14
    normal_style.alignment = TA_JUSTIFY
    
    # ===== PAGE 1: TITLE PAGE =====
    story.append(Spacer(1, 1.5*inch))
    
    # Title
    story.append(Paragraph("Customer Experience Analytics", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("for Fintech Mobile Banking Apps", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Subtitle
    subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#616161')
    )
    story.append(Paragraph("Interim Report", subtitle))
    story.append(Spacer(1, 0.3*inch))
    
    # Date
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#757575')
    )
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", date_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Project info
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#424242')
    )
    story.append(Paragraph("Omega Consultancy", info_style))
    story.append(Paragraph("Week 2: Data Collection & Early Analysis", info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Banks analyzed
    story.append(Paragraph("Analyzed Banks:", info_style))
    story.append(Paragraph("• Commercial Bank of Ethiopia (CBE)", info_style))
    story.append(Paragraph("• Bank of Abyssinia (BOA)", info_style))
    story.append(Paragraph("• Dashen Bank", info_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 2: EXECUTIVE SUMMARY & DATA COLLECTION =====
    story.append(Paragraph("Executive Summary", heading_style))
    
    # Business Objective
    story.append(Paragraph("Business Objective", subheading_style))
    objective_text = """
    <b>The primary business objective of this project is to identify customer satisfaction 
    drivers and pain points for mobile banking applications</b> used by three major Ethiopian 
    banks: Commercial Bank of Ethiopia (CBE), Bank of Abyssinia (BOA), and Dashen Bank. 
    By analyzing user reviews from the Google Play Store, Omega Consultancy aims to provide 
    actionable insights that will help these banks improve their mobile applications, enhance 
    customer retention, and increase user satisfaction. This analysis will uncover what 
    features and aspects users value most, as well as identify critical issues that need 
    immediate attention.
    """
    story.append(Paragraph(objective_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    if df_cleaned is not None:
        total_reviews = len(df_cleaned)
        bank_counts = df_cleaned['bank'].value_counts()
        
        summary_text = f"""
        This interim report presents the initial findings from analyzing customer reviews 
        of mobile banking applications for the three banks. A total of 
        <b>{total_reviews:,}</b> reviews were collected from the Google Play Store, with 
        comprehensive data preprocessing and early sentiment analysis completed.
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Data collection table
        story.append(Paragraph("Data Collection Summary", subheading_style))
        
        collection_data = [['Bank', 'Reviews Collected']]
        for bank, count in bank_counts.items():
            collection_data.append([bank, f"{count:,}"])
        collection_data.append(['Total', f"{total_reviews:,}"])
        
        # Calculate total row index (last row)
        total_row_idx = len(collection_data) - 1
        
        collection_table = Table(collection_data, colWidths=[4*inch, 2*inch])
        collection_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#e8eaf6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f5f5f5')]),
            ('FONTNAME', (0, total_row_idx), (-1, total_row_idx), 'Helvetica-Bold'),  # Bold for total row
            ('FONTSIZE', (0, total_row_idx), (-1, total_row_idx), 11),  # Slightly larger for emphasis
        ]))
        story.append(collection_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Create and add review count chart
        fig, ax = plt.subplots(figsize=(5, 3))
        bank_counts_sorted = bank_counts.sort_values(ascending=True)
        colors_list = ['#3949ab', '#5c6bc0', '#7986cb']  # Blue gradient
        bars = ax.barh(bank_counts_sorted.index, bank_counts_sorted.values, color=colors_list)
        ax.set_xlabel('Number of Reviews', fontsize=10, fontweight='bold')
        ax.set_title('Reviews Collected by Bank', fontsize=11, fontweight='bold', pad=10)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (bank, count) in enumerate(bank_counts_sorted.items()):
            ax.text(count + 10, i, f'{count:,}', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Add image to report
        img = Image(img_buffer, width=5*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 0.3*inch))
    
    # Methodology
    story.append(Paragraph("Data Collection Methodology", subheading_style))
    methodology_text = """
    Reviews were collected from the Google Play Store using the google-play-scraper 
    library. The scraping process targeted a minimum of 400 reviews per bank, sorted by 
    newest reviews first. Rate limiting was implemented to respect Google Play Store's 
    terms of service and avoid being blocked. Each review captured includes:
    """
    story.append(Paragraph(methodology_text, normal_style))
    
    bullet_points = [
        "Review text content",
        "Star rating (1-5)",
        "Review posting date",
        "Bank/app identifier",
        "Data source (Google Play Store)"
    ]
    
    for point in bullet_points:
        story.append(Paragraph(f"• {point}", normal_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 3: DATA PREPROCESSING & QUALITY =====
    story.append(Paragraph("Data Preprocessing & Quality", heading_style))
    
    preprocessing_text = """
    All collected reviews underwent comprehensive preprocessing to ensure data quality 
    and consistency. The preprocessing pipeline included:
    """
    story.append(Paragraph(preprocessing_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    preprocessing_steps = [
        ("Duplicate Removal", "Removed duplicate reviews based on review text and bank identifier"),
        ("Missing Data Handling", "Removed rows with empty review text and validated ratings (1-5)"),
        ("Date Normalization", "Standardized all dates to YYYY-MM-DD format"),
        ("Data Quality Validation", "Calculated and verified data quality metrics")
    ]
    
    for step, desc in preprocessing_steps:
        story.append(Paragraph(f"<b>{step}:</b> {desc}", normal_style))
        story.append(Spacer(1, 0.1*inch))
    
    if df_cleaned is not None:
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Data Quality Metrics", subheading_style))
        
        # Calculate quality metrics
        total = len(df_cleaned)
        missing_text = df_cleaned['review'].isna().sum() + (df_cleaned['review'].str.strip() == '').sum()
        missing_rating = df_cleaned['rating'].isna().sum()
        missing_date = (df_cleaned['date'].isna() | (df_cleaned['date'] == '')).sum()
        
        quality_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Reviews', f"{total:,}", '✓'],
            ['Missing Review Text', f"{missing_text} ({missing_text/total*100:.2f}%)", '✓' if missing_text/total < 0.05 else '⚠'],
            ['Missing Ratings', f"{missing_rating} ({missing_rating/total*100:.2f}%)", '✓'],
            ['Missing Dates', f"{missing_date} ({missing_date/total*100:.2f}%)", '✓' if missing_date/total < 0.05 else '⚠'],
        ]
        
        quality_table = Table(quality_data, colWidths=[2.5*inch, 2*inch, 1*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(quality_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Rating distribution
    if df_cleaned is not None:
        story.append(Paragraph("Rating Distribution", subheading_style))
        rating_dist = df_cleaned['rating'].value_counts().sort_index()
        
        rating_data = [['Rating', 'Count', 'Percentage']]
        for rating, count in rating_dist.items():
            pct = (count / total) * 100
            rating_data.append([f"{rating} Star{'s' if rating != 1 else ''}", f"{count:,}", f"{pct:.1f}%"])
        
        rating_table = Table(rating_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        rating_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        story.append(rating_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Create and add rating distribution chart
        fig, ax = plt.subplots(figsize=(5, 3))
        rating_dist_sorted = rating_dist.sort_index()
        colors_list = ['#d32f2f', '#f57c00', '#fbc02d', '#689f38', '#388e3c']  # Red to green gradient
        rating_labels = [f"{r} Star{'s' if r > 1 else ''}" for r in rating_dist_sorted.index]
        bars = ax.bar(rating_labels, rating_dist_sorted.values, color=colors_list[:len(rating_dist_sorted)])
        ax.set_xlabel('Rating', fontsize=10, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=10, fontweight='bold')
        ax.set_title('Rating Distribution', fontsize=11, fontweight='bold', pad=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, (rating, count) in enumerate(rating_dist_sorted.items()):
            ax.text(i, count + 10, f'{count:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Add image to report
        img = Image(img_buffer, width=5*inch, height=3*inch)
        story.append(img)
    
    story.append(PageBreak())
    
    # ===== PAGE 4: EARLY ANALYSIS RESULTS =====
    story.append(Paragraph("Early Analysis Results", heading_style))
    
    # Sentiment Analysis
    story.append(Paragraph("Sentiment Analysis", subheading_style))
    sentiment_text = """
    Sentiment analysis was performed using DistilBERT-base-uncased-finetuned-sst-2-english, 
    a transformer-based model fine-tuned for sentiment classification. The analysis classified 
    reviews as positive, negative, or neutral with confidence scores.
    """
    story.append(Paragraph(sentiment_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    if df_sentiment is not None:
        # Summary by bank
        story.append(Paragraph("Sentiment Summary by Bank", ParagraphStyle(
            'SmallHeading',
            parent=normal_style,
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )))
        
        bank_sentiment = []
        for bank in df_cleaned['bank'].unique():
            bank_df = df_sentiment[df_sentiment['bank'] == bank]
            total_bank_reviews = bank_df['review_count'].sum()
            positive = (bank_df['positive_pct'] * bank_df['review_count'] / 100).sum() / total_bank_reviews * 100
            negative = (bank_df['negative_pct'] * bank_df['review_count'] / 100).sum() / total_bank_reviews * 100
            
            bank_sentiment.append([
                bank,
                f"{total_bank_reviews:,}",
                f"{positive:.1f}%",
                f"{negative:.1f}%"
            ])
        
        sentiment_summary_data = [['Bank', 'Reviews', 'Positive %', 'Negative %']] + bank_sentiment
        
        sentiment_table = Table(sentiment_summary_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.2*inch])
        sentiment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(sentiment_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Thematic Analysis
    story.append(Paragraph("Thematic Analysis", subheading_style))
    theme_text = """
    Thematic analysis identified key topics and concerns across reviews using TF-IDF keyword 
    extraction and rule-based clustering. Reviews were categorized into 7 major themes:
    """
    story.append(Paragraph(theme_text, normal_style))
    
    themes_list = [
        "Account Access Issues",
        "Transaction Performance",
        "User Interface & Experience",
        "App Reliability & Bugs",
        "Customer Support",
        "Security & Privacy",
        "Feature Requests"
    ]
    
    for theme in themes_list:
        story.append(Paragraph(f"• {theme}", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    if df_themes is not None:
        story.append(Paragraph("Identified Themes by Bank", ParagraphStyle(
            'SmallHeading',
            parent=normal_style,
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )))
        
        # Count themes per bank
        theme_counts = df_themes.groupby('bank')['theme'].count()
        theme_data = [['Bank', 'Number of Themes']]
        for bank, count in theme_counts.items():
            theme_data.append([bank, str(count)])
        
        theme_table = Table(theme_data, colWidths=[4*inch, 2*inch])
        theme_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3949ab')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c5cae9')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(theme_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Next Steps
    story.append(Paragraph("Next Steps", subheading_style))
    next_steps_text = """
    The next phase of analysis will include deeper sentiment analysis by rating category, 
    comprehensive theme extraction with examples, database design for structured storage, 
    and visualization of key insights to support actionable recommendations for each bank.
    """
    story.append(Paragraph(next_steps_text, normal_style))
    
    # Build PDF
    doc.build(story)
    print(f"Report generated successfully: {output_file}")


if __name__ == "__main__":
    create_report_pdf()

