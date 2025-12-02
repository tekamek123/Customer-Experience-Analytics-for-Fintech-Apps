"""
Generate Recommendations Report
Creates actionable recommendations based on insights analysis
"""

import pandas as pd
from analyze_insights import load_data, identify_drivers, identify_pain_points, compare_banks
from datetime import datetime


def generate_recommendations(df, insights):
    """
    Generate recommendations for each bank based on insights.
    
    Args:
        df: Reviews dataframe
        insights: Dictionary with drivers and pain points per bank
    
    Returns:
        Dictionary of recommendations per bank
    """
    recommendations = {}
    
    for bank, data in insights.items():
        bank_recommendations = []
        
        drivers = data['drivers']
        pain_points = data['pain_points']
        
        # Recommendation 1: Address top pain point
        if pain_points:
            top_pain = pain_points[0]
            if 'Crashes' in top_pain['pain_point'] or 'Bugs' in top_pain['pain_point']:
                bank_recommendations.append({
                    'priority': 'High',
                    'category': 'Technical',
                    'recommendation': 'Implement comprehensive bug fixing and stability improvements',
                    'details': [
                        'Conduct thorough QA testing before releases',
                        'Implement crash reporting and monitoring',
                        'Prioritize fixing critical bugs affecting core functionality',
                        'Establish a bug triage process'
                    ],
                    'expected_impact': 'Reduce negative reviews by 30-40%',
                    'based_on': top_pain['pain_point']
                })
            elif 'Access' in top_pain['pain_point'] or 'Login' in top_pain['pain_point']:
                bank_recommendations.append({
                    'priority': 'High',
                    'category': 'Technical',
                    'recommendation': 'Improve login and authentication system',
                    'details': [
                        'Implement biometric authentication (fingerprint, face ID)',
                        'Add "Remember Me" option for trusted devices',
                        'Improve offline mode functionality',
                        'Optimize connection handling and retry logic'
                    ],
                    'expected_impact': 'Improve user experience and reduce access-related complaints',
                    'based_on': top_pain['pain_point']
                })
        
        # Recommendation 2: Enhance top driver
        if drivers:
            top_driver = drivers[0]
            if 'Interface' in top_driver['driver']:
                bank_recommendations.append({
                    'priority': 'Medium',
                    'category': 'UX/UI',
                    'recommendation': 'Enhance user interface based on positive feedback',
                    'details': [
                        'Maintain simplicity and ease of use',
                        'Add more customization options',
                        'Improve navigation flow',
                        'Implement dark mode option'
                    ],
                    'expected_impact': 'Increase user satisfaction and retention',
                    'based_on': top_driver['driver']
                })
            elif 'Transaction' in top_driver['driver']:
                bank_recommendations.append({
                    'priority': 'Medium',
                    'category': 'Performance',
                    'recommendation': 'Optimize transaction processing speed',
                    'details': [
                        'Implement transaction queuing for better performance',
                        'Add transaction status notifications',
                        'Optimize backend API response times',
                        'Add batch transaction capability'
                    ],
                    'expected_impact': 'Maintain competitive advantage in transaction speed',
                    'based_on': top_driver['driver']
                })
        
        # Recommendation 3: Address second pain point
        if len(pain_points) > 1:
            second_pain = pain_points[1]
            if 'Slow' in second_pain['pain_point']:
                bank_recommendations.append({
                    'priority': 'Medium',
                    'category': 'Performance',
                    'recommendation': 'Improve app performance and loading times',
                    'details': [
                        'Optimize app startup time',
                        'Implement lazy loading for non-critical features',
                        'Cache frequently accessed data',
                        'Optimize image and asset sizes'
                    ],
                    'expected_impact': 'Reduce user frustration and improve ratings',
                    'based_on': second_pain['pain_point']
                })
            elif 'Support' in second_pain['pain_point']:
                bank_recommendations.append({
                    'priority': 'Medium',
                    'category': 'Customer Service',
                    'recommendation': 'Enhance customer support within the app',
                    'details': [
                        'Add in-app chat support',
                        'Implement AI chatbot for common queries',
                        'Add FAQ section with search functionality',
                        'Provide video tutorials for common tasks'
                    ],
                    'expected_impact': 'Reduce support tickets and improve user satisfaction',
                    'based_on': second_pain['pain_point']
                })
        
        # Recommendation 4: Feature requests
        bank_recommendations.append({
            'priority': 'Low',
            'category': 'Features',
            'recommendation': 'Add requested features based on user feedback',
            'details': [
                'Transaction history export (PDF/CSV)',
                'Budgeting and expense tracking tools',
                'Multiple account management in single app',
                'Bill payment reminders and scheduling',
                'Spending analytics and insights'
            ],
            'expected_impact': 'Increase app value proposition and user engagement',
            'based_on': 'Feature Requests theme analysis'
        })
        
        recommendations[bank] = bank_recommendations
    
    return recommendations


