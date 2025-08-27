#!/usr/bin/env python3
"""
Output Generation Module

Handles file output generation in multiple formats (JSON, TXT).
"""

import json
import os
from datetime import datetime
import pandas as pd


def create_run_directory(base_output_dir: str, selected_team: str, selected_location: str) -> str:
    """Create a timestamped directory for this analysis run."""
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


def generate_filename(base_name: str, extension: str, run_dir: str) -> str:
    """Generate simple filename within the run directory."""
    filename = f"{base_name}.{extension}"
    return os.path.join(run_dir, filename)



def save_json_summary(stats: dict, run_dir: str) -> str:
    """Save analysis summary to JSON format."""
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


def generate_text_report(stats: dict, categories: dict, recommendations: list, run_dir: str, missing_questions: list = None) -> str:
    """Generate comprehensive text report."""
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
        f.write(f"Categories Analyzed: {len(categories)}\n")
        
        # Report missing questions if any
        if missing_questions:
            f.write(f"Missing Questions: {len(missing_questions)} questions from config not found in data\n")
        
        f.write("\n")
        
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
            # Maintain config order instead of sorting by performance
            for i, (category, questions) in enumerate(categories.items(), 1):
                if category in stats['category_performance']:
                    score = stats['category_performance'][category]
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
        
        for category_name, questions_list in categories.items():
            if category_name in stats['question_details']:
                f.write(f"\n{category_name}:\n")
                questions_data = stats['question_details'][category_name]
                
                # Find highest and lowest scoring questions in this category
                valid_questions = []
                for question in questions_list:
                    if question in questions_data and questions_data[question]['filtered_score'] is not None:
                        valid_questions.append((question, questions_data[question]['filtered_score']))
                
                if valid_questions:
                    # Sort by score to find highest and lowest
                    sorted_questions = sorted(valid_questions, key=lambda x: x[1], reverse=True)
                    highest_question, highest_score = sorted_questions[0]
                    lowest_question, lowest_score = sorted_questions[-1]
                    
                    f.write(f"   🔥 Highest: {highest_question} ({highest_score:.2f})\n")
                    f.write(f"   ❄️  Lowest: {lowest_question} ({lowest_score:.2f})\n")
                    f.write(f"\n")
                
                # Process questions in config order
                for question in questions_list:
                    if question in questions_data:
                        data = questions_data[question]
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
        
        # Add missing questions section if any
        if missing_questions:
            f.write(f"\nMISSING QUESTIONS FROM CONFIG\n")
            f.write("-" * 40 + "\n")
            f.write("The following questions were listed in config but not found in the data file:\n\n")
            for category, question in missing_questions:
                f.write(f"[{category}]\n")
                f.write(f"   • {question}\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"End of Detailed Report for {team_display} + {location_display}\n")
    
    return filename


def save_analysis_results(df: pd.DataFrame, stats: dict, categories: dict, comment_fields: dict, recommendations: list, 
                          selected_team: str, selected_location: str, team_column: str, location_column: str, 
                          overall_df: pd.DataFrame, output_settings: dict, missing_questions: list = None) -> tuple[str, list]:
    """Save analysis results in all configured formats to a timestamped run directory."""
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
    txt_file = generate_text_report(stats, categories, recommendations, run_dir, missing_questions)
    generated_files.append(txt_file)
    print(f"📄 Report saved to: {os.path.basename(txt_file)}")
    
    
    print(f"\n📁 All files saved in: {run_dir}")
    
    return run_dir, generated_files