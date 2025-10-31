# CCG Time & Expense Agent - Multi-Agent Architecture

**Multi-Agent Demo** for Contoso Consulting Group's Time & Expense Tracking Challenge

## Overview

This directory contains an enhanced **multi-agent architecture** implementation where specialized agents collaborate to identify missing billable time and provide intelligent recommendations.

## Architecture

### Agent Roles

1. **Calendar Agent** - Specializes in calendar event analysis
   - Extracts and interprets calendar events
   - Identifies travel, client meetings, and billable activities
   - Flags potential billable time blocks

2. **Timesheet Agent** - Specializes in timesheet validation
   - Analyzes existing timesheet entries
   - Validates entry completeness and accuracy
   - Identifies gaps and inconsistencies

3. **Suggestion Agent** - Specializes in recommendations
   - Cross-references calendar and timesheet data
   - Generates missing entry suggestions with rationale
   - Applies billability rules and business logic

4. **Revenue Agent** - Specializes in financial impact analysis
   - Calculates missing billable hours
   - Computes revenue impact per consultant
   - Scales projections to firm-wide impact

5. **Compliance Agent** (Optional) - Specializes in policy enforcement
   - Checks for policy violations
   - Ensures audit trail compliance
   - Flags entries requiring manager approval

6. **Orchestrator/Manager Agent** - Coordinates workflow
   - Routes tasks to appropriate agents
   - Aggregates results from multiple agents
   - Provides unified response to user

## Benefits of Multi-Agent Approach

### Specialization
- Each agent is an expert in its domain
- More accurate and context-aware analysis
- Easier to fine-tune individual agent behaviors

### Scalability
- Agents can work in parallel for faster processing
- Easy to add new agents (e.g., approval agent, notification agent)
- Can distribute across multiple compute resources

### Maintainability
- Clear separation of concerns
- Easier to test individual agents
- Simpler to extend or modify specific capabilities

### Flexibility
- Can invoke agents selectively based on user needs
- Different workflows for different scenarios
- Can run agents sequentially or in parallel

## Comparison with Single-Agent Approach

| Aspect | Single Agent (`ccg-demo/`) | Multi-Agent (`ccg-demo-multi-agent/`) |
|--------|---------------------------|--------------------------------------|
| **Complexity** | Simpler, all-in-one | More complex, distributed logic |
| **Specialization** | Generalist | Multiple specialists |
| **Performance** | Sequential processing | Can parallelize operations |
| **Maintainability** | Harder to extend | Easier to modify individual agents |
| **Use Case** | Quick POC, simple demos | Production-ready, complex workflows |

## Files

- `multi_agent_demo.py` - Console demo with multi-agent orchestration
- `multi_agent_streamlit.py` - Interactive Streamlit UI showcasing agent collaboration
- `agents/` - Individual agent implementations
  - `calendar_agent.py` - Calendar analysis specialist
  - `timesheet_agent.py` - Timesheet validation specialist
  - `suggestion_agent.py` - Recommendation specialist
  - `revenue_agent.py` - Financial impact specialist
  - `orchestrator_agent.py` - Workflow coordinator
- `shared/` - Shared utilities and data sources
  - Symlinks to `../ccg-demo/calendar_sample.json`
  - Symlinks to `../ccg-demo/timesheet_sample.json`
- `requirements.txt` - Dependencies (same as single-agent)
- `.env.example` - Environment variable template

## Quick Start

### Prerequisites

Same as single-agent demo:
- Python 3.10+
- Azure OpenAI or OpenAI API access
- Virtual environment activated

### Installation

```bash
# From project root
cd ccg-demo-multi-agent

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Running the Demo

#### Console Demo
```bash
python multi_agent_demo.py
```

#### Streamlit Web UI
```bash
streamlit run multi_agent_streamlit.py
```

## Demo Scenarios

### Scenario 1: Parallel Agent Execution
- Calendar Agent and Timesheet Agent analyze data simultaneously
- Results are merged by Orchestrator
- Faster than sequential processing

### Scenario 2: Agent Collaboration
- User asks: "Find my missing time"
- Orchestrator routes to Calendar + Timesheet agents
- Suggestion Agent synthesizes findings
- Revenue Agent calculates impact
- All results presented in unified view

### Scenario 3: Selective Agent Invocation
- User asks: "What's my revenue impact?"
- Orchestrator directly invokes Revenue Agent
- Skips unnecessary agents for faster response

## Development Roadmap

### Phase 1: Core Multi-Agent (Current)
- [x] Define agent roles and responsibilities
- [ ] Implement individual agents
- [ ] Create orchestrator logic
- [ ] Console demo

### Phase 2: Streamlit UI
- [ ] Multi-agent visualization dashboard
- [ ] Show individual agent contributions
- [ ] Interactive agent selection
- [ ] Parallel execution indicators

### Phase 3: Advanced Features
- [ ] Manager/Approval agent for workflows
- [ ] Compliance agent for policy enforcement
- [ ] Historical learning from corrections
- [ ] Agent-to-agent communication (vs. orchestrator-only)

## Technical Notes

### Agent Communication Patterns

**Hub-and-Spoke (Current):**
- Orchestrator coordinates all agents
- Agents don't talk directly to each other
- Simpler, easier to debug

**Peer-to-Peer (Future):**
- Agents can communicate directly
- More flexible, autonomous
- Requires more sophisticated coordination

### Data Sharing

- Agents share access to common data sources
- Each agent has read-only access to raw data
- Orchestrator manages state and results

## Contributing

This is part of the TTU Agentic Revolution Challenge demo. Feedback welcome!

## License

MIT License - see root LICENSE file for details

---

**Built with Microsoft Agent Framework | Azure OpenAI | Streamlit**  
**TTU Agentic Revolution Challenge 2025**
