from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState

from app.graph.nodes import (
    investigate_operations,
    investigate_weather,
    analyze_evidence,
    verify_analysis,
    revise_analysis,
)


def should_continue(
    state: InvestigationState,
) -> str:
    """
    Decides whether the investigation can finish
    or requires another revision attempt.
    """

    verification = state["verification_assessment"]

    if verification.approved:
        return "end"

    if state["revision_count"] >= state["max_revisions"]:
        return "end"

    return "revise"


def build_investigation_graph():
    """
    Builds the AeroWatch evidence-grounded
    investigation workflow.

    Operations and weather investigations run
    independently, followed by analysis,
    verification, and conditional revision.
    """

    workflow = StateGraph(InvestigationState)

    # Investigation nodes
    workflow.add_node(
        "operations",
        investigate_operations,
    )

    workflow.add_node(
        "weather",
        investigate_weather,
    )

    # Reasoning nodes
    workflow.add_node(
        "analysis",
        analyze_evidence,
    )

    workflow.add_node(
        "verification",
        verify_analysis,
    )

    workflow.add_node(
        "revision",
        revise_analysis,
    )

    # Parallel investigations
    workflow.add_edge(
        START,
        "operations",
    )

    workflow.add_edge(
        START,
        "weather",
    )

    # Merge evidence
    workflow.add_edge(
        "operations",
        "analysis",
    )

    workflow.add_edge(
        "weather",
        "analysis",
    )

    # Verify generated analysis
    workflow.add_edge(
        "analysis",
        "verification",
    )

    # Conditional decision
    workflow.add_conditional_edges(
        "verification",
        should_continue,
        {
            "end": END,
            "revise": "revision",
        },
    )

    # Revised analysis gets verified again
    workflow.add_edge(
        "revision",
        "verification",
    )

    return workflow.compile()