# Week 2 Progress Report

**Project:** RiskRadar AI - Fraud Transaction Investigation Assistant
**Capstone Theme:** IIT Roorkee AIOps Capstone, Theme 13
**Status:** Week 2 Day 4 complete
**Primary Goal:** Build a working fraud investigation assistant with policy-grounded evidence retrieval, agentic workflow orchestration, explainable recommendations, human decision capture, and an analyst-facing Streamlit dashboard.

---

## Executive Summary

Week 2 converted the Week 1 foundation into a working investigation workflow. The system now generates fraud alerts from synthetic transaction data, runs a parallel LangGraph investigation, retrieves policy evidence through a FAISS-backed RAG pipeline, produces explainable risk reasoning, recommends analyst action, and records human decisions for audit and future evaluation.

The current demo flow is:

```text
Synthetic transactions
      -> generated alert queue
      -> selected alert
      -> parallel LangGraph investigation
      -> risk reasoning + policy evidence + recommendation
      -> analyst decision
      -> feedback log
```

---

## Day 1: Policy RAG Pipeline

### Completed

- Built the policy retrieval layer for fraud investigation support.
- Loaded policy files from `data/policies/`.
- Added document loading and text chunking for the four fraud policy documents.
- Created a FAISS vector index for similarity search.
- Added policy-context retrieval by triggered policy name.
- Returned source document names with retrieved context for auditability.

### Key Files

- `src/rag/rag_pipeline.py`
- `data/policies/High_Value_Transaction_Policy.txt`
- `data/policies/Velocity_and_Burst_Detection_Policy.txt`
- `data/policies/Geographic_Anomaly_Policy.txt`
- `data/policies/Device_and_Payment_Instrument_Policy.txt`

### Outcome

The project can retrieve relevant policy evidence for triggered fraud indicators and surface the source policy documents in investigation output.

---

## Day 2: Fraud Risk Engine and LangGraph Workflow

### Completed

- Implemented deterministic fraud risk scoring.
- Mapped alert rules to policy names.
- Added weighted policy scoring:
  - High Value Transaction: 30
  - Geographic Anomaly: 25
  - Velocity and Burst Detection: 25
  - Device and Payment Instrument: 20
- Added risk-level classification:
  - `HIGH` for score >= 70
  - `MEDIUM` for score >= 20
  - `LOW` otherwise
- Built the initial LangGraph investigation workflow.
- Added investigation output fields for risk score, triggered policies, reasoning, summary, recommendation, action reason, and sources.
- Added scenario tests for high, medium, and low risk cases.

### Key Files

- `src/fraud/risk_engine.py`
- `src/fraud/models.py`
- `src/fraud/service.py`
- `src/graph/state.py`
- `src/graph/nodes.py`
- `src/graph/workflow.py`
- `src/tests/test_scenarios.py`
- `src/tests/sample_alerts.py`

### Outcome

The system can classify fraud risk, explain which policies were triggered, retrieve supporting policy sources, and produce an action recommendation.

---

## Day 3: Alert Queue and Streamlit Dashboard

### Completed

- Added alert generation from synthetic transaction data.
- Added queue-priority assignment based on triggered rule count.
- Added an alert adapter to convert generated alerts into workflow-ready fraud alerts.
- Built a Streamlit alert queue for analysts.
- Added selected-alert overview with transaction, customer, amount, queue priority, location, and triggered rules.
- Added investigation execution from the selected alert.
- Displayed workflow result fields in the UI:
  - Workflow risk
  - Recommendation
  - Triggered policies
  - Risk reasoning
  - Investigation summary
  - Parallel agent trace
  - Policy sources

### Key Files

- `src/fraud/alert_generator.py`
- `src/fraud/alert_adapter.py`
- `src/fraud/alert_models.py`
- `streamlit_app/app.py`
- `src/tests/test_alert_generator.py`
- `src/tests/test_alert_queue.py`

### Outcome

Analysts can select generated fraud alerts from the dashboard and run a structured investigation without using the command line.

---

## Day 4: Parallel Workflow, Human Approval, Error Handling, and UI Polish

### Completed

