"""
Agents Package - Multi-Agent Architecture for CCG Time & Expense
================================================================
"""

from .calendar_agent import create_calendar_agent, get_calendar_events
from .timesheet_agent import create_timesheet_agent, get_timesheet_entries
from .suggestion_agent import create_suggestion_agent, suggest_timesheet_entry
from .revenue_agent import create_revenue_agent, calculate_revenue_impact
from .orchestrator_agent import create_orchestrator, AgentOrchestrator

__all__ = [
    'create_calendar_agent',
    'create_timesheet_agent',
    'create_suggestion_agent',
    'create_revenue_agent',
    'create_orchestrator',
    'AgentOrchestrator',
    'get_calendar_events',
    'get_timesheet_entries',
    'suggest_timesheet_entry',
    'calculate_revenue_impact',
]
