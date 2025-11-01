# Multi-Agent Timesheet Assistant - PRODUCTION VERSION

🤖 **Intelligent timesheet assistant with approval workflow and write capabilities**

## Overview

This is the **PRODUCTION VERSION** of the Multi-Agent Timesheet Assistant, featuring:

- ✅ **Approval Workflow**: Review and approve/reject suggestions before writing
- 💾 **Write Capabilities**: Approved entries are written directly to timesheet
- 📋 **Audit Logging**: Complete audit trail of all operations
- ➕ **Manual Entry**: Direct write capability for manual timesheet entries
- 🔒 **Compliance**: All actions tracked with timestamps and user attribution

## Key Differences from Dev Version

| Feature | Dev Version | Production Version |
|---------|-------------|-------------------|
| Write Access | ❌ Read-only | ✅ Full write access |
| Approval Workflow | ❌ No approval | ✅ User approval required |
| Audit Trail | ❌ No logging | ✅ Complete audit log |
| Manual Entry | ❌ Not available | ✅ Direct write form |
| Agents | 4 agents | 5 agents (+ Approval) |

## Architecture

The system uses **Microsoft Agent Framework** with 5 specialized agents:

1. **📅 Calendar Agent** - Analyzes calendar events, identifies billable time
2. **📝 Timesheet Agent** - Reviews existing entries, identifies gaps
3. **💡 Suggestion Agent** - Cross-references data, proposes entries
4. **✅ Approval Agent** - Processes approvals/rejections, writes to timesheet ⭐ NEW
5. **💰 Revenue Agent** - Calculates financial impact

See `diagrams/architecture.md` for complete system architecture.

## Quick Start

### Prerequisites

- Python 3.11+
- Azure OpenAI or OpenAI API access
- Azure CLI (for deployment)

### Local Development

1. **Clone and navigate:**
   ```bash
   cd ccg-demo-multi-agent-prod
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

4. **Run the application:**
   ```bash
   streamlit run multi_agent_streamlit.py
   ```

5. **Access the UI:**
   ```
   http://localhost:8501
   ```

### Azure Deployment

Deploy to Azure Container Apps using the automated script:

```bash
# Ensure .env is configured
./deploy-aca.sh
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## Usage

### 1. Analysis & Approval

1. Enter user email (e.g., `sarah.johnson@contoso.com`)
2. Click **"Analyze Missing Time"**
3. Review the analysis results and suggestions
4. For each suggestion:
   - Click **"Approve"** to write to timesheet
   - Click **"Reject"** to log rejection (with reason)

### 2. Revenue Impact

1. Go to **"Revenue Impact"** tab
2. Enter missing hours and billable rate
3. Click **"Calculate Impact"**
4. View financial projections

### 3. Audit Log

1. Go to **"Audit Log"** tab
2. Set number of entries to display
3. Click **"Refresh Audit Log"**
4. Review all operations with timestamps

### 4. Manual Entry

1. In **"Analysis & Approval"** tab, expand **"Manual Entry"**
2. Fill in entry details (date, time, task, project)
3. Click **"Add Manual Entry"**
4. Entry is written immediately with audit logging

## Project Structure

```
ccg-demo-multi-agent-prod/
├── agents/                      # Specialized agent modules
│   ├── calendar_agent.py        # Calendar event analysis
│   ├── timesheet_agent.py       # Timesheet validation
│   ├── suggestion_agent.py      # Entry recommendations
│   ├── approval_agent.py        # ⭐ Approval workflow (NEW)
│   ├── revenue_agent.py         # Financial impact
│   └── orchestrator_agent.py    # Agent coordination
├── tools/                       # ⭐ Write tools (NEW)
│   └── timesheet_tools.py       # Write & audit functions
├── shared/                      # Shared data
│   ├── calendar_sample.json     # Calendar events
│   ├── timesheet_sample.json    # Timesheet entries
│   └── audit_log.json           # ⭐ Audit trail (NEW)
├── diagrams/                    # Architecture diagrams
│   ├── architecture.md          # System architecture
│   └── workflow.md              # Workflow sequence
├── multi_agent_streamlit.py     # Streamlit web UI
├── Dockerfile                   # Container definition
├── deploy-aca.sh               # Azure deployment script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── DEPLOYMENT.md               # Deployment guide
```

## Approval Workflow

The production version implements a secure approval workflow:

```
1. Analysis → 2. Suggestions → 3. Review → 4. Approve/Reject → 5. Write/Log → 6. Audit
```

