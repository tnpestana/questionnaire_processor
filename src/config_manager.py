#!/usr/bin/env python3
"""
Configuration Management Module

Handles YAML configuration loading, validation, and default creation.
"""

import yaml
import os


def load_config(config_path="config.yaml"):
    """
    Load configuration from YAML file.
    
    Args:
        config_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✅ Configuration loaded from: {config_path}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML configuration: {e}")
        raise


def create_default_config(config_path):
    """
    Create a default configuration file if one doesn't exist.
    """
    default_config = {
        'data_source': {
            'file_path': 'input/User Categorization Form(1-25).xlsx',
            'sheet_name': ''
        },
        'columns': {
            'team_column': 'Which team are you part of?',
            'location_column': 'Select your primary work location'
        },
        'categories': {
            'Category 1 (Team Support & Tools)': [
                'I feel well supported by my team.',
                'The tools I use are effective for my work.',
                'Communication within my team is clear.'
            ],
            'Category 2 (Professional Growth)': [
                'I have opportunities for professional growth.',
                'My contributions are recognized.',
                'I receive constructive feedback regularly.'
            ],
            'Category 3 (Work Environment)': [
                'I have a good work-life balance.',
                'The workplace environment is positive.',
                'I am satisfied with the resources provided.'
            ]
        },
        'comment_fields': {
            'Category 1 (Team Support & Tools)': 'Category 1: Please provide any suggestions for improvement.',
            'Category 2 (Professional Growth)': 'Category 2: Please provide any suggestions for improvement.',
            'Category 3 (Work Environment)': 'Category 3: Please provide any suggestions for improvement.'
        },
        'likert_mapping': {
            'Strongly Disagree': -2,
            'Disagree': -1,
            'Neutral': 0,
            'Agree': 1,
            'Strongly Agree': 1,
            'I don\'t know': None
        },
        'analysis': {
            'significant_difference_threshold': 0.2,
            'similar_threshold': 0.1
        },
        'output': {
            'include_timestamp': True,
            'formats': ['csv', 'json', 'txt', 'excel'],
            'output_directory': 'output'
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    print(f"📄 Default configuration created: {config_path}")


def validate_config(config):
    """
    Validate configuration structure and required fields.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        bool: True if valid, raises exception if invalid
    """
    required_sections = ['data_source', 'columns', 'categories']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    required_columns = ['team_column', 'location_column']
    for column in required_columns:
        if column not in config['columns']:
            raise ValueError(f"Missing required column configuration: {column}")
    
    if not config['categories']:
        raise ValueError("Categories configuration cannot be empty")
    
    return True


def get_output_settings(config):
    """
    Get output settings with defaults applied.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Output settings
    """
    output_config = config.get('output', {})
    
    return {
        'include_timestamp': output_config.get('include_timestamp', True),
        'formats': output_config.get('formats', ['csv', 'json', 'txt']),
        'output_directory': output_config.get('output_directory', '')
    }


def get_analysis_settings(config):
    """
    Get analysis settings with defaults applied.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Analysis settings
    """
    analysis_config = config.get('analysis', {})
    
    return {
        'significant_difference_threshold': analysis_config.get('significant_difference_threshold', 0.2),
        'similar_threshold': analysis_config.get('similar_threshold', 0.1),
        'max_individual_responses': analysis_config.get('max_individual_responses', 10)
    }