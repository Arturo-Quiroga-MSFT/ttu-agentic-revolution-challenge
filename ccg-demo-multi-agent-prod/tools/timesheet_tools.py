"""
Timesheet Write Tools - Functions for writing approved entries to timesheet
===========================================================================
These tools allow the approval agent to write approved suggestions to
the timesheet system with full audit logging.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def add_timesheet_entry(
    user_email: str,
    date: str,
    start_time: str,
    end_time: str,
    duration_hours: float,
    task: str,
    project: str,
    billable: bool,
    approved_by: str = "system"
) -> str:
    """
    Add an approved timesheet entry to the user's timesheet.
    
    This function writes to the actual timesheet file and logs the operation
    for audit purposes.
    
    Args:
        user_email: The email address of the consultant
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM format (24-hour)
        end_time: End time in HH:MM format (24-hour)
        
    Returns:
        JSON confirmation of the write operation
    """
    timesheet_path = Path(__file__).parent.parent / "shared" / "timesheet_sample.json"
    
    # Load existing timesheet (array of user objects)
    try:
        with open(timesheet_path, 'r') as f:
            timesheet_data = json.load(f)
    except FileNotFoundError:
        timesheet_data = []
    
    # Find user's timesheet entry in the array
    user_timesheet = None
    for user_entry in timesheet_data:
        if user_entry.get("user") == user_email:
            user_timesheet = user_entry
            break
    
    # If user doesn't exist, create new user entry
    if user_timesheet is None:
        user_timesheet = {"user": user_email, "entries": []}
        timesheet_data.append(user_timesheet)
    
    # Generate new entry ID
    max_id = 0
    for user_entry in timesheet_data:
        for entry in user_entry.get("entries", []):
            entry_id = entry.get("id", "ts-000")
            try:
                id_num = int(entry_id.split('-')[1])
                max_id = max(max_id, id_num)
            except (ValueError, IndexError):
                continue
    
    # Create new entry
    new_entry = {
        "id": f"ts-{max_id + 1:03d}",
        "date": date,
        "start": start_time,
        "end": end_time,
        "duration_hours": duration_hours,
        "task": task,
        "project": project,
        "billable": billable,
        "added_by_system": True,
        "approved_by": approved_by,
        "created_at": datetime.now().isoformat()
    }
    
    # Append to user's entries
    if "entries" not in user_timesheet:
        user_timesheet["entries"] = []
    
    user_timesheet["entries"].append(new_entry)
    
    # Write back to file (entire array)
    with open(timesheet_path, 'w') as f:
        json.dump(timesheet_data, f, indent=2)
    
    # Log the audit trail
    audit_entry = {
        "action": "add_timesheet_entry",
        "user": user_email,
        "entry": new_entry,
        "timestamp": datetime.now().isoformat(),
        "approved_by": approved_by
    }
    
    log_audit_entry(audit_entry)
    
    return json.dumps({
        "status": "success",
        "message": f"Added timesheet entry for {user_email} on {date}",
        "entry": new_entry
    }, indent=2)


def log_audit_entry(audit_data: Dict[str, Any]) -> None:
    """
    Log an audit entry for compliance and tracking.
    
    Args:
        audit_data: Dictionary containing audit information
    """
    audit_path = Path(__file__).parent.parent / "shared" / "audit_log.json"
    
    # Load existing audit log
    try:
        with open(audit_path, 'r') as f:
            audit_log = json.load(f)
    except FileNotFoundError:
        audit_log = {"entries": []}
    
    # Append new entry
    if "entries" not in audit_log:
        audit_log["entries"] = []
    
    audit_log["entries"].append(audit_data)
    
    # Write back to file
    with open(audit_path, 'w') as f:
        json.dump(audit_log, f, indent=2)


def get_audit_log(limit: int = 100) -> str:
    """
    Retrieve recent audit log entries.
    
    Args:
        limit: Maximum number of entries to return (default: 100)
        
    Returns:
        JSON string containing audit log entries
    """
    audit_path = Path(__file__).parent.parent / "shared" / "audit_log.json"
    
    try:
        with open(audit_path, 'r') as f:
            audit_log = json.load(f)
        
        # Return most recent entries (limited)
        entries = audit_log.get("entries", [])
        recent_entries = entries[-limit:] if len(entries) > limit else entries
        
        return json.dumps({
            "total_entries": len(entries),
            "returned_entries": len(recent_entries),
            "entries": recent_entries
        }, indent=2)
    
    except FileNotFoundError:
        return json.dumps({
            "total_entries": 0,
            "returned_entries": 0,
            "entries": []
        }, indent=2)


def reject_suggestion(
    user_email: str,
    date: str,
    task: str,
    reason: str,
    rejected_by: str = "system"
) -> str:
    """
    Log a rejected suggestion for audit purposes.
    
    Args:
        user_email: The email of the user
        date: Date of the suggested entry
        task: Task description that was rejected
        reason: Reason for rejection
        rejected_by: Who rejected this entry (default: "system")
        
    Returns:
        JSON confirmation of the rejection
    """
    rejection_entry = {
        "action": "reject_suggestion",
        "user": user_email,
        "date": date,
        "task": task,
        "reason": reason,
        "rejected_by": rejected_by,
        "timestamp": datetime.now().isoformat()
    }
    
    log_audit_entry(rejection_entry)
    
    return json.dumps({
        "status": "success",
        "message": f"Rejection logged for {user_email} on {date}",
        "rejection": rejection_entry
    }, indent=2)
