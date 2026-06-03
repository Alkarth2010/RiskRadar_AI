from src.fraud.risk_engine import calculate_risk
from src.fraud.models import FraudAlert


from src.fraud.models import FraudAlert

import logging

logger = logging.getLogger(__name__)

def risk_analysis_node(state):

    raw_alert = state["alert"]

    if isinstance(raw_alert, FraudAlert):
        alert = raw_alert
    else:
        alert = FraudAlert(**raw_alert)

    result = calculate_risk(alert)

    return {
        "risk_score": result["risk_level"],
        "triggered_policies": result["triggered_policies"],
        "agent_trace": [
            "Transaction loaded",
            f"Risk assessment completed ({result['risk_level']})",
            f"{len(result['triggered_policies'])} policy violations detected"
        ]
    }

from src.rag.rag_pipeline import RiskRadarRAG

rag = RiskRadarRAG()


'''def retrieval_node(state):

    policies = state["triggered_policies"]

    if not policies:
        return {
            "retrieved_context": "",
            "sources": []
        }

    result = rag.retrieve_policy_context(
        policies
    )

    return {
        "retrieved_context": result["context"],
        "sources": result["sources"]
    }'''

from typing import Any

def retrieval_node(state):

    triggered_policies = state.get(
        "triggered_policies",
        []
    )

    # No policies triggered → skip retrieval
    if not triggered_policies:

        return {
            "retrieved_context": "",
            "sources": [],
            "error": ""
        }

    try:

        rag_result = rag.retrieve_policy_context(
            triggered_policies
        )

        trace = state.get(
            "agent_trace",
            []
        )

        trace.append(
            f"Policy retrieval completed ({len(rag_result.get('sources', []))} documents)"
        )

        return {
            "retrieved_context":
                rag_result.get("context", ""),

            "sources":
                rag_result.get("sources", []),

            "agent_trace":
                trace,

            "error": ""
        }

    except Exception as e:

        logger.error(
            f"RAG retrieval failed: {e}"
        )

        return {
            "retrieved_context": "",
            "sources": [],
            "error":
                f"RAG retrieval failed: {str(e)}"
        }

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
    max_retries=1
)


'''def summary_node(state):

    prompt = f"""
You are a senior fraud investigation analyst at a financial institution.

Transaction Alert:
{state['alert']}

Risk Score:
{state['risk_score']}

Triggered Policies:
{state['triggered_policies']}

Policy Context:
{state['retrieved_context']}

Return your response EXACTLY in the following format:

RISK_REASONING:
- Bullet point 1
- Bullet point 2
- Bullet point 3
(Maximum 5 bullets)

INVESTIGATION_SUMMARY:
- Finding 1
- Finding 2
- Finding 3
- Recommended verification steps
- Required investigation actions
(Maximum 10 bullets)

Rules:
- Use concise professional fraud-investigation language.
- Reference policy findings where relevant.
- Do not include markdown headings other than the required labels.
- Do not include recommendations outside the investigation summary.
"""

    try:

        response = llm.invoke(prompt)

        text = response.content

        parts = text.split(
            "INVESTIGATION_SUMMARY:"
        )

        reasoning = (
            parts[0]
            .replace(
                "RISK_REASONING:",
                ""
            )
            .strip()
        )

        summary = parts[1].strip()

        trace = state.get(
            "agent_trace",
            []
        )

        trace.append(
            "Investigation summary generated"
        )

        return {
            "risk_reasoning": reasoning,
            "investigation_summary": summary,
            "agent_trace": trace,
            "error": ""
        }

    except Exception as e:

        trace = state.get(
            "agent_trace",
            []
        )

        trace.append(
            "Investigation summary generation failed"
        )

        return {
            "risk_reasoning":
                "Unable to generate AI reasoning due to model quota limits.",

            "investigation_summary":
                "Investigation summary unavailable. Review triggered policies manually.",

            "agent_trace":
                trace,

            "error": str(e)
        }'''

#### Alternative summary node with deterministic logic to avoid LLM dependency during testing and development
# This can be used as a fallback or for unit testing the workflow without relying on the LLM.
# In production, the LLM-based summary_node can be used for richer insights.
 
def summary_node(state):

    risk = state.get("risk_score", "LOW")
    policies = state.get("triggered_policies", [])
    alert = state.get("alert", {})

    findings = []

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

    summary = "\n".join(
        investigation_actions
    )

    trace = state.get(
        "agent_trace",
        []
    )

    trace.append(
        "Investigation summary generated"
    )

    return {
        "risk_reasoning": reasoning,
        "investigation_summary": summary,
        "agent_trace": trace,
        "error": ""
    }


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

    trace = state.get(
        "agent_trace",
        []
    )

    trace.append(
        f"Recommendation generated: {action}"
    )
    
    return {
        "recommended_action": action,
        "action_reason": reason,
        "agent_trace": trace
    }
