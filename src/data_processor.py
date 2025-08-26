#!/usr/bin/env python3
"""
Data Processing Module

Handles data loading, Likert scale conversion, and data validation.
"""

from tools import sanitize_text

import pandas as pd
import numpy as np

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


def normalize_data(df, categories, likert_mapping=None):
    """
    Normalize raw survey data by cleaning column names, converting Likert responses,
    and standardizing the DataFrame for analysis.
    
    Args:
        df (pandas.DataFrame): Raw survey data
        categories (dict): Dictionary mapping category names to question lists
        likert_mapping (dict): Optional mapping of response text to numeric scores
        
    Returns:
        tuple: (normalized_df, categories_with_clean_names, missing_questions)
    """
    import re
    
    # Step 1: Create normalized DataFrame with clean column names
    normalized_df = df.copy()
    column_mapping = {}  # Maps original column names to normalized names
    reverse_mapping = {}  # Maps normalized names back to original
    
    # Normalize all column names
    for col in df.columns:
         # Replaces any sequence of whitespace with a single space " "
        normalized_col = sanitize_text(str(col))
        column_mapping[col] = normalized_col
        reverse_mapping[normalized_col] = col
        
    # Rename columns in the DataFrame
    normalized_df.columns = [column_mapping[col] for col in normalized_df.columns]
    
    # Step 2: Match questions from config to normalized columns
    matched_questions = {}  # Maps category -> list of matched column names
    missing_questions = []
    
    for category_name, questions in categories.items():
        matched_questions[category_name] = []
        for question in questions:
            normalized_question = sanitize_text(question)
            
            if normalized_question in normalized_df.columns:
                matched_questions[category_name].append(normalized_question)
            else:
                missing_questions.append((category_name, question))
    
    # Step 3: Convert Likert responses to numeric values
    def normalize_likert_response(text):
        if pd.isna(text):
            return np.nan
        
        text_str = str(text).strip()
        
        # Normalize whitespace in the response
        normalized_text = sanitize_text(text_str)
        
        # Try mapping from config
        if likert_mapping:
            # Try exact match first
            if normalized_text in likert_mapping:
                return likert_mapping[normalized_text]
            
            # Try case-insensitive match
            for key, value in likert_mapping.items():
                normalized_key = sanitize_text(str(key))
                if normalized_text.lower() == normalized_key.lower():
                    return value
        
        return np.nan
    
    # Convert all matched Likert questions to numeric
    total_questions = sum(len(questions) for questions in matched_questions.values())
    print(f"📊 Converting {total_questions} Likert scale questions grouped into {len(categories)} categories...")
    
    if missing_questions:
        print(f"⚠️  {len(missing_questions)} questions from config not found in data:")
        for category, question in missing_questions:
            print(f"   • [{category}] {question}")
        print()
    
    for category_name, questions in matched_questions.items():
        for question in questions:
            if question in normalized_df.columns:
                # Convert responses to numeric scores
                normalized_df[question] = normalized_df[question].apply(normalize_likert_response)
                print(f"   ✅ {question} → {category_name}")
    
    return normalized_df, matched_questions, missing_questions


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