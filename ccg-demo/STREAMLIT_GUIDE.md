# 🎨 Streamlit Web UI for CCG Demo

A beautiful, interactive web interface for the CCG Time & Expense Agent demo.

## 🚀 Quick Start

### 1. Install Streamlit

```bash
pip install streamlit
```

Or update all requirements:

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run ccg-demo/streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## ✨ Features

### 🎯 Interactive Chat Interface
- **Natural conversation flow** with the agent
- **Multi-turn memory** — agent remembers the entire conversation
- **Real-time responses** with loading indicators
- **Message history** with clear user/agent distinction

### 📊 Live Metrics Dashboard
- **Missing hours** recovered per consultant
- **Revenue impact** calculation ($2,000/week per consultant)
- **Annual projections** ($2.6M for 50 consultants)

### 🎬 Quick Demo Scenarios
- **Basic Demo**: One-click demo of missing time detection
- **Quick Actions**: Pre-built buttons for common queries
  - Check Missing Time
  - Calculate Revenue Impact
  - Submit Entries

### 🤖 Agent Status Panel
- Real-time agent status (Online/Offline)
- List of available function tools
- Conversation reset button

### 🎨 Modern UI Design
- Clean, professional interface
- Color-coded messages (user vs agent)
- Responsive layout
- Custom styling with Azure color scheme

---

## 💡 Usage Tips

### Starting a Conversation

Type in the chat box or use quick action buttons:

**Example queries:**
- "Review my calendar and timesheet for November 13-14"
- "What's the total missing billable hours?"
- "Yes, please submit those entries"
- "Can you remind me which entries were missing?"

### Using Quick Actions

1. **Check Missing Time** — Automatically analyzes calendar vs timesheet
2. **Calculate Impact** — Shows revenue impact of missing time
3. **Submit Entries** — Confirms and records suggested entries

### Multi-Turn Conversation

The agent remembers context across messages:

```
You: "Review my timesheet for this week"
Agent: [Analyzes and finds 8 missing hours]

You: "What's the revenue impact?"
Agent: [Calculates $2,000 without re-analyzing]

You: "Yes, submit those entries"
Agent: [Remembers which entries and submits them]
```

### Starting Over

Click **"🔄 New Conversation"** in the sidebar to:
- Clear chat history
- Reset agent memory
- Start fresh analysis

---

## 🎤 Demo Presentation Tips

### 1. Pre-Event Setup

**Before the audience arrives:**
```bash
# Start the app
streamlit run ccg-demo/streamlit_app.py

# Navigate to localhost:8501
# Verify agent initializes successfully
```

**Check the sidebar shows:**
- ✅ Agent Online
- Function tools listed
- Metrics displayed

### 2. Opening Script (30 seconds)

> "Let me show you an AI agent that automatically detects missing billable time. This uses Microsoft's Agent Framework with three function tools that read calendar events, timesheet entries, and suggest corrections."

**Action:** Show the sidebar with tools and metrics.

### 3. Live Demo (90 seconds)

**Click "📋 Run Basic Demo"** or type:
```
"Review my calendar and timesheet for November 13-14, 2025 for alice@ccg.com"
```

**Point out:**
- Agent calls function tools (check calendar, check timesheet)
- Identifies 8 missing hours
- Provides rationale for each entry
- Asks for confirmation

**Then click "✅ Submit Entries"** or type:
```
"Yes, please submit those entries"
```

**Highlight:**
- Agent remembers the context (multi-turn memory)
- Confirms submission without re-analyzing

### 4. Impact Reveal (30 seconds)

**Point to the sidebar metrics:**
- "8 hours/week recovered = $2,000 per consultant"
- "For 50 consultants = $2.6M annually in captured revenue"
- "Agent runs for ~$0.01 per invocation"

**Return on Investment is massive.**

### 5. Interactive Q&A (30 seconds)

**Take a live question from the audience:**

Examples:
- "Can it handle different billing rates?" → Yes, configurable
- "What if calendar is wrong?" → Agent provides rationale for human review
- "Can it integrate with our systems?" → Yes, replace sample files with real APIs

---

## 🔧 Customization

### Changing the Billable Rate

Edit the metrics in the sidebar (lines 85-87 in `streamlit_app.py`):

