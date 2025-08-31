#!/usr/bin/env python3
"""
Output Generation Module

Handles file output generation in multiple formats (JSON, TXT, MD).
"""

import json
import os
from datetime import datetime
import pandas as pd


def create_run_directory(base_output_dir: str, selected_team: str, selected_location: str) -> str:
    """Create a timestamped directory for this analysis run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    team_part = selected_team.replace(' ', '_') if selected_team != 'all' else 'AllTeams'
    location_part = selected_location.replace(' ', '_') if selected_location != 'all' else 'AllLocations'
    
    run_folder_name = f"{timestamp}_{team_part}_{location_part}"
    run_dir = os.path.join(base_output_dir, run_folder_name)
    
    os.makedirs(run_dir, exist_ok=True)
    print(f"📁 Created analysis run directory: {run_dir}")
    return run_dir


def generate_filename(base_name: str, extension: str, run_dir: str) -> str:
    """Generate simple filename within the run directory."""
    return os.path.join(run_dir, f"{base_name}.{extension}")


def save_json_summary(stats: dict, run_dir: str) -> str:
    """Save analysis summary to JSON format."""
    filename = generate_filename("summary", "json", run_dir)
    
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
                {"rank": i + 1, "category": category, "average_score": score}
                for i, (category, score) in enumerate(
                    sorted(stats['category_performance'].items(), key=lambda x: x[1], reverse=True)
                )
            ]
        },
        "detailed_question_analysis": stats['question_details']
    }
    
    if 'comments' in stats and stats['comments']:
        json_data["comments_by_category"] = stats['comments']
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return filename


class ReportFormatter:
    """Handles format-specific styling for reports."""
    
    def __init__(self, format_type: str):
        self.format_type = format_type
        
        if format_type == 'md':
            self.config = {
                'h1': '# ', 'h2': '## ', 'h3': '### ', 'h4': '#### ',
                'bold': lambda x: f'**{x}**',
                'italic': lambda x: f'*{x}*',
                'hr': '\n---\n\n',
                'section_break': '\n',
                'list_item': lambda x: f'- {x}',
                'trend_up': '📈', 'trend_neutral': '➡️', 'trend_down': '📉',
                'trophy': '🏆', 'warning': '⚠️',
                'table_start': lambda headers: self._md_table_header(headers),
                'table_row': lambda cells: f"| {' | '.join(str(cell) for cell in cells)} |\n"
            }
        else:  # txt format
            self.config = {
                'h1': '', 'h2': '', 'h3': '', 'h4': '',
                'bold': lambda x: x,
                'italic': lambda x: f'"{x}"',
                'hr': '\n' + '=' * 50 + '\n\n',
                'section_break': '\n',
                'list_item': lambda x: f'  • {x}',
                'trend_up': '↗', 'trend_neutral': '→', 'trend_down': '↘',
                'trophy': 'Top Performer(s)', 'warning': 'Needs Attention',
                'table_start': lambda headers: '',
                'table_row': lambda cells: f"{cells[0]}. {cells[1]}\n   Score: {cells[2]} | Benchmark: {cells[3]} | Variance: {cells[4]} | Status: {cells[5]}\n"
            }
    
    def _md_table_header(self, headers):
        header_row = f"| {' | '.join(headers)} |\n"
        separator = f"|{'|'.join(['---' for _ in headers])}|\n"
        return header_row + separator
    
    def format_element(self, element_type, *args, **kwargs):
        """Apply formatting for the specified element type."""
        if element_type in self.config:
            formatter = self.config[element_type]
            if callable(formatter):
                return formatter(*args, **kwargs)
            return formatter
        return str(args[0]) if args else ''


def generate_unified_report(stats: dict, categories: dict, recommendations: list, run_dir: str, format_type: str, missing_questions: list = None) -> str:
    """Generate report in specified format using unified logic."""
    filename = generate_filename("report", format_type, run_dir)
    formatter = ReportFormatter(format_type)
    
    # Extract common data
    selected_team = stats['metadata']['selected_team']
    selected_location = stats['metadata']['selected_location']
    team_display = selected_team if selected_team != 'all' else 'All Teams'
    location_display = selected_location if selected_location != 'all' else 'All Locations'
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"{formatter.format_element('h1')}Form Data Analysis Report\n\n")
        if format_type == 'md':
            f.write(f"**Focus:** {team_display} + {location_display}  \n")
            f.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}  \n")
            f.write(f"**Sample Size:** {stats['metadata']['filtered_responses']} responses (from {stats['metadata']['total_responses']} total)  \n")
            f.write(f"**Categories:** {len(stats['category_performance'])}  \n")
            if missing_questions:
                f.write(f"**Note:** {len(missing_questions)} question{'s' if len(missing_questions) != 1 else ''} from config not found in data  \n")
        else:
            f.write("=" * 80 + "\n")
            f.write(f"Focus: {team_display} + {location_display}\n")
            f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n")
            f.write(f"Sample Size: {stats['metadata']['filtered_responses']} responses (from {stats['metadata']['total_responses']} total)\n")
            f.write(f"Categories: {len(stats['category_performance'])}\n")
            if missing_questions:
                f.write(f"Note: {len(missing_questions)} question{'s' if len(missing_questions) != 1 else ''} from config not found in data\n")
        
        f.write(formatter.format_element('hr'))
        
        # Category Performance
        f.write(f"{formatter.format_element('h2')}Category Performance Overview\n\n")
        
        if stats['category_performance']:
            valid_categories = [(cat, score) for cat, score in stats['category_performance'].items() if score is not None]
            if valid_categories:
                sorted_categories = sorted(valid_categories, key=lambda x: x[1], reverse=True)
                highest_score, lowest_score = sorted_categories[0][1], sorted_categories[-1][1]
                
                highest_cats = [cat for cat, score in valid_categories if score == highest_score]
                lowest_cats = [cat for cat, score in valid_categories if score == lowest_score]
                
                # Top/Bottom performers
                f.write(f"{formatter.format_element('h3')}{formatter.format_element('trophy')} Top Performer(s)\n")
                for cat in highest_cats:
                    bold_cat = formatter.format_element('bold', cat)
                    f.write(f"{formatter.format_element('list_item', f'{bold_cat} (score: {highest_score:.2f})')}\n")
                
                f.write(f"\n{formatter.format_element('h3')}{formatter.format_element('warning')} Needs Attention\n")
                for cat in lowest_cats:
                    bold_cat = formatter.format_element('bold', cat)
                    f.write(f"{formatter.format_element('list_item', f'{bold_cat} (score: {lowest_score:.2f})')}\n")
                
                # Detailed scores
                f.write(f"\n{formatter.format_element('h3')}Detailed Category Scores\n\n")
                
                if format_type == 'md':
                    f.write(formatter.format_element('table_start', ['#', 'Category', 'Score', 'Benchmark', 'Variance', 'Status']))
                else:
                    f.write("-" * 25 + "\n")
                
                for i, (category, questions) in enumerate(categories.items(), 1):
                    if category in stats['category_performance']:
                        score = stats['category_performance'][category]
                        comparison = stats['comparisons'].get(category, {})
                        overall_avg = comparison.get('overall_score', 0)
                        difference = comparison.get('difference', 0)
                        
                        if difference > 0.1:
                            status = "Above Average"
                            trend = formatter.format_element('trend_up')
                        elif abs(difference) <= 0.1:
                            status = "At Average"
                            trend = formatter.format_element('trend_neutral')
                        else:
                            status = "Below Average"
                            trend = formatter.format_element('trend_down')
                        
                        status_with_trend = f"{status} {trend}"
                        
                        if format_type == 'md':
                            f.write(formatter.format_element('table_row', [i, category, f"{score:.2f}", f"{overall_avg:.2f}", f"{difference:+.2f}", status_with_trend]))
                        else:
                            f.write(f"{i}. {category}\n")
                            f.write(f"   Score: {score:.2f} | Benchmark: {overall_avg:.2f} | Variance: {difference:+.2f} | Status: {status_with_trend}\n")
        else:
            f.write("No data available for selected combination.\n")
        
        f.write(formatter.format_element('hr'))
        
        # Question Analysis
        f.write(f"{formatter.format_element('h2')}Question-Level Analysis\n\n")
        
        for category_name, questions_list in categories.items():
            if category_name in stats['question_details']:
                f.write(f"{formatter.format_element('h3')}{category_name}\n")
                if format_type == 'txt':
                    f.write("-" * len(category_name) + "\n")
                f.write("\n")
                
                questions_data = stats['question_details'][category_name]
                
                # Find highest and lowest scoring questions
                valid_questions = [(q, questions_data[q]['filtered_score']) 
                                 for q in questions_list 
                                 if q in questions_data and questions_data[q]['filtered_score'] is not None]
                
                if valid_questions:
                    sorted_questions = sorted(valid_questions, key=lambda x: x[1], reverse=True)
                    highest_score, lowest_score = sorted_questions[0][1], sorted_questions[-1][1]
                    
                    highest_questions = [q for q, score in valid_questions if score == highest_score]
                    lowest_questions = [q for q, score in valid_questions if score == lowest_score]
                    
                    # Top/Bottom questions
                    f.write(f"{formatter.format_element('h4')}{formatter.format_element('trophy')} Strongest Performance\n")
                    for q in highest_questions:
                        bold_q = formatter.format_element('bold', q)
                        f.write(f"{formatter.format_element('list_item', f'{bold_q} (score: {highest_score:.2f})')}\n")
                    
                    f.write(f"\n{formatter.format_element('h4')}{formatter.format_element('warning')} Weakest Performance\n")
                    for q in lowest_questions:
                        bold_q = formatter.format_element('bold', q)
                        f.write(f"{formatter.format_element('list_item', f'{bold_q} (score: {lowest_score:.2f})')}\n")
                    
                    f.write(f"\n{formatter.format_element('h4')}Complete Question Breakdown\n\n")
                    
                    if format_type == 'md':
                        f.write(formatter.format_element('table_start', ['#', 'Question', 'Score', 'Benchmark', 'Variance', 'Responses', 'Trend']))
                    
                    # All questions
                    for i, question in enumerate(questions_list, 1):
                        if question in questions_data:
                            data = questions_data[question]
                            filtered_score = data['filtered_score']
                            overall_score = data['overall_score']
                            difference = data['difference']
                            responses = data['filtered_responses']
                            
                            if filtered_score is not None:
                                if difference > 0.1:
                                    trend = formatter.format_element('trend_up')
                                    performance = "above average"
                                elif abs(difference) <= 0.1:
                                    trend = formatter.format_element('trend_neutral')
                                    performance = "at average"
                                else:
                                    trend = formatter.format_element('trend_down')
                                    performance = "below average"
                                
                                if format_type == 'md':
                                    f.write(formatter.format_element('table_row', [i, question, f"{filtered_score:.2f}", f"{overall_score:.2f}", f"{difference:+.2f}", responses, trend]))
                                else:
                                    f.write(f"{i}. {question}\n")
                                    f.write(f"   Score: {filtered_score:.2f} | Benchmark: {overall_score:.2f} | Variance: {difference:+.2f} | Responses: {responses} | Trend: {performance} {trend}\n")
                            else:
                                if format_type == 'md':
                                    f.write(formatter.format_element('table_row', [i, question, "No data", "-", "-", responses, "-"]))
                                else:
                                    f.write(f"{i}. {question}\n")
                                    f.write(f"   Score: No data available | Responses: {responses}\n")
                f.write("\n")
        
        # Comments
        if 'comments' in stats and stats['comments']:
            f.write(f"{formatter.format_element('h2')}Respondent Feedback\n\n")
            
            for category_name, comment_data in stats['comments'].items():
                f.write(f"{formatter.format_element('h3')}{category_name}\n")
                comment_count_text = f"{comment_data['count']} comment{'s' if comment_data['count'] != 1 else ''}"
                
                if format_type == 'md':
                    f.write(f"{formatter.format_element('italic', comment_count_text)}\n\n")
                else:
                    f.write(f"({comment_count_text})\n")
                    f.write("-" * len(category_name) + "\n")
                
                for i, comment in enumerate(comment_data['comments'], 1):
                    team_info = f" [{comment['team']}]" if selected_team == 'all' else ""
                    location_info = f" [{comment['location']}]" if selected_location == 'all' else ""
                    
                    if format_type == 'md':
                        team_info = formatter.format_element('bold', team_info) if team_info else ""
                        location_info = formatter.format_element('bold', location_info) if location_info else ""
                        italic_comment = formatter.format_element('italic', f'"{comment["text"]}"')
                        f.write(f"{i}. {italic_comment}{team_info}{location_info}\n")
                    else:
                        f.write(f"{i}. \"{comment['text']}\"{team_info}{location_info}\n")
                f.write("\n")
        
        # Recommendations
        f.write(f"{formatter.format_element('h2')}Action Recommendations\n\n")
        for i, recommendation in enumerate(recommendations, 1):
            f.write(f"{i}. {recommendation}\n")
        
        # Missing questions
        if missing_questions:
            f.write(f"\n{formatter.format_element('h2')}Data Quality Notes\n\n")
            validation_text = f"Configuration Validation: {len(missing_questions)} question{'s' if len(missing_questions) != 1 else ''} from configuration not found in dataset"
            
            if format_type == 'md':
                bold_validation = formatter.format_element('bold', validation_text)
                f.write(f"{bold_validation}\n\n")
                for category, question in missing_questions:
                    bold_category = formatter.format_element('bold', 'Category:')
                    bold_missing = formatter.format_element('bold', 'Missing:')
                    f.write(f"{formatter.format_element('list_item', f'{bold_category} {category}')}\n")
                    f.write(f"  {bold_missing} {question}\n\n")
            else:
                f.write(f"{validation_text}\n\n")
                for category, question in missing_questions:
                    f.write(f"Category: {category}\n")
                    f.write(f"Missing: {question}\n\n")
        
        # Footer
        if format_type == 'md':
            f.write("\n---\n\n")
            italic_timestamp = formatter.format_element('italic', f'Report Generated: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}')
            italic_complete = formatter.format_element('italic', f'Analysis Complete for {team_display} + {location_display}')
            f.write(f"{italic_timestamp}\n")
            f.write(f"{italic_complete}\n")
        else:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n")
            f.write(f"Analysis Complete for {team_display} + {location_display}\n")
            f.write("=" * 80)
    
    return filename


def generate_text_report(stats: dict, categories: dict, recommendations: list, run_dir: str, missing_questions: list = None) -> str:
    """Generate comprehensive text report."""
    return generate_unified_report(stats, categories, recommendations, run_dir, 'txt', missing_questions)


def generate_markdown_report(stats: dict, categories: dict, recommendations: list, run_dir: str, missing_questions: list = None) -> str:
    """Generate comprehensive Markdown report with enhanced formatting."""
    return generate_unified_report(stats, categories, recommendations, run_dir, 'md', missing_questions)


def save_analysis_results(df: pd.DataFrame, stats: dict, categories: dict, comment_fields: dict, recommendations: list, 
                          selected_team: str, selected_location: str, team_column: str, location_column: str, 
                          overall_df: pd.DataFrame, output_settings: dict, missing_questions: list = None) -> tuple[str, list]:
    """Save analysis results in all configured formats to a timestamped run directory."""
    run_dir = create_run_directory('output', selected_team, selected_location)
    generated_files = []
    
    print("\n" + "=" * 50)
    print("💾 SAVING ANALYSIS RESULTS")
    print("=" * 50)
    
    # Save all formats
    json_file = save_json_summary(stats, run_dir)
    generated_files.append(json_file)
    print(f"📋 Summary saved to: {os.path.basename(json_file)}")
    
    txt_file = generate_text_report(stats, categories, recommendations, run_dir, missing_questions)
    generated_files.append(txt_file)
    print(f"📄 Report saved to: {os.path.basename(txt_file)}")
    
    md_file = generate_markdown_report(stats, categories, recommendations, run_dir, missing_questions)
    generated_files.append(md_file)
    print(f"📝 Markdown report saved to: {os.path.basename(md_file)}")
    
    print(f"\n📁 All files saved in: {run_dir}")
    return run_dir, generated_files