"""
Orchestrator Agent - Coordinates workflow between specialized agents (PRODUCTION)
=================================================================================
This enhanced version includes approval workflow and write capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents to complete complex tasks.
    
    Production version with approval workflow:
    - Phase 1: Analysis (Calendar + Timesheet agents in parallel)
    - Phase 2: Suggestions (Suggestion agent synthesizes findings)
    - Phase 3: Approval (User approves/rejects suggestions)
    - Phase 4: Write (Approval agent writes to timesheet)
    - Optional: Revenue Impact (Revenue agent calculates business value)
    """
    
    def __init__(
        self,
        calendar_agent=None,
        timesheet_agent=None,
        suggestion_agent=None,
        revenue_agent=None,
        approval_agent=None
    ):
        """
        Initialize the orchestrator with specialized agents.
        
        Args:
            calendar_agent: Calendar analysis expert
            timesheet_agent: Timesheet validation expert
            suggestion_agent: Recommendation expert
            revenue_agent: Revenue impact expert
            approval_agent: Approval processing expert (NEW)
        """
        self.calendar_agent = calendar_agent
        self.timesheet_agent = timesheet_agent
        self.suggestion_agent = suggestion_agent
        self.revenue_agent = revenue_agent
        self.approval_agent = approval_agent
        
        # Track agent execution for debugging/visualization
        self.execution_log = []
        
        # Store suggestions for approval workflow
        self.pending_suggestions = []
    
    async def analyze_missing_time(
        self,
        user_email: str,
        thread_calendar=None,
        thread_timesheet=None,
        thread_suggestion=None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Complete analysis workflow to find missing time entries.
        
        Steps:
        1. Calendar Agent analyzes calendar events
        2. Timesheet Agent analyzes existing entries
        3. Suggestion Agent cross-references and proposes entries
        
        Args:
            user_email: User's email address
            thread_calendar: Thread for calendar agent (optional)
            thread_timesheet: Thread for timesheet agent (optional)
            thread_suggestion: Thread for suggestion agent (optional)
            parallel: Whether to run calendar/timesheet agents in parallel
            
        Returns:
            Dict with results from all agents
        """
        results = {
            "user_email": user_email,
            "calendar_analysis": None,
            "timesheet_analysis": None,
            "suggestions": None,
            "execution_log": []
        }
        
        # Step 1 & 2: Analyze calendar and timesheet (parallel if enabled)
        if parallel and self.calendar_agent and self.timesheet_agent:
            self.execution_log.append("Starting parallel execution: Calendar + Timesheet agents")
            
            calendar_task = self.calendar_agent.run(
                f"Analyze calendar events for {user_email}. List all events with billability classification.",
                thread=thread_calendar
            )
            timesheet_task = self.timesheet_agent.run(
                f"Analyze timesheet entries for {user_email}. Calculate total hours and identify gaps.",
                thread=thread_timesheet
            )
            
            calendar_result, timesheet_result = await asyncio.gather(calendar_task, timesheet_task)
            
            results["calendar_analysis"] = calendar_result.text
            results["timesheet_analysis"] = timesheet_result.text
            
            self.execution_log.append("Completed: Calendar + Timesheet agents (parallel)")
        else:
            # Sequential execution
            if self.calendar_agent:
                self.execution_log.append("Starting: Calendar agent")
                calendar_result = await self.calendar_agent.run(
                    f"Analyze calendar events for {user_email}. List all events with billability classification.",
                    thread=thread_calendar
                )
                results["calendar_analysis"] = calendar_result.text
                self.execution_log.append("Completed: Calendar agent")
            
            if self.timesheet_agent:
                self.execution_log.append("Starting: Timesheet agent")
                timesheet_result = await self.timesheet_agent.run(
                    f"Analyze timesheet entries for {user_email}. Calculate total hours and identify gaps.",
                    thread=thread_timesheet
                )
                results["timesheet_analysis"] = timesheet_result.text
                self.execution_log.append("Completed: Timesheet agent")
        
        # Step 3: Generate suggestions based on calendar + timesheet analysis
        if self.suggestion_agent and results["calendar_analysis"] and results["timesheet_analysis"]:
            self.execution_log.append("Starting: Suggestion agent")
            
            suggestion_prompt = f"""
Based on the following analyses, identify missing timesheet entries and suggest them:

CALENDAR ANALYSIS:
{results['calendar_analysis']}

TIMESHEET ANALYSIS:
{results['timesheet_analysis']}

For each missing entry, call suggest_timesheet_entry with complete details and rationale.
Focus on billable time, especially travel and client meetings.
"""
            
            suggestion_result = await self.suggestion_agent.run(
                suggestion_prompt,
                thread=thread_suggestion
            )
            results["suggestions"] = suggestion_result.text
            self.execution_log.append("Completed: Suggestion agent")
        
        results["execution_log"] = self.execution_log.copy()
        return results
    
    async def process_approval(
        self,
        user_email: str,
        entry_data: Dict[str, Any],
        approved: bool,
        approved_by: str = "system",
        rejection_reason: Optional[str] = None,
        thread=None
    ) -> Dict[str, Any]:
        """
        Process an approval or rejection of a suggested entry.
        
        Args:
            user_email: User's email address
            entry_data: Dictionary with entry details (date, time, task, etc.)
            approved: True if approved, False if rejected
            approved_by: Who approved/rejected (default: "system")
            rejection_reason: Required if approved=False
            thread: Thread for approval agent (optional)
            
        Returns:
            Dict with approval result
        """
        results = {
            "user_email": user_email,
            "action": "approve" if approved else "reject",
            "result": None,
            "execution_log": []
        }
        
        if not self.approval_agent:
            results["result"] = "Error: Approval agent not initialized"
            return results
        
        self.execution_log.append(f"Starting: Approval agent ({'approve' if approved else 'reject'})")
        
        if approved:
            # Approve and write to timesheet
            approval_prompt = f"""
Approve and write this timesheet entry:

User: {user_email}
Date: {entry_data.get('date')}
Start Time: {entry_data.get('start_time')}
End Time: {entry_data.get('end_time')}
Duration: {entry_data.get('duration_hours')} hours
Task: {entry_data.get('task')}
Project: {entry_data.get('project')}
Billable: {entry_data.get('billable')}
Approved By: {approved_by}

Use add_timesheet_entry() to write this to the timesheet system.
"""
        else:
            # Reject and log
            approval_prompt = f"""
Reject this timesheet suggestion and log the rejection:

User: {user_email}
Date: {entry_data.get('date')}
Task: {entry_data.get('task')}
Reason: {rejection_reason or 'Not specified'}
Rejected By: {approved_by}

Use reject_suggestion() to log this rejection.
"""
        
        approval_result = await self.approval_agent.run(
            approval_prompt,
            thread=thread
        )
        
        results["result"] = approval_result.text
        self.execution_log.append(f"Completed: Approval agent ({'approve' if approved else 'reject'})")
        results["execution_log"] = self.execution_log.copy()
        
        return results
    
    async def calculate_impact(
        self,
        user_email: str,
        missing_hours: float,
        billable_rate: float = 250.0,
        thread=None
    ) -> Dict[str, Any]:
        """
        Calculate revenue impact of missing billable hours.
        
        Args:
            user_email: User's email address
            missing_hours: Number of missing billable hours
            billable_rate: Hourly rate (default: $250)
            thread: Thread for revenue agent (optional)
            
        Returns:
            Dict with revenue impact analysis
        """
        results = {
            "user_email": user_email,
            "revenue_analysis": None,
            "execution_log": []
        }
        
        if self.revenue_agent:
            self.execution_log.append("Starting: Revenue agent")
            
            revenue_result = await self.revenue_agent.run(
                f"Calculate revenue impact for {user_email} with {missing_hours} missing hours at ${billable_rate}/hour. "
                f"Provide complete financial analysis including weekly, annual, and firm-wide projections.",
                thread=thread
            )
            results["revenue_analysis"] = revenue_result.text
            self.execution_log.append("Completed: Revenue agent")
        
        results["execution_log"] = self.execution_log.copy()
        return results
    
    async def get_audit_history(
        self,
        limit: int = 50,
        thread=None
    ) -> Dict[str, Any]:
        """
        Retrieve audit log history.
        
        Args:
            limit: Maximum number of entries to retrieve
            thread: Thread for approval agent (optional)
            
        Returns:
            Dict with audit log entries
        """
        results = {
            "audit_log": None,
            "execution_log": []
        }
        
        if self.approval_agent:
            self.execution_log.append("Starting: Approval agent (audit log)")
            
            audit_result = await self.approval_agent.run(
                f"Retrieve the audit log with up to {limit} recent entries using get_audit_log().",
                thread=thread
            )
            results["audit_log"] = audit_result.text
            self.execution_log.append("Completed: Approval agent (audit log)")
        
        results["execution_log"] = self.execution_log.copy()
        return results
    
    def get_execution_summary(self) -> str:
        """
        Get a summary of agent execution for debugging/visualization.
        
        Returns:
            Formatted execution log
        """
        return "\n".join([f"[{i+1}] {log}" for i, log in enumerate(self.execution_log)])


def create_orchestrator(chat_client, enable_parallel: bool = True):
    """
    Create an orchestrator with all specialized agents (PRODUCTION).
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        enable_parallel: Whether to enable parallel agent execution
        
    Returns:
        Configured AgentOrchestrator with approval workflow
    """
    from .calendar_agent import create_calendar_agent
    from .timesheet_agent import create_timesheet_agent
    from .suggestion_agent import create_suggestion_agent
    from .revenue_agent import create_revenue_agent
    from .approval_agent import create_approval_agent
    
    calendar_agent = create_calendar_agent(chat_client)
    timesheet_agent = create_timesheet_agent(chat_client)
    suggestion_agent = create_suggestion_agent(chat_client)
    revenue_agent = create_revenue_agent(chat_client)
    approval_agent = create_approval_agent(chat_client)
    
    orchestrator = AgentOrchestrator(
        calendar_agent=calendar_agent,
        timesheet_agent=timesheet_agent,
        suggestion_agent=suggestion_agent,
        revenue_agent=revenue_agent,
        approval_agent=approval_agent
    )
    
    return orchestrator
