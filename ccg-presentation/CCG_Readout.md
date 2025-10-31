# Contoso Consulting Group (CCG) — Readout Template & Script

Prepared: 2025-10-31

Contents:
- 3-slide readout template (prefilled) for the CCG Time & Expense Agentic AI challenge
- 3-minute scripted walkthrough (timed) and presenter notes
- Quick demo runbook, tech stack suggestions, sample input and prompts

---

## Slide 1 — Title / Problem & Impact (30–45s)

Slide title: Contoso Consulting Group — Intelligent Time & Expense Assistant

Slide body (bullets):
- Problem: Manual time entry causes missed billable hours, travel is often omitted, and managers waste time reconciling inconsistent reports.
- Impact: Reduced billable accuracy, lost revenue, slow visibility into project utilization and compliance risk.
- Our focus (chosen feature): Context-aware detection of missing time/travel and proactive suggestion workflow.
- One-line value prop: Reduce lost billable time and manager reconciliation effort by proactively surfacing and suggesting missing entries.

Presenter notes (30–45s):
- Start: "Hi — we're Team X. In 90 seconds we'll show a tight, agentic concept that can reduce lost billable time and make consultant time entry effortless."
- Describe the core problem quickly: missed travel/time, manual entry, manager reconciliation.
- State the focus: we built a context-aware assistant that reasons over calendar+travel data and suggests missing entries.

Timing cue: 30–45 seconds. Move on promptly.

---

## Slide 2 — Solution Overview & Architecture (60–75s)

Slide title: Solution — Agentic Flow & Architecture

Slide body (diagram placeholders):
- Inputs: Calendar events, calendar metadata (location/time), timesheet entries (sample JSON), optional travel/expense receipts.
- Agentic Core: Azure OpenAI (reasoning), a small orchestration agent (Semantic Kernel or a scripted controller), connector modules (calendar, timesheet API mock), confirmation UI (chat/Teams/CLI).
- Outputs: Suggested time entries (with confidence), one-click confirm flows, audit trail for managers.
- Key agentic behaviors demonstrated: reasoning (identify gaps), tool use (call calendar and timesheet APIs), proactivity (push suggestions / reminders).

Presenter notes (60–75s):
- Explain the architecture diagram: data in → agent reasoning → suggestion generation → confirmation step that updates timesheet.
- Emphasize agentic behavior: the agent doesn't just answer prompts — it reasons over context, calls tools (calendar/timesheet), and proactively pushes suggestions.
- Mention tech used in the demo: Azure OpenAI (mocked in our demo), simple connector code (Python), and a short confirm flow.

Optional tech stack bullet (one-liner): Azure OpenAI + Semantic Kernel or a small Python-based agent + calendar connector + mock timesheet API.

---

## Slide 3 — Demo Summary, Impact, Next Steps & Ask (45–60s)

Slide title: Demo & Next Steps

Slide body (bullets):
- Demo: 60s mock walkthrough showing missing-time detection and a confirm flow (mocked API). Key observable: suggestion accuracy and one-click confirm.
- Impact metrics (expected): +X% reduction in missed billable time; -Y hours/week manager reconciliation (put placeholders and callouts).
- Next steps: pilot with 10 consultants, integrate real calendar + travel receipts, add compliance checks.
- Ask: Access to sample calendar data and a test timesheet sandbox for pilot.

Presenter notes (45–60s):
- Run the demo (or slide-based simulation) showing: 1) agent identifies two missing entries for a consultant, 2) agent proposes entries with confidence and rationale, 3) consultant confirms and entries are added to the timesheet (mock).
- Close with the business impact and a short call-to-action: pilot ask and what success looks like.

---

## 3-minute readout script (timed) — copy and practice

Total target: 3:00 minutes (180 seconds). Shorter is fine; practice to 2:30–3:00.

