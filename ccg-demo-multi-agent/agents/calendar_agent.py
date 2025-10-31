"""
Calendar Agent - Specialized agent for calendar event analysis
=============================================================
This agent focuses on extracting and interpreting calendar events,
identifying billable time blocks, and understanding event context.
"""

import os
import json
from pathlib import Path


def get_calendar_events(user_email: str) -> str:
    """
    Retrieve calendar events for a specific user.
    
    Args:
        user_email: The email address of the user
        
    Returns:
        JSON string containing calendar events
    """
    # Load calendar data from shared directory
    data_path = Path(__file__).parent.parent / "shared" / "calendar_sample.json"
    
    with open(data_path, 'r') as f:
        events = json.load(f)
    
    # Filter events for the requested user
    user_events = [event for event in events if user_email in event.get('attendees', [])]
    
    return json.dumps(user_events, indent=2)


def create_calendar_agent(chat_client):
    """
    Create a specialized Calendar Agent.
    
    This agent is an expert in:
    - Analyzing calendar events
    - Identifying travel time (flights, drives)
    - Recognizing client meetings and workshops
    - Distinguishing billable vs non-billable events
    - Understanding event categories and locations
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        
    Returns:
        Configured ChatAgent specialized for calendar analysis
    """
    
    agent_instructions = """
You are the Calendar Analysis Expert for Contoso Consulting Group's Time & Expense system.

Your specialty is analyzing calendar events to identify potentially billable time blocks.

EXPERTISE:
- Travel time identification (flights, drives to client sites)
- Client-facing events (workshops, meetings, Q&A sessions)
- Working meals and client dinners
- Preparation time for deliverables
- Distinguishing billable vs non-billable activities

BILLABILITY RULES:
✅ BILLABLE:
- All travel to/from client sites (flights, drives, trains)
- Client workshops, meetings, and presentations
- Working lunches/dinners with clients
- Client Q&A sessions and technical discussions
- Preparation time for client deliverables
- Remote/virtual client meetings

❌ NON-BILLABLE:
- Internal team meetings and syncs
- Internal Lunch & Learn sessions
- Office social events
- Networking without specific client
- Focus time without client context

YOUR ROLE:
When analyzing calendar events, provide:
1. List of all events with start/end times
2. Classification (Billable/Non-Billable) with rationale
3. Identification of travel time (often missed in timesheets)
4. Duration calculations
5. Event context and business purpose

Be thorough, accurate, and provide clear explanations for your classifications.
Focus especially on travel time - it's the most commonly forgotten billable category.
"""
    
    agent = chat_client.create_agent(
        name="Calendar Analysis Expert",
        instructions=agent_instructions,
        tools=[get_calendar_events]
    )
    
    return agent
