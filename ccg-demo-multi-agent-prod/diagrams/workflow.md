```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant Orch as Orchestrator
    participant Cal as Calendar Agent
    participant Time as Timesheet Agent
    participant Sug as Suggestion Agent
    participant App as Approval Agent
    participant Rev as Revenue Agent
    participant Data as Data Layer
    participant Audit as Audit Log

    Note over User,Audit: Phase 1: Analysis (Parallel Execution)
    User->>UI: Enter email & click "Analyze"
    UI->>Orch: analyze_missing_time(email)
    
    par Parallel Analysis
        Orch->>Cal: Analyze calendar events
        Cal->>Data: get_calendar_events()
        Data-->>Cal: Calendar data
        Cal-->>Orch: Billable/non-billable events
    and
        Orch->>Time: Analyze timesheet entries
        Time->>Data: get_timesheet_entries()
        Data-->>Time: Timesheet data
        Time-->>Orch: Hours logged & gaps
    end
    
    Note over User,Audit: Phase 2: Suggestions
    Orch->>Sug: Synthesize findings
    Sug->>Data: Read calendar + timesheet
    Data-->>Sug: Combined data
    Sug-->>Orch: Suggested entries
    Orch-->>UI: Analysis results + suggestions
    UI-->>User: Display suggestions with approve/reject buttons
    
    Note over User,Audit: Phase 3: Approval Workflow (PRODUCTION)
    alt User Approves Entry
        User->>UI: Click "Approve" button
        UI->>App: process_approval(entry, approved=true)
        App->>Data: add_timesheet_entry()
        Data-->>App: Entry written
        App->>Audit: log_audit_entry(approval)
        Audit-->>App: Logged
        App-->>UI: Success confirmation
        UI-->>User: ✅ Entry added to timesheet
    else User Rejects Entry
        User->>UI: Click "Reject" button + reason
        UI->>App: process_approval(entry, approved=false)
        App->>Audit: reject_suggestion(reason)
        Audit-->>App: Logged
        App-->>UI: Rejection confirmed
        UI-->>User: ❌ Rejection logged
    end
    
    Note over User,Audit: Optional: Revenue Impact Analysis
    User->>UI: Calculate revenue impact
    UI->>Orch: calculate_impact(hours, rate)
    Orch->>Rev: Calculate financial impact
    Rev-->>Orch: Revenue projections
    Orch-->>UI: Impact analysis
    UI-->>User: Display financial metrics
    
    Note over User,Audit: Optional: View Audit History
    User->>UI: View audit log
    UI->>App: get_audit_history()
    App->>Audit: get_audit_log()
    Audit-->>App: Recent entries
    App-->>UI: Audit data
    UI-->>User: Display audit trail
```

**Workflow Sequence - PRODUCTION VERSION**

This diagram illustrates the complete workflow including approval and write operations:

**Phase 1: Analysis (Parallel)**
- Calendar Agent and Timesheet Agent run simultaneously
- Reduces analysis time by ~50%
- Both agents query their respective data sources

**Phase 2: Suggestions**
- Suggestion Agent cross-references findings
- Proposes missing entries with rationale
- Results displayed to user for review

**Phase 3: Approval Workflow** ⭐ NEW
- User reviews each suggestion
- Approves → Writes to timesheet + logs in audit
- Rejects → Logs rejection reason in audit
- All actions attributed to user

**Phase 4: Revenue Impact (Optional)**
- Calculate financial value of missing time
- Show ROI of time tracking improvements
- Scale to firm-wide projections

**Phase 5: Audit History (Optional)**
- View complete audit trail
- Track all approvals and rejections
- Compliance and troubleshooting
