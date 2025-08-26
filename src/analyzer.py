#!/usr/bin/env python3
"""
Analysis Module

Handles statistical analysis, comparisons, and detailed statistics generation.
"""

import pandas as pd
import numpy as np
from data_processor import collect_comments

def calculate_category_scores(df: pd.DataFrame, categories: dict) -> dict:
    """Calculate average scores for each category."""
    category_scores = {}
    for category_name, questions in categories.items():
        if questions and len(df) > 0:
            # Calculate average of question averages (each question gets equal weight)
            question_averages = []
            for question in questions:
                if question in df.columns:
                    col_mean = df[question].mean()
                    if not pd.isna(col_mean):
                        question_averages.append(col_mean)
            
            if question_averages:
                category_avg = np.mean(question_averages)
                category_scores[category_name] = category_avg
    
    return category_scores


def compare_with_overall(filtered_df: pd.DataFrame, overall_df: pd.DataFrame, categories: dict) -> dict:
    """Compare filtered data scores with overall averages."""
    comparisons = {}
    
    for category_name, questions in categories.items():
        if questions:
            # Calculate averages for filtered data (average of question averages)
            if len(filtered_df) > 0:
                question_averages = []
                for question in questions:
                    if question in filtered_df.columns:
                        col_mean = filtered_df[question].mean()
                        if not pd.isna(col_mean):
                            question_averages.append(col_mean)
                filtered_avg = np.mean(question_averages) if question_averages else 0
            else:
                filtered_avg = 0
            
            # Calculate averages for overall data (average of question averages)
            question_averages = []
            for question in questions:
                if question in overall_df.columns:
                    col_mean = overall_df[question].mean()
                    if not pd.isna(col_mean):
                        question_averages.append(col_mean)
            overall_avg = np.mean(question_averages) if question_averages else 0
            difference = filtered_avg - overall_avg
            
            comparisons[category_name] = {
                'filtered_score': float(filtered_avg),
                'overall_score': float(overall_avg),
                'difference': float(difference),
                'status': get_performance_status(difference)
            }
    
    return comparisons


def get_performance_status(difference: float, significant_threshold: float = 0.2, similar_threshold: float = 0.1) -> str:
    """Determine performance status based on difference from overall average."""
    if difference > significant_threshold:
        return "significantly_above"
    elif difference > similar_threshold:
        return "above"
    elif abs(difference) <= similar_threshold:
        return "similar"
    elif difference < -significant_threshold:
        return "significantly_below"
    else:
        return "below"


def generate_detailed_statistics(filtered_df: pd.DataFrame, overall_df: pd.DataFrame, categories: dict, comment_fields: dict, 
                                team_column: str, location_column: str, selected_team: str, selected_location: str) -> dict:
    """Generate detailed statistics for the selected combination."""
    stats = {
        'metadata': {
            'selected_team': selected_team,
            'selected_location': selected_location,
            'filtered_responses': len(filtered_df),
            'total_responses': len(overall_df)
        }
    }
    
    # Category performance for filtered data
    filtered_category_scores = calculate_category_scores(filtered_df, categories)
    stats['category_performance'] = filtered_category_scores
    
    # Comparisons with overall
    stats['comparisons'] = compare_with_overall(filtered_df, overall_df, categories)
    
    # Detailed question analysis
    question_details = {}
    for category_name, questions in categories.items():
        category_questions = {}
        for question in questions:
            if question in filtered_df.columns:
                if len(filtered_df) > 0:
                    filtered_score = filtered_df[question].mean()
                    filtered_responses = int(filtered_df[question].notna().sum())
                else:
                    filtered_score = None
                    filtered_responses = 0
                
                overall_score = overall_df[question].mean()
                total_responses = int(overall_df[question].notna().sum())
                
                category_questions[question] = {
                    'filtered_score': float(filtered_score) if filtered_score is not None else None,
                    'overall_score': float(overall_score),
                    'difference': float(filtered_score - overall_score) if filtered_score is not None else None,
                    'filtered_responses': filtered_responses,
                    'total_responses': total_responses
                }
        
        if category_questions:
            question_details[category_name] = category_questions
    
    stats['question_details'] = question_details
    
    # Collect comments for the filtered data
    filtered_comments = collect_comments(filtered_df, comment_fields, team_column, location_column)
    stats['comments'] = filtered_comments
    
    return stats


def get_recommendations(stats: dict, categories: dict) -> list:
    """Generate recommendations based on analysis results."""
    recommendations = []
    
    if stats['metadata']['filtered_responses'] == 0:
        return ["No data available for this combination - unable to provide recommendations."]
    
    # Category-focused recommendations
    comparisons = stats['comparisons']
    if comparisons:
        # Find worst performing category
        worst_category = min(comparisons.keys(), key=lambda cat: comparisons[cat]['filtered_score'])
        worst_score = comparisons[worst_category]['filtered_score']
        worst_status = comparisons[worst_category]['status']
        
        if worst_status in ['significantly_below', 'below']:
            recommendations.append(
                f"CATEGORY FOCUS: Address {worst_category} "
                f"(score: {worst_score:.2f}, {worst_status.replace('_', ' ')})"
            )
    
    # Team/location specific recommendations
    selected_team = stats['metadata']['selected_team']
    selected_location = stats['metadata']['selected_location']
    
    if selected_team != 'all' and selected_location != 'all':
        # Specific combination recommendations
        below_average_categories = [
            cat for cat, comp in comparisons.items() 
            if comp['status'] in ['significantly_below', 'below']
        ]
        
        if below_average_categories:
            recommendations.append(
                f"COMBINATION IMPACT: {selected_team} in {selected_location} "
                f"shows lower performance in {len(below_average_categories)} categories"
            )
    
    if not recommendations:
        recommendations.append("No specific issues identified - performance appears satisfactory for this combination.")
    
    return recommendations