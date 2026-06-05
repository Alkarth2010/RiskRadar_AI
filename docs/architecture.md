# RiskRadar AI — System Architecture & Workflow

**IIT Roorkee AIOps Capstone Project — Theme 13**
**Project:** RiskRadar AI – Fraud Transaction Investigation Assistant
**Version:** 1.1 (Week 2 Day 4)
**Last Updated:** June 2026

---

# 1. High-Level Architecture

```text
                    RiskRadar AI

┌────────────────────────────────────────────┐
│              Fraud Alert Input             │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          LangGraph Orchestrator            │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│              Alert Intake Node             │
│                                            │
│ • Alert normalization                      │
│ • Shared investigation state setup         │
│ • Agent trace initialization               │
└───────────────────┬────────────────────────┘
                    │
                    ├──────────────────────┬──────────────────────┐
                    ▼                      ▼                      ▼
┌────────────────────────────┐ ┌────────────────────────────┐ ┌────────────────────────────┐
│    Risk Scoring Analyst    │ │  Policy Evidence Analyst   │ │ Behavioral Pattern Analyst │
│                            │ │                            │ │                            │
│ • Triggered policies       │ │ • FAISS policy retrieval   │ │ • Amount pattern review    │
│ • Weighted risk scoring    │ │ • Gemini embeddings        │ │ • Device and velocity cues │
│ • Risk classification      │ │ • Evidence source capture  │ │ • Location review          │
└──────────────┬─────────────┘ └──────────────┬─────────────┘ └──────────────┬─────────────┘
               └──────────────────────────────┼──────────────────────────────┘
                                              ▼
┌────────────────────────────────────────────┐
│             Evidence Fusion Node           │
│                                            │
│ • Risk reasoning                           │
│ • Investigation summary                    │
│ • Review actions and policy source summary │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          Recommendation Node               │
│                                            │
│ • ESCALATE                                 │
│ • MONITOR                                  │
│ • APPROVE                                  │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│       Structured Investigation Output      │
└────────────────────────────────────────────┘
```

---

# 2. Current System Components

## 2.1 Fraud Alert Layer

Input to the system is a structured fraud alert.

Example:

```python
{
    "transaction_id": "TXN001",
    "amount": 250000,
    "country": "Russia",
    "new_device": True,
    "transactions_last_10min": 15
}
```

Validation is performed using Pydantic models.

---

## 2.2 Alert Intake

The alert intake node receives a structured alert and starts the shared
LangGraph investigation state. It also initializes the agent trace that is
displayed in the Streamlit investigation report.

---

## 2.3 Risk Scoring Analyst

The risk scoring analyst performs:

* Policy trigger detection
* Weighted risk scoring
* Risk classification

### Policy Triggers

| Policy                      | Condition                      |
| --------------------------- | ------------------------------ |
| High Value Transaction      | Amount > ₹100,000              |
| Geographic Anomaly          | High-risk country              |
| Velocity & Burst Detection  | >10 transactions in 10 minutes |
| Device & Payment Instrument | New device detected            |

### Policy Weights

| Policy                      | Weight |
| --------------------------- | ------ |
| High Value Transaction      | 30     |
| Geographic Anomaly          | 25     |
| Velocity & Burst Detection  | 25     |
| Device & Payment Instrument | 20     |

### Risk Levels

```text
3+ triggered policies → HIGH

Score >= 70 → HIGH

Score >= 20 → MEDIUM

Else → LOW
```

---

## 2.4 Policy Evidence Analyst

The policy evidence analyst provides policy-grounded investigation support.
It derives policy names from alert rules, retrieves matching policy context,
captures source documents for auditability, and falls back gracefully when
retrieval is unavailable.

### Policy Repository

```text
data/policies/

├── High_Value_Transaction_Policy.txt
├── Geographic_Anomaly_Policy.txt
├── Velocity_and_Burst_Detection_Policy.txt
└── Device_and_Payment_Instrument_Policy.txt
```

### Retrieval Pipeline

```text
Policy Files
      ↓
Document Loader
      ↓
Chunking
      ↓
Gemini Embeddings
      ↓
FAISS Vector Store
      ↓
Similarity Retrieval
      ↓
Policy Context
```

---

## 2.5 Behavioral Pattern Analyst

