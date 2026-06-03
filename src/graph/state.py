from typing import TypedDict, List


class InvestigationState(TypedDict):
    alert: dict

    risk_score: str
    risk_reasoning: str

    triggered_policies: List[str]

    retrieved_context: str
    sources: List[str]

    investigation_summary: str

    recommended_action: str

    action_reason: str

    agent_trace: List[str]

    error: str