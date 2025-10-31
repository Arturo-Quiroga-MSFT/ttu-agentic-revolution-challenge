"""
CCG Time & Expense Agent - Streamlit Web UI
============================================
Interactive web interface for the Microsoft Agent Framework demo.

Run with: streamlit run streamlit_app.py
"""

import asyncio
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient

# Import function tools
from calendar_plugin import get_calendar_events
from timesheet_plugin import get_timesheet_entries, suggest_timesheet_entry, calculate_revenue_impact

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="CCG Time & Expense Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0078D4;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .agent-message {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'thread' not in st.session_state:
        st.session_state.thread = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False
    if 'demo_running' not in st.session_state:
        st.session_state.demo_running = False


def create_agent():
    """Create a ChatAgent with function tools."""
    azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4")
    
    agent_instructions = """
You are an intelligent assistant for Contoso Consulting Group's Time & Expense system.

Your role is to help consultants identify missing time entries by analyzing their calendar events and existing timesheet entries.

When a user asks you to review their time, you should:
1. Retrieve their calendar events using the get_calendar_events function.
2. Retrieve their existing timesheet entries using the get_timesheet_entries function.
3. Identify any time blocks in the calendar that are not reflected in the timesheet.
4. For each missing entry, determine:
   - The date, start time, end time, and duration
   - An appropriate task description based on the calendar event
   - The likely project name
   - Whether it should be billable (travel and client work are billable; internal meetings are not)
5. Provide a clear rationale for each suggestion.

Focus especially on:
- Travel time (flights, drives to client sites)
- Client meetings or workshops
- Any calendar event that represents work but is not in the timesheet

Present your findings in a clear, structured format. Be helpful and conversational.
"""
    
    if azure_deployment and azure_endpoint:
        if azure_api_key:
            chat_client = AzureOpenAIChatClient(
                deployment_name=azure_deployment,
                endpoint=azure_endpoint,
                api_key=azure_api_key
            )
        else:
            chat_client = AzureOpenAIChatClient(
                deployment_name=azure_deployment,
                endpoint=azure_endpoint,
                credential=AzureCliCredential()
            )
    elif openai_api_key:
        chat_client = OpenAIChatClient(
            model_id=openai_model,
            api_key=openai_api_key
        )
    else:
        raise ValueError("No AI service configured. Set environment variables.")
    
    agent = chat_client.create_agent(
        name="CCG Time Assistant",
        instructions=agent_instructions,
        tools=[
            get_calendar_events,
            get_timesheet_entries,
            suggest_timesheet_entry,
            calculate_revenue_impact
        ]
    )
    
    return agent


async def init_agent():
    """Initialize the agent asynchronously."""
    try:
        agent = create_agent()
        thread = agent.get_new_thread()
        return agent, thread
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {e}")
        return None, None


def render_sidebar():
    """Render the sidebar with info and controls."""
    with st.sidebar:
        st.markdown("## 🤖 Agent Info")
        
        if st.session_state.agent_initialized:
            st.success("✅ Agent Online")
            st.markdown("### Function Tools")
            st.markdown("""
            - 📅 `get_calendar_events`
            - 📊 `get_timesheet_entries`
            - ✏️ `suggest_timesheet_entry`
            """)
        else:
            st.warning("⏳ Agent not initialized")
        
        st.markdown("---")
        
        st.markdown("## 💡 About")
        st.markdown("""
        This demo showcases an **Agentic AI** solution for Contoso Consulting Group's 
        Time & Expense tracking challenge.
        
        **Key Features:**
        - 🔍 Automatic missing time detection
        - 💰 Revenue impact calculation
        - 🧠 Multi-turn conversation memory
        - 🎯 Context-aware billability rules
        """)
        
        st.markdown("---")
        
        st.markdown("## 📊 Business Impact")
        st.metric("Missing Hours Recovered", "8.0 hrs/week", "per consultant")
        st.metric("Revenue @ $250/hr", "$2,000/week", "per consultant")
        st.metric("Annual Impact (50)", "$2.6M/year", "captured revenue")
        
        st.markdown("---")
        
        # Clear conversation button
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.thread = st.session_state.agent.get_new_thread()
            st.rerun()
        
        # Demo scenarios
        st.markdown("## 🎬 Quick Demos")
        if st.button("📋 Run Basic Demo", use_container_width=True):
            st.session_state.demo_running = True
            st.session_state.demo_type = "basic"
            st.rerun()


