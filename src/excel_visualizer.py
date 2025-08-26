#!/usr/bin/env python3
"""
Excel Visualization Generator Module

Creates Excel files with embedded charts and data visualizations for form analysis results.
"""

import pandas as pd
import xlsxwriter
from datetime import datetime
import os
import numpy as np


def create_excel_dashboard(stats: dict, categories: dict, comment_fields: dict, overall_df: pd.DataFrame, filtered_df: pd.DataFrame,
                          team_column: str, location_column: str, selected_team: str, selected_location: str, run_dir: str) -> str:
    """Create an Excel file with multiple worksheets and embedded charts."""
    filename = os.path.join(run_dir, 'dashboard.xlsx')
    
    # Create workbook with xlsxwriter for chart support
    # Enable nan_inf_to_errors option to handle NaN/Inf values
    workbook = xlsxwriter.Workbook(filename, {'nan_inf_to_errors': True})
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    subheader_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#D9E2F3',
        'align': 'center'
    })
    
    number_format = workbook.add_format({'num_format': '0.00'})
    percent_format = workbook.add_format({'num_format': '0.00%'})
    
    # Create summary dashboard worksheet
    create_summary_worksheet(workbook, stats, categories, selected_team, selected_location,
                            header_format, subheader_format, number_format)
    
    # Create category comparison chart
    create_category_chart_worksheet(workbook, stats, categories, header_format, subheader_format, number_format)
    
    # Create team/location breakdown if applicable
    if selected_team == 'all' or selected_location == 'all':
        create_breakdown_worksheet(workbook, overall_df, filtered_df, categories, 
                                 team_column, location_column, selected_team, selected_location,
                                 header_format, subheader_format, number_format)
    
    # Create detailed data worksheet
    create_data_worksheet(workbook, filtered_df, categories, comment_fields,
                         header_format, subheader_format)
    
    # Create comments worksheet if comments exist
    if 'comments' in stats and stats['comments']:
        create_comments_worksheet(workbook, stats['comments'], selected_team, selected_location,
                                header_format, subheader_format)
    
    workbook.close()
    
    return filename


def create_summary_worksheet(workbook, stats: dict, categories: dict, selected_team: str, selected_location: str,
                           header_format, subheader_format, number_format):
    """Create executive summary worksheet with key metrics."""
    worksheet = workbook.add_worksheet('Executive Summary')
    
    # Set column widths
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 20)
    
    row = 0
    
    # Title
    team_display = selected_team if selected_team != 'all' else 'All Teams'
    location_display = selected_location if selected_location != 'all' else 'All Locations'
    
    worksheet.merge_range(row, 0, row, 3, f'Form Analysis Dashboard: {team_display} + {location_display}', header_format)
    row += 2
    
    # Metadata
    worksheet.write(row, 0, 'Analysis Date:', subheader_format)
    worksheet.write(row, 1, datetime.now().strftime('%Y-%m-%d %H:%M'))
    row += 1
    
    worksheet.write(row, 0, 'Filtered Responses:', subheader_format)
    worksheet.write(row, 1, stats['metadata']['filtered_responses'])
    row += 1
    
    worksheet.write(row, 0, 'Total Dataset Responses:', subheader_format)
    worksheet.write(row, 1, stats['metadata']['total_responses'])
    row += 2
    
    # Category Performance Summary
    worksheet.write(row, 0, 'Category Performance Summary', subheader_format)
    row += 1
    
    worksheet.write(row, 0, 'Category', subheader_format)
    worksheet.write(row, 1, 'Filtered Score', subheader_format)
    worksheet.write(row, 2, 'Overall Score', subheader_format)
    worksheet.write(row, 3, 'Difference', subheader_format)
    row += 1
    
    for category in categories.keys():
        if category in stats['category_performance']:
            worksheet.write(row, 0, category)
            
            # Handle potential NaN values
            filtered_score = stats['category_performance'][category]
            if pd.isna(filtered_score):
                worksheet.write(row, 1, "N/A")
            else:
                worksheet.write(row, 1, filtered_score, number_format)
            
            if category in stats['comparisons']:
                overall_score = stats['comparisons'][category]['overall_score']
                difference = stats['comparisons'][category]['difference']
                
                if pd.isna(overall_score):
                    worksheet.write(row, 2, "N/A")
                else:
                    worksheet.write(row, 2, overall_score, number_format)
                    
                if pd.isna(difference):
                    worksheet.write(row, 3, "N/A")
                else:
                    worksheet.write(row, 3, difference, number_format)
            
            row += 1
    
    return worksheet


