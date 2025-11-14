# Data Design Decision: JSON Files for POC

## Why JSON Files?

This POC uses static JSON files for calendar and timesheet data instead of live API integrations.

### Rationale

**1. Focus on AI Agent Capabilities**
- Demonstrate multi-agent orchestration
- Showcase intelligent reasoning about billability
- Highlight cross-referencing logic
- Prove approval workflow functionality

**2. Demo Portability**
- No API keys or external credentials required
- Works offline at presentations
- Fast and predictable for live demos
- Easy to version control and share

**3. Rapid Iteration**
- Quickly add new consultants with different scenarios
- Test edge cases (missing travel, complete entries, varied patterns)
- Control demo narrative with curated data
- 5 consultants with 53 calendar events created in hours

**4. Workshop Requirements**
- Scenario mentioned calendar and timesheet systems
- Did NOT mandate specific data sources
- JSON approach fulfills functional requirements

## Production Integration Plan

### Phase 2: Real Data Sources (2-4 weeks)

**Calendar Data:**
- Microsoft Graph API for Outlook/Teams calendars
- Real-time event retrieval
- Attendee information and meeting details

**Timesheet Data:**
- ERP system integration (SAP, Workday, NetSuite)
- REST APIs for timesheet entries
- Write-back capabilities for approved entries

**Authentication:**
- Azure Active Directory (Entra ID)
- OAuth 2.0 with proper scopes
- Role-based access control

## Current Data Structure

### calendar_sample.json
- 53 events across 5 consultants
- Nov 13-23, 2025 date range
- Includes: client meetings, travel (flights/drives), internal meetings
- Categories: Billable, Travel, Client Meeting, Internal

### timesheet_sample.json
- Array of 5 user objects
- Each with partial entries (demonstrating missing time)
- Fields: id, date, start, end, duration_hours, task, project, billable

### audit_log.json
- Tracks all approval/rejection actions
- Immutable add-only log
- Fields: timestamp, action, user, entry_data, approved_by

## Benefits for TTU Demo

✅ **Consistent data** - Same results every time  
✅ **Rich scenarios** - Multiple consultant patterns  
✅ **No dependencies** - Internet/API failures won't break demo  
✅ **Fast execution** - No network latency  
✅ **Easy troubleshooting** - Static data simplifies debugging  

## Trade-offs

❌ Not "live" data (acceptable for POC)  
❌ Manual updates required (Phase 2 solves this)  
❌ Single-user modification (audit log is local)  

## Conclusion

JSON files were the **optimal choice for a time-constrained POC** that needed to demonstrate AI agent intelligence without the complexity of enterprise integrations. The approach successfully showcases the solution's value proposition while maintaining a clear path to production with real data sources.