- 0:00–0:05  — "Hello, we are Team X." (intro)
- 0:05–0:35  — Slide 1: Problem & Impact (30s) — "Consultants miss travel/time; managers reconcile manually; lost billable hours and compliance risk. We focused on context-aware missing-time detection."
- 0:35–1:50  — Slide 2: Solution & Architecture (75s) — "Our agent ingests calendar and timesheet data, uses LLM reasoning to detect gaps, and calls tools to propose entries. Here's the flow..." (point to architecture). Briefly call out agentic behaviors: reasoning, tool use, proactivity.
- 1:50–2:50  — Slide 3: Demo & Next Steps (60s) — Run or narrate the demo: show the suggestion, show the confirm action, note the audit trail. Then present impact numbers and next steps.
- 2:50–3:00  — Closing (10s) — "Thanks — we'd love to pilot with a small group and test integration with real calendar/timesheet data."

Presenter delivery notes:
- Keep each slide to one main idea.
- Use exact numbers only if you can justify them; otherwise use ranges (e.g., "we expect a measurable reduction in missed time by 10–30% in a pilot").
- If the demo is mocked, be explicit: "This demo is a deterministic mock but represents the agentic flow we would wire to real APIs." Judges appreciate honesty.

---

## Demo runbook (quick) — what to show and how to keep it robust

Demo length: 60s (max). Prepare a mocked but deterministic demo to avoid network flakiness.

1) Prepare sample inputs (calendar JSON and sample timesheet entries). Example minimal calendar entry:

```json
// calendar_sample.json
[
  {"title":"Client Onsite - Contoso Corp","start":"2025-10-30T09:00:00-05:00","end":"2025-10-30T12:00:00-05:00","location":"Contoso HQ","attendees":["alice@contoso.com"]},
  {"title":"Flight to Client","start":"2025-10-30T07:00:00-05:00","end":"2025-10-30T09:00:00-05:00","location":"JFK->LGA","attendees":["alice@contoso.com"]}
]
```

2) Sample timesheet entries (missing travel blocks):

```json
// timesheet_sample.json
{
  "user":"alice@contoso.com",
  "entries":[{"date":"2025-10-30","hours":3,"task":"Client Work - Contoso"}]
}
```

3) Demo script (mocked):
- Run small script that: 1) loads calendar and timesheet samples; 2) calls a local mock of Azure OpenAI (or a mocked function returning structured reasoning); 3) prints suggested entries (e.g., travel time 2 hours) and the LLM rationale; 4) simulate confirmation and print updated timesheet.

4) Fallback plan: If live LLM call fails or keys are unavailable, present a short recorded console output or a slide-based screenshot showing the before/after.

---

## Suggested minimal code/prompt (for your demo)

Prompt pattern (short):

"Given this consultant's calendar events and existing timesheet entries, identify likely missing time entries and produce suggested entries with start/end, duration, task label, and a short rationale for each suggestion. Return JSON array with fields: start,end,duration,task,rationale,confidence."

Example small deterministic mock response (what to show in demo):

```json
[
  {"start":"2025-10-30T07:00:00-05:00","end":"2025-10-30T09:00:00-05:00","duration":2.0,"task":"Travel - Contoso Onsite","rationale":"Calendar shows flight during this period; no timesheet entry exists.","confidence":0.92}
]
```

Implementation note: use a short system prompt to force structured JSON output and a few-shot pattern with 2 examples so output is deterministic.

---

## Ethics & short risk notes (one-slide talking points)

- Data privacy: only read calendar and timesheet data with explicit consent and use least-privilege connectors.
- False positives: show rationale with each suggestion and require user confirmation to avoid auto-time injection.
- Auditability: keep an audit log of suggestions, confirmations, and who approved them.

---

## Files created and where to put them

- Put any demo scripts and sample inputs in a folder `ccg-demo/` at repo root. Example files:
  - `ccg-demo/calendar_sample.json`
  - `ccg-demo/timesheet_sample.json`
  - `ccg-demo/mock_agent.py` (simple script to produce the deterministic output above)

If you'd like, I can scaffold `ccg-demo/` with the sample files and a runnable `mock_agent.py` that prints the mock JSON and simulates the confirm flow. Tell me and I'll create it next.

---

End of template and script. Practice the 3-minute run twice and aim to finish in 2:30–3:00.