### Approval Process

**When user approves:**
- Entry data validated
- `add_timesheet_entry()` writes to timesheet
- Operation logged in audit trail
- User receives confirmation

**When user rejects:**
- Rejection reason captured
- `reject_suggestion()` logs rejection
- No write to timesheet
- Rejection stored in audit trail

### Audit Trail

All operations logged with:
- ✅ Timestamp (ISO format)
- 👤 User attribution
- 📝 Complete entry details
- 🔄 Action type (approve/reject)
- 💬 Reason (for rejections)

## Security & Compliance

### Write Access Control

- ✅ User approval required before writing
- ✅ No modifications to existing entries (add-only)
- ✅ No deletions (immutable timesheet)
- ✅ All writes attributed to approver

### Audit Logging

- ✅ Comprehensive audit trail
- ✅ Timestamp for every operation
- ✅ User attribution
- ✅ Immutable log (append-only)

### Data Validation

Before writing, the system validates:
- Date format (YYYY-MM-DD)
- Time format (HH:MM:SS)
- Duration calculations
- Required fields present
- Billability classification

## Environment Variables

Required configuration in `.env`:

```bash
# Azure OpenAI (recommended)
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-10-21

# OR OpenAI
USE_AZURE_OPENAI=false
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
```

## Performance

- **Parallel Execution**: Calendar + Timesheet agents run simultaneously
- **Response Time**: ~5-10 seconds for complete analysis
- **Scalability**: Handles 1-3 replicas in Azure Container Apps
- **Cost**: ~$0.01 per analysis (Azure OpenAI)

## Troubleshooting

### Import Errors

Ensure `microsoft-agent` is installed:
```bash
pip install microsoft-agent>=1.2.1
```

### Write Operations Fail

Check file permissions in `shared/` directory:
```bash
chmod 755 shared/
chmod 644 shared/*.json
```

### Agent Initialization Fails

Verify environment variables are set:
```bash
cat .env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('AZURE_OPENAI_ENDPOINT'))"
```

### Audit Log Issues

Ensure `audit_log.json` exists and is writable:
```bash
touch shared/audit_log.json
echo '{"entries": []}' > shared/audit_log.json
```

## Testing

Test the complete workflow:

```bash
# 1. Start application
streamlit run multi_agent_streamlit.py

# 2. Test analysis
# Enter email: sarah.johnson@contoso.com
# Click: "Analyze Missing Time"

# 3. Test approval
# Review suggestions
# Click: "Approve" on first suggestion
# Verify: Success message appears

# 4. Test rejection
# Click: "Reject" on second suggestion
# Enter reason: "Not billable"
# Verify: Rejection logged

# 5. Test audit log
# Navigate to "Audit Log" tab
# Click: "Refresh Audit Log"
# Verify: Approved and rejected operations visible

# 6. Test manual entry
# Expand: "Manual Entry"
# Fill in form
# Click: "Add Manual Entry"
# Verify: Entry added confirmation
```

## API Usage

For programmatic access (future enhancement):

```python
from agents.orchestrator_agent import create_orchestrator
from microsoft_agent import AzureOpenAIChatClient

# Initialize
client = AzureOpenAIChatClient(...)
orch = create_orchestrator(client)

# Analyze
results = await orch.analyze_missing_time("user@example.com")

# Approve entry
approval = await orch.process_approval(
    user_email="user@example.com",
    entry_data={...},
    approved=True,
    approved_by="api_client"
)
```

## Roadmap

Future enhancements:
- [ ] Azure AD authentication
- [ ] Persistent storage (Azure Blob)
- [ ] Real-time notifications
- [ ] Bulk approval capability
- [ ] Export to Excel/CSV
- [ ] Integration with time tracking systems (Workday, SAP)
- [ ] Mobile-responsive UI
- [ ] Multi-language support

## Documentation

- **Architecture**: See `diagrams/architecture.md`
- **Workflow**: See `diagrams/workflow.md`
- **Deployment**: See `DEPLOYMENT.md`
- **Code**: Inline documentation in all Python files

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review agent logs in Streamlit UI
3. Check Azure Container Apps logs (if deployed)
4. Review audit log for operation history

## License

© 2025 Contoso Consulting Group - Internal Use Only

## Credits

Built with:
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Streamlit](https://streamlit.io)
- [Azure Container Apps](https://azure.microsoft.com/en-us/products/container-apps)

---

**Version:** 2.0 (Production)  
**Last Updated:** November 2025  
**Status:** ✅ Production Ready
