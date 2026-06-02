# src/fraud/service.py

from src.graph.workflow import build_workflow
from src.fraud.models import FraudAlert, InvestigationResult

workflow = build_workflow()


def investigate_fraud_alert(alert: FraudAlert):

    result = workflow.invoke(
        {
            "alert": alert.model_dump()
        }
    )

    return InvestigationResult(
        risk_score=result["risk_score"],
        risk_reasoning=result["risk_reasoning"],
        triggered_policies=result["triggered_policies"],
        investigation_summary=result["investigation_summary"],
        recommended_action=result["recommended_action"],
        action_reason=result["action_reason"],
        sources=result["sources"]
    )