- Reworked the LangGraph flow into a real fan-out/fan-in parallel workflow:
  - Alert intake
  - Risk scoring analyst
  - Policy evidence analyst
  - Behavioral pattern analyst
  - Evidence fusion
  - Recommendation
  - Human decision pending
- Added human-in-the-loop analyst decision capture in Streamlit.
- Added analyst decision options:
  - `Approve`
  - `Monitor`
  - `Escalate`
- Added visual selected-state feedback for analyst decision buttons.
- Added optional analyst note / override reason for audit context.
- Added feedback logging to `data/feedback_log.csv`.
- Updated feedback fields to use `queue_priority` instead of `alert_severity`.
- Normalized queue-priority values as:
  - `HIGH_PRIORITY`
  - `MEDIUM_PRIORITY`
  - `LOW_PRIORITY`
- Added feedback fields for transaction, customer, queue priority, workflow risk, system recommendation, analyst decision, analyst note, triggered rules, triggered policies, and sources.
- Added a read-only Decision History view from `data/feedback_log.csv`.
- Removed handled transaction IDs from the active alert queue after analyst decisions are saved.
- Added Streamlit error handling for:
  - Alert generation failure
  - Empty alert queue
  - Workflow failure
  - Missing result fields
  - RAG retrieval issues
  - Feedback save failure
- Fixed stale investigation state so previous reports clear after feedback save or alert selection changes.
- Improved UI wording so queue priority and workflow risk are not confused.
- Added optional Gemini-assisted summary generation behind `USE_LLM_SUMMARY=true`.
- Kept deterministic summary generation as the default path for free-tier quota safety.
- Improved Streamlit layout for demo screenshots with alert metrics, cleaner alert overview, result metrics, section dividers, and a clearer Parallel Agent Trace section.
- Added `src/tests/test_day4_e2e.py` for light end-to-end validation.

### Key Files

- `src/graph/workflow.py`
- `src/graph/nodes.py`
- `src/utils/feedback_logger.py`
- `streamlit_app/app.py`
- `src/tests/test_day4_e2e.py`
- `data/feedback_log.csv`

### Outcome

The app now demonstrates an end-to-end analyst workflow: generated alert queue, parallel fraud investigation, policy evidence, recommendation, analyst decision, note capture, feedback logging, handled-alert removal, and Decision History.

---

## Current LangGraph Workflow

```text
alert_intake
      ├── risk_scoring
      ├── policy_evidence
      └── behavioral_pattern
              ↓
       evidence_fusion
              ↓
       recommendation
              ↓
            END
```

### Node Responsibilities

- `alert_intake`: starts the shared investigation state and initializes the agent trace.
- `risk_scoring`: maps triggered rules to weighted policy risk and classifies workflow risk.
- `policy_evidence`: retrieves relevant policy context and source documents.
- `behavioral_pattern`: adds deterministic findings about amount, device, velocity, and location.
- `evidence_fusion`: merges risk, evidence, and behavior into reasoning and investigation actions.
- `recommendation`: generates `ESCALATE`, `MONITOR`, or `APPROVE`.

### Optional LLM Mode

- Default: `USE_LLM_SUMMARY=false`
- Final-demo option: set `USE_LLM_SUMMARY=true`
- Model default: `GEMINI_MODEL=gemini-2.5-flash`
- If Gemini quota, API, or response parsing fails, the workflow automatically uses deterministic reasoning and summary output.

---

## Verification and Test Commands

### Full Health Check

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

### Latest Health Check Result

- `py_compile`: passed.
- `test_alert_generator`: passed and generated 78 alerts.
- `test_alert_queue`: passed.
- `test_risk_engine`: passed.
- `test_langgraph`: passed.
- `test_day4_e2e`: passed, including feedback logging.
- `test_scenarios`: passed.
- `test_investigator`: passed.
- `test_models.py`: passed when run with `riskradar_env/bin/python`.

### Environment Notes

- Running `test_models.py` with the default Anaconda `python` fails because that environment does not have `google.generativeai` installed.
- Running `python -m pytest src/tests -q` exits with code 5 because the current files are script-style tests, not pytest-collected test functions.
- Test runs may show LangGraph, LangChain, TensorFlow, NumPy, or Google Python 3.9 deprecation warnings. These warnings did not block the current app flow.

