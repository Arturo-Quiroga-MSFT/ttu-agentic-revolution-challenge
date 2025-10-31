"""
Orchestrator Agent - Coordinates workflow between specialized agents
====================================================================
This agent manages the overall workflow, routes requests to appropriate
agents, and synthesizes results into unified responses.
"""

import asyncio
from typing import Dict, List, Any


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents to complete complex tasks.
    
    The orchestrator:
    - Receives user queries
    - Determines which agents to invoke
    - Coordinates agent execution (sequential or parallel)
    - Aggregates results
    - Provides unified response to user
    """
    
    def __init__(
        self,
        calendar_agent=None,
        timesheet_agent=None,
        suggestion_agent=None,
        revenue_agent=None
    ):
        """
        Initialize the orchestrator with specialized agents.
        
        Args:
            calendar_agent: Calendar analysis expert
            timesheet_agent: Timesheet validation expert
            suggestion_agent: Recommendation expert
            revenue_agent: Revenue impact expert
        """
        self.calendar_agent = calendar_agent
        self.timesheet_agent = timesheet_agent
        self.suggestion_agent = suggestion_agent
        self.revenue_agent = revenue_agent
        
        # Track agent execution for debugging/visualization
        self.execution_log = []
    
    async def analyze_missing_time(
        self,
        user_email: str,
        thread_calendar=None,
        thread_timesheet=None,
        thread_suggestion=None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Complete workflow to find missing time entries.
        
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
    
    def get_execution_summary(self) -> str:
        """
        Get a summary of agent execution for debugging/visualization.
        
        Returns:
            Formatted execution log
        """
        return "\n".join([f"[{i+1}] {log}" for i, log in enumerate(self.execution_log)])


def create_orchestrator(chat_client, enable_parallel: bool = True):
    """
    Create an orchestrator with all specialized agents.
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        enable_parallel: Whether to enable parallel agent execution
        
    Returns:
        Configured AgentOrchestrator
    """
    from .calendar_agent import create_calendar_agent
    from .timesheet_agent import create_timesheet_agent
    from .suggestion_agent import create_suggestion_agent
    from .revenue_agent import create_revenue_agent
    
    calendar_agent = create_calendar_agent(chat_client)
    timesheet_agent = create_timesheet_agent(chat_client)
    suggestion_agent = create_suggestion_agent(chat_client)
    revenue_agent = create_revenue_agent(chat_client)
    
    orchestrator = AgentOrchestrator(
        calendar_agent=calendar_agent,
        timesheet_agent=timesheet_agent,
        suggestion_agent=suggestion_agent,
        revenue_agent=revenue_agent
    )
    
    return orchestrator