def create_category_chart_worksheet(workbook, stats: dict, categories: dict, header_format, subheader_format, number_format):
    """Create worksheet with category performance charts."""
    worksheet = workbook.add_worksheet('Category Analysis')
    
    # Set column widths
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:C', 15)
    
    row = 0
    
    # Title
    worksheet.merge_range(row, 0, row, 2, 'Category Performance Analysis', header_format)
    row += 2
    
    # Data for chart
    worksheet.write(row, 0, 'Category', subheader_format)
    worksheet.write(row, 1, 'Filtered Score', subheader_format)
    worksheet.write(row, 2, 'Overall Average', subheader_format)
    row += 1
    
    start_data_row = row
    
    for category in categories.keys():
        if category in stats['category_performance']:
            worksheet.write(row, 0, category)
            
            # Handle NaN values for chart data
            filtered_score = stats['category_performance'][category]
            if pd.isna(filtered_score):
                worksheet.write(row, 1, 0)  # Use 0 for charts instead of N/A
            else:
                worksheet.write(row, 1, filtered_score, number_format)
            
            if category in stats['comparisons']:
                overall_score = stats['comparisons'][category]['overall_score']
                if pd.isna(overall_score):
                    worksheet.write(row, 2, 0)  # Use 0 for charts instead of N/A
                else:
                    worksheet.write(row, 2, overall_score, number_format)
            
            row += 1
    
    end_data_row = row - 1
    
    # Create bar chart
    chart = workbook.add_chart({'type': 'column'})
    
    # Add filtered scores series
    chart.add_series({
        'name': 'Selected Combination',
        'categories': [worksheet.name, start_data_row, 0, end_data_row, 0],
        'values': [worksheet.name, start_data_row, 1, end_data_row, 1],
        'fill': {'color': '#4472C4'}
    })
    
    # Add overall average series
    chart.add_series({
        'name': 'Overall Average',
        'categories': [worksheet.name, start_data_row, 0, end_data_row, 0],
        'values': [worksheet.name, start_data_row, 2, end_data_row, 2],
        'fill': {'color': '#70AD47'}
    })
    
    chart.set_title({'name': 'Category Performance Comparison'})
    chart.set_x_axis({'name': 'Categories'})
    chart.set_y_axis({'name': 'Average Score'})
    chart.set_style(2)
    
    # Insert chart
    worksheet.insert_chart('E2', chart, {'x_scale': 1.2, 'y_scale': 1.2})
    
    return worksheet


def create_breakdown_worksheet(workbook, overall_df: pd.DataFrame, filtered_df: pd.DataFrame, categories: dict, team_column: str, location_column: str,
                              selected_team: str, selected_location: str, header_format, subheader_format, number_format):
    """Create worksheet with team/location breakdown charts."""
    worksheet = workbook.add_worksheet('Team-Location Breakdown')
    
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 15)
    
    row = 0
    
    # Title
    worksheet.merge_range(row, 0, row, 1, 'Team and Location Breakdown', header_format)
    row += 2
    
    # Get numeric columns for scoring
    numeric_cols = [col for col in overall_df.columns if col.endswith('_numeric')]
    
    if selected_team == 'all' and team_column in filtered_df.columns:
        # Team breakdown
        worksheet.write(row, 0, 'Team Performance', subheader_format)
        row += 2
        
        worksheet.write(row, 0, 'Team', subheader_format)
        worksheet.write(row, 1, 'Average Score', subheader_format)
        row += 1
        
        start_team_row = row
        
        if numeric_cols:
            team_scores = filtered_df.groupby(team_column)[numeric_cols].mean().mean(axis=1).sort_values(ascending=False)
            
            for team, score in team_scores.items():
                worksheet.write(row, 0, team)
                if pd.isna(score):
                    worksheet.write(row, 1, 0, number_format)
                else:
                    worksheet.write(row, 1, score, number_format)
                row += 1
            
            end_team_row = row - 1
            
            # Create team chart
            team_chart = workbook.add_chart({'type': 'bar'})
            team_chart.add_series({
                'name': 'Team Performance',
                'categories': [worksheet.name, start_team_row, 0, end_team_row, 0],
                'values': [worksheet.name, start_team_row, 1, end_team_row, 1],
                'fill': {'color': '#FFC000'}
            })
            
            team_chart.set_title({'name': 'Performance by Team'})
            team_chart.set_x_axis({'name': 'Average Score'})
            team_chart.set_y_axis({'name': 'Teams'})
            
            worksheet.insert_chart('D2', team_chart)
    
    if selected_location == 'all' and location_column in filtered_df.columns:
        # Location breakdown
        row += 2
        worksheet.write(row, 0, 'Location Performance', subheader_format)
        row += 2
        
        worksheet.write(row, 0, 'Location', subheader_format)
        worksheet.write(row, 1, 'Average Score', subheader_format)
        row += 1
        
        start_location_row = row
        
        if numeric_cols:
            location_scores = filtered_df.groupby(location_column)[numeric_cols].mean().mean(axis=1).sort_values(ascending=False)
            
            for location, score in location_scores.items():
                worksheet.write(row, 0, location)
                if pd.isna(score):
                    worksheet.write(row, 1, 0, number_format)
                else:
                    worksheet.write(row, 1, score, number_format)
                row += 1
            
            end_location_row = row - 1
            
            # Create location chart
            location_chart = workbook.add_chart({'type': 'pie'})
            location_chart.add_series({
                'name': 'Location Performance',
                'categories': [worksheet.name, start_location_row, 0, end_location_row, 0],
                'values': [worksheet.name, start_location_row, 1, end_location_row, 1],
            })
            
            location_chart.set_title({'name': 'Performance by Location'})
            
            worksheet.insert_chart('D15', location_chart)
    
    return worksheet