```python
st.metric("Missing Hours Recovered", "8.0 hrs/week", "per consultant")
st.metric("Revenue @ $300/hr", "$2,400/week", "per consultant")  # Changed rate
st.metric("Annual Impact (50)", "$3.1M/year", "captured revenue")  # Updated
```

### Adding More Quick Actions

Add new buttons in the Quick Actions section (lines 280-310):

```python
with col4:
    if st.button("📈 Weekly Report", use_container_width=True):
        query = "Generate a weekly summary report for alice@ccg.com"
        # ... rest of button logic
```

### Customizing Colors

Edit the CSS in lines 25-60:

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;  /* Change header color */
    }
    .metric-card {
        border-left: 4px solid #YOUR_COLOR;  /* Change accent color */
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📸 Screenshots for Slides

### Recommended Screenshots:

1. **Initial State**
   - Shows agent online with tools listed
   - Clean interface, ready for input

2. **Analysis in Progress**
   - "🤖 Agent thinking..." spinner
   - Shows the agent is working

3. **Results Display**
   - Full analysis with 8 missing entries
   - Rationale for each entry
   - Professional formatting

4. **Multi-Turn Conversation**
   - User asks follow-up question
   - Agent remembers context and responds

5. **Sidebar Metrics**
   - Close-up of business impact numbers
   - $2.6M annual impact highlighted

---

## 🐛 Troubleshooting

### App Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Fix:**
```bash
pip install streamlit
```

### Agent Won't Initialize

**Error:** "⚠️ Agent failed to initialize"

**Fix:** Check your `.env` file has valid Azure OpenAI credentials:
```
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-key
```

### Port Already in Use

**Error:** `Address already in use`

**Fix:** Specify a different port:
```bash
streamlit run ccg-demo/streamlit_app.py --server.port 8502
```

### Agent Responses Are Slow

**Expected:** First response may take 3-5 seconds (LLM processing + function calls)

**To speed up:**
- Use `gpt-4o-mini` instead of `gpt-4` (faster, cheaper)
- Pre-run the demo once before the event to warm up

---

## 🎭 Advanced: Full-Screen Presentation Mode

For a cleaner presentation:

```bash
streamlit run ccg-demo/streamlit_app.py --server.headless true
```

Then in the browser:
1. Press `F11` for full-screen
2. Click the `⋮` menu (top right) → Settings
3. Set **"Wide mode"** ON
4. Set **"Run on save"** OFF (to avoid accidental reloads)

---

## 📊 Metrics Explained

### Missing Hours Recovered: 8.0 hrs/week
- Based on sample data (2 flights × 2 hrs + lunch + Q&A + prep)
- Real consultants average 5-10 hrs/week missing

### Revenue Impact: $2,000/week per consultant
- 8 hours × $250/hr = $2,000
- Conservative estimate (some firms bill $400+/hr)

### Annual Impact: $2.6M
- $2,000/week × 50 consultants × 52 weeks = $5.2M
- Assume 50% detection rate → $2.6M conservatively

---

## 🔮 Future Enhancements

Ideas for post-event:

1. **Data Visualization**
   - Add charts showing missing time trends
   - Weekly/monthly summaries

2. **Multi-User Support**
   - Dropdown to select different consultants
   - Compare capture rates across team

3. **Real-Time Integration**
   - Connect to live Microsoft Graph API
   - Pull real calendar and timesheet data

4. **Approval Workflow**
   - Manager review interface
   - Approve/reject suggestions with one click

5. **Export Functionality**
   - Download suggested entries as CSV
   - Generate PDF reports

---

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Microsoft Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

---

## 📝 License & Credits

Built for the **TTU Agentic Revolution Challenge 2025**

**Technologies:**
- Microsoft Agent Framework (Python)
- Azure OpenAI (GPT-4)
- Streamlit (Web UI)
- Python 3.13

---

## 🆘 Support

If you encounter issues during the demo:

1. **Check the terminal** where Streamlit is running for error messages
2. **Refresh the browser** (sometimes fixes UI glitches)
3. **Restart the app** (Ctrl+C in terminal, then re-run)
4. **Fall back to CLI demo** (`python ccg-demo/agent_demo.py`)

**Questions?** Check `ccg-demo/DEMO_IMPROVEMENTS.md` for additional guidance.
