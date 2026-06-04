from langgraph.graph import StateGraph
from langgraph.graph import END

from src.graph.state import InvestigationState

from src.graph.nodes import (
    alert_intake_node,
    risk_scoring_node,
    policy_evidence_node,
    behavioral_pattern_node,
    evidence_fusion_node,
    recommendation_node
)


def build_workflow():

    graph = StateGraph(
        InvestigationState
    )

    graph.add_node(
        "alert_intake",
        alert_intake_node
    )

    graph.add_node(
        "risk_scoring",
        risk_scoring_node
    )

    graph.add_node(
        "policy_evidence",
        policy_evidence_node
    )

    graph.add_node(
        "behavioral_pattern",
        behavioral_pattern_node
    )

    graph.add_node(
        "evidence_fusion",
        evidence_fusion_node
    )

    graph.add_node(
        "recommendation",
        recommendation_node
    )

    graph.set_entry_point(
        "alert_intake"
    )

    graph.add_edge(
        "alert_intake",
        "risk_scoring"
    )

    graph.add_edge(
        "alert_intake",
        "policy_evidence"
    )

    graph.add_edge(
        "alert_intake",
        "behavioral_pattern"
    )

    graph.add_edge(
        [
            "risk_scoring",
            "policy_evidence",
            "behavioral_pattern",
        ],
        "evidence_fusion"
    )

    graph.add_edge(
        "evidence_fusion",
        "recommendation"
    )

    graph.add_edge(
        "recommendation",
        END
    )

    return graph.compile()
