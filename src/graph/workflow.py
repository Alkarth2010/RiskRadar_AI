from langgraph.graph import StateGraph
from langgraph.graph import END

from src.graph.state import InvestigationState

from src.graph.nodes import (
    risk_analysis_node,
    retrieval_node,
    summary_node,
    recommendation_node
)


def build_workflow():

    graph = StateGraph(
        InvestigationState
    )

    graph.add_node(
        "risk_analysis",
        risk_analysis_node
    )

    graph.add_node(
        "retrieval",
        retrieval_node
    )

    graph.add_node(
        "summary",
        summary_node
    )

    graph.add_node(
        "recommendation",
        recommendation_node
    )

    graph.set_entry_point(
        "risk_analysis"
    )

    graph.add_edge(
        "risk_analysis",
        "retrieval"
    )

    graph.add_edge(
        "retrieval",
        "summary"
    )

    graph.add_edge(
        "summary",
        "recommendation"
    )

    graph.add_edge(
        "recommendation",
        END
    )

    return graph.compile()