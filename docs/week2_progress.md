# Week 2 Progress Notes

## Day 4: Human Approval, Parallel Workflow, Error Handling, UI Polish

### Completed

- Added human-in-the-loop analyst decision capture in the Streamlit investigation report.
- Added analyst decision options: `Approve`, `Monitor`, and `Escalate`.
- Added optional analyst note / override reason field for audit context.
- Added feedback logging to `data/feedback_log.csv`.
- Added feedback fields for transaction, customer, alert severity, system risk score, recommendation, analyst decision, note, triggered rules, triggered policies, and sources.
- Added basic Streamlit error handling for alert generation, empty alert queues, workflow failure, missing result keys, RAG retrieval issues, and feedback save failure.
- Fixed stale investigation state so previous reports clear after feedback save or alert selection changes.
- Added a real parallel LangGraph workflow:
  - Alert intake
  - Risk scoring analyst
  - Policy evidence analyst
  - Behavioral pattern analyst
  - Evidence fusion
  - Recommendation
  - Human decision pending
- Kept the existing frontend contract intact for risk score, recommendation, policies, summary, agent trace, and sources.
- Improved Streamlit UI for demo screenshots with alert metrics, cleaner alert overview, result metrics, section dividers, and a clearer Parallel Agent Trace section.
- Added `src/tests/test_day4_e2e.py` for light end-to-end validation.

### Verified

- Streamlit alert queue loads and investigations run from selected alerts.
- RAG sources appeared in the Streamlit UI during manual verification.
- Analyst decisions save successfully to the feedback log.
- Feedback save fallback message was manually verified.
- Stale investigation reports clear correctly after saving feedback and when switching alerts.
- Existing LangGraph test completed successfully.
- Day 4 E2E test completed successfully for HIGH, MEDIUM, and LOW alert examples.

### Test Commands

```bash
python -m py_compile streamlit_app/app.py src/graph/state.py src/graph/nodes.py src/graph/workflow.py src/tests/test_day4_e2e.py
python -m src.tests.test_alert_generator
python -m src.tests.test_langgraph
python -m src.tests.test_day4_e2e
streamlit run streamlit_app/app.py
```

### Notes

- Shell test runs currently show noisy NumPy optional dependency warnings from local package compatibility, but alert generation still completes.
- Shell test runs may show RAG fallback if `sentence_transformers` is missing in that Python environment.
- Streamlit manual testing confirmed policy sources were retrieved successfully.
- Alert severity and workflow risk score can differ because alert severity is based on number of triggered rules, while risk score is based on weighted policy risk.

### RFP Alignment

- Supports fraud explanation through risk reasoning and investigation summary.
- Supports risk scoring through the risk scoring analyst branch.
- Supports policy evidence through RAG-backed policy retrieval.
- Supports parallel fraud analysis through real LangGraph fan-out/fan-in branches.
- Supports human approval through analyst decision capture.
- Supports auditability through feedback logging.
- Supports dashboard workflow through the Streamlit alert queue and investigation report.
- Supports error handling for normal demo failure cases.
