#!/usr/bin/env python3
"""
Form Analysis Main Application

Orchestrates the form data analysis process using modular components.
This is the main entry point for the configurable form analysis tool.
"""

import sys
from config_manager import load_config, validate_config, get_output_settings, get_analysis_settings
from data_processor import load_data, extract_likert_scores, validate_columns, analyze_available_groups, filter_data
from analyzer import generate_detailed_statistics, get_recommendations
from output_generator import save_analysis_results
from user_interface import get_user_selections, display_analysis_results


def main():
    """Main function to run interactive category-focused analysis"""
    
    print("🚀 Enhanced Form Data Analysis - Modular Architecture")
    print("=" * 60)
    
    try:
        # Load and validate configuration
        config = load_config()
        validate_config(config)
        
        # Get configuration sections
        data_source = config['data_source']
        columns = config['columns']
        categories = config['categories']
        comment_fields = config.get('comment_fields', {})
        output_settings = get_output_settings(config)
        analysis_settings = get_analysis_settings(config)
        
        # Load data
        print(f"\n📂 Loading data from: {data_source['file_path']}")
        df = load_data(data_source['file_path'], data_source.get('sheet_name'))
        
        # Validate required columns exist
        validate_columns(df, columns['team_column'], columns['location_column'])
        
        # Extract numeric scores from Likert responses
        likert_mapping = config.get('likert_mapping', None)
        df_numeric, categories, missing_questions = extract_likert_scores(df, categories, likert_mapping)
        
        # Analyze available groups
        group_info = analyze_available_groups(
            df_numeric, 
            columns['team_column'], 
            columns['location_column']
        )
        
        # Get user selections
        selected_team, selected_location = get_user_selections(group_info)
        
        if selected_team is None or selected_location is None:
            print("👋 Analysis cancelled by user.")
            return None
        
        # Filter data based on selections
        filtered_df = filter_data(
            df_numeric,
            columns['team_column'],
            columns['location_column'], 
            selected_team,
            selected_location
        )
        
        # Generate detailed statistics
        stats = generate_detailed_statistics(
            filtered_df,
            df_numeric,
            categories,
            comment_fields,
            columns['team_column'],
            columns['location_column'],
            selected_team,
            selected_location
        )
        
        # Generate recommendations
        recommendations = get_recommendations(stats, categories)
        
        # Display results to console
        display_analysis_results(stats, categories, recommendations)
        
        # Save analysis results to files
        run_dir, generated_files = save_analysis_results(
            filtered_df,
            stats,
            categories,
            comment_fields,
            recommendations,
            selected_team,
            selected_location,
            columns['team_column'],
            columns['location_column'],
            df_numeric,
            output_settings,
            missing_questions
        )
        
        # Final success message
        team_name = selected_team if selected_team != 'all' else 'All Teams'
        location_name = selected_location if selected_location != 'all' else 'All Locations'
        print(f"\n✨ Analysis complete for {team_name} + {location_name}!")
        print(f"📄 Generated {len(generated_files)} files in run directory")
        
        return df_numeric
        
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        return None
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted by user.")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = main()