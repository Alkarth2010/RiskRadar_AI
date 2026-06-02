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
        "triggered_policies": result["triggered_policies"]
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

        return {
            "retrieved_context":
                rag_result.get("context", ""),

            "sources":
                rag_result.get("sources", []),

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


def summary_node(state):

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

        return {
            "risk_reasoning": reasoning,
            "investigation_summary": summary,
            "error": ""
        }

    except Exception as e:

        return {
            "risk_reasoning":
                "Unable to generate AI reasoning due to model quota limits.",

            "investigation_summary":
                "Investigation summary unavailable. Review triggered policies manually.",

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

    return {
        "recommended_action": action,
        "action_reason": reason
    }
