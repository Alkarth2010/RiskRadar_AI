from src.fraud.risk_engine import calculate_risk
from src.fraud.models import FraudAlert

import logging

logger = logging.getLogger(__name__)


RULE_TO_POLICY = {
    "High Value Transaction":
        "High_Value_Transaction_Policy",

    "New Device":
        "Device_and_Payment_Instrument_Policy",

    "Velocity Spike":
        "Velocity_and_Burst_Detection_Policy",

    "Geographic Anomaly":
        "Geographic_Anomaly_Policy"
}

HIGH_RISK_COUNTRIES = {
    "Russia",
    "North Korea",
    "Iran"
}


def _load_alert(state):

    raw_alert = state["alert"]

    if isinstance(raw_alert, FraudAlert):
        return raw_alert

    return FraudAlert(**raw_alert)


def _derive_policies_from_rules(alert):
    triggered_rules = alert.triggered_rules or []

    policies = list(
        {
            RULE_TO_POLICY[rule]
            for rule in triggered_rules
            if rule in RULE_TO_POLICY
        }
    )

    if policies:
        return policies

    fallback_policies = []

    if alert.amount > 100000:
        fallback_policies.append(
            "High_Value_Transaction_Policy"
        )

    if alert.new_device:
        fallback_policies.append(
            "Device_and_Payment_Instrument_Policy"
        )

    if alert.transactions_last_10min > 10:
        fallback_policies.append(
            "Velocity_and_Burst_Detection_Policy"
        )

    if alert.country in HIGH_RISK_COUNTRIES:
        fallback_policies.append(
            "Geographic_Anomaly_Policy"
        )

    return list(set(fallback_policies))


def alert_intake_node(state):
    return {
        "agent_trace": [
            "Alert intake completed",
            "Parallel fraud analysis started"
        ]
    }


def risk_scoring_node(state):

    alert = _load_alert(state)

    result = calculate_risk(alert)

    return {
        "risk_score": result["risk_level"],
        "triggered_policies": result["triggered_policies"],
        "agent_trace": [
            f"Risk scoring analyst completed ({result['risk_level']})"
        ]
    }


def risk_analysis_node(state):
    return risk_scoring_node(state)


rag = None


def policy_evidence_node(state):

    alert = _load_alert(state)

    triggered_policies = _derive_policies_from_rules(alert)

    # No policies triggered → skip retrieval
    if not triggered_policies:

        return {
            "retrieved_context": "",
            "sources": [],
            "agent_trace": [
                "Policy evidence analyst completed (0 documents)"
            ],
            "error": ""
        }

    try:
        global rag

        if rag is None:
            from src.rag.rag_pipeline import RiskRadarRAG

            rag = RiskRadarRAG()

        rag_result = rag.retrieve_policy_context(
            triggered_policies
        )

        return {
            "retrieved_context":
                rag_result.get("context", ""),

            "sources":
                rag_result.get("sources", []),

            "agent_trace":
                [
                    "Policy evidence analyst completed "
                    f"({len(rag_result.get('sources', []))} documents)"
                ],

            "error": ""
        }

    except Exception as e:

        logger.error(
            f"RAG retrieval failed: {e}"
        )

        return {
            "retrieved_context": "",
            "sources": [],
            "agent_trace": [
                "Policy evidence analyst failed; fallback evidence path used"
            ],
            "error":
                f"RAG retrieval failed: {str(e)}"
        }


def retrieval_node(state):
    return policy_evidence_node(state)


# Deterministic summary logic keeps tests and demos independent of LLM quota.
def behavioral_pattern_node(state):

    alert = _load_alert(state)

    findings = []

    if alert.amount > 2500:
        findings.append(
            f"High amount observed (Amount: ₹{alert.amount:,.2f})."
        )

    if alert.new_device:
        findings.append(
            "New device indicator present."
        )

    if alert.transactions_last_10min >= 3:
        findings.append(
            f"Velocity pattern observed ({alert.transactions_last_10min} recent transactions)."
        )

    if alert.country:
        findings.append(
            f"Transaction location reviewed ({alert.country})."
        )

    if not findings:
        findings.append(
            "No additional behavioral anomalies identified."
        )

    return {
        "behavioral_findings": findings,
        "agent_trace": [
            "Behavioral pattern analyst completed"
        ]
    }


def evidence_fusion_node(state):

    risk = state.get("risk_score", "LOW")
    policies = state.get("triggered_policies", [])
    alert = state.get("alert", {})
    behavioral_findings = state.get(
        "behavioral_findings",
        []
    )
    sources = state.get(
        "sources",
        []
    )

    findings = []

    findings.append(
        f"Risk scoring classified the alert as {risk}."
    )

    if "High_Value_Transaction_Policy" in policies:
        findings.append(
            f"High-value transaction detected (Amount: ₹{alert.get('amount'):,})."
        )

    if "Velocity_and_Burst_Detection_Policy" in policies:
        findings.append(
            "Velocity anomaly detected based on transaction burst activity."
        )

    if "Geographic_Anomaly_Policy" in policies:
        findings.append(
            f"Geographic anomaly detected ({alert.get('country')})."
        )

    if "Device_and_Payment_Instrument_Policy" in policies:
        findings.append(
            "Transaction originated from a new or untrusted device."
        )

    findings.extend(behavioral_findings)

    if not findings:
        findings.append(
            "No significant fraud indicators detected."
        )

    reasoning = "\n".join(
        [f"- {x}" for x in findings]
    )

    investigation_actions = []

    if "High_Value_Transaction_Policy" in policies:
        investigation_actions.append(
            "- Review customer's historical transaction amounts."
        )

    if "Geographic_Anomaly_Policy" in policies:
        investigation_actions.append(
            "- Verify whether the customer is currently in the transaction country."
        )

    if "Velocity_and_Burst_Detection_Policy" in policies:
        investigation_actions.append(
            "- Reconstruct timeline of recent transactions."
        )

    if "Device_and_Payment_Instrument_Policy" in policies:
        investigation_actions.append(
            "- Confirm ownership of the new device."
        )

    investigation_actions.append(
        "- Perform step-up authentication."
    )

    if sources:
        investigation_actions.append(
            f"- Review retrieved policy evidence from {len(sources)} source document(s)."
        )

    summary = "\n".join(
        investigation_actions
    )

    return {
        "risk_reasoning": reasoning,
        "investigation_summary": summary,
        "agent_trace": [
            "Evidence fusion completed"
        ],
        "error": ""
    }


def summary_node(state):
    return evidence_fusion_node(state)


def recommendation_node(state):

    risk = state["risk_score"]

    policies = state["triggered_policies"]

    count = len(policies)

    if count == 1:
        suffix = "policy indicator"
    else:
        suffix = "policy indicators"

    if risk == "HIGH":

        action = "ESCALATE"

        reason = (
            f"HIGH risk alert triggered by "
            f"{len(policies)} policy violations: "
            f"{', '.join(policies)}."
        )

    elif risk == "MEDIUM":

        action = "MONITOR"

        reason = (
            f"MEDIUM risk alert triggered by "
            f"{len(policies)} {suffix}."
        )

    else:

        action = "APPROVE"

        reason = (
            "No material fraud indicators identified."
        )

    return {
        "recommended_action": action,
        "action_reason": reason,
        "agent_trace": [
            f"Recommendation generated: {action}",
            "Human decision pending"
        ]
    }
