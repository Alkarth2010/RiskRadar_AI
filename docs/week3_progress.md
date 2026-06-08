# Week 3 Progress Report

**Project:** RiskRadar AI - Fraud Transaction Investigation Assistant
**Capstone Theme:** IIT Roorkee AIOps Capstone, Theme 13
**RFP Week:** Week 3, 8 June 2026 to 14 June 2026
**Status:** Week 3 core implementation complete; Week 4 deployment and final submission work pending
**Primary Goal:** Complete multi-agent integration, workflow testing, and the analyst-facing dashboard needed for the final demo.

---

## Executive Summary

Week 3 focused on converting the Week 2 prototype into a clearer end-to-end demo workflow. The project now supports a generated alert queue, parallel agent investigation, policy-grounded evidence, recommendation output, human analyst decision capture, feedback logging, handled-alert removal, and a Decision History view in Streamlit.

The Week 3 demo flow is:

```text
Generated alert queue
      -> analyst selects alert
      -> parallel LangGraph investigation
      -> workflow risk + policy evidence + recommendation
      -> analyst decision and note
      -> feedback log
      -> handled alert removed from queue
      -> Decision History
```

---

## Completed Features

### Multi-Agent Workflow Integration

- Finalized the LangGraph investigation workflow using fan-out/fan-in orchestration.
- Kept specialist investigation steps separated into:
  - Risk scoring analyst
  - Policy evidence analyst
  - Behavioral pattern analyst
  - Evidence fusion
  - Recommendation
- Added trace output so the demo can show how the workflow moved through each step.
- Preserved deterministic workflow behavior for reliable testing and repeatable demos.

### RAG and Evidence Support

- Continued using the FAISS-backed RAG pipeline for policy retrieval.
- Returned policy source names with the investigation result for auditability.
- Kept the workflow grounded in the four fraud policy documents:
  - High Value Transaction Policy
  - Velocity and Burst Detection Policy
  - Geographic Anomaly Policy
  - Device and Payment Instrument Policy

### Analyst Dashboard Improvements

- Enhanced the Streamlit alert queue and investigation result layout for demo readability.
- Clarified the difference between queue priority and workflow risk:
  - Queue priority: `HIGH_PRIORITY`, `MEDIUM_PRIORITY`, `LOW_PRIORITY`
  - Workflow risk: `HIGH`, `MEDIUM`, `LOW`
- Added immediate selected-state feedback for analyst decision buttons.
- Added analyst note capture for decision context.
- Added feedback save handling with a clear error message if saving fails.

### Feedback Loop and Decision History

- Updated feedback logging to use `queue_priority` instead of the older `alert_severity` label.
- Added a read-only Decision History view in Streamlit.
- Removed handled transaction IDs from the active alert queue after the analyst saves a decision.
- Kept feedback fields useful for audit and final-report evidence:
  - Transaction ID
  - Customer ID
  - Queue priority
  - Workflow risk
  - System recommendation
  - Analyst decision
  - Analyst note
  - Triggered rules
  - Triggered policies
  - Policy sources

### Optional LLM Summary Mode

- Added Gemini-assisted summary generation behind a feature flag.
- Default setting remains `USE_LLM_SUMMARY=false` to protect free-tier quota and keep local tests stable.
- Verified the real LLM path once, then switched back to deterministic mode.
- Added fallback behavior so quota, API, or parsing failures do not break the workflow.

### Demo Evidence

- Captured the main Streamlit demo states in `docs/screenshots/week2_demo/`.
- Screenshot coverage includes:
  - Alert queue
  - Selected high-priority alert
  - Investigation running state
  - Investigation result overview
  - Risk reasoning and policy evidence
  - Investigation summary and trace
  - Sources and analyst decision controls
  - Selected decision state
  - Analyst note before save
  - Decision History

---

## RFP Alignment

| RFP Week 3 Expectation | Current Status | Evidence |
| --- | --- | --- |
| Multi-agent implementation | Complete | LangGraph workflow with specialist nodes and agent trace |
| Workflow integration | Complete | Alert queue connects to investigation workflow and feedback logging |
| Frontend/dashboard creation | Complete | Streamlit analyst dashboard with queue, investigation result, and Decision History |
| Workflow testing | Complete for current scope | Script-based health checks for alert generation, queue, risk engine, LangGraph, scenarios, and E2E flow |
| Human approval step | Complete | Analyst decision buttons and notes saved to feedback log |
| Error handling/retry | Partially complete | UI and workflow fallback handling added; broader retry strategy can be documented in final report |
| AWS deployment | Pending for Week 4 | EC2/S3 deployment proof still required by RFP |

---

## Key Files

- `streamlit_app/app.py`
- `src/graph/workflow.py`
- `src/graph/nodes.py`
- `src/graph/state.py`
- `src/rag/rag_pipeline.py`
- `src/fraud/alert_generator.py`
- `src/fraud/alert_adapter.py`
- `src/fraud/risk_engine.py`
- `src/utils/feedback_logger.py`
- `src/tests/test_day4_e2e.py`
- `docs/screenshots/week2_demo/`

---

## Verification and Test Commands

Use these commands for the Week 3 health check:

```bash
python -m py_compile streamlit_app/app.py src/graph/state.py src/graph/nodes.py src/graph/workflow.py src/fraud/*.py src/rag/*.py src/utils/*.py src/tests/*.py test_models.py fix_sqlite.py
python -m src.tests.test_alert_generator
python -m src.tests.test_alert_queue
python -m src.tests.test_risk_engine
python -m src.tests.test_langgraph
python -m src.tests.test_day4_e2e
python -m src.tests.test_scenarios
python -m src.tests.test_investigator
riskradar_env/bin/python test_models.py
```

Expected result:

- All script-style tests pass.
- `pytest` collection is not used yet because the current tests are runnable script modules.
- Known warnings from LangChain/LangGraph dependencies do not block the demo.

---

## Demo Notes

- Keep `USE_LLM_SUMMARY=false` for normal development and screenshots.
- Turn on `USE_LLM_SUMMARY=true` only if a final demo specifically needs a live LLM-generated summary.
- During the demo, start with a high-priority alert so the workflow visibly shows multiple triggered policies and richer reasoning.
- Save one analyst decision to show the alert moving out of the active queue and into Decision History.

---

## Week 4 Handoff

The project is ready to move into Week 4 tasks:

- Deploy the Streamlit dashboard on AWS EC2.
- Store deployment evidence or project artifacts in AWS S3 if required for submission proof.
- Capture deployment screenshots.
- Prepare final report using Week 1, Week 2, and Week 3 progress documents.
- Prepare final PPT and recorded presentation.
- Package source code, dataset, policy documents, screenshots, and deployment evidence for submission.
