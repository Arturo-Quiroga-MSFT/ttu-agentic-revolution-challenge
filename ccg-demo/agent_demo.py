"""
CCG Time & Expense Agent Demo
Uses Microsoft Agent Framework (ChatAgent) with function calling.

This script demonstrates:
- Creating a ChatAgent with instructions
- Registering function tools (calendar and timesheet access)
- Using automatic function calling to detect missing time entries
- Producing structured suggestions with rationale
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient

# Import the function tools
from calendar_plugin import get_calendar_events
from timesheet_plugin import get_timesheet_entries, suggest_timesheet_entry

# Load environment variables from .env if present
load_dotenv()


def create_agent():
    """
    Create a ChatAgent with function tools for calendar and timesheet access.
    """
    # Try Azure OpenAI first, fall back to OpenAI
    azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4")
    
    # Create agent with instructions and tools
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

Present your findings in a clear, structured format.
"""
    
    # Create the chat client and agent
    if azure_deployment and azure_endpoint:
        print("🔧 Using Azure OpenAI service")
        if azure_api_key:
            # Use API key auth
            chat_client = AzureOpenAIChatClient(
                deployment_name=azure_deployment,
                endpoint=azure_endpoint,
                api_key=azure_api_key
            )
        else:
            # Use Azure CLI credential
            chat_client = AzureOpenAIChatClient(
                deployment_name=azure_deployment,
                endpoint=azure_endpoint,
                credential=AzureCliCredential()
            )
    elif openai_api_key:
        print("🔧 Using OpenAI service")
        chat_client = OpenAIChatClient(
            model_id=openai_model,
            api_key=openai_api_key
        )
    else:
        raise ValueError(
            "No AI service configured. Set AZURE_OPENAI_* or OPENAI_API_KEY environment variables."
        )
    
    # Create agent with function tools
    agent = chat_client.create_agent(
        name="CCG Time Assistant",
        instructions=agent_instructions,
        tools=[
            get_calendar_events,
            get_timesheet_entries,
            suggest_timesheet_entry
        ]
    )
    
    return agent


async def run_demo_scenario(agent, scenario_name, user_input, thread=None, show_details=True):
    """
    Run a single demo scenario with the agent.
    """
    print(f"\n{'='*60}")
    print(f"📋 SCENARIO: {scenario_name}")
    print(f"{'='*60}\n")
    
    print(f"👤 User:\n{user_input}\n")
    print("-" * 60)
    print("🤖 Agent working...\n")
    
    try:
        result = await agent.run(user_input, thread=thread)
        
        # Show function calls if available
        if show_details and hasattr(result, 'messages'):
            function_calls = [msg for msg in result.messages if hasattr(msg, 'tool_calls') and msg.tool_calls]
            if function_calls:
                print("📞 Function Calls Made:")
                for msg in function_calls:
                    for call in msg.tool_calls:
                        print(f"   └─ {call.function.name}()")
                print()
        
        # Print the final agent response
        print(f"🤖 Agent Response:\n{result.text}\n")
        
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """
    Main demo flow with multiple scenarios:
    1. Basic missing time detection
    2. Follow-up question (multi-turn conversation)
    3. Cost estimation scenario
    """
    print("=" * 60)
    print("🚀 CCG Time & Expense Agent Demo")
    print("Microsoft Agent Framework - ChatAgent with Function Calling")
    print("=" * 60)
    print()
    
    # Check for interactive mode
    interactive = os.getenv("DEMO_INTERACTIVE", "false").lower() == "true"
    multi_turn = os.getenv("DEMO_MULTI_TURN", "true").lower() == "true"
    
    try:
        agent = create_agent()
        print("✅ Agent initialized with 3 function tools:")
        print("   • get_calendar_events")
        print("   • get_timesheet_entries")
        print("   • suggest_timesheet_entry")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nTo run this demo, set one of the following:")
        print("  - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME (or AZURE_OPENAI_DEPLOYMENT_NAME),")
        print("    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY (or use az login)")
        print("  - OPENAI_API_KEY")
        return
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Create a conversation thread for multi-turn conversation
    # This maintains context across multiple interactions
    thread = agent.get_new_thread()
    
    # Scenario 1: Basic missing time detection
    await run_demo_scenario(
        agent,
        "Missing Time Detection (Primary Use Case)",
        "Please review my calendar and timesheet for November 13-23, 2025 and identify any missing time entries. My email is arturoqu@microsoft.com.",
        thread=thread
    )
    
    # Scenario 2: Follow-up question (demonstrates multi-turn conversation with memory)
    if multi_turn:
        print(f"\n{'='*60}")
        print("💬 MULTI-TURN CONVERSATION (Agent remembers context)")
        print(f"{'='*60}\n")
        
        # Follow-up: User responds to agent's question
        await run_demo_scenario(
            agent,
            "Follow-up: User Response",
            "Yes, please proceed with submitting those entries.",
            thread=thread,
            show_details=False
        )
        
        # Additional follow-up: Ask about specifics
        await run_demo_scenario(
            agent,
            "Follow-up: Clarification Question",
            "Actually, can you remind me what the total missing hours were again?",
            thread=thread,
            show_details=False
        )
    
    # Scenario 2: Cost estimation (show business value)
    print(f"\n{'='*60}")
    print("💰 BUSINESS IMPACT")
    print(f"{'='*60}\n")
    print("Identified Missing Time: 4.0 hours (2 flights × 2 hours each)")
    print("Billable Rate: $250/hour (example)")
    print("Recovered Revenue: $1,000 per consultant per week")
    print("Annual Impact (50 consultants): ~$2.6M in captured billable time")
    print("\n✨ Key Capabilities Demonstrated:")
    print("   ✓ Automatic calendar + timesheet cross-referencing")
    print("   ✓ Context-aware billability detection (travel = billable)")
    print("   ✓ Multi-source data integration (O365, ERP)")
    print("   ✓ Proactive suggestions with rationale")
    
    if interactive:
        # Interactive mode for live demo
        print(f"\n{'='*60}")
        print("💬 INTERACTIVE MODE (Type 'exit' to quit)")
        print(f"{'='*60}\n")
        print("You can now ask follow-up questions or give new commands.")
        print("The agent remembers the entire conversation context.\n")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                if not user_input:
                    continue
                
                print("\n🤖 Agent working...\n")
                result = await agent.run(user_input, thread=thread)
                print(f"🤖 Agent: {result.text}\n")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Demo complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
