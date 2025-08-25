#!/usr/bin/env python3
"""
Output Generation Module

Handles file output generation in multiple formats (JSON, TXT, Excel).
"""

import json
import os
from datetime import datetime
import pandas as pd
from excel_visualizer import create_excel_dashboard


def create_run_directory(base_output_dir, selected_team, selected_location):
    """
    Create a timestamped directory for this analysis run.
    
    Args:
        base_output_dir (str): Base output directory path
        selected_team (str): Selected team name
        selected_location (str): Selected location name
        
    Returns:
        str: Path to the created run directory
    """
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create descriptive folder name
    team_part = selected_team.replace(' ', '_') if selected_team != 'all' else 'AllTeams'
    location_part = selected_location.replace(' ', '_') if selected_location != 'all' else 'AllLocations'
    
    run_folder_name = f"{timestamp}_{team_part}_{location_part}"
    run_dir = os.path.join(base_output_dir, run_folder_name)
    
    # Create the directory
    os.makedirs(run_dir, exist_ok=True)
    print(f"📁 Created analysis run directory: {run_dir}")
    
    return run_dir


def generate_filename(base_name, extension, run_dir):
    """
    Generate simple filename within the run directory.
    
    Args:
        base_name (str): Base filename (e.g., 'data', 'summary', 'report')
        extension (str): File extension
        run_dir (str): Run directory path
        
    Returns:
        str: Complete filename with path
    """
    filename = f"{base_name}.{extension}"
    return os.path.join(run_dir, filename)



def save_json_summary(stats, run_dir):
    """
    Save analysis summary to JSON format.
    
    Args:
        stats (dict): Analysis statistics
        run_dir (str): Run directory path
        
    Returns:
        str: Filename of saved file
    """
    filename = generate_filename("summary", "json", run_dir)
    
    # Prepare JSON data structure
    json_data = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "analysis_focus": f"{stats['metadata']['selected_team']} + {stats['metadata']['selected_location']}",
            "selected_team": stats['metadata']['selected_team'],
            "selected_location": stats['metadata']['selected_location'],
            "filtered_responses": stats['metadata']['filtered_responses'],
            "total_responses": stats['metadata']['total_responses']
        },
        "category_performance": {
            "filtered_averages": stats['category_performance'],
            "comparison_with_overall": stats['comparisons'],
            "ranked_categories": [
                {
                    "rank": i + 1,
                    "category": category,
                    "average_score": score
                }
                for i, (category, score) in enumerate(
                    sorted(stats['category_performance'].items(), key=lambda x: x[1], reverse=True)
                )
            ]
        },
        "detailed_question_analysis": stats['question_details']
    }
    
    # Add comments if available
    if 'comments' in stats and stats['comments']:
        json_data["comments_by_category"] = stats['comments']
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return filename


