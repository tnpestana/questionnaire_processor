#!/usr/bin/env python3
"""
Configuration Management Module

Handles YAML configuration loading, validation, and default creation.
"""

import yaml
import os


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
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



def validate_config(config: dict) -> bool:
    """Validate configuration structure and required fields."""
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


def get_output_settings(config: dict) -> dict:
    """Get output settings with defaults applied."""
    output_config = config.get('output', {})
    
    return {
        'include_timestamp': output_config.get('include_timestamp', True),
    }


def get_analysis_settings(config: dict) -> dict:
    """Get analysis settings with defaults applied."""
    analysis_config = config.get('analysis', {})
    
    return {
        'significant_difference_threshold': analysis_config.get('significant_difference_threshold', 0.2),
        'similar_threshold': analysis_config.get('similar_threshold', 0.1),
        'max_individual_responses': analysis_config.get('max_individual_responses', 10)
    }