import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
from src.fraud.alert_generator import generate_alerts

from src.fraud.alert_adapter import (
    convert_to_workflow_alert
)

from src.graph.workflow import (
    build_workflow
)
from src.utils.feedback_logger import (
    FEEDBACK_LOG_PATH,
    save_feedback,
    sync_feedback_from_s3,
)

st.set_page_config(
    page_title="RiskRadar AI",
    layout="wide"
)

st.title("🛡️ RiskRadar AI")
st.caption(
    "AI Fraud Transaction Investigation Assistant"
)

st.sidebar.header("🚨 Alert Queue")


def format_queue_priority(severity):
    if not severity:
        return ""

    normalized = str(severity).strip().upper()

    if normalized.endswith("_PRIORITY"):
        return normalized

    return f"{normalized}_PRIORITY"


def load_decision_history():
    sync_feedback_from_s3()

    if not FEEDBACK_LOG_PATH.exists():
        return pd.DataFrame()

    try:
        history = pd.read_csv(
            FEEDBACK_LOG_PATH
        )
    except Exception:
        return pd.DataFrame()

    if history.empty:
        return history

    if (
        "queue_priority" not in history.columns
        and "alert_severity" in history.columns
    ):
        history["queue_priority"] = history[
            "alert_severity"
        ].apply(format_queue_priority)

    if "queue_priority" in history.columns:
        history["queue_priority"] = history[
            "queue_priority"
        ].fillna("").apply(format_queue_priority)

    return history


def get_handled_transaction_ids(history):
    if (
        history.empty
        or "transaction_id" not in history.columns
    ):
        return set()

    return set(
        history["transaction_id"]
        .dropna()
        .astype(str)
    )


def render_decision_history(history):
    st.divider()
    st.subheader("Decision History")

    if history.empty:
        st.info(
            "No analyst decisions have been saved yet."
        )
        return

    display_columns = [
        "timestamp",
        "transaction_id",
        "customer_id",
        "queue_priority",
        "system_risk_score",
        "system_recommendation",
        "analyst_decision",
        "analyst_note",
    ]

    for column in display_columns:
        if column not in history.columns:
            history[column] = ""

    recent_history = (
        history[display_columns]
        .tail(10)
        .iloc[::-1]
        .reset_index(drop=True)
    )

    st.caption(
        "Recently handled alerts are removed from the active queue."
    )
    st.dataframe(
        recent_history,
        use_container_width=True,
        hide_index=True,
    )


decision_history = load_decision_history()
handled_transaction_ids = get_handled_transaction_ids(
    decision_history
)

try:
    alerts = generate_alerts()
except Exception:
    st.error(
        "Alert generation failed. Please check logs."
    )
    st.stop()

alerts = [
    alert
    for alert in alerts
    if alert.transaction_id not in handled_transaction_ids
]

if not alerts:
    st.info(
        "No active alerts available. Handled alerts are shown in Decision History."
    )
    render_decision_history(
        decision_history
    )
    st.stop()


severity_counts = {
    "HIGH": 0,
    "MEDIUM": 0,
    "LOW": 0,
}

for alert in alerts:
    severity_counts[alert.severity] = (
        severity_counts.get(alert.severity, 0) + 1
    )

metric_cols = st.columns(4)

with metric_cols[0]:
    st.metric(
        "Total Alerts",
        len(alerts),
    )

with metric_cols[1]:
    st.metric(
        "HIGH_PRIORITY",
        severity_counts.get("HIGH", 0),
    )

with metric_cols[2]:
    st.metric(
        "MEDIUM_PRIORITY",
        severity_counts.get("MEDIUM", 0),
    )

with metric_cols[3]:
    st.metric(
        "LOW_PRIORITY",
        severity_counts.get("LOW", 0),
    )

alert_options = {
    (
        f"{format_queue_priority(alert.severity)} | "
        f"{alert.transaction_id}"
    ): alert
    for alert in alerts
}

selected_alert_label = st.sidebar.selectbox(
    "Select Alert",
    list(alert_options.keys())
)

selected_alert = alert_options[
    selected_alert_label
]


def clear_investigation_state():
    for key in [
        "investigation_result",
        "investigated_alert",
        "analyst_decision",
        "analyst_note",
    ]:
        st.session_state.pop(
            key,
            None,
        )


def set_analyst_decision(decision):
    st.session_state["analyst_decision"] = decision


if (
    st.session_state.get("selected_alert_id")
    != selected_alert.transaction_id
):
    st.session_state["selected_alert_id"] = selected_alert.transaction_id
    clear_investigation_state()

st.divider()
st.subheader("Alert Overview")

overview_cols = st.columns(4)

with overview_cols[0]:
    st.caption("Transaction ID")
    st.write(
        f"**{selected_alert.transaction_id}**"
    )

with overview_cols[1]:
    st.caption("Customer ID")
    st.write(
        f"**{selected_alert.customer_id}**"
    )

with overview_cols[2]:
    st.caption("Amount")
    st.write(
        f"**₹{selected_alert.amount:,.2f}**"
    )

