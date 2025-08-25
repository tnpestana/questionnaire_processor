#!/usr/bin/env python3
"""
User Interface Module

Handles user interaction and input collection.
"""


def get_user_selections(group_info):
    """
    Prompt user to select specific team and location for detailed analysis.
    
    Args:
        group_info (dict): Information about available groups
        
    Returns:
        tuple: (selected_team, selected_location) or (None, None) if cancelled
    """
    print("\n" + "="*60)
    print("🎯 DETAILED ANALYSIS SELECTION")
    print("="*60)
    print("Select a specific team and location combination for detailed analysis.")
    print("Choose 'All' for either dimension to include all groups in that category.")
    
    # Team selection
    selected_team = None
    if 'teams' in group_info:
        print(f"\n👥 Available Teams ({group_info['teams']['total']}):")
        for i, team in enumerate(group_info['teams']['names'], 1):
            count = group_info['teams']['counts'][team]
            print(f"   {i}. {team} ({count} responses)")
        
        all_teams_num = len(group_info['teams']['names']) + 1
        print(f"   {all_teams_num}. All Teams - Include all team data")
        
        while True:
            try:
                print(f"\n🔢 Select team (1-{all_teams_num}): ", end="")
                choice = input().strip()
                
                if not choice:
                    print("🚨 Please enter a number.")
                    continue
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(group_info['teams']['names']):
                    selected_team = group_info['teams']['names'][choice_num - 1]
                    print(f"✅ Selected team: {selected_team}")
                    break
                elif choice_num == all_teams_num:
                    selected_team = 'all'
                    print(f"✅ Selected: All Teams")
                    break
                else:
                    print(f"🚨 Please enter a number between 1 and {all_teams_num}.")
                    
            except ValueError:
                print("🚨 Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Analysis cancelled by user.")
                return None, None
    
    # Location selection
    selected_location = None
    if 'locations' in group_info:
        print(f"\n🌍 Available Locations ({group_info['locations']['total']}):")
        for i, location in enumerate(group_info['locations']['names'], 1):
            count = group_info['locations']['counts'][location]
            print(f"   {i}. {location} ({count} responses)")
        
        all_locations_num = len(group_info['locations']['names']) + 1
        print(f"   {all_locations_num}. All Locations - Include all location data")
        
        while True:
            try:
                print(f"\n🔢 Select location (1-{all_locations_num}): ", end="")
                choice = input().strip()
                
                if not choice:
                    print("🚨 Please enter a number.")
                    continue
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(group_info['locations']['names']):
                    selected_location = group_info['locations']['names'][choice_num - 1]
                    print(f"✅ Selected location: {selected_location}")
                    break
                elif choice_num == all_locations_num:
                    selected_location = 'all'
                    print(f"✅ Selected: All Locations")
                    break
                else:
                    print(f"🚨 Please enter a number between 1 and {all_locations_num}.")
                    
            except ValueError:
                print("🚨 Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Analysis cancelled by user.")
                return None, None
    
    # Show final selection
    team_display = selected_team if selected_team != 'all' else 'All Teams'
    location_display = selected_location if selected_location != 'all' else 'All Locations'
    print(f"\n🎉 Final Selection: {team_display} + {location_display}")
    
    return selected_team, selected_location


def display_analysis_results(stats, categories, recommendations):
    """
    Display analysis results to the console.
    
    Args:
        stats (dict): Analysis statistics
        categories (dict): Category definitions
        recommendations (list): Recommendations
    """
    selected_team = stats['metadata']['selected_team']
    selected_location = stats['metadata']['selected_location']
    
    team_display = selected_team if selected_team != 'all' else 'All Teams'
    location_display = selected_location if selected_location != 'all' else 'All Locations'
    
    print("\n" + "="*70)
    print(f"🔍 DETAILED ANALYSIS: {team_display} + {location_display}")
    print("="*70)
    print(f"Filtered Dataset: {stats['metadata']['filtered_responses']} responses")
    
    if stats['metadata']['filtered_responses'] == 0:
        print("⚠️  No responses found for this team+location combination!")
        return
    
    # Category performance
    print(f"\n📈 Category Performance for {team_display} + {location_display}:")
    sorted_categories = sorted(stats['category_performance'].items(), key=lambda x: x[1], reverse=True)
    for i, (category, score) in enumerate(sorted_categories, 1):
        print(f"   {i}. {category}: {score:.2f}")
    
    # Detailed question analysis
    print(f"\n📊 Detailed Question Analysis:")
    for category_name, questions_data in stats['question_details'].items():
        print(f"\n   {category_name}:")
        for question, data in questions_data.items():
            if data['filtered_score'] is not None:
                print(f"      • {question}: {data['filtered_score']:.2f} ({data['filtered_responses']} responses)")
            else:
                print(f"      • {question}: No data ({data['filtered_responses']} responses)")
    
    # Comments by Category
    if 'comments' in stats and stats['comments']:
        print(f"\n💬 Comments by Category:")
        for category_name, comment_data in stats['comments'].items():
            print(f"\n   {category_name} ({comment_data['count']} comments):")
            
            for i, comment in enumerate(comment_data['comments'], 1):
                # Show team/location if analyzing 'all'
                team_info = f" - {comment['team']}" if selected_team == 'all' else ""
                location_info = f" ({comment['location']})" if selected_location == 'all' else ""
                
                # Limit comment display length for console
                comment_text = comment['text']
                if len(comment_text) > 100:
                    comment_text = comment_text[:97] + "..."
                
                print(f"      {i}. \"{comment_text}\"{team_info}{location_info}")
    
    # Comparison with overall data
    print(f"\n🔄 Comparison with Overall Averages:")
    for category_name, comparison in stats['comparisons'].items():
        difference = comparison['difference']
        status_emoji = "🟢 Above" if difference > 0.1 else "🟡 Similar" if abs(difference) <= 0.1 else "🔴 Below"
        print(f"   {category_name}: {comparison['filtered_score']:.2f} vs {comparison['overall_score']:.2f} "
               f"({difference:+.2f}) {status_emoji}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, recommendation in enumerate(recommendations, 1):
        print(f"   {i}. {recommendation}")