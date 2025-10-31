# CCG Time & Expense — Agent Demo

This folder contains a working **ChatAgent** (Microsoft Agent Framework) demo for the Contoso Consulting Group Time & Expense challenge.

## What's inside

- `calendar_sample.json` — sample calendar events for a consultant
- `timesheet_sample.json` — sample existing timesheet entries
- `calendar_plugin.py` — function tool that provides calendar access (read events)
- `timesheet_plugin.py` — function tools that provide timesheet access (read/suggest entries)
- `agent_demo.py` — the main runnable script with the `ChatAgent`
- `requirements.txt` — Python dependencies (Microsoft Agent Framework, Azure identity)

## How it works

1. The agent is initialized with instructions to detect missing time entries.
2. Three function tools (`get_calendar_events`, `get_timesheet_entries`, `suggest_timesheet_entry`) are registered — these are "tools" the agent can call.
3. The agent reasons over calendar events and timesheet entries, identifies gaps, and proposes missing entries with rationale and confidence.
4. The agent uses **function calling** (tool use) automatically — demonstrating core agentic behaviors: reasoning, tool use, proactivity.

## Prerequisites

- Python 3.10+ (you have 3.13 in the venv)
- Azure OpenAI endpoint + API key (or OpenAI key) — set via environment variables or `.env` file
- Microsoft Agent Framework installed (`pip install agent-framework`)

## Setup

1. Activate the project venv:
   ```bash
   source /Users/arturoquiroga/TTU-AGENTIC-REVOLUTION-CHALLENGE/.venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r ccg-demo/requirements.txt
   ```

3. Set Azure OpenAI environment variables (or create a `.env` file in `ccg-demo/`):
   ```bash
   export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="your-deployment-name"
   export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
   export AZURE_OPENAI_API_KEY="your-api-key"  # or use az login for Azure CLI auth
   ```

   Or for OpenAI (not Azure):
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export OPENAI_CHAT_MODEL_ID="gpt-4"  # optional, defaults to gpt-4
   ```

## Running the demo

### Console Demo (Original)
```bash
cd /Users/arturoquiroga/TTU-AGENTIC-REVOLUTION-CHALLENGE
python ccg-demo/agent_demo.py
```

Expected output:
- Agent reads calendar and timesheet via function calls.
- Agent identifies missing travel time (8 hours) and produces structured suggestions with rationale.
- Multi-turn conversation demonstrates memory and context awareness.

### Streamlit Web App Demo (Interactive UI) 🎉
```bash
cd /Users/arturoquiroga/TTU-AGENTIC-REVOLUTION-CHALLENGE/ccg-demo
streamlit run streamlit_app.py
```

Features:
- 🎨 Professional web interface with chat UI
- 💬 Real-time conversation with the agent
- 📊 Business metrics dashboard
- 🔘 Quick action buttons for common prompts
- 📱 Responsive design for presentations
- 🔄 Persistent conversation memory
- ✨ Function call visibility

## What to show in the readout

- Explain the architecture: calendar + timesheet function tools → agent reasoning → suggestions.
- Run `agent_demo.py` live (or show pre-recorded console output if network is flaky).
- Highlight the function calls in the output (agent invoking `get_calendar_events` and `get_timesheet_entries`).
- Show the final suggestion with confidence and rationale.

## Customization for live API keys

If you want to test with real Azure OpenAI:
- Set the env vars above.
- Optionally adjust the `agent_demo.py` prompt or add more sample calendar/timesheet entries.

If keys are unavailable:
- The demo is deterministic (uses sample data files).
- Record console output once and present screenshots/slides.

## Tech stack

- **Agent Framework**: Microsoft Agent Framework `ChatAgent` (Python)
- **Function Tools**: `get_calendar_events`, `get_timesheet_entries`, `suggest_timesheet_entry` (simple Python functions)
- **LLM**: Azure OpenAI or OpenAI (gpt-4 or gpt-4o)
- **Function calling**: Automatic (agent framework handles tool orchestration)

## Next steps after the event

- Wire real calendar API (Microsoft Graph for Outlook/Teams calendar)
- Wire real timesheet API (custom or ERP integration)
- Add confirmation flow (chat UI or Teams message action)
- Add audit trail and manager dashboard

---

Questions? See `CCG_Readout.md` in the repo root for the full readout script and slide template.
