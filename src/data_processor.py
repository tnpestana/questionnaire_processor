#!/usr/bin/env python3
"""
Data Processing Module

Handles data loading, Likert scale conversion, and data validation.
"""

import pandas as pd
import numpy as np
import re


def load_data(file_path, sheet_name=None):
    """
    Load data from Excel or CSV file.
    
    Args:
        file_path (str): Path to the data file
        sheet_name (str, optional): Excel sheet name
        
    Returns:
        pandas.DataFrame: Loaded data
    """
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"✅ Loaded {df.shape[0]} responses from sheet '{sheet_name}' with {df.shape[1]} columns")
            else:
                df = pd.read_excel(file_path)
                print(f"✅ Loaded {df.shape[0]} responses with {df.shape[1]} columns")
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            print(f"✅ Loaded {df.shape[0]} responses with {df.shape[1]} columns from CSV")
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading data from {file_path}: {e}")


def extract_likert_scores(df, categories):
    """
    Extract numeric scores from Likert scale responses and group by categories.
    
    Converts responses like "Strongly Agree (1)" to numeric value 1.
    Groups questions into logical categories based on configuration.
    
    Args:
        df (pandas.DataFrame): The form data
        categories (dict): Dictionary mapping category names to question lists
        
    Returns:
        tuple: (DataFrame with numeric columns, category groupings)
    """
    df_numeric = df.copy()
    
    # Find and convert Likert scale columns
    likert_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            sample_values = df[col].dropna().head().tolist()
            if any('(' in str(val) and ')' in str(val) for val in sample_values):
                likert_columns.append(col)
    
    print(f"📊 Converting {len(likert_columns)} Likert scale questions grouped into {len(categories)} categories...")
    
    # Convert each Likert column to numeric
    for col in likert_columns:
        numeric_col = col + '_numeric'
        
        def extract_number(text):
            if pd.isna(text):
                return np.nan
            match = re.search(r'\(([+-]?\d+)\)', str(text))
            if match:
                return int(match.group(1))
            return np.nan
        
        df_numeric[numeric_col] = df[col].apply(extract_number)
        
        # Find which category this question belongs to
        category_name = "Uncategorized"
        for cat_name, questions in categories.items():
            if col in questions:
                category_name = cat_name
                break
        
        print(f"   ✅ {col} → {category_name}")
    
    return df_numeric, categories


def validate_columns(df, team_column, location_column):
    """
    Validate that required columns exist in the dataframe.
    
    Args:
        df (pandas.DataFrame): The dataframe to validate
        team_column (str): Name of the team column
        location_column (str): Name of the location column
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If required columns are missing
    """
    missing_columns = []
    
    if team_column not in df.columns:
        missing_columns.append(team_column)
    
    if location_column not in df.columns:
        missing_columns.append(location_column)
    
    if missing_columns:
        available_cols = list(df.columns)
        raise ValueError(
            f"Missing required columns: {missing_columns}\n"
            f"Available columns: {available_cols}"
        )
    
    return True


def analyze_available_groups(df, team_column, location_column):
    """
    Analyze available teams and locations in the data.
    
    Args:
        df (pandas.DataFrame): The DataFrame with data
        team_column (str): Name of team column
        location_column (str): Name of location column
        
    Returns:
        dict: Information about available groups
    """
    group_info = {}
    
    if team_column and team_column in df.columns:
        teams = df[team_column].dropna().unique()
        team_counts = df[team_column].value_counts()
        group_info['teams'] = {
            'names': sorted(teams),
            'counts': team_counts.to_dict(),
            'total': len(teams)
        }
    
    if location_column and location_column in df.columns:
        locations = df[location_column].dropna().unique()
        location_counts = df[location_column].value_counts()
        group_info['locations'] = {
            'names': sorted(locations),
            'counts': location_counts.to_dict(),
            'total': len(locations)
        }
    
    return group_info


def filter_data(df, team_column, location_column, selected_team, selected_location):
    """
    Filter dataframe based on team and location selections.
    
    Args:
        df (pandas.DataFrame): The dataframe to filter
        team_column (str): Name of team column
        location_column (str): Name of location column
        selected_team (str): Selected team or 'all'
        selected_location (str): Selected location or 'all'
        
    Returns:
        pandas.DataFrame: Filtered dataframe
    """
    filtered_df = df.copy()
    
    if selected_team != 'all':
        filtered_df = filtered_df[filtered_df[team_column] == selected_team]
    
    if selected_location != 'all':
        filtered_df = filtered_df[filtered_df[location_column] == selected_location]
    
    return filtered_df


def collect_comments(df, comment_fields, team_column, location_column):
    """
    Collect comments from the dataframe, organized by category.
    
    Args:
        df (pandas.DataFrame): The dataframe containing comments
        comment_fields (dict): Mapping of category names to comment column names
        team_column (str): Name of team column
        location_column (str): Name of location column
        
    Returns:
        dict: Comments organized by category with metadata
    """
    comments_by_category = {}
    
    for category_name, comment_column in comment_fields.items():
        if comment_column not in df.columns:
            continue
            
        category_comments = []
        
        for idx, row in df.iterrows():
            comment_text = row[comment_column]
            
            # Skip empty, null, or very short comments
            if pd.isna(comment_text) or not str(comment_text).strip() or len(str(comment_text).strip()) < 3:
                continue
            
            comment_data = {
                'text': str(comment_text).strip(),
                'team': row[team_column] if team_column in df.columns else 'Unknown',
                'location': row[location_column] if location_column in df.columns else 'Unknown'
            }
            
            category_comments.append(comment_data)
        
        if category_comments:
            comments_by_category[category_name] = {
                'comments': category_comments,
                'count': len(category_comments)
            }
    
    return comments_by_category