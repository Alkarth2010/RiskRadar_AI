"""
RiskRadar AI - Streamlit Investigation Interface (Week 1 Stub)

Run with: streamlit run streamlit_app/app.py
"""

import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_transactions

st.set_page_config(page_title="RiskRadar AI", page_icon="📡", layout="wide")

st.title("📡 RiskRadar AI")
st.caption("IIT Roorkee AIOps Capstone — Theme 13 | Week 1 Foundation")

st.success("✅ Project skeleton ready. Week 2 will add LangGraph agents + RAG.")

df = load_transactions()

st.subheader("Synthetic Bank Transactions (200 rows)")
st.dataframe(df.head(15), use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
col1.metric("Total Transactions", len(df))
col2.metric("Fraud Cases", int(df["is_fraud"].sum()))

st.info("Full agent-powered investigation UI coming in Week 2.")
