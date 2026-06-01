# RiskRadar AI

**AI-Powered Fraud Transaction Investigation Assistant**

**IIT Roorkee AIOps Capstone Project — Theme 13**

---

## Project Overview

RiskRadar AI is an intelligent agentic system that assists fraud analysts in investigating suspicious bank transactions in real time. Built with LangGraph and LangChain, it combines multi-agent reasoning, policy-grounded RAG retrieval, and explainable recommendations inside an interactive Streamlit interface.

The system aims to reduce investigation time while improving consistency, auditability, and decision quality for fraud alerts.

---

## Week 1 Deliverables (Completed)

| # | Deliverable                              | Status |
|---|------------------------------------------|--------|
| 1 | Complete project folder structure        | ✅     |
| 2 | requirements.txt with all required pkgs  | ✅     |
| 3 | 200 realistic synthetic transactions     | ✅     |
| 4 | 4 detailed fraud policy documents        | ✅     |
| 5 | README.md + setup instructions           | ✅     |
| 6 | .env configuration template              | ✅     |
| 7 | docs/architecture.md                     | ✅     |
| 8 | Week1_Progress.md (root)                 | ✅     |

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
│   ├── agents/                       # LangGraph agents (to be built)
│   ├── rag/                          # Policy RAG + ChromaDB
│   └── utils/                        # Data loaders, helpers
├── streamlit_app/                    # Analyst investigation UI
├── docs/
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
# Edit .env and add your real OPENAI_API_KEY
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

### 3. Run Streamlit App (Week 2+)

```bash
streamlit run streamlit_app/app.py
```

---

## Key Technologies

- **Agent Orchestration**: LangGraph
- **LLM Framework**: LangChain + OpenAI (GPT-4o / GPT-4o-mini)
- **Vector Store**: ChromaDB
- **UI**: Streamlit + Plotly
- **Data**: pandas

---

## Next Steps (Week 2+)

- Implement LangGraph multi-agent workflow
- Build ChromaDB policy RAG pipeline
- Develop Streamlit investigation dashboard with agent traces
- Add evaluation harness

---

**Course**: AIOps Capstone (IIT Roorkee)  
**Theme**: 13 — AI Fraud Transaction Investigation Assistant  
**Project**: RiskRadar AI

For setup issues, contact the project team.
