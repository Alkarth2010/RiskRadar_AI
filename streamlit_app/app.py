import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from src.fraud.alert_generator import generate_alerts

from src.fraud.alert_adapter import (
    convert_to_workflow_alert
)

from src.graph.workflow import (
    build_workflow
)

st.set_page_config(
    page_title="RiskRadar AI",
    layout="wide"
)

st.title("🛡️ RiskRadar AI")
st.write("Fraud Investigation Assistant")

st.sidebar.header("🚨 Alert Queue")

alerts = generate_alerts()

alert_options = {
    f"{alert.severity} | {alert.transaction_id}": alert
    for alert in alerts
}

selected_alert_label = st.sidebar.selectbox(
    "Select Alert",
    list(alert_options.keys())
)

selected_alert = alert_options[
    selected_alert_label
]

st.subheader("Alert Overview")

col1, col2 = st.columns(2)

with col1:
    st.write(
        f"**Transaction ID:** "
        f"{selected_alert.transaction_id}"
    )

    st.write(
        f"**Customer ID:** "
        f"{selected_alert.customer_id}"
    )

    st.write(
        f"**Amount:** "
        f"₹{selected_alert.amount:,.2f}"
    )

with col2:
    st.write(
        f"**Severity:** "
        f"{selected_alert.severity}"
    )

    st.write(
        f"**Location:** "
        f"{selected_alert.location}"
    )

st.write("**Triggered Rules:**")

for rule in selected_alert.triggered_rules:
    st.write(f"• {rule}")

run_investigation = st.button(
    "🔍 Run Investigation"
)    

if run_investigation:

    workflow_alert = (
        convert_to_workflow_alert(
            selected_alert
        )
    )

    workflow = build_workflow()

    result = workflow.invoke(
        {
            "alert": workflow_alert.dict()
        }
    )

    st.success(
        "Investigation completed"
    )


    st.subheader("Investigation Result")

    st.metric(
        "Risk Score",
        result["risk_score"]
    )

    st.metric(
        "Recommendation",
        result["recommended_action"]
    )

    st.subheader("Risk Reasoning")

    st.write(result["risk_reasoning"])

    st.subheader("Triggered Policies")

    for policy in result["triggered_policies"]:
        st.write(f"• {policy}")
    st.subheader("Investigation Summary")

    st.write(
        result["investigation_summary"]
    )

    st.subheader("Agent Trace")

    for step in result["agent_trace"]:
        st.write(f"• {step}")

    st.subheader("Sources")

    for source in result["sources"]:
        st.write(f"• {source}")
    