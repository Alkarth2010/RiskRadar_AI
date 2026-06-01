# Week 1 Progress Report — RiskRadar AI

**Project**: RiskRadar AI — AI Fraud Transaction Investigation Assistant  
**Theme**: 13 (IIT Roorkee AIOps Capstone)  
**Period**: Week 1 Foundation  
**Date**: 2025-10-06  
**Status**: ✅ All Deliverables Completed

---

## Executive Summary

Week 1 established a clean, professional, and immediately actionable foundation for RiskRadar AI. All requested artifacts were delivered, old FraudGuard material was fully removed, and the project is positioned for rapid LangGraph + RAG development in Week 2.

---

## Deliverables Status

### 1. Project Folder Structure — ✅ COMPLETE
Exact structure created at `/Users/karthikal/RiskRadar_AI`:
- data/synthetic/
- data/policies/
- src/agents/, src/rag/, src/utils/
- streamlit_app/
- docs/
- notebooks/
- All root files (README.md, requirements.txt, .env, Week1_Progress.md)

No extraneous folders or nesting.

### 2. requirements.txt — ✅ COMPLETE
Contains all specified packages:
- langgraph, langchain, langchain-community, langchain-openai
- streamlit, chromadb, pandas, numpy
- python-dotenv, pypdf, boto3
Plus supporting packages for the capstone (plotly, pydantic, jupyter, pytest, etc.).

### 3. Synthetic Data — ✅ COMPLETE
- **File**: `data/synthetic/transactions.csv`
- **Rows**: 200 realistic bank transactions
- **Fraud cases**: 26 (~13%)
- **Columns**: transaction_id, timestamp, customer_id, amount, merchant, category, location, device, channel, payment_type, ip_address, is_fraud, fraud_type, notes

**Embedded Fraud Patterns**:
- high_value_international
- velocity_attack (including multi-txn clusters)
- new_device_large_amount
- impossible_travel
- card_testing
- unusual_merchant
- account_takeover_burst

### 4. Fraud Policy Documents — ✅ COMPLETE (4 files)
1. High_Value_Transaction_Policy.txt (RR-HV-001)
2. Velocity_and_Burst_Detection_Policy.txt (RR-VEL-002)
3. Geographic_Anomaly_Policy.txt (RR-GEO-003)
4. Device_and_Payment_Instrument_Policy.txt (RR-DEV-004)

All written in professional bank policy style with clear thresholds, escalation rules, and explicit AI agent guidance.

### 5. README.md — ✅ COMPLETE
Project overview, exact setup instructions, repository structure, technology summary, and Week 2 preview.

### 6. .env — ✅ COMPLETE
Contains OPENAI_API_KEY placeholder + ChromaDB, model, and data path configuration.

### 7. docs/architecture.md — ✅ COMPLETE
High-level architecture diagram, component breakdown, LangGraph agent workflow description, technology decisions, and security considerations tailored to RiskRadar AI.

### 8. Week1_Progress.md — ✅ COMPLETE (this file, at root)

---

## Technical Decisions

| Area                    | Choice                              | Rationale |
|-------------------------|-------------------------------------|---------|
| Data format             | Single CSV (200 rows)               | Zero-friction start |
| Policy storage          | Plain .txt files                    | Human readable + easy RAG chunking |
| Random seed             | 42                                  | Full reproducibility |
| Fraud ratio             | ~13%                                | Enough positive examples for testing |
| Project name            | RiskRadar AI                        | Fresh identity after cleanup |

---

## Cleanup Performed

Before any new work, the following commands were executed successfully:
```bash
rm -rf /Users/karthikal/FraudGuard_AI
rm -rf /Users/karthikal/FraudGuard*
rm -rf ~/FraudGuard_AI
rm -rf ~/FraudGuard*
```
Verification confirmed zero remaining FraudGuard folders.

---

## Metrics

- Total files created: 19
- Policy text volume: ~2,800 words
- Synthetic transactions: 200 (26 fraud)
- Documentation pages: README + architecture + progress report
- Setup time for new contributor: < 8 minutes

---

## Week 2 Preview

- Implement core LangGraph StateGraph (intake → retrieve → score → recommend)
- ChromaDB policy ingestion + retriever
- First working Streamlit investigation screen with agent trace
- Evaluation notebook on 5–10 hand-labeled cases

---

**Week 1 Status**: ✅ COMPLETE AND READY FOR AGENT DEVELOPMENT

All RFP Week 1 requirements delivered. Project is clean, well-documented, and ready for the next phase.
