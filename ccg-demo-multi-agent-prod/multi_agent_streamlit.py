"""
Multi-Agent Timesheet Assistant - Production Web Interface
==========================================================
Streamlit web application with approval workflow and write capabilities.
"""

import os
import sys
import asyncio
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Add agents directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator_agent import create_orchestrator

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Timesheet Assistant (PRODUCTION)",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "suggestions_parsed" not in st.session_state:
    st.session_state.suggestions_parsed = []
if "user_email" not in st.session_state:
    st.session_state.user_email = "arturoqu@microsoft.com"


def initialize_orchestrator():
    """Initialize the multi-agent orchestrator."""
    
    # Determine which client to use
    use_azure = os.getenv("USE_AZURE_OPENAI", "true").lower() == "true"
    
    if use_azure:
        from agent_framework.azure import AzureOpenAIChatClient
        
        client = AzureOpenAIChatClient(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
    else:
        from agent_framework.openai import OpenAIChatClient
        
        client = OpenAIChatClient(
            model_id=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    return create_orchestrator(client)


def parse_suggestions(suggestion_text):
    """
    Parse suggestion agent output to extract individual suggestions.
    This is a simplified parser - in production you'd use structured output.
    """
    suggestions = []
    
    if not suggestion_text:
        return suggestions
    
    # Look for common patterns in the suggestion text
    lines = suggestion_text.split('\n')
    
    current_suggestion = {}
    for line in lines:
        line = line.strip()
        
        if not line or ':' not in line:
            continue
            
        parts = line.split(':', 1)
        if len(parts) < 2:
            continue
        
        if 'date' in parts[0].lower():
            if current_suggestion:
                suggestions.append(current_suggestion)
            current_suggestion = {'date': parts[1].strip()}
        elif 'start' in parts[0].lower() and 'time' in parts[0].lower():
            current_suggestion['start_time'] = parts[1].strip()
        elif 'end' in parts[0].lower() and 'time' in parts[0].lower():
            current_suggestion['end_time'] = parts[1].strip()
        elif 'duration' in parts[0].lower():
            current_suggestion['duration_hours'] = parts[1].strip()
        elif 'task' in parts[0].lower():
            current_suggestion['task'] = parts[1].strip()
        elif 'project' in parts[0].lower():
            current_suggestion['project'] = parts[1].strip()
        elif 'billable' in parts[0].lower():
            current_suggestion['billable'] = 'yes' in parts[1].lower() or 'true' in parts[1].lower()
    
    if current_suggestion:
        suggestions.append(current_suggestion)
    
    return suggestions


# Main header
st.title("🤖 Multi-Agent Timesheet Assistant")
st.markdown("**PRODUCTION VERSION** - Analyze, Approve, and Write Timesheet Entries")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analysis & Approval",
    "💰 Revenue Impact",
    "📋 Audit Log",
    "ℹ️ About"
])