The behavioral pattern analyst adds deterministic context about the alert:

* Amount pattern
* New device indicator
* Velocity pattern
* Transaction country / location

---

## 2.6 Evidence Fusion Node

The evidence fusion node combines risk scoring, policy evidence, and
behavioral findings into the final investigation narrative.

* Generate risk reasoning
* Generate investigation summary
* Explain detected fraud indicators
* Include recommended manual review actions
* Reference the number of retrieved source documents when available

The current implementation uses deterministic fusion logic so tests and demos
do not depend on LLM quota availability.

---

## 2.7 Recommendation Engine

Produces final investigator action:

| Risk Level | Recommendation |
| ---------- | -------------- |
| HIGH       | ESCALATE       |
| MEDIUM     | MONITOR        |
| LOW        | APPROVE        |

Each recommendation includes an explanation based on triggered policies.

---

# 3. LangGraph Workflow

Current LangGraph StateGraph:

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

The workflow uses a real fan-out/fan-in pattern. Risk scoring, policy evidence,
and behavioral analysis run as parallel LangGraph branches after alert intake.
Their outputs merge at evidence fusion before the final recommendation is
generated.

---

# 4. Data Models

## FraudAlert

```python
FraudAlert
```

Fields:

* transaction_id
* amount
* country
* new_device
* transactions_last_10min
* merchant_category
* triggered_rules

---

## InvestigationResult

```python
InvestigationResult
```

Fields:

* risk_score
* risk_reasoning
* triggered_policies
* investigation_summary
* recommended_action
* action_reason
* sources
* error

## InvestigationState

```python
InvestigationState
```

Fields:

* alert
* risk_score
* risk_reasoning
* triggered_policies
* retrieved_context
* sources
* behavioral_findings
* investigation_summary
* recommended_action
* action_reason
* agent_trace
* error

---

# 5. Technology Stack

| Component              | Technology           |
| ---------------------- | -------------------- |
| Workflow Orchestration | LangGraph            |
| Embeddings             | Gemini Embedding 001 |
| Vector Database        | FAISS                |
| RAG Framework          | LangChain            |
| Data Validation        | Pydantic             |
| Data Processing        | Pandas               |
| UI                     | Streamlit            |
| Visualization          | Plotly               |
| Language               | Python 3.9           |

---

# 6. Testing Status

Validated scenarios:

### Scenario 1

High Value + High Risk Geography + Velocity + New Device

Result:

```text
HIGH
ESCALATE
```

### Scenario 2

New Device Only

Result:

```text
MEDIUM
MONITOR
```

### Scenario 3

Normal Transaction

Result:

```text
LOW
APPROVE
```

### Scenario 4

High Value + Geographic Anomaly

Result:

```text
MEDIUM
MONITOR
```

---

# 7. Current Project Status

## Week 2 Day 1

✅ RAG Pipeline Complete

* Policy loading
* Embeddings
* FAISS indexing
* Retrieval

## Week 2 Day 2

✅ Fraud Investigation Workflow Complete

* Risk Engine
* Policy Detection
* LangGraph Workflow
* Investigation Summary
* Recommendation Engine
* Scenario Testing

## Week 2 Day 3

✅ Alert Queue Workflow Complete

* Alert generation from synthetic transactions
* Queue-driven Streamlit investigation flow
* Alert adapter between generated alerts and workflow input
* Investigation report display

## Week 2 Day 4

✅ Parallel Workflow, Human Approval, and UI Polish Complete

* Parallel LangGraph branches for risk scoring, policy evidence, and behavioral analysis
* Evidence fusion node for final reasoning and investigation summary
* Human-in-the-loop analyst decisions: APPROVE, MONITOR, ESCALATE
* Analyst notes and feedback logging to `data/feedback_log.csv`
* Streamlit error handling for common demo failure cases
* Day 4 E2E validation for HIGH, MEDIUM, and LOW examples

---

# 8. Planned Enhancements

* Investigation Report Export
* Historical Case Retrieval
* Evaluation Harness
* LangGraph Workflow Visualization

---

**Status:** Week 2 Day 4 Complete – Working parallel LangGraph-based Fraud Investigation Assistant with Streamlit alert queue, policy evidence retrieval, human decision capture, and feedback logging.
