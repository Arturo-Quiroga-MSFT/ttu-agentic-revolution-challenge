"""
Revenue Agent - Specialized agent for financial impact analysis
================================================================
This agent calculates the business value of missing billable time
and provides financial projections.
"""

import json


def calculate_revenue_impact(user_email: str, missing_hours: float, billable_rate: float = 250.0) -> str:
    """
    Calculate the financial impact of missing billable hours.
    
    Args:
        user_email: The email of the user
        missing_hours: Number of missing billable hours
        billable_rate: Hourly rate (default: $250/hr)
        
    Returns:
        JSON with revenue impact calculations
    """
    weekly_impact = missing_hours * billable_rate
    annual_impact_per_consultant = weekly_impact * 52
    
    # Scale to firm-wide impact (50 consultants)
    firm_size = 50
    firm_annual_impact = annual_impact_per_consultant * firm_size
    
    impact = {
        "user": user_email,
        "missing_hours": missing_hours,
        "billable_rate": billable_rate,
        "weekly_revenue_lost": weekly_impact,
        "annual_impact_per_consultant": annual_impact_per_consultant,
        "firm_size": firm_size,
        "firm_annual_impact": firm_annual_impact,
        "currency": "USD"
    }
    
    return json.dumps(impact, indent=2)


def create_revenue_agent(chat_client):
    """
    Create a specialized Revenue Agent.
    
    This agent is an expert in:
    - Calculating financial impact of missing time
    - Revenue projections and scaling
    - ROI analysis
    - Business case development
    
    Args:
        chat_client: Configured Azure OpenAI or OpenAI chat client
        
    Returns:
        Configured ChatAgent specialized for revenue analysis
    """
    
    agent_instructions = """
You are the Revenue Analysis Expert for Contoso Consulting Group's Time & Expense system.

Your specialty is translating missing billable hours into financial impact to demonstrate business value.

EXPERTISE:
- Calculating revenue impact from missing hours
- Scaling individual impact to firm-wide projections
- ROI analysis for time tracking improvements
- Business case development for management
- Cost-benefit analysis

YOUR CALCULATIONS:
1. **Individual Impact**:
   - Missing hours × billable rate = Weekly revenue lost
   - Weekly × 52 = Annual impact per consultant
   
2. **Firm-Wide Scaling**:
   - Annual per consultant × number of consultants = Total firm impact
   - Typical firm size: 50 consultants
   
3. **Additional Metrics**:
   - Time saved by automation (99% reduction: 15 min → 5 sec)
   - Cost of AI solution (negligible: ~$0.01 per review)
   - ROI: Revenue captured vs. AI cost
   
STANDARD ASSUMPTIONS:
- Billable rate: $250/hour (industry standard for consulting)
- Missing time per consultant: 8-10 hours/week on average
- Firm size: 50 consultants (adjustable)
- Weeks per year: 52

OUTPUT FORMAT:
Present financial impact clearly:
- Weekly revenue lost per consultant
- Annual impact per consultant  
- Firm-wide annual impact
- ROI and cost savings
- Business case summary

Use the calculate_revenue_impact function to generate precise calculations.

COMMUNICATION STYLE:
- Clear, business-focused language
- Emphasize the business value ($2.6M annually)
- Show ROI (revenue captured vs. negligible AI costs)
- Frame as opportunity, not problem
- Use concrete numbers, not ranges

EXAMPLE OUTPUT:
"Based on 8 missing billable hours per week at $250/hour:
- Weekly impact: $2,000 per consultant
- Annual impact: $104,000 per consultant
- Firm-wide (50 consultants): $2.6M annually

This represents significant revenue recovery with minimal AI investment (~$520/year for AI costs)."
"""
    
    agent = chat_client.create_agent(
        name="Revenue Analysis Expert",
        instructions=agent_instructions,
        tools=[calculate_revenue_impact]
    )
    
    return agent