# Tab 1: Analysis & Approval
with tab1:
    st.header("Missing Time Analysis & Approval Workflow")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_email = st.text_input(
            "User Email",
            value=st.session_state.user_email,
            help="Enter the email of the consultant to analyze"
        )
        st.session_state.user_email = user_email
    
    with col2:
        st.markdown("### Quick Actions")
        if st.button("🔍 Analyze Missing Time", type="primary", use_container_width=True):
            if not st.session_state.orchestrator:
                st.session_state.orchestrator = initialize_orchestrator()
            
            with st.status("🤖 Running multi-agent analysis...", expanded=True) as status:
                st.write("📅 Calendar Agent: Analyzing calendar events...")
                st.write("📝 Timesheet Agent: Analyzing existing entries...")
                
                # Run the analysis
                results = asyncio.run(
                    st.session_state.orchestrator.analyze_missing_time(
                        user_email=user_email,
                        parallel=True
                    )
                )
                
                st.write("💡 Suggestion Agent: Generating recommendations...")
                
                st.session_state.analysis_results = results
                
                # Parse suggestions for approval workflow
                if results.get("suggestions"):
                    st.session_state.suggestions_parsed = parse_suggestions(results["suggestions"])
                
                status.update(label="✅ Analysis complete!", state="complete")
    
    # Display results if available
    if st.session_state.analysis_results:
        st.divider()
        
        # Show analysis summary
        with st.expander("📊 Analysis Results", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 Calendar Analysis")
                st.markdown(st.session_state.analysis_results.get("calendar_analysis", "No data"))
            
            with col2:
                st.subheader("📝 Timesheet Analysis")
                st.markdown(st.session_state.analysis_results.get("timesheet_analysis", "No data"))
        
        # Show suggestions
        st.divider()
        st.subheader("💡 Suggested Entries (Pending Approval)")
        
        suggestions_text = st.session_state.analysis_results.get("suggestions", "")
        st.markdown(suggestions_text)
        
        # Approval workflow
        st.divider()
        st.subheader("✅ Approval Workflow")
        
        if st.session_state.suggestions_parsed:
            st.info(f"Found {len(st.session_state.suggestions_parsed)} suggestions ready for approval")
            
            for idx, suggestion in enumerate(st.session_state.suggestions_parsed):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Entry {idx + 1}:**")
                        st.markdown(f"📅 **Date:** {suggestion.get('date', 'N/A')}")
                        st.markdown(f"📝 **Task:** {suggestion.get('task', 'N/A')}")
                        st.markdown(f"🏢 **Project:** {suggestion.get('project', 'N/A')}")
                        st.markdown(f"⏱️ **Duration:** {suggestion.get('duration_hours', 'N/A')} hours")
                        st.markdown(f"💰 **Billable:** {'Yes' if suggestion.get('billable') else 'No'}")
                    
                    with col2:
                        if st.button("✅ Approve", key=f"approve_{idx}", type="primary", use_container_width=True):
                            if not st.session_state.orchestrator:
                                st.session_state.orchestrator = initialize_orchestrator()
                            
                            with st.spinner("Writing to timesheet..."):
                                approval_result = asyncio.run(
                                    st.session_state.orchestrator.process_approval(
                                        user_email=user_email,
                                        entry_data=suggestion,
                                        approved=True,
                                        approved_by="web_ui_user"
                                    )
                                )
                                st.success("✅ Entry added to timesheet!")
                                st.markdown(approval_result.get("result", ""))
                    
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{idx}", use_container_width=True):
                            rejection_reason = st.text_input(
                                "Reason (optional)",
                                key=f"reason_{idx}",
                                placeholder="Not billable, duplicate, etc."
                            )
                            
                            if st.button("Confirm Reject", key=f"confirm_reject_{idx}"):
                                if not st.session_state.orchestrator:
                                    st.session_state.orchestrator = initialize_orchestrator()
                                
                                with st.spinner("Logging rejection..."):
                                    rejection_result = asyncio.run(
                                        st.session_state.orchestrator.process_approval(
                                            user_email=user_email,
                                            entry_data=suggestion,
                                            approved=False,
                                            approved_by="web_ui_user",
                                            rejection_reason=rejection_reason
                                        )
                                    )
                                    st.info("Rejection logged")
                                    st.markdown(rejection_result.get("result", ""))
        else:
            st.warning("No suggestions available. Run analysis first or use manual entry form below.")
        
        # Manual entry form
        st.divider()
        with st.expander("➕ Manual Entry (Write Directly to Timesheet)"):
            st.markdown("Use this form to manually add a timesheet entry without going through suggestions.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                manual_date = st.date_input("Date")
                manual_start = st.time_input("Start Time")
                manual_end = st.time_input("End Time")
                manual_duration = st.number_input("Duration (hours)", min_value=0.0, step=0.5)
            
            with col2:
                manual_task = st.text_input("Task Description")
                manual_project = st.text_input("Project Name")
                manual_billable = st.checkbox("Billable", value=True)
            
            if st.button("💾 Add Manual Entry", type="secondary"):
                manual_entry = {
                    'date': str(manual_date),
                    'start_time': str(manual_start),
                    'end_time': str(manual_end),
                    'duration_hours': manual_duration,
                    'task': manual_task,
                    'project': manual_project,
                    'billable': manual_billable
                }
                
                if not st.session_state.orchestrator:
                    st.session_state.orchestrator = initialize_orchestrator()
                
                with st.spinner("Writing manual entry..."):
                    result = asyncio.run(
                        st.session_state.orchestrator.process_approval(
                            user_email=user_email,
                            entry_data=manual_entry,
                            approved=True,
                            approved_by="web_ui_manual"
                        )
                    )
                    st.success("✅ Manual entry added!")
                    st.markdown(result.get("result", ""))

# Tab 2: Revenue Impact
with tab2:
    st.header("💰 Revenue Impact Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        impact_email = st.text_input(
            "User Email",
            value=st.session_state.user_email,
            key="impact_email",
            help="Enter the email for revenue analysis"
        )
        missing_hours = st.number_input(
            "Missing Billable Hours",
            min_value=0.0,
            value=8.0,
            step=0.5,
            help="Number of missing billable hours per week"
        )
        billable_rate = st.number_input(
            "Billable Rate ($/hour)",
            min_value=0.0,
            value=250.0,
            step=10.0,
            help="Hourly billing rate"
        )
    
    with col2:
        st.markdown("### Calculate")
        if st.button("💰 Calculate Impact", type="primary", use_container_width=True):
            if not st.session_state.orchestrator:
                st.session_state.orchestrator = initialize_orchestrator()
            
            with st.status("💰 Calculating revenue impact...", expanded=True) as status:
                try:
                    results = asyncio.run(
                        st.session_state.orchestrator.calculate_impact(
                            user_email=impact_email,
                            missing_hours=missing_hours,
                            billable_rate=billable_rate
                        )
                    )
                    
                    st.markdown("### 📊 Financial Analysis")
                    if results.get("revenue_analysis"):
                        st.markdown(results["revenue_analysis"])
                    else:
                        st.warning("No revenue analysis data returned")
                    
                    status.update(label="✅ Calculation complete!", state="complete")
                except Exception as e:
                    st.error(f"Error calculating revenue impact: {str(e)}")
                    status.update(label="❌ Calculation failed", state="error")

# Tab 3: Audit Log
with tab3:
    st.header("📋 Audit Log")
    st.markdown("View all approved and rejected timesheet operations with full audit trail.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        audit_limit = st.number_input("Number of entries to display", min_value=10, max_value=500, value=50)
    
    with col2:
        if st.button("🔄 Refresh Audit Log", type="primary", use_container_width=True):
            if not st.session_state.orchestrator:
                st.session_state.orchestrator = initialize_orchestrator()
            
            with st.spinner("Loading audit log..."):
                try:
                    audit_results = asyncio.run(
                        st.session_state.orchestrator.get_audit_history(limit=audit_limit)
                    )
                    
                    st.markdown("### 📜 Recent Operations")
                    if audit_results.get("audit_log"):
                        st.markdown(audit_results["audit_log"])
                    else:
                        st.info("No audit entries found")
                except Exception as e:
                    st.error(f"Error loading audit log: {str(e)}")
    
    st.info("💡 All write operations (approvals and rejections) are logged with timestamps, user info, and complete entry details for compliance and troubleshooting.")

# Tab 4: About
with tab4:
    st.header("About Multi-Agent Timesheet Assistant (PRODUCTION)")
    
    st.markdown("""
    ### 🎯 Production Features
    
    This is the **PRODUCTION VERSION** with full approval workflow and write capabilities:
    
    **✨ Key Enhancements:**
    - ✅ **Approval Workflow**: Review and approve/reject suggestions before writing
    - 💾 **Write Capabilities**: Approved entries are written directly to timesheet
    - 📋 **Audit Logging**: Complete audit trail of all operations
    - ➕ **Manual Entry**: Direct write capability for manual timesheet entries
    - 🔒 **Compliance**: All actions tracked with timestamps and user attribution
    
    **🤖 Agent Architecture:**
    
    1. **Calendar Agent** 📅
       - Analyzes calendar events
       - Identifies travel time and client meetings
       - Classifies billable vs non-billable activities
    
    2. **Timesheet Agent** 📝
       - Reviews existing timesheet entries
       - Calculates total logged hours
       - Identifies gaps and missing entries
    
    3. **Suggestion Agent** 💡
       - Cross-references calendar and timesheet data
       - Proposes missing entries with clear rationale
       - Provides actionable recommendations
    
    4. **Approval Agent** ✅ **(NEW - Production Only)**
       - Processes approved suggestions
       - Writes entries to timesheet system
       - Logs rejections with reasons
       - Maintains complete audit trail
    
    5. **Revenue Agent** 💰
       - Calculates financial impact
       - Projects firm-wide revenue recovery
       - Demonstrates ROI
    
    **⚡ Performance:**
    - Parallel execution of Calendar + Timesheet agents
    - Real-time status updates
    - Efficient agent coordination
    
    **🔐 Security:**
    - All write operations logged
    - User attribution for approvals/rejections
    - Immutable audit trail
    - No deletion capability (add-only)
    
    **📚 Documentation:**
    - Architecture diagrams available in `/diagrams` folder
    - Deployment guide: `DEPLOYMENT.md`
    - Agent specialization details in code
    """)
    
    # Display architecture diagram if available
    diagram_path = Path(__file__).parent / "diagrams" / "architecture.md"
    if diagram_path.exists():
        st.divider()
        st.subheader("🏗️ System Architecture")
        with open(diagram_path) as f:
            diagram_content = f.read()
            st.code(diagram_content, language="mermaid")

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ System Status")
    
    # Try to initialize orchestrator on first load
    if not st.session_state.orchestrator:
        try:
            st.session_state.orchestrator = initialize_orchestrator()
            st.success("✅ Orchestrator initialized")
        except Exception as e:
            st.error(f"❌ Orchestrator initialization failed: {str(e)}")
    else:
        st.success("✅ Orchestrator initialized")
    
    st.divider()
    
    st.markdown("### 📖 Quick Reference")
    st.markdown("""
    **Workflow:**
    1. Enter user email
    2. Click "Analyze Missing Time"
    3. Review suggestions
    4. Approve or reject each entry
    5. Check audit log
    
    **Tips:**
    - Approvals write to timesheet
    - Rejections are logged
    - Manual entry available
    - All actions audited
    """)
    
    st.divider()
    
    st.markdown("### 🔗 Resources")
    st.markdown("""
    - [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
    - [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
    - [Streamlit Docs](https://docs.streamlit.io)
    """)
    
    st.divider()
    
    st.caption("Multi-Agent Timesheet Assistant v2.0 (PRODUCTION)")
    st.caption("Contoso Consulting Group © 2025")
