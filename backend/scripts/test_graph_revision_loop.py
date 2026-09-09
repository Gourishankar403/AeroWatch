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

    The structured disruption_detected field is deliberately
    set to True regardless of the actual operational evidence.
    This tests whether the verifier can detect structured
    hallucination and whether the RevisionAgent can repair it.
    """

    operations = state["operations_assessment"]
    weather = state["weather_assessment"]

    # --------------------------------------------------
    # Deliberately create an invalid analysis.
    #
    # The operational evidence is authoritative, but the
    # test intentionally flips the disruption flag.
    # --------------------------------------------------

    bad_disruption_value = (
        not operations.disruption_detected
    )

    bad_analysis = AnalysisAssessment(
        airport=state["airport"],

        # DELIBERATE ERROR:
        # This is intentionally opposite to the real
        # operational evidence.
        disruption_detected=bad_disruption_value,

        # Keep weather state consistent so that the test
        # specifically exercises operational hallucination.
        weather_risk_detected=(
            weather.weather_risk_detected
        ),

        observed_facts=[
            "The analysis has been deliberately corrupted "
            "for revision-loop testing."
        ],

        potential_factors=[
            "Weather conditions may be relevant, but "
            "causation is not established."
        ],

        overall_assessment=(
            f"The deliberately corrupted analysis reports "
            f"an operational disruption at {state['airport']}."
        ),

        confidence="high",

        limitations=[
            "This analysis is intentionally corrupted for "
            "LangGraph revision-loop testing."
        ],
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

    The real AeroWatch investigation nodes are used, but a
    test-only node deliberately corrupts the analysis before
    verification.
    """

    workflow = StateGraph(InvestigationState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    workflow.add_node(
        "operations",
        investigate_operations,
    )

    workflow.add_node(
        "weather",
        investigate_weather,
    )

    workflow.add_node(
        "analysis",
        analyze_evidence,
    )

    workflow.add_node(
        "force_bad_analysis",
        force_bad_analysis,
    )

    workflow.add_node(
        "verification",
        verify_analysis,
    )

    workflow.add_node(
        "revision",
        revise_analysis,
    )

    # --------------------------------------------------
    # Investigation
    # --------------------------------------------------

    workflow.add_edge(
        START,
        "operations",
    )

    workflow.add_edge(
        START,
        "weather",
    )

    workflow.add_edge(
        "operations",
        "analysis",
    )

    workflow.add_edge(
        "weather",
        "analysis",
    )

    # --------------------------------------------------
    # LLM Analysis
    # --------------------------------------------------

    workflow.add_edge(
        "analysis",
        "force_bad_analysis",
    )

    # --------------------------------------------------
    # Verification
    # --------------------------------------------------

    workflow.add_edge(
        "force_bad_analysis",
        "verification",
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
        "verification",
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

    print(
        "Running AeroWatch LangGraph...\n"
    )

    result = graph.invoke(
        initial_state
    )

    # --------------------------------------------------
    # Final results
    # --------------------------------------------------

    print(
        "===== OPERATIONS =====\n"
    )

    print(
        result["operations_assessment"]
        .model_dump_json(indent=2)
    )

    print(
        "\n===== WEATHER =====\n"
    )

    print(
        result["weather_assessment"]
        .model_dump_json(indent=2)
    )

    print(
        "\n===== FINAL ANALYSIS =====\n"
    )

    print(
        result["analysis_assessment"]
        .model_dump_json(indent=2)
    )

    print(
        "\n===== FINAL VERIFICATION =====\n"
    )

    print(
        result["verification_assessment"]
        .model_dump_json(indent=2)
    )

    print(
        "\n===== REVISION INFORMATION =====\n"
    )

    print(
        "Revision count:",
        result["revision_count"],
    )

    print(
        "Maximum revisions:",
        result["max_revisions"],
    )

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    # Evidence collection must succeed.
    assert (
        result["operations_assessment"]
        is not None
    )

    assert (
        result["weather_assessment"]
        is not None
    )

    # An analysis must exist.
    assert (
        result["analysis_assessment"]
        is not None
    )

    # Verification must exist.
    assert (
        result["verification_assessment"]
        is not None
    )

    # --------------------------------------------------
    # Revision must have happened.
    # --------------------------------------------------

    assert (
        result["revision_count"] >= 1
    ), (
        "The intentionally corrupted analysis did not "
        "trigger the revision loop."
    )

    # --------------------------------------------------
    # Final analysis must be the expected Pydantic model.
    # --------------------------------------------------

    assert (
        type(
            result["analysis_assessment"]
        ).__name__
        == "AnalysisAssessment"
    )

    # --------------------------------------------------
    # Final structured analysis must agree with evidence.
    # --------------------------------------------------

    final_analysis = (
        result["analysis_assessment"]
    )

    operations = (
        result["operations_assessment"]
    )

    weather = (
        result["weather_assessment"]
    )

    assert (
        final_analysis.airport
        == operations.airport
    ), (
        "Final analysis airport does not match "
        "operational evidence."
    )

    assert (
        final_analysis.disruption_detected
        == operations.disruption_detected
    ), (
        "Final disruption_detected value does not "
        "match operational evidence."
    )

    assert (
        final_analysis.weather_risk_detected
        == weather.weather_risk_detected
    ), (
        "Final weather_risk_detected value does not "
        "match weather evidence."
    )

    # --------------------------------------------------
    # Final verification must approve the repaired
    # analysis.
    # --------------------------------------------------

    assert (
        result["verification_assessment"].approved
        is True
    ), (
        "The revised analysis was not approved by "
        "the final verification step."
    )

    # --------------------------------------------------
    # The revision count must remain within the limit.
    # --------------------------------------------------

    assert (
        result["revision_count"]
        <= result["max_revisions"]
    ), (
        "Revision count exceeded max_revisions."
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
        "4. Deliberately corrupted the analysis"
    )

    print(
        "5. Detected the corrupted analysis"
    )

    print(
        "6. Routed the analysis to the LLM RevisionAgent"
    )

    print(
        "7. Produced a schema-valid revised analysis"
    )

    print(
        "8. Re-verified the revised analysis"
    )

    print(
        "9. Confirmed structured fields match evidence"
    )

    print(
        "10. Accepted the corrected analysis"
    )


if __name__ == "__main__":
    main()