from langgraph.graph import StateGraph,START,END

from app.graph.state import InvestigationState


from app.graph.nodes import(
    investigate_weather,
    investigate_operations
)

from app.graph.nodes import (
    investigate_operations,
    investigate_weather,
    analyze_evidence,
)


def build_investigation_graph():
    """Builds the AeroWatch investigation workflow.
    Independent investigations are executed in parallel"""


    workflow=StateGraph(InvestigationState)

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
    analyze_evidence)

    workflow.add_edge(START, "operations")
    workflow.add_edge(START, "weather")

    workflow.add_edge("operations", "analysis")
    workflow.add_edge("weather", "analysis")

    workflow.add_edge("analysis", END)


    return workflow.compile()


