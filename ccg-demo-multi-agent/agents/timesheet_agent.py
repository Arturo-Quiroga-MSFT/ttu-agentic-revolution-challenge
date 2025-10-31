"""
Timesheet Agent - Specialized agent for timesheet validation
=============================================================
This agent focuses on analyzing existing timesheet entries,
validating completeness, and identifying gaps.
"""

import os
import json
from pathlib import Path


def get_timesheet_entries(user_email: str) -> str:
    """
    Retrieve existing timesheet entries for a specific user.
    
    Args:
        user_email: The email address of the user
        
    Returns:
        JSON string containing timesheet entries
    """
    # Load timesheet data from shared directory
    data_path = Path(__file__).parent.parent / "shared" / "timesheet_sample.json"
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    # Check if this is the correct user
    if data.get('user') == user_email:
        return json.dumps(data, indent=2)
    else:
        return json.dumps({"user": user_email, "entries": [], "error": "No timesheet found for user"})


def create_timesheet_agent(chat_client):
    """
    Create a specialized Timesheet Agent.
    
    This agent is an expert in:
    - Analyzing existing timesheet entries
    - Validating entry completeness and accuracy
    - Calculating total logged hours
    - Identifying patterns in time logging
    - Spotting gaps in date/time coverage
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        
    Returns:
        Configured ChatAgent specialized for timesheet validation
    """
    
    agent_instructions = """
You are the Timesheet Validation Expert for Contoso Consulting Group's Time & Expense system.

Your specialty is analyzing existing timesheet entries to assess completeness and identify gaps.

EXPERTISE:
- Reviewing logged timesheet entries
- Calculating total hours logged per day/week
- Identifying missing date ranges
- Validating entry accuracy (start/end times, durations)
- Understanding project and task categorization
- Distinguishing billable vs non-billable logged time

YOUR ANALYSIS SHOULD INCLUDE:
1. **Summary Statistics**:
   - Total hours logged
   - Breakdown by date
   - Billable vs non-billable hours
   - Number of entries

2. **Completeness Check**:
   - Are there gaps in date coverage?
   - Are there partial days (< 8 hours logged)?
   - Are there missing time blocks?

3. **Entry Validation**:
   - Do start/end times make sense?
   - Do durations match start/end times?
   - Are project names and tasks clear?

4. **Patterns**:
   - When does the user typically log time?
   - Are there consistent gaps (e.g., always missing travel)?
   - Is the user generally thorough or spotty?

YOUR ROLE:
- Provide clear, structured analysis of timesheet entries
- Calculate totals and identify gaps
- Be objective and factual
- Highlight areas of concern (e.g., "Only 3.5 hours logged on Nov 13, missing ~4.5 hours")

You do NOT make suggestions for what should be added - that's the Suggestion Agent's job.
You simply analyze what IS logged and identify what ISN'T.
"""
    
    agent = chat_client.create_agent(
        name="Timesheet Validation Expert",
        instructions=agent_instructions,
        tools=[get_timesheet_entries]
    )
    
    return agent