def generate_report():
    """Generate comprehensive recommendations report."""
    print("=" * 70)
    print("Generating Recommendations Report")
    print("=" * 70)
    
    # Load data
    df_reviews, _ = load_data()
    if df_reviews is None:
        return
    
    # Get insights
    from analyze_insights import generate_insights_report
    insights, comparison = generate_insights_report()
    
    if insights is None:
        return
    
    # Generate recommendations
    recommendations = generate_recommendations(df_reviews, insights)
    
    # Create report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("RECOMMENDATIONS REPORT")
    report_lines.append("Customer Experience Analytics for Fintech Apps")
    report_lines.append(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    report_lines.append("=" * 70)
    
    # Executive Summary
    report_lines.append("\n## EXECUTIVE SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append("\nThis report provides actionable recommendations for improving")
    report_lines.append("mobile banking applications based on analysis of 1,200+ user reviews")
    report_lines.append("from the Google Play Store for three Ethiopian banks.")
    report_lines.append("\nKey Findings:")
    report_lines.append(f"- Total reviews analyzed: {len(df_reviews):,}")
    report_lines.append(f"- Banks analyzed: {len(df_reviews['bank'].unique())}")
    report_lines.append(f"- Average rating across all banks: {df_reviews['rating'].mean():.2f}")
    report_lines.append(f"- Sentiment coverage: 100%")
    
    # Bank Comparison
    report_lines.append("\n## BANK COMPARISON")
    report_lines.append("-" * 70)
    report_lines.append(comparison.to_string(index=False))
    
    # Recommendations by Bank
    report_lines.append("\n## RECOMMENDATIONS BY BANK")
    report_lines.append("=" * 70)
    
    for bank, recs in recommendations.items():
        report_lines.append(f"\n### {bank}")
        report_lines.append("-" * 70)
        
        # Drivers
        if insights[bank]['drivers']:
            report_lines.append("\n**Satisfaction Drivers:**")
            for i, driver in enumerate(insights[bank]['drivers'], 1):
                report_lines.append(f"  {i}. {driver['driver']}")
                report_lines.append(f"     Evidence: {driver['evidence']}")
        
        # Pain Points
        if insights[bank]['pain_points']:
            report_lines.append("\n**Pain Points:**")
            for i, pp in enumerate(insights[bank]['pain_points'], 1):
                report_lines.append(f"  {i}. {pp['pain_point']} [{pp.get('severity', 'N/A')} Severity]")
                report_lines.append(f"     Evidence: {pp['evidence']}")
        
        # Recommendations
        report_lines.append(f"\n**Recommendations ({len(recs)}):**")
        for i, rec in enumerate(recs, 1):
            report_lines.append(f"\n  {i}. [{rec['priority']} Priority] {rec['recommendation']}")
            report_lines.append(f"     Category: {rec['category']}")
            report_lines.append(f"     Based on: {rec['based_on']}")
            report_lines.append(f"     Expected Impact: {rec['expected_impact']}")
            report_lines.append(f"     Action Items:")
            for detail in rec['details']:
                report_lines.append(f"       - {detail}")
    
    # Ethics and Limitations
    report_lines.append("\n## ETHICS AND LIMITATIONS")
    report_lines.append("=" * 70)
    report_lines.append("\n### Potential Biases in Review Data:")
    report_lines.append("\n1. **Negative Review Bias:**")
    report_lines.append("   - Users with negative experiences are more likely to leave reviews")
    report_lines.append("   - This may skew sentiment analysis toward negative outcomes")
    report_lines.append("   - Mitigation: Consider that actual user satisfaction may be higher")
    report_lines.append("\n2. **Selection Bias:**")
    report_lines.append("   - Only users who download and use the app can leave reviews")
    report_lines.append("   - Users who uninstall immediately may not be represented")
    report_lines.append("   - Mitigation: Reviews represent engaged users, not all potential users")
    report_lines.append("\n3. **Temporal Bias:**")
    report_lines.append("   - Reviews span multiple years (2018-2025)")
    report_lines.append("   - Recent app updates may not be fully reflected")
    report_lines.append("   - Mitigation: Focus on recent reviews for current state assessment")
    report_lines.append("\n4. **Language Bias:**")
    report_lines.append("   - Analysis focused on English-language reviews")
    report_lines.append("   - May not represent all user segments")
    report_lines.append("   - Mitigation: Consider multi-language analysis for comprehensive insights")
    report_lines.append("\n5. **Rating Interpretation:**")
    report_lines.append("   - 1-2 star ratings may indicate critical issues")
    report_lines.append("   - 4-5 star ratings indicate satisfaction but may lack detail")
    report_lines.append("   - Mitigation: Combined sentiment and rating analysis provides balance")
    
    report_lines.append("\n### Data Limitations:")
    report_lines.append("- Sample size: 1,200 reviews (400 per bank)")
    report_lines.append("- Source: Google Play Store only (excludes iOS users)")
    report_lines.append("- Time period: Reviews from 2018-2025")
    report_lines.append("- Analysis method: Automated sentiment and theme extraction")
    
    report_lines.append("\n### Recommendations for Future Analysis:")
    report_lines.append("1. Collect reviews from multiple sources (iOS App Store, direct feedback)")
    report_lines.append("2. Conduct user surveys to complement review analysis")
    report_lines.append("3. Perform longitudinal analysis to track improvements over time")
    report_lines.append("4. Include demographic analysis if available")
    report_lines.append("5. Compare with industry benchmarks")
    
    # Save report
    report_text = '\n'.join(report_lines)
    
    with open('RECOMMENDATIONS_REPORT.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print("\n[OK] Recommendations report saved to: RECOMMENDATIONS_REPORT.txt")
    
    # Also save recommendations as CSV
    recs_data = []
    for bank, recs in recommendations.items():
        for rec in recs:
            recs_data.append({
                'bank': bank,
                'priority': rec['priority'],
                'category': rec['category'],
                'recommendation': rec['recommendation'],
                'expected_impact': rec['expected_impact'],
                'based_on': rec['based_on']
            })
    
    recs_df = pd.DataFrame(recs_data)
    recs_df.to_csv('data/processed/recommendations.csv', index=False)
    print("[OK] Recommendations saved to: data/processed/recommendations.csv")
    
    # Print summary
    print("\n" + "=" * 70)
    print("Report Summary")
    print("=" * 70)
    print(f"\nTotal recommendations generated: {sum(len(r) for r in recommendations.values())}")
    for bank, recs in recommendations.items():
        high_priority = sum(1 for r in recs if r['priority'] == 'High')
        print(f"  {bank}: {len(recs)} recommendations ({high_priority} high priority)")
    
    return report_text


if __name__ == "__main__":
    generate_report()