def create_data_worksheet(workbook, filtered_df: pd.DataFrame, categories: dict, comment_fields: dict, header_format, subheader_format):
    """Create worksheet with detailed data."""
    worksheet = workbook.add_worksheet('Detailed Data')
    
    row = 0
    
    # Title
    worksheet.write(row, 0, 'Filtered Dataset', header_format)
    row += 2
    
    # Write filtered dataframe
    # Select relevant columns
    relevant_cols = []
    
    # Add team/location columns
    for col in filtered_df.columns:
        if 'team' in col.lower() or 'location' in col.lower():
            relevant_cols.append(col)
    
    # Add numeric score columns
    for col in filtered_df.columns:
        if col.endswith('_numeric'):
            relevant_cols.append(col)
    
    # Add comment columns
    for comment_col in comment_fields.values():
        if comment_col in filtered_df.columns:
            relevant_cols.append(comment_col)
    
    # Remove duplicates and maintain order
    relevant_cols = list(dict.fromkeys(relevant_cols))
    
    if relevant_cols:
        # Write headers
        for col_idx, col_name in enumerate(relevant_cols):
            worksheet.write(row, col_idx, col_name, subheader_format)
            worksheet.set_column(col_idx, col_idx, 20)
        
        row += 1
        
        # Write data
        for _, data_row in filtered_df[relevant_cols].iterrows():
            for col_idx, value in enumerate(data_row):
                # Handle NaN values explicitly
                if pd.isna(value):
                    worksheet.write(row, col_idx, "")  # Write empty string instead of NaN
                else:
                    worksheet.write(row, col_idx, value)
            row += 1
    
    return worksheet


def create_comments_worksheet(workbook, comments_data: dict, selected_team: str, selected_location: str, header_format, subheader_format):
    """Create worksheet with organized comments."""
    worksheet = workbook.add_worksheet('Comments')
    
    # Set column widths
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 60)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    
    row = 0
    
    # Title
    worksheet.merge_range(row, 0, row, 3, 'Comments by Category', header_format)
    row += 2
    
    # Headers
    worksheet.write(row, 0, 'Category', subheader_format)
    worksheet.write(row, 1, 'Comment', subheader_format)
    if selected_team == 'all':
        worksheet.write(row, 2, 'Team', subheader_format)
    if selected_location == 'all':
        worksheet.write(row, 3, 'Location', subheader_format)
    row += 1
    
    # Write comments
    for category_name, category_data in comments_data.items():
        for comment in category_data['comments']:
            worksheet.write(row, 0, category_name)
            worksheet.write(row, 1, comment['text'])
            
            col_idx = 2
            if selected_team == 'all':
                worksheet.write(row, col_idx, comment['team'])
                col_idx += 1
            if selected_location == 'all':
                worksheet.write(row, col_idx, comment['location'])
            
            row += 1
    
    return worksheet