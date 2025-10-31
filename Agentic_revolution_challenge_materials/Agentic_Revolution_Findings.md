## Agentic Revolution — Findings and Notes

Last updated: 2025-10-31

This document captures the findings from the event materials in this repo, plus the steps I used to extract text from the provided presentation. Keep this file as the single-source reference for planning and prep.

---

## Source files
- `Agentic Revolution Challenge Session 3.txt` — event invitation and scheduling notes (3-hour sessions on Oct 31, Nov 7, Nov 14).
- `Agentic Revolution Challenges.pptx` — original presentation (legacy format). I also created:
  - `Agentic_Revolution_Challenges.pdf` — your converted PDF (provided by you).
  - `Agentic_Revolution_Challenges.pdf.txt` — text extracted with `pdftotext` (layout preserved).

Paths (workspace root):

```
/Users/arturoquiroga/TTU-AGENTIC-REVOLUTION-CHALLENGE/
  Agentic Revolution Challenge Session 3.txt
  Agentic Revolution Challenges.pptx
  Agentic Revolution Challenges.pdf
  Agentic_Revolution_Challenges.pdf.txt
  Agentic_Revolution_Challenges_extracted.txt    # intermediate attempt using strings
```

---

## How I extracted text (for reproducibility)

- I first attempted to parse the `.pptx` with `python-pptx`, but the file reported as a legacy Composite Document (old Mac PowerPoint format) and `python-pptx` could not open it.
- I then used `strings`/binary-dump attempts as a fallback which produced noisy output.
- You converted the presentation to PDF and placed it at `Agentic Revolution Challenges.pdf`. I used `pdftotext -layout` to extract clean, slide-preserving text:

```bash
/opt/homebrew/bin/pdftotext -layout 'Agentic Revolution Challenges.pdf' 'Agentic_Revolution_Challenges.pdf.txt'
```

If text extraction from the PDF ever fails (slides are images), use OCR (e.g., `tesseract`) on the PDF pages or convert slides to images first.

---

## Key takeaways from the materials

- Event format: 3-hour workshop; kickoff, scenario overview, ~2-hour team breakouts, readouts, wrap. Readouts are short (3–5 minutes).
- Deliverables common across scenarios:
  - Short presentation targeted to C-suite and technical audiences.
  - Architecture diagram or solution mapping.
  - A demo/script or conceptual prototype showing agentic behaviors (reasoning, tool use, proactive assistance).
  - README or summary slide listing AI tools used, limitations, and ethics considerations.
- Recommended use of Microsoft/Azure AI tooling (Azure OpenAI, Semantic Kernel, Copilot Studio, Azure Cognitive Services). Sample artifacts suggested include IaC for migrations (Bicep/Terraform) and Spring Petclinic sample for modernization demos.

---

## Challenges enumerated in the deck (summaries)

1) Agentic migration & modernization — Manufacturing customer
   - Problem: Large manufacturing customer with legacy ERP, CRM and on-prem datacenters needs migration and modernization.
   - Deliverables: Migration plan, architecture diagram, migrate vs modernize rationale, security & roadmap, sample IaC or sample app modernization (Spring Petclinic recommended).

2) Contoso Consulting Group (CCG) — Time & Expense reporting (Agentic AI)
   - Problem: Manual time entry, missing travel, misclassified expenses, manager reconciliation overhead.
   - Focus (pick one): Context Awareness (detect missing travel/time), Proactive Suggestions, Conversational Interface.
   - Deliverables: Concept diagram, demo/mock interaction or working prototype, README listing AI tools used. Demonstrate agentic behaviors.

3) Contoso Coffee & Tea — Reinvent café experience with AI
   - Problem: Low engagement, generic mobile experience, underutilized feedback.
   - Goal: Design new mobile/web feature to boost engagement and personalization.
   - Deliverables: Prototype or walkthrough, architecture, demo, documentation including ethics/limitations.

4) Additional functional-area examples and templates included in the deck (customer service, sales, finance, marketing, HR, legal, IT) — useful for inspiration and alternate ideas.

---

## Recommendations (short)

- If your team is small (1–3) and you want a high chance to deliver a clean demo: pick Contoso CCG (Time & Expense). Narrow scope to one feature (e.g., calendar-based missing time detection) and produce a simple LLM-based script or slide-driven mock.
- If your team has cloud/infrastructure and backend developers and you want to show depth: pick the Manufacturing migration/modernization — produce a clear migration plan, architecture, and one IaC snippet or modernization example (use Spring Petclinic as a demonstrator).

---

## Quick prep checklist (for the 2-hour breakout)

- Roles: Presenter (1), Demo/Code (1), Architect/Diagram (1), Slides/Notes (1) — assign before the session.
- 0–10 min: Scope & roles. Choose single sub-feature to implement and define acceptance for the readout.
- 10–30 min: Draft 1-slide elevator pitch + 1-slide architecture/approach.
- 30–90 min: Build core demo or slide-based mock (keep it deterministic). If using external APIs, prepare a mocked fallback.
- 90–110 min: Finalize readout slides (3 slides recommended: Problem, Design/Architecture, Demo & Next steps).
- 110–120 min: Rehearse 3–5 min readout and finalize README/one-slide summary listing tools and ethical considerations.

---

## Next steps I can do for you (choose any)

- Generate a 3-slide readout template prefilled for your chosen challenge.
- Create a runnable Python prototype (CCG calendar-based missing time detector) with sample input and a mock Azure OpenAI call.
- Produce a minimal IaC file (Bicep/Terraform) and README scaffold for the migration scenario.

Tell me which artifact you want first and the team composition (roles/skills). I will create the chosen artifact and update the task list.

---

## References / commands used during extraction

- `pdftotext -layout 'Agentic Revolution Challenges.pdf' 'Agentic_Revolution_Challenges.pdf.txt'` — produced the readable slide text used to make these notes.
- Workspace files: see the list in the "Source files" section above.

---

Agentic Revolution — compiled by your assistant for prep and delivery notes.
