"""
Multi-Agent Console Demo for Contoso Consulting Group
Demonstrates orchestrated collaboration between specialized agents.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient
from agents.orchestrator_agent import create_orchestrator

# Load environment variables
load_dotenv()

async def run_demo():
    """Run the multi-agent demo with various queries."""
    
    print("=" * 80)
    print("CONTOSO CONSULTING GROUP - MULTI-AGENT TIME & EXPENSE DEMO")
    print("=" * 80)
    print()
    
    # Initialize the chat client using Microsoft Agent Framework
    azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4")
    
    if azure_deployment and azure_endpoint:
        print("🔧 Using Azure OpenAI service")
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
        print("🔧 Using OpenAI service")
        chat_client = OpenAIChatClient(
            model_id=openai_model,
            api_key=openai_api_key
        )
    else:
        print("❌ No AI service configured. Set AZURE_OPENAI_* or OPENAI_API_KEY environment variables.")
        return
    
    orchestrator = create_orchestrator(chat_client)
    
    # Demo queries showcasing different agent capabilities
    user_email = "arturoqu@microsoft.com"
    
    print("=" * 80)
    print("DEMO: Analyzing Missing Time Entries")
    print("=" * 80)
    print(f"User: {user_email}")
    print("\nThis demo will:")
    print("1. Analyze calendar events (Calendar Agent)")
    print("2. Review timesheet entries (Timesheet Agent)")
    print("3. Identify missing entries (Suggestion Agent)")
    print("4. Calculate revenue impact (Revenue Agent)")
    print()
    
    try:
        # Run the complete missing time analysis workflow
        print(f"{'-' * 80}")
        print("Phase 1: Analyzing calendar and timesheet data...")
        print(f"{'-' * 80}\n")
        
        analysis_results = await orchestrator.analyze_missing_time(
            user_email=user_email,
            parallel=True
        )
        
        print("\n" + "=" * 80)
        print("CALENDAR ANALYSIS")
        print("=" * 80)
        print(analysis_results.get("calendar_analysis", "No results"))
        
        print("\n" + "=" * 80)
        print("TIMESHEET ANALYSIS")
        print("=" * 80)
        print(analysis_results.get("timesheet_analysis", "No results"))
        
        print("\n" + "=" * 80)
        print("SUGGESTIONS FOR MISSING ENTRIES")
        print("=" * 80)
        print(analysis_results.get("suggestions", "No suggestions"))
        
        # Calculate revenue impact if we have suggestions
        print("\n" + f"{'-' * 80}")
        print("Phase 2: Calculating revenue impact...")
        print(f"{'-' * 80}\n")
        
        # Estimate missing hours (simplified for demo)
        missing_hours = 20.0  # Example value
        
        impact_results = await orchestrator.calculate_impact(
            user_email=user_email,
            missing_hours=missing_hours,
            billable_rate=250.0
        )
        
        print("\n" + "=" * 80)
        print("REVENUE IMPACT ANALYSIS")
        print("=" * 80)
        print(impact_results.get("revenue_analysis", "No analysis"))
        
        # Show execution summary
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(orchestrator.get_execution_summary())
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 80}")
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nKey Observations:")
    print("✓ Calendar and Timesheet agents run in parallel for efficiency")
    print("✓ Suggestion agent synthesizes findings from both sources")
    print("✓ Revenue agent calculates business impact")
    print("✓ Orchestrator coordinates the complete workflow")
    print("✓ Each agent maintains domain expertise and focused context")
    print()

async def interactive_mode():
    """Run in interactive mode for custom queries."""
    
    print("=" * 80)
    print("CONTOSO CONSULTING GROUP - INTERACTIVE MULTI-AGENT MODE")
    print("=" * 80)
    print()
    print("Enter your queries and see the multi-agent system in action.")
    print("Type 'exit' or 'quit' to end the session.")
    print()
    
    # Initialize the chat client using Microsoft Agent Framework
    azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_CHAT_MODEL_ID", "gpt-4")
    
    if azure_deployment and azure_endpoint:
        print("🔧 Using Azure OpenAI service")
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
        print("🔧 Using OpenAI service")
        chat_client = OpenAIChatClient(
            model_id=openai_model,
            api_key=openai_api_key
        )
    else:
        print("❌ No AI service configured. Set AZURE_OPENAI_* or OPENAI_API_KEY environment variables.")
        return
    
    orchestrator = create_orchestrator(chat_client)
    
    user_email = "arturoqu@microsoft.com"
    
    while True:
        print(f"\n{'-' * 80}")
        print("\nOptions:")
        print("1. Analyze missing time entries")
        print("2. Calculate revenue impact")
        print("3. Exit")
        print()
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '3' or choice.lower() in ['exit', 'quit', 'q']:
            print("\nExiting interactive mode. Goodbye!")
            break
        
        if choice == '1':
            print(f"{'-' * 80}")
            print("Analyzing missing time entries...")
            print(f"{'-' * 80}\n")
            
            try:
                results = await orchestrator.analyze_missing_time(
                    user_email=user_email,
                    parallel=True
                )
                
                print("\nCALENDAR ANALYSIS:")
                print(results.get("calendar_analysis", "No results"))
                print("\nTIMESHEET ANALYSIS:")
                print(results.get("timesheet_analysis", "No results"))
                print("\nSUGGESTIONS:")
                print(results.get("suggestions", "No suggestions"))
                print("\nEXECUTION LOG:")
                print(orchestrator.get_execution_summary())
                
            except Exception as e:
                print(f"ERROR: {str(e)}")
                print(f"Type: {type(e).__name__}")
        
        elif choice == '2':
            print(f"{'-' * 80}")
            hours = input("Enter missing billable hours: ").strip()
            rate = input("Enter hourly rate (default 250): ").strip() or "250"
            
            try:
                missing_hours = float(hours)
                billable_rate = float(rate)
                
                print("\nCalculating revenue impact...")
                print(f"{'-' * 80}\n")
                
                results = await orchestrator.calculate_impact(
                    user_email=user_email,
                    missing_hours=missing_hours,
                    billable_rate=billable_rate
                )
                
                print("\nREVENUE IMPACT:")
                print(results.get("revenue_analysis", "No analysis"))
                print("\nEXECUTION LOG:")
                print(orchestrator.get_execution_summary())
                
            except ValueError:
                print("Invalid input. Please enter numeric values.")
            except Exception as e:
                print(f"ERROR: {str(e)}")
                print(f"Type: {type(e).__name__}")
        
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def main():
    """Main entry point for the demo."""
    
    # Check for required environment variables
    required_vars = ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_DEPLOYMENT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return
    
    print("\nSelect Mode:")
    print("1. Guided Demo (pre-defined queries)")
    print("2. Interactive Mode (custom queries)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        asyncio.run(run_demo())
    elif choice == '2':
        asyncio.run(interactive_mode())
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
