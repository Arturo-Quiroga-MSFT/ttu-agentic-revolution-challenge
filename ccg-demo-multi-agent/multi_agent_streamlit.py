"""
Multi-Agent Streamlit UI for Contoso Consulting Group
Interactive web interface for the multi-agent time & expense system.
"""

import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient
from agents.orchestrator_agent import create_orchestrator

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="CCG Multi-Agent Time & Expense",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #605E5C;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F2F1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0078D4;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .agent-calendar {
        background-color: #E1F5FE;
        color: #01579B;
    }
    .agent-timesheet {
        background-color: #F3E5F5;
        color: #4A148C;
    }
    .agent-suggestion {
        background-color: #E8F5E9;
        color: #1B5E20;
    }
    .agent-revenue {
        background-color: #FFF3E0;
        color: #E65100;
    }
    .stExpander {
        border: 1px solid #E1DFDD;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_chat_client():
    """Initialize the Azure OpenAI or OpenAI chat client."""
    if 'chat_client' not in st.session_state:
        azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4")
        
        if azure_deployment and azure_endpoint:
            if azure_api_key:
                st.session_state.chat_client = AzureOpenAIChatClient(
                    deployment_name=azure_deployment,
                    endpoint=azure_endpoint,
                    api_key=azure_api_key
                )
            else:
                st.session_state.chat_client = AzureOpenAIChatClient(
                    deployment_name=azure_deployment,
                    endpoint=azure_endpoint,
                    credential=AzureCliCredential()
                )
            st.session_state.ai_service = "Azure OpenAI"
        elif openai_api_key:
            st.session_state.chat_client = OpenAIChatClient(
                model_id=openai_model,
                api_key=openai_api_key
            )
            st.session_state.ai_service = "OpenAI"
        else:
            st.error("❌ No AI service configured. Set AZURE_OPENAI_* or OPENAI_API_KEY environment variables.")
            st.stop()


def initialize_orchestrator():
    """Initialize the multi-agent orchestrator."""
    if 'orchestrator' not in st.session_state:
        initialize_chat_client()
        st.session_state.orchestrator = create_orchestrator(st.session_state.chat_client)


async def run_missing_time_analysis(user_email: str, parallel: bool = True):
    """Run the missing time analysis workflow."""
    initialize_orchestrator()
    
    with st.spinner("🔄 Analyzing calendar and timesheet data..."):
        results = await st.session_state.orchestrator.analyze_missing_time(
            user_email=user_email,
            parallel=parallel
        )
    
    return results


async def run_revenue_impact_analysis(user_email: str, missing_hours: float, billable_rate: float):
    """Run the revenue impact calculation."""
    initialize_orchestrator()
    
    with st.spinner("💰 Calculating revenue impact..."):
        results = await st.session_state.orchestrator.calculate_impact(
            user_email=user_email,
            missing_hours=missing_hours,
            billable_rate=billable_rate
        )
    
    return results


def display_agent_badges(execution_log):
    """Display badges for agents that were involved."""
    agent_map = {
        "Calendar": "agent-calendar",
        "Timesheet": "agent-timesheet",
        "Suggestion": "agent-suggestion",
        "Revenue": "agent-revenue"
    }
    
    active_agents = []
    for log in execution_log:
        for agent_name, badge_class in agent_map.items():
            if agent_name.lower() in log.lower():
                active_agents.append((agent_name, badge_class))
    
    if active_agents:
        st.markdown("**Agents Involved:**")
        badges_html = ""
        for agent_name, badge_class in set(active_agents):
            badges_html += f'<span class="agent-badge {badge_class}">{agent_name} Agent</span>'
        st.markdown(badges_html, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">🤖 CCG Multi-Agent Time & Expense System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent time tracking powered by specialized AI agents</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏢 Contoso Consulting Group")
        st.markdown("**Time & Expense System**")
        st.markdown("---")
        
        st.markdown("### 👤 User Settings")
        user_email = st.text_input(
            "Email Address",
            value="arturoqu@microsoft.com",
            help="Enter the consultant's email address"
        )
        
        st.markdown("### ⚙️ Configuration")
        enable_parallel = st.checkbox(
            "Enable Parallel Execution",
            value=True,
            help="Run Calendar and Timesheet agents in parallel for faster results"
        )
        
        billable_rate = st.number_input(
            "Billable Rate ($/hr)",
            min_value=0.0,
            value=250.0,
            step=25.0,
            help="Hourly billable rate for revenue calculations"
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Sample Queries")
        st.markdown("*Click to view example analysis*")
        
        if st.button("💬 What meetings do I have on November 15th?", key="sample_1", width="stretch"):
            st.info("This query would analyze calendar events for November 15th. Use the 'Run Analysis' button above for full analysis.")
        
        if st.button("💬 How many hours did I log in November?", key="sample_2", width="stretch"):
            st.info("This query would summarize timesheet entries. Use the 'Run Analysis' button above for full analysis.")
        
        if st.button("💬 Are there any days with meetings but no time entries?", key="sample_3", width="stretch"):
            st.info("This query finds gaps between calendar and timesheet. Use the 'Run Analysis' button above for full analysis.")
        
        if st.button("💬 What's my total billable revenue for November?", key="sample_4", width="stretch"):
            st.info("This query calculates revenue. Use the 'Revenue Impact' tab for detailed calculations.")
        
        if st.button("💬 Show me missing travel time entries", key="sample_5", width="stretch"):
            st.info("This query identifies unbilled travel. Use the 'Run Analysis' button above for full analysis.")
        
        st.markdown("---")
        if 'ai_service' in st.session_state:
            st.success(f"✅ Connected: {st.session_state.ai_service}")
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📊 Missing Time Analysis", "💰 Revenue Impact", "ℹ️ About"])
    
    with tab1:
        st.markdown("### 🔍 Identify Missing Time Entries")
        st.markdown("Analyze calendar events and timesheet data to find billable hours that haven't been logged.")
        
        # Quick action buttons for sample scenarios
        st.markdown("#### 🎯 Quick Actions")
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            if st.button("📅 Analyze All November Data", key="quick_november", width="stretch"):
                st.session_state.run_analysis = True
                st.session_state.quick_action = "november"
        with col_q2:
            if st.button("✈️ Find Missing Travel Time", key="quick_travel", width="stretch"):
                st.session_state.run_analysis = True
                st.session_state.quick_action = "travel"
        with col_q3:
            if st.button("🔍 Find All Gaps", key="quick_gaps", width="stretch"):
                st.session_state.run_analysis = True
                st.session_state.quick_action = "gaps"
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Analysis Scope:**")
            st.info(f"📧 User: **{user_email}**\n\n⚡ Parallel Execution: **{'Enabled' if enable_parallel else 'Disabled'}**")
        with col2:
            if st.button("🚀 Run Full Analysis", type="primary", width="stretch"):
                st.session_state.run_analysis = True
        
        if st.session_state.get('run_analysis', False):
            try:
                results = asyncio.run(run_missing_time_analysis(user_email, enable_parallel))
                
                # Display results in expandable sections
                with st.expander("📅 Calendar Analysis", expanded=True):
                    st.markdown(results.get("calendar_analysis", "No results"))
                
                with st.expander("📝 Timesheet Analysis", expanded=True):
                    st.markdown(results.get("timesheet_analysis", "No results"))
                
                with st.expander("💡 Suggestions for Missing Entries", expanded=True):
                    st.markdown(results.get("suggestions", "No suggestions"))
                
                with st.expander("🔧 Execution Summary"):
                    execution_log = results.get("execution_log", [])
                    display_agent_badges(execution_log)
                    st.markdown("**Execution Timeline:**")
                    for i, log in enumerate(execution_log, 1):
                        st.text(f"[{i}] {log}")
                
                # Store results for revenue analysis
                st.session_state.analysis_results = results
                st.session_state.run_analysis = False
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🐛 Error Details"):
                    st.code(traceback.format_exc())
    
    with tab2:
        st.markdown("### 💵 Calculate Revenue Impact")
        st.markdown("Estimate the financial impact of missing billable hours across consultants and the firm.")
        
        col1, col2 = st.columns(2)
        with col1:
            missing_hours = st.number_input(
                "Missing Billable Hours (per week)",
                min_value=0.0,
                value=20.0,
                step=1.0,
                help="Estimated missing billable hours per consultant per week"
            )
        with col2:
            num_consultants = st.number_input(
                "Number of Consultants",
                min_value=1,
                value=50,
                step=1,
                help="Total number of consultants in the firm"
            )
        
        if st.button("📈 Calculate Impact", type="primary", width="stretch"):
            st.session_state.run_revenue = True
        
        if st.session_state.get('run_revenue', False):
            try:
                results = asyncio.run(run_revenue_impact_analysis(user_email, missing_hours, billable_rate))
                
                # Display revenue analysis
                st.markdown("#### 💰 Revenue Impact Analysis")
                st.markdown(results.get("revenue_analysis", "No analysis"))
                
                # Display metrics
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                weekly_revenue = missing_hours * billable_rate
                annual_revenue = weekly_revenue * 52
                firm_wide_revenue = annual_revenue * num_consultants
                
                with col1:
                    st.metric(
                        "Weekly Loss (per consultant)",
                        f"${weekly_revenue:,.0f}",
                        delta=f"-{missing_hours} hrs",
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Annual Loss (per consultant)",
                        f"${annual_revenue:,.0f}",
                        delta=f"-{missing_hours * 52} hrs/year",
                        delta_color="inverse"
                    )
                
                with col3:
                    st.metric(
                        "Firm-Wide Annual Impact",
                        f"${firm_wide_revenue:,.0f}",
                        delta=f"{num_consultants} consultants",
                        delta_color="inverse"
                    )
                
                # Execution summary
                with st.expander("🔧 Execution Summary"):
                    execution_log = results.get("execution_log", [])
                    display_agent_badges(execution_log)
                    st.markdown("**Execution Timeline:**")
                    for i, log in enumerate(execution_log, 1):
                        st.text(f"[{i}] {log}")
                
                st.session_state.run_revenue = False
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🐛 Error Details"):
                    st.code(traceback.format_exc())
    
    with tab3:
        st.markdown("### 📖 About This System")
        
        st.markdown("""
        **Contoso Consulting Group Multi-Agent Time & Expense System** is an intelligent solution
        that helps consultants capture all billable hours by analyzing calendar events and timesheet entries.
        
        #### 🤖 Multi-Agent Architecture
        
        This system uses **four specialized AI agents** coordinated by an orchestrator:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📅 Calendar Agent</h4>
                <p>Analyzes calendar events, identifies billable activities, and classifies meetings.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h4>💡 Suggestion Agent</h4>
                <p>Cross-references calendar and timesheet data to propose missing entries with rationale.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>📝 Timesheet Agent</h4>
                <p>Reviews timesheet entries, validates completeness, and identifies gaps.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h4>💰 Revenue Agent</h4>
                <p>Calculates financial impact of missing billable hours across the organization.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        #### ⚡ Key Benefits
        
        - **Parallel Execution**: Calendar and Timesheet agents run simultaneously for faster results
        - **Domain Expertise**: Each agent specializes in its area with focused context
        - **Scalability**: Independent agents can be maintained and optimized separately
        - **Transparency**: Clear execution logs show which agents were involved
        - **Business Impact**: Quantifies revenue recovery opportunity
        
        #### 🏗️ Technical Stack
        
        - **Microsoft Agent Framework**: ChatAgent with function calling
        - **Azure OpenAI**: GPT-4o or GPT-4 for intelligent analysis
        - **Streamlit**: Interactive web interface
        - **Python 3.13+**: Modern async/await patterns
        """)
        
        st.markdown("---")
        st.info("💡 **Tip**: Use the sidebar sample queries to quickly test different scenarios.")


if __name__ == "__main__":
    main()
