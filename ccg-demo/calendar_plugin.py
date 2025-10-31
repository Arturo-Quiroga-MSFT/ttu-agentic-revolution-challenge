"""Calendar tool functions for the CCG Time & Expense agent."""

import json
import os


def get_calendar_events(user_email: str = "alice@ccg.com") -> str:
    """
    Retrieves all calendar events for a consultant for analysis.
    
    Args:
        user_email: The email of the consultant whose calendar to retrieve
        
    Returns:
        JSON string of calendar events with title, start, end, location, and description
    """
    # Load calendar events from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calendar_path = os.path.join(script_dir, "calendar_sample.json")
    
    try:
        with open(calendar_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        # Filter by user if needed (in this sample, all events are for alice@ccg.com)
        # In production, this would call Microsoft Graph API or another calendar service
        
        return json.dumps(events, indent=2)
    except FileNotFoundError:
        return json.dumps({"error": f"Calendar file not found: {calendar_path}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
