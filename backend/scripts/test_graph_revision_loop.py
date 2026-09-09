from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState
from app.graph.nodes import (
    investigate_operations,
    investigate_weather,
    analyze_evidence,
    verify_analysis,
    revise_analysis,
)
from app.models.analysis import AnalysisAssessment


def force_bad_analysis(state: InvestigationState) -> dict:
    """
    Test-only node.

    Replaces the valid LLM analysis with a deliberately
    unsupported analysis so that the LangGraph revision
    branch is guaranteed to execute.
    """

    bad_analysis = AnalysisAssessment(
        airport=state["airport"],

        observed_facts=[
            "No active FAA operational events were detected."
        ],

        potential_factors=[
            "Weather conditions caused the airport disruption."
        ],

        overall_assessment=(
            "Poor weather caused an operational disruption "
            f"at {state['airport']}."
        ),

        confidence="high",

        limitations=[],
    )

    return {
        "analysis_assessment": bad_analysis
    }


def should_continue(state: InvestigationState) -> str:
    """
    Determines whether the graph should finish or
    send the analysis through the revision agent.
    """

    verification = state["verification_assessment"]

    if verification.approved:
        return "end"

    if state["revision_count"] >= state["max_revisions"]:
        return "end"

    return "revise"


def build_test_graph():
    """
    Builds a controlled LangGraph specifically for testing
    the autonomous revision loop.

    The real AeroWatch graph is used, but a test-only node
    deliberately corrupts the analysis before verification.
    """

    workflow = StateGraph(InvestigationState)

    workflow.add_node(
        "operations",
        investigate_operations
    )

    workflow.add_node(
        "weather",
        investigate_weather
    )

    workflow.add_node(
        "analysis",
        analyze_evidence
    )

    workflow.add_node(
        "force_bad_analysis",
        force_bad_analysis
    )

    workflow.add_node(
        "verification",
        verify_analysis
    )

    workflow.add_node(
        "revision",
        revise_analysis
    )

    # --------------------------------------------------
    # Investigation
    # --------------------------------------------------

    workflow.add_edge(
        START,
        "operations"
    )

    workflow.add_edge(
        START,
        "weather"
    )

    workflow.add_edge(
        "operations",
        "analysis"
    )

    workflow.add_edge(
        "weather",
        "analysis"
    )

    # --------------------------------------------------
    # LLM Analysis
    # --------------------------------------------------

    workflow.add_edge(
        "analysis",
        "force_bad_analysis"
    )

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    workflow.add_edge(
        "force_bad_analysis",
        "verification"
    )

    # --------------------------------------------------
    # Revision loop
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "verification",
        should_continue,
        {
            "end": END,
            "revise": "revision",
        },
    )

    workflow.add_edge(
        "revision",
        "verification"
    )

    return workflow.compile()


def main():

    print(
        "\n===== AEROWATCH LANGGRAPH "
        "LLM REVISION LOOP TEST =====\n"
    )

    graph = build_test_graph()

    initial_state = {
        "query": (
            "Investigate current operational conditions "
            "at JFK airport"
        ),

        "airport": "KJFK",

        "operations_assessment": None,

        "weather_assessment": None,

        "analysis_assessment": None,

        "verification_assessment": None,

        "revision_count": 0,

        "max_revisions": 2,

        "investigation_complete": False,
    }

    print("Running AeroWatch LangGraph...\n")

    result = graph.invoke(initial_state)

    # --------------------------------------------------
    # Final results
    # --------------------------------------------------

    print("===== OPERATIONS =====\n")

    print(
        result["operations_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n===== WEATHER =====\n")

    print(
        result["weather_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n===== FINAL ANALYSIS =====\n")

    print(
        result["analysis_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n===== FINAL VERIFICATION =====\n")

    print(
        result["verification_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n===== REVISION INFORMATION =====\n")

    print(
        "Revision count:",
        result["revision_count"]
    )

    print(
        "Maximum revisions:",
        result["max_revisions"]
    )

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    assert result["operations_assessment"] is not None

    assert result["weather_assessment"] is not None

    assert result["analysis_assessment"] is not None

    assert result["verification_assessment"] is not None

    # The test deliberately creates a bad analysis,
    # therefore at least one revision must happen.
    assert result["revision_count"] >= 1

    # The LLM RevisionAgent must produce a valid
    # AnalysisAssessment.
    assert (
        type(result["analysis_assessment"]).__name__
        == "AnalysisAssessment"
    )

    # The revised analysis must ultimately pass
    # deterministic verification.
    assert (
        result["verification_assessment"].approved
        is True
    )

    print(
        "\n===== LANGGRAPH TEST PASSED ====="
    )

    print(
        "The AeroWatch graph successfully:"
    )

    print(
        "1. Collected operational evidence"
    )

    print(
        "2. Collected weather evidence"
    )

    print(
        "3. Generated an LLM analysis"
    )

    print(
        "4. Detected an intentionally bad analysis"
    )

    print(
        "5. Routed the analysis to the LLM RevisionAgent"
    )

    print(
        "6. Re-verified the revised analysis"
    )

    print(
        "7. Accepted the corrected analysis"
    )


if __name__ == "__main__":
    main()