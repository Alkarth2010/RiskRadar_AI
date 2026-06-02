# RiskRadar AI — System Architecture & Workflow

**IIT Roorkee AIOps Capstone Project — Theme 13**
**Project:** RiskRadar AI – Fraud Transaction Investigation Assistant
**Version:** 1.0 (Week 2 Complete)
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
│          Risk Analysis Node                │
│                                            │
│ • Policy Trigger Detection                 │
│ • Weighted Risk Scoring                    │
│ • Risk Classification                      │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│          Policy Retrieval Node             │
│                                            │
│ • FAISS Vector Search                      │
│ • Gemini Embeddings                        │
│ • Policy Context Retrieval                 │
└───────────────────┬────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────┐
│         Investigation Summary Node         │
│                                            │
│ • Gemini 2.5 Flash                         │
│ • Risk Reasoning                           │
│ • Investigation Summary                    │
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

## 2.2 Risk Analysis Engine

The Risk Analysis Node performs:

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

## 2.3 RAG Subsystem

The RAG subsystem provides policy-grounded investigation support.

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

## 2.4 Investigation Summary Node

Uses:

```text
Gemini 2.5 Flash
```

Responsibilities:

* Generate risk reasoning
* Generate investigation summary
* Explain detected fraud indicators

Fallback handling is implemented for quota exhaustion or model failures.

---

## 2.5 Recommendation Engine

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
risk_analysis
      ↓
retrieval
      ↓
summary
      ↓
recommendation
      ↓
END
```

Each node updates a shared investigation state object.

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

---

# 5. Technology Stack

| Component              | Technology           |
| ---------------------- | -------------------- |
| Workflow Orchestration | LangGraph            |
| LLM                    | Gemini 2.5 Flash     |
| Embeddings             | Gemini Embedding 001 |
| Vector Database        | FAISS                |
| RAG Framework          | LangChain            |
| Data Validation        | Pydantic             |
| Data Processing        | Pandas               |
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

---

# 8. Planned Enhancements

* Streamlit Investigation Dashboard
* LangGraph Workflow Visualization
* Investigation Report Export
* Historical Case Retrieval
* Analyst Feedback Loop

---

**Status:** Week 2 Complete – Working LangGraph-based Fraud Investigation Assistant
