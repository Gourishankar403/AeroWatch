from langgraph.graph import StateGraph,START,END


from app.graph.state import InvestigationState


from app.graph.nodes import(
    investigate_operations,
    investigate_weather

)


def build_investigation_graph():
    """builds the initial aerowatch investigation workflow"""

    workflow=StateGraph(InvestigationState)

    workflow.add_node(
        "operations",
        investigate_operations
    )

    workflow.add_node(
        "weather",
        investigate_weather

    )

    workflow.add_edge(
        START,
        "operations"

    )

    workflow.add_edge(
        "operations",
        "weather"

    )

    workflow.add_edge(
        "weather",
        END
    )


    return workflow.compile()

