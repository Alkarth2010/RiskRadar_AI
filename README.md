# RiskRadar AI

**AI-Powered Fraud Transaction Investigation Assistant**

**IIT Roorkee AIOps Capstone Project — Theme 13**

---

## Project Overview

RiskRadar AI is an intelligent agentic system that assists fraud analysts in investigating suspicious bank transactions in real time. Built with LangGraph and LangChain, it combines multi-agent reasoning, policy-grounded RAG retrieval, and explainable recommendations inside an interactive Streamlit interface.

The system aims to reduce investigation time while improving consistency, auditability, and decision quality for fraud alerts.

---

## Repository Structure

```
RiskRadar_AI/
├── data/
│   ├── synthetic/
│   │   └── transactions.csv          # 200 bank transactions (26 fraud)
│   └── policies/
│       ├── High_Value_Transaction_Policy.txt
│       ├── Velocity_and_Burst_Detection_Policy.txt
│       ├── Geographic_Anomaly_Policy.txt
│       └── Device_and_Payment_Instrument_Policy.txt
├── src/
│   ├── fraud/                        # Risk engine, alert models, investigation service
│   ├── graph/                        # Parallel LangGraph workflow and nodes
│   ├── rag/                          # Policy RAG + FAISS
│   ├── tests/                        # Scenario, workflow, alert, and E2E tests
│   └── utils/                        # Data loaders, helpers
├── streamlit_app/                    # Analyst alert queue and investigation UI
├── docs/
│   ├── week2_progress.md
│   └── architecture.md
├── notebooks/                        # EDA and prototyping
├── README.md
├── requirements.txt
├── .env
└── Week1_Progress.md
```

---

## Quick Start

### 1. Setup

```bash
cd /Users/karthikal/RiskRadar_AI

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and set GOOGLE_API_KEY for Gemini embeddings
```

### 2. Explore the Data

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/synthetic/transactions.csv')
print('Total transactions:', len(df))
print('Fraud cases:', df['is_fraud'].sum())
print(df[df['is_fraud']==1][['transaction_id','amount','fraud_type']].head())
"
```

### 3. Run Streamlit App

```bash
streamlit run streamlit_app/app.py
```

---

## Current Capabilities

- Generates fraud alerts from synthetic transaction data.
- Runs a parallel LangGraph investigation workflow.
- Scores risk using triggered policies and weighted rules.
- Retrieves policy evidence with LangChain, local sentence-transformer embeddings, and FAISS.
- Produces risk reasoning, investigation actions, and explainable recommendations.
- Captures human analyst decisions and notes.
- Logs feedback to `data/feedback_log.csv` for audit and future evaluation.
- Removes handled transactions from the active queue and shows them in Decision History.
- Displays alert metrics, agent trace, policy sources, investigation output, and handled decisions in Streamlit.

---

## Key Technologies

- **Agent Orchestration**: LangGraph
- **RAG Framework**: LangChain
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS
- **UI**: Streamlit + Plotly
- **Data**: pandas

---

## Next Steps

- Add evaluation harness
- Add investigation report export
- Add workflow visualization
- Add historical case retrieval

---

**Course**: AIOps Capstone (IIT Roorkee)  
**Theme**: 13 — AI Fraud Transaction Investigation Assistant  
**Project**: RiskRadar AI

For setup issues, contact the project team.
