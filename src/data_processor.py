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


def extract_likert_scores(df, categories, likert_mapping=None):
    """
    Extract numeric scores from Likert scale responses and group by categories.
    
    Converts responses using either embedded scores like "Strongly Agree (1)" 
    or text mapping from configuration.
    
    Args:
        df (pandas.DataFrame): The form data
        categories (dict): Dictionary mapping category names to question lists
        likert_mapping (dict): Optional mapping of response text to numeric scores
        
    Returns:
        tuple: (DataFrame with numeric columns, category groupings, missing_questions)
    """
    df_numeric = df.copy()
    
    # Get Likert columns from categories configuration
    likert_columns = []
    missing_questions = []
    for category_name, questions in categories.items():
        for question in questions:
            if question in df.columns:
                likert_columns.append(question)
            else:
                # Try to find the question with normalized whitespace
                normalized_question = question.replace('\u00a0', ' ').strip()
                found = False
                for col in df.columns:
                    normalized_col = col.replace('\u00a0', ' ').strip()
                    if normalized_question == normalized_col:
                        likert_columns.append(col)  # Use the actual column name from data
                        found = True
                        break
                
                if not found:
                    missing_questions.append((category_name, question))
    
    print(f"📊 Converting {len(likert_columns)} Likert scale questions grouped into {len(categories)} categories...")
    
    if missing_questions:
        print(f"⚠️  {len(missing_questions)} questions from config not found in data:")
        for category, question in missing_questions:
            print(f"   • [{category}] {question}")
        print()
    
    # Convert each Likert column to numeric
    for col in likert_columns:
        numeric_col = col + '_numeric'
        
        def extract_score(text):
            if pd.isna(text):
                return np.nan
            
            text_str = str(text).strip()
            
            # Use mapping from config
            if likert_mapping and text_str in likert_mapping:
                return likert_mapping[text_str]
            
            # Case-insensitive fallback
            if likert_mapping:
                for key, value in likert_mapping.items():
                    if text_str.lower() == key.lower():
                        return value
            
            return np.nan
        
        df_numeric[numeric_col] = df[col].apply(extract_score)
        
        # Find which category this question belongs to
        category_name = "Uncategorized"
        for cat_name, questions in categories.items():
            if col in questions:
                category_name = cat_name
                break
        
        print(f"   ✅ {col} → {category_name}")
    
    return df_numeric, categories, missing_questions


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