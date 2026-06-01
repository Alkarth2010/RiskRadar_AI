# RiskRadar AI — System Architecture & Agent Workflow

**IIT Roorkee AIOps Capstone Project — Theme 13**  
**Version**: 0.1 (Week 1)  
**Last Updated**: 2025-10-06

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT INVESTIGATION UI                        │
│   (Alert Queue | Transaction Detail | Agent Trace | What-If | Feedback)
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                            │
│  Supervisor (Router) → Planner → Executor (with conditional edges)   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
│  RAG RETRIEVER   │   │  STRUCTURED DATA     │   │  TOOLS / MCP     │
│  (Policies +     │   │  LOADER (Pandas)     │   │  (Future)        │
│   Past Cases)    │   │  Customer 360        │   │                  │
└──────────────────┘   └──────────────────────┘   └──────────────────┘
          │                        │
          ▼                        ▼
   ┌──────────────┐         ┌──────────────┐
   │  ChromaDB    │         │  transactions│
   │  (Vector)    │         │  .csv        │
   └──────────────┘         └──────────────┘
```

**Design Principles**
- Agentic & multi-step reasoning (not single LLM calls)
- Every recommendation must be grounded in policy text or data evidence
- Full reasoning trace visible to the human analyst
- Human-in-the-loop at key decision points

---

## 2. Core Components

### 2.1 Data Layer
- `data/synthetic/transactions.csv` — 200 realistic bank transactions (26 labeled fraud)
- `data/policies/*.txt` — 4 detailed fraud investigation policies
- Future: Customer profiles, historical cases, device graph

### 2.2 RAG Subsystem (`src/rag/`)
- Policy document loader + chunker (LangChain text splitters)
- ChromaDB vector store with OpenAI embeddings
- Metadata-aware hybrid retrieval
- Citation engine that returns policy ID + section for explainability

### 2.3 Agent Layer (`src/agents/`)
Planned LangGraph nodes:
- `intake_node` — Load transaction + enrich with customer aggregates
- `policy_retriever_node` — Semantic search over policies + past cases
- `evidence_gatherer` — Velocity, geo, device, amount signals
- `risk_scorer` — Composite risk score (rules + LLM judgment)
- `recommendation_agent` — Final decision (Approve / Hold / Block) + rationale + citations
- `critic_node` (optional) — Self-critique for policy violations or hallucinations

State is defined in a TypedDict (`state.py`) containing transaction, context, retrieved policies, signals, risk_score, recommendation, full trace, and human feedback fields.

### 2.4 Streamlit UI (`streamlit_app/`)
Planned views:
- Alert queue with filters
- Investigation workspace showing agent trace, policy citations, similar cases
- What-if simulator (change amount/location/device → re-run agent)
- Analyst feedback capture for continuous improvement

---

## 3. Agent Workflow (High-Level)

1. **Intake & Context Assembly** — Load txn + compute customer 360 view
2. **Parallel Tool Calls** — Evidence extraction + Policy RAG
3. **Risk Scoring** — Weighted combination of rule signals + LLM assessment
4. **Recommendation Generation** — Decision + 3-bullet rationale + required actions + citations
5. **Self-Critique** (optional) — Check for contradictions with policies
6. **Human Review** — Analyst sees full trace, accepts / overrides / asks clarifying question
7. **Feedback Loop** — Store outcome for future RAG augmentation

---

## 4. Technology Stack

| Component              | Technology                     |
|------------------------|--------------------------------|
| Agent Framework        | LangGraph 0.2+                 |
| LLM                    | OpenAI GPT-4o / GPT-4o-mini    |
| Embeddings             | text-embedding-3-small         |
| Vector DB              | ChromaDB (local)               |
| UI                     | Streamlit + Plotly             |
| Data Processing        | pandas + pydantic              |

---

## 5. Security & Auditability

- API keys only via environment variables
- All reasoning steps logged with timestamps
- Every recommendation includes explicit policy citations
- Synthetic data only — no real PII in repository

---

**Status**: Week 1 foundation complete. Agent implementation begins Week 2.
