from langgraph.graph import StateGraph,START,END

from app.graph.state import InvestigationState


from app.graph.nodes import(
    investigate_weather,
    investigate_operations
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

    workflow.add_edge(START,"operations")
    workflow.add_edge(START,"weather")

    workflow.add_edge("operations",END)
    workflow.add_edge("weather",END)


    return workflow.compile()