with overview_cols[3]:
    st.caption("Queue Priority")
    st.write(
        f"**{format_queue_priority(selected_alert.severity)}**"
    )

location_cols = st.columns(2)

with location_cols[0]:
    st.caption("Location")
    st.write(
        selected_alert.location
    )

st.markdown("**Triggered Rules**")

for rule in selected_alert.triggered_rules:
    st.write(f"• {rule}")

run_investigation = st.button(
    "🔍 Run Investigation"
)

if run_investigation:

    try:
        workflow_alert = (
            convert_to_workflow_alert(
                selected_alert
            )
        )

        workflow = build_workflow()

        with st.spinner(
            "Running investigation..."
        ):
            result = workflow.invoke(
                {
                    "alert": workflow_alert.dict()
                }
            )

    except Exception:
        st.error(
            "Investigation failed. Please check logs."
        )
        st.stop()

    st.session_state["investigation_result"] = result
    st.session_state["investigated_alert"] = selected_alert
    st.session_state["analyst_decision"] = result.get(
        "recommended_action",
        "MONITOR",
    ).title()

if "investigation_result" in st.session_state:

    result = st.session_state["investigation_result"]
    investigated_alert = st.session_state["investigated_alert"]

    risk_score = result.get(
        "risk_score",
        "Unavailable",
    )
    recommended_action = result.get(
        "recommended_action",
        "MONITOR",
    )
    risk_reasoning = result.get(
        "risk_reasoning",
        "Risk reasoning unavailable.",
    )
    triggered_policies = result.get(
        "triggered_policies",
        [],
    )
    investigation_summary = result.get(
        "investigation_summary",
        "Investigation summary unavailable.",
    )
    agent_trace = result.get(
        "agent_trace",
        [],
    )
    sources = result.get(
        "sources",
        [],
    )
    result_error = result.get(
        "error",
        "",
    )

    st.success(
        "Investigation completed"
    )

    if result_error:
        st.warning(
            "Policy retrieval had an issue. Sources may be unavailable."
        )

    st.divider()
    st.subheader("Investigation Result")

    result_cols = st.columns(3)

    with result_cols[0]:
        st.metric(
            "Workflow Risk",
            risk_score
        )

    with result_cols[1]:
        st.metric(
            "Recommendation",
            recommended_action
        )

    with result_cols[2]:
        st.metric(
            "Queue Priority",
            format_queue_priority(investigated_alert.severity)
        )

    st.divider()
    st.subheader("Risk Reasoning")

    st.write(risk_reasoning)

    st.divider()
    st.subheader("Triggered Policies")

    for policy in triggered_policies:
        st.write(f"• {policy}")

    st.divider()
    st.subheader("Investigation Summary")

    st.write(
        investigation_summary
    )

    st.divider()
    st.subheader("Parallel Agent Trace")

    for step in agent_trace:
        st.write(f"• {step}")

    st.divider()
    st.subheader("Sources")

    for source in sources:
        st.write(f"• {source}")

    st.divider()
    st.subheader("Analyst Decision")

    st.write(
        "System recommendation: "
        f"**{recommended_action}**"
    )

    decision_cols = st.columns(3)

    decisions = [
        "Approve",
        "Monitor",
        "Escalate",
    ]

    selected_decision = st.session_state.get(
        "analyst_decision",
        "Monitor",
    )

    for index, decision in enumerate(decisions):
        with decision_cols[index]:
            st.button(
                decision,
                key=f"analyst_decision_{decision.lower()}",
                type=(
                    "primary"
                    if selected_decision == decision
                    else "secondary"
                ),
                use_container_width=True,
                on_click=set_analyst_decision,
                args=(decision,),
            )

    if selected_decision == "Approve":
        st.success(
            "Selected analyst decision: APPROVE"
        )
    elif selected_decision == "Escalate":
        st.warning(
            "Selected analyst decision: ESCALATE"
        )
    else:
        st.info(
            "Selected analyst decision: MONITOR"
        )

    analyst_note = st.text_area(
        "Analyst note / override reason",
        key="analyst_note",
        placeholder="Optional note for audit trail",
    )

    if st.button(
        "Save Analyst Decision",
        type="primary",
    ):
        try:
            feedback_path = save_feedback(
                transaction_id=investigated_alert.transaction_id,
                customer_id=investigated_alert.customer_id,
                alert_severity=format_queue_priority(
                    investigated_alert.severity
                ),
                system_risk_score=risk_score,
                system_recommendation=recommended_action,
                analyst_decision=selected_decision.upper(),
                analyst_note=analyst_note,
                triggered_rules=investigated_alert.triggered_rules,
                triggered_policies=triggered_policies,
                sources=sources,
            )

            st.success(
                f"Analyst decision saved to {feedback_path}"
            )

            clear_investigation_state()
            st.rerun()

        except Exception as e:
            st.error(
                f"Feedback could not be saved: {e}"
            )
render_decision_history(
    load_decision_history()
)
