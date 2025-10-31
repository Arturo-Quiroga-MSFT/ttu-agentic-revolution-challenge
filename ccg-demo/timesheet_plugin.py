"""Timesheet tool functions for the CCG Time & Expense agent."""

import json
import os
from datetime import datetime


def get_timesheet_entries(user_email: str = "alice@ccg.com") -> str:
    """
    Retrieves all existing timesheet entries for a consultant.
    
    Args:
        user_email: The email of the consultant whose timesheet to retrieve
        
    Returns:
        JSON string of timesheet entries with date, start, end, duration, task, project, and billable status
    """
    # Load timesheet entries from file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timesheet_path = os.path.join(script_dir, "timesheet_sample.json")
    
    try:
        with open(timesheet_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter by user if needed
        # In production, this would call a timesheet API or ERP system
        if data.get("user") == user_email:
            return json.dumps(data, indent=2)
        else:
            return json.dumps({"user": user_email, "entries": []})
    except FileNotFoundError:
        return json.dumps({"error": f"Timesheet file not found: {timesheet_path}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def suggest_timesheet_entry(
    user_email: str,
    date: str,
    start_time: str,
    end_time: str,
    duration_hours: float,
    task: str,
    project: str,
    billable: bool,
    rationale: str
) -> str:
    """
    Records a suggestion for a missing timesheet entry.
    
    Args:
        user_email: The consultant's email
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM:SS format
        end_time: End time in HH:MM:SS format
        duration_hours: Duration in hours
        task: Task description
        project: Project name
        billable: Whether the time is billable
        rationale: Explanation for why this entry is suggested
        
    Returns:
        JSON confirmation message
    """
    suggestion = {
        "user": user_email,
        "date": date,
        "start": start_time,
        "end": end_time,
        "duration_hours": duration_hours,
        "task": task,
        "project": project,
        "billable": billable,
        "rationale": rationale,
        "status": "suggested"
    }
    
    return json.dumps({
        "message": "Timesheet entry suggestion recorded",
        "suggestion": suggestion
    }, indent=2)


def calculate_revenue_impact(
    user_email: str = "alice@ccg.com",
    billable_rate: float = 250.0
) -> str:
    """
    Calculate potential revenue impact from missing billable time.
    
    Args:
        user_email: User's email address
        billable_rate: Hourly billable rate in dollars (default: $250/hour)
    
    Returns:
        JSON string with revenue impact analysis
    """
    # Load sample data to analyze gaps
    script_dir = os.path.dirname(os.path.abspath(__file__))
    calendar_file = os.path.join(script_dir, "calendar_sample.json")
    timesheet_file = os.path.join(script_dir, "timesheet_sample.json")
    
    try:
        with open(calendar_file, 'r') as f:
            calendar_events = json.load(f)
        
        with open(timesheet_file, 'r') as f:
            timesheet_data = json.load(f)
        
        # Simple calculation: find billable calendar events not in timesheet
        total_missing_hours = 0.0
        missing_entries = []
        
        for event in calendar_events:
            # Check if it's a billable event based on categories or title
            categories = event.get('categories', [])
            is_billable = any(cat.lower() in ['billable', 'client', 'travel'] 
                             for cat in categories)
            
            if is_billable:
                # Parse times and calculate duration
                start = datetime.fromisoformat(event['start'])
                end = datetime.fromisoformat(event['end'])
                duration = (end - start).total_seconds() / 3600
                
                # Check if already in timesheet (simplified check)
                found = False
                for entry in timesheet_data.get('entries', []):
                    if (entry['date'] == start.strftime('%Y-%m-%d') and 
                        abs(entry['duration_hours'] - duration) < 0.1):
                        found = True
                        break
                
                if not found:
                    total_missing_hours += duration
                    missing_entries.append({
                        "event": event['title'],
                        "date": start.strftime('%Y-%m-%d'),
                        "hours": round(duration, 2)
                    })
        
        revenue_impact = total_missing_hours * billable_rate
        
        return json.dumps({
            "user_email": user_email,
            "missing_billable_hours": round(total_missing_hours, 2),
            "billable_rate": billable_rate,
            "revenue_impact": round(revenue_impact, 2),
            "missing_entries": missing_entries,
            "analysis": f"Found {total_missing_hours:.1f} hours of unbilled time worth ${revenue_impact:,.2f}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