def generate_text_report(stats, categories, recommendations, run_dir):
    """
    Generate comprehensive text report.
    
    Args:
        stats (dict): Analysis statistics
        categories (dict): Category definitions
        recommendations (list): List of recommendations
        run_dir (str): Run directory path
        
    Returns:
        str: Filename of saved file
    """
    filename = generate_filename("report", "txt", run_dir)
    
    # Get team and location from stats
    selected_team = stats['metadata']['selected_team']
    selected_location = stats['metadata']['selected_location']
    
    team_display = selected_team if selected_team != 'all' else 'All Teams'
    location_display = selected_location if selected_location != 'all' else 'All Locations'
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"FORM DATA ANALYSIS REPORT - {team_display} + {location_display}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Analysis Focus: {team_display} + {location_display}\n")
        f.write(f"Filtered Responses: {stats['metadata']['filtered_responses']}\n")
        f.write(f"Total Responses in Dataset: {stats['metadata']['total_responses']}\n")
        f.write(f"Categories Analyzed: {len(categories)}\n\n")
        
        # Executive Summary
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 40 + "\n")
        
        if stats['category_performance']:
            best_category = max(stats['category_performance'], key=stats['category_performance'].get)
            worst_category = min(stats['category_performance'], key=stats['category_performance'].get)
            f.write(f"• Highest performing category for selected combination: {best_category} "
                   f"(avg: {stats['category_performance'][best_category]:.2f})\n")
            f.write(f"• Lowest performing category for selected combination: {worst_category} "
                   f"(avg: {stats['category_performance'][worst_category]:.2f})\n")
        f.write("\n")
        
        # Category Performance Analysis
        f.write(f"CATEGORY PERFORMANCE ANALYSIS - {team_display} + {location_display}\n")
        f.write("-" * 40 + "\n")
        
        if stats['category_performance']:
            sorted_categories = sorted(stats['category_performance'].items(), key=lambda x: x[1], reverse=True)
            for i, (category, score) in enumerate(sorted_categories, 1):
                # Show comparison with overall average
                comparison = stats['comparisons'].get(category, {})
                overall_avg = comparison.get('overall_score', 0)
                difference = comparison.get('difference', 0)
                
                status_emoji = "⬆️" if difference > 0.1 else "➡️" if abs(difference) <= 0.1 else "⬇️"
                f.write(f"{i}. {category}: {score:.2f} (vs overall {overall_avg:.2f}, {difference:+.2f}) {status_emoji}\n")
        else:
            f.write("No data available for selected combination.\n")
        f.write("\n")
        
        # Detailed Question Analysis
        f.write("DETAILED QUESTION ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        for category_name, questions_data in stats['question_details'].items():
            f.write(f"\n{category_name}:\n")
            for question, data in questions_data.items():
                filtered_score = data['filtered_score']
                overall_score = data['overall_score']
                difference = data['difference']
                responses = data['filtered_responses']
                
                if filtered_score is not None:
                    f.write(f"   • {question}: {filtered_score:.2f} "
                           f"(vs overall {overall_score:.2f}, {difference:+.2f}) "
                           f"({responses} responses)\n")
                else:
                    f.write(f"   • {question}: No data ({responses} responses)\n")
        
        # Comments by Category
        if 'comments' in stats and stats['comments']:
            f.write(f"\nCOMMENTS BY CATEGORY\n")
            f.write("-" * 40 + "\n")
            
            for category_name, comment_data in stats['comments'].items():
                f.write(f"\n{category_name} ({comment_data['count']} comments):\n")
                
                for i, comment in enumerate(comment_data['comments'], 1):
                    # Show team/location if analyzing 'all'
                    team_info = f" - {comment['team']}" if selected_team == 'all' else ""
                    location_info = f" ({comment['location']})" if selected_location == 'all' else ""
                    
                    f.write(f"   {i}. \"{comment['text']}\"{team_info}{location_info}\n")
        
        # Recommendations
        f.write(f"\nRECOMMENDATIONS FOR {team_display} + {location_display}\n")
        f.write("-" * 40 + "\n")
        
        for i, recommendation in enumerate(recommendations, 1):
            f.write(f"{i}. {recommendation}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"End of Detailed Report for {team_display} + {location_display}\n")
    
    return filename


def save_analysis_results(df, stats, categories, comment_fields, recommendations, selected_team, selected_location, 
                          team_column, location_column, overall_df, output_settings):
    """
    Save analysis results in all configured formats to a timestamped run directory.
    
    Args:
        df (pandas.DataFrame): Processed/filtered data
        stats (dict): Analysis statistics
        categories (dict): Category definitions
        comment_fields (dict): Comment field mappings
        recommendations (list): Recommendations
        selected_team (str): Selected team
        selected_location (str): Selected location
        team_column (str): Team column name
        location_column (str): Location column name
        overall_df (pandas.DataFrame): Complete original dataset
        output_settings (dict): Output configuration
        
    Returns:
        tuple: (run_directory_path, list_of_generated_filenames)
    """
    # Create timestamped run directory (always use 'output' folder)
    run_dir = create_run_directory('output', selected_team, selected_location)
    
    generated_files = []
    
    print("\n" + "=" * 50)
    print(f"💾 SAVING ANALYSIS RESULTS")
    print("=" * 50)
    
    # Always save JSON summary
    json_file = save_json_summary(stats, run_dir)
    generated_files.append(json_file)
    print(f"📋 Summary saved to: {os.path.basename(json_file)}")
    
    # Always save text report
    txt_file = generate_text_report(stats, categories, recommendations, run_dir)
    generated_files.append(txt_file)
    print(f"📄 Report saved to: {os.path.basename(txt_file)}")
    
    # Always save Excel dashboard with charts
    excel_file = create_excel_dashboard(
        stats, categories, comment_fields, overall_df, df,
        team_column, location_column, selected_team, selected_location, run_dir
    )
    generated_files.append(excel_file)
    print(f"📊 Excel dashboard saved to: {os.path.basename(excel_file)}")
    
    print(f"\n📁 All files saved in: {run_dir}")
    
    return run_dir, generated_files