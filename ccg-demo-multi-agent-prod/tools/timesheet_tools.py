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
        user_email: The email of the user
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM:SS format
        end_time: End time in HH:MM:SS format
        duration_hours: Number of hours
        task: Task description
        project: Project name
        billable: Whether this is billable
        approved_by: Who approved this entry (default: "system")
        
    Returns:
        JSON confirmation of the write operation
    """
    timesheet_path = Path(__file__).parent.parent / "shared" / "timesheet_sample.json"
    
    # Load existing timesheet
    try:
        with open(timesheet_path, 'r') as f:
            timesheet_data = json.load(f)
    except FileNotFoundError:
        timesheet_data = {"user": user_email, "entries": []}
    
    # Create new entry
    new_entry = {
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
    
    # Append to entries
    if "entries" not in timesheet_data:
        timesheet_data["entries"] = []
    
    timesheet_data["entries"].append(new_entry)
    
    # Write back to file
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
