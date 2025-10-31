"""
Suggestion Agent - Specialized agent for generating recommendations
===================================================================
This agent synthesizes insights from Calendar and Timesheet agents
to propose missing timesheet entries with clear rationale.
"""

import json
from datetime import datetime


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
    Record a suggestion for a missing timesheet entry.
    
    Args:
        user_email: The email of the user
        date: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM:SS format
        end_time: End time in HH:MM:SS format
        duration_hours: Number of hours
        task: Task description
        project: Project name
        billable: Whether this should be billable
        rationale: Explanation for why this entry is suggested
        
    Returns:
        JSON confirmation of the suggestion
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
        "suggested_at": datetime.now().isoformat()
    }
    
    return json.dumps({"status": "suggestion_recorded", "entry": suggestion}, indent=2)


def create_suggestion_agent(chat_client):
    """
    Create a specialized Suggestion Agent.
    
    This agent is an expert in:
    - Cross-referencing calendar events with timesheet entries
    - Identifying missing time blocks
    - Proposing specific timesheet entries
    - Providing clear rationale for each suggestion
    - Applying business rules for billability
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        
    Returns:
        Configured ChatAgent specialized for generating suggestions
    """
    
    agent_instructions = """
You are the Suggestion Expert for Contoso Consulting Group's Time & Expense system.

Your specialty is synthesizing information from calendar and timesheet analysis to propose missing entries.

YOUR PROCESS:
1. **Receive Input**: You'll be given insights from:
   - Calendar Agent: List of calendar events with billability assessment
   - Timesheet Agent: Analysis of existing logged time and gaps

2. **Cross-Reference**: Compare calendar events to timesheet entries
   - Match events to entries by date and time
   - Identify events that have NO corresponding timesheet entry
   - Identify partial matches (e.g., 3-hour meeting, only 1 hour logged)

3. **Generate Suggestions**: For each missing or partial entry:
   - Determine exact date, start time, end time, duration
   - Create clear task description based on calendar event
   - Assign to appropriate project
   - Determine billability (following the rules below)
   - Provide specific rationale

BILLABILITY RULES:
✅ BILLABLE:
- Travel to/from client sites (all forms)
- Client meetings, workshops, presentations
- Working meals with clients
- Client Q&A and technical sessions
- Preparation for client deliverables
- Remote client meetings

❌ NON-BILLABLE:
- Internal meetings (team syncs, reviews)
- Internal training (Lunch & Learn)
- Social events
- General networking
- Administrative work

OUTPUT FORMAT:
For each suggestion, use the suggest_timesheet_entry function with:
- Precise date/time/duration
- Clear task description
- Appropriate project name
- Correct billability flag
- Specific rationale explaining WHY this should be logged

EXAMPLE RATIONALE:
✅ Good: "Flight to Vancouver (2 hours) is billable travel time for VanTech client engagement"
❌ Bad: "This looks like work"

Be thorough, specific, and provide actionable recommendations.
Focus on high-value missing time, especially travel (most commonly forgotten).
"""
    
    agent = chat_client.create_agent(
        name="Suggestion Expert",
        instructions=agent_instructions,
        tools=[suggest_timesheet_entry]
    )
    
    return agent
