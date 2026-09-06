from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState

from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.analysis import AnalysisAssessment

from app.agents.verification_agent import VerificationAgent
from app.agents.revision_agent import RevisionAgent


# --------------------------------------------------
# Test node: deliberately creates flawed analysis
# --------------------------------------------------

def create_bad_analysis(
    state: InvestigationState,
) -> dict:
    """
    Creates an intentionally flawed analysis to force
    the verification failure branch.
    """

    analysis = AnalysisAssessment(
        airport=state["airport"],
        observed_facts=[
            "No operational disruption detected."
        ],
        potential_factors=[
            "Weather conditions may influence operations."
        ],
        overall_assessment=(
            "Weather conditions caused a significant "
            "operational disruption at the airport."
        ),
        confidence="high",
        limitations=[],
    )

    return {
        "analysis_assessment": analysis
    }


# --------------------------------------------------
# Verification node
# --------------------------------------------------

def verify_test_analysis(
    state: InvestigationState,
) -> dict:
    """
    Verifies the current analysis.
    """

    verifier = VerificationAgent()

    verification = verifier.verify(
        operations=state["operations_assessment"],
        weather=state["weather_assessment"],
        analysis=state["analysis_assessment"],
    )

    return {
        "verification_assessment": verification
    }


# --------------------------------------------------
# Revision node
# --------------------------------------------------

def revise_test_analysis(
    state: InvestigationState,
) -> dict:
    """
    Revises the analysis using verification feedback.
    """

    revision_agent = RevisionAgent()

    revised_analysis = revision_agent.revise(
        operations=state["operations_assessment"],
        weather=state["weather_assessment"],
        analysis=state["analysis_assessment"],
        verification=state["verification_assessment"],
    )

    return {
        "analysis_assessment": revised_analysis,
        "revision_count": state["revision_count"] + 1,
    }


# --------------------------------------------------
# Conditional routing
# --------------------------------------------------

def should_continue(
    state: InvestigationState,
) -> str:
    """
    Decides whether to end or perform another revision.
    """

    verification = state["verification_assessment"]

    if verification.approved:
        return "end"

    if state["revision_count"] >= state["max_revisions"]:
        return "end"

    return "revise"


# --------------------------------------------------
# Build controlled test graph
# --------------------------------------------------

def build_test_graph():

    workflow = StateGraph(InvestigationState)

    workflow.add_node(
        "analysis",
        create_bad_analysis,
    )

    workflow.add_node(
        "verification",
        verify_test_analysis,
    )

    workflow.add_node(
        "revision",
        revise_test_analysis,
    )

    workflow.add_edge(
        START,
        "analysis",
    )

    workflow.add_edge(
        "analysis",
        "verification",
    )

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


# --------------------------------------------------
# Run test
# --------------------------------------------------

def main():

    graph = build_test_graph()

    operations = OperationsAssessment(
        airport="TEST",
        disruption_detected=False,
        event_count=0,
        findings=[
            "No operational disruption detected."
        ],
        limitations=[
            "This assessment reflects controlled test operational evidence."
        ],
        evidence={
            "airport": "TEST",
            "source": "test",
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "events": [],
            "summary": "No operational events detected."
        },
    )

    weather = WeatherAssessment(
        airport="TEST",
        weather_risk_detected=False,
        risk_level="low",
        findings=[
            "No significant weather risk detected."
        ],
        limitations=[
            "This assessment reflects controlled test weather evidence."
        ],
        evidence={
            "airport": "TEST",
            "source": "test",
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "temperature_c": 20.0,
            "wind_speed_knots": 5.0,
            "wind_gust_knots": None,
            "visibility_meters": None,
            "visibility_raw": "10+",
            "weather_conditions": [],
            "flight_category": "VFR",
            "raw_observation": "TEST METAR",
        },
    )

    initial_state = {
        "query": "Test LangGraph revision loop",
        "airport": "TEST",

        "operations_assessment": operations,
        "weather_assessment": weather,

        "analysis_assessment": None,
        "verification_assessment": None,

        "revision_count": 0,
        "max_revisions": 2,

        "investigation_complete": False,
    }

    result = graph.invoke(initial_state)

    print(
        "\n===== LANGGRAPH REVISION LOOP TEST =====\n"
    )

    print("Revision count:")
    print(result["revision_count"])

    print("\n--- FINAL ANALYSIS ---")

    print(
        result["analysis_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n--- FINAL VERIFICATION ---")

    print(
        result["verification_assessment"]
        .model_dump_json(indent=2)
    )

    print("\n===== TEST RESULT =====")

    if (
        result["verification_assessment"].approved
        and result["revision_count"] > 0
    ):
        print(
            "SUCCESS: LangGraph correctly routed "
            "the failed analysis through revision "
            "and re-verification."
        )
    else:
        print(
            "FAILURE: LangGraph revision routing "
            "did not behave as expected."
        )


if __name__ == "__main__":
    main()