---

## Demo Notes

### Recommended Demo Path

1. Start the app:

```bash
streamlit run streamlit_app/app.py
```

2. Show the alert queue metrics:
   - Total Alerts
   - `HIGH_PRIORITY`
   - `MEDIUM_PRIORITY`
   - `LOW_PRIORITY`

3. Select a high-priority alert from the sidebar.
4. Walk through the Alert Overview:
   - Transaction ID
   - Customer ID
   - Amount
   - Queue Priority
   - Location
   - Triggered Rules
5. Click `Run Investigation`.
6. Show Investigation Result:
   - Workflow Risk
   - Recommendation
   - Queue Priority
7. Explain Risk Reasoning and Triggered Policies.
8. Show Investigation Summary and recommended review actions.
9. Show Parallel Agent Trace to demonstrate the multi-agent workflow.
10. Show Sources to demonstrate policy-grounded evidence.
11. Choose an analyst decision:
    - Approve
    - Monitor
    - Escalate
12. Add an analyst note.
13. Save the analyst decision and confirm feedback logging.
14. Show Decision History and confirm the handled transaction is removed from the active queue.

### Screenshot Checklist

- Alert queue with top metrics visible.
- Sidebar alert selection with priority labels.
- Alert Overview before investigation.
- Investigation Result after running a high-priority alert.
- Risk Reasoning section.
- Triggered Policies section.
- Investigation Summary section.
- Parallel Agent Trace section.
- Sources section.
- Analyst Decision section with selected button state.
- Feedback saved confirmation.
- Decision History table with recently handled alerts.
- Feedback log CSV showing `queue_priority` and analyst decision fields.

### Demo Talking Points

- Queue priority is the alert queue label derived from triggered rule count.
- Workflow risk is the investigation result derived from weighted policy risk.
- The system intentionally displays both values because queue triage and investigation scoring are related but not identical.
- Policy sources make recommendations auditable.
- The analyst can override or confirm the system recommendation.
- Feedback logging creates the base for future evaluation and continuous improvement.
- Decision History shows handled alerts and keeps the active queue focused on unresolved work.

---

## RFP Alignment

| RFP / Capstone Need | Week 2 Implementation |
| --- | --- |
| Fraud alert investigation assistant | Streamlit dashboard and workflow-driven investigation report |
| Explainable fraud reasoning | Risk reasoning, investigation summary, triggered policies, and action reason |
| Risk scoring | Weighted policy risk engine and workflow risk classification |
| Policy-grounded evidence | FAISS-backed RAG retrieval from fraud policy documents |
| LLM support | Optional Gemini-assisted summary generation with deterministic fallback |
| Agentic workflow | LangGraph orchestration with parallel analyst branches |
| Human approval / review | Analyst decision buttons, selected-state feedback, notes, and save action |
| Auditability | Policy sources, agent trace, queue priority, workflow risk, and feedback log |
| Dashboard workflow | Active alert queue, selected alert details, investigation result, handled-alert removal, Decision History, and feedback capture |
| Error handling | UI handling for generation, workflow, retrieval, missing fields, and feedback failures |
| Demo readiness | Clear UI labels, screenshot-ready sections, and end-to-end E2E test |

---

## Current Limitations

- Feedback is stored in a CSV file, not a database.
- Tests are script-style and not yet structured as pytest assertions across the full suite.
- Historical case retrieval is not yet implemented.
- Investigation report export is not yet implemented.
- Workflow visualization is not yet implemented in the UI.
- Some dependency warnings remain due to Python 3.9 and package deprecations.

---

## Recommended Next Steps

1. Continue Week 3 tracking in `docs/week3_progress.md`.
2. Add an evaluation harness for recommendation accuracy and evidence coverage if time allows.
3. Add investigation report export for final report/demo use if time allows.
4. Convert script-style tests into pytest-compatible tests if time allows.
5. Use the captured screenshots in `docs/screenshots/week2_demo/` for the report and presentation.
6. Clean dependency/environment notes so the demo setup is easier to reproduce.