async def run_agent_query(agent, thread, user_input):
    """Run a query through the agent."""
    try:
        result = await agent.run(user_input, thread=thread)
        return result.text
    except Exception as e:
        return f"❌ Error: {str(e)}"


def render_message(role, content):
    """Render a chat message."""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You:</strong><br/>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="agent-message">
            <strong>🤖 Agent:</strong><br/>
            {content}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🚀 CCG Time & Expense Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Microsoft Agent Framework - Intelligent Time Tracking Assistant<br/>TTU Agentic Revolution Challenge (Nov 14th)</div>', unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Initialize agent if not done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing agent..."):
            agent, thread = asyncio.run(init_agent())
            if agent and thread:
                st.session_state.agent = agent
                st.session_state.thread = thread
                st.session_state.agent_initialized = True
                st.rerun()
    
    # Main content area
    if not st.session_state.agent_initialized:
        st.error("⚠️ Agent failed to initialize. Please check your Azure OpenAI configuration in `.env` file.")
        st.markdown("""
        ### Required Environment Variables:
        ```
        AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment-name
        AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
        AZURE_OPENAI_API_KEY=your-api-key
        ```
        """)
        return
    
    # Handle demo scenarios
    if st.session_state.demo_running and st.session_state.demo_type == "basic":
        st.markdown("### 📋 Running Basic Demo Scenario")
        
        demo_query = "Please review my calendar and timesheet for November 13-15, 2025 and identify any missing time entries. My email is arturoqu@microsoft.com."
        
        st.session_state.messages.append({"role": "user", "content": demo_query})
        
        with st.spinner("🤖 Agent analyzing calendar and timesheet..."):
            response = asyncio.run(
                run_agent_query(st.session_state.agent, st.session_state.thread, demo_query)
            )
            st.session_state.messages.append({"role": "agent", "content": response})
        
        st.session_state.demo_running = False
        st.rerun()
    
    # Chat interface
    st.markdown("### 💬 Conversation")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            render_message(message["role"], message["content"])
    
    # Input area
    st.markdown("---")
    
    # Sample questions section
    st.markdown("### 💡 Try These Questions")
    
    sample_questions = [
        "📋 Review my calendar and timesheet for November 13-23, 2025. My email is arturoqu@microsoft.com.",
        "💰 Calculate the revenue impact for the missing billable hours you found.",
        "🤔 Which entries are billable vs non-billable?",
        "🔍 Can you help me understand my missing time entries?",
        "✅ Yes, please proceed with submitting those missing timesheet entries."
    ]
    
    # Display sample questions as full-width clickable buttons
    for idx, question in enumerate(sample_questions):
        if st.button(question, key=f"sample_q_{idx}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("🤖 Agent thinking..."):
                response = asyncio.run(
                    run_agent_query(st.session_state.agent, st.session_state.thread, question)
                )
                st.session_state.messages.append({"role": "agent", "content": response})
            st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask the agent:",
            placeholder="e.g., 'Review my timesheet for this week' or 'What's the total missing hours?'",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)
    
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get agent response
        with st.spinner("🤖 Agent thinking..."):
            response = asyncio.run(
                run_agent_query(st.session_state.agent, st.session_state.thread, user_input)
            )
            st.session_state.messages.append({"role": "agent", "content": response})
        
        st.rerun()
    
    # Quick action buttons
    st.markdown("### 🎯 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Check Missing Time", use_container_width=True):
            query = "Please check for any missing time entries in my calendar and timesheet for arturoqu@microsoft.com."
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 Analyzing..."):
                response = asyncio.run(
                    run_agent_query(st.session_state.agent, st.session_state.thread, query)
                )
                st.session_state.messages.append({"role": "agent", "content": response})
            st.rerun()
    
    with col2:
        if st.button("💰 Calculate Impact", use_container_width=True):
            query = "What's the total missing billable hours and revenue impact?"
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 Calculating..."):
                response = asyncio.run(
                    run_agent_query(st.session_state.agent, st.session_state.thread, query)
                )
                st.session_state.messages.append({"role": "agent", "content": response})
            st.rerun()
    
    with col3:
        if st.button("✅ Submit Entries", use_container_width=True):
            query = "Yes, please proceed with submitting those missing timesheet entries."
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 Submitting..."):
                response = asyncio.run(
                    run_agent_query(st.session_state.agent, st.session_state.thread, query)
                )
                st.session_state.messages.append({"role": "agent", "content": response})
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Built with Microsoft Agent Framework | Azure OpenAI | Streamlit<br/>
        TTU Agentic Revolution Challenge 2025
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
