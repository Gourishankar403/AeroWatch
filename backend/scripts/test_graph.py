from app.graph.workflow import build_investigation_graph


graph = build_investigation_graph()


initial_state = {
    "query": "Investigate current operational conditions at JFK airport",

    "airport": "KJFK",

    "operations_assessment": None,

    "weather_assessment": None,

    "analysis_assessment": None,

    "verification_assessment": None,

    "revision_count": 0,

    "max_revisions": 2,

    "investigation_complete": False,
}


result = graph.invoke(initial_state)


print("\n===== AEROWATCH INVESTIGATION RESULT =====\n")

print("Airport:", result["airport"])


print("\n--- OPERATIONS ---")

print(
    result["operations_assessment"]
    .model_dump_json(indent=2)
)


print("\n--- WEATHER ---")

print(
    result["weather_assessment"]
    .model_dump_json(indent=2)
)


print("\n--- ANALYSIS ---")

print(
    result["analysis_assessment"]
    .model_dump_json(indent=2)
)


print("\n--- VERIFICATION ---")

print(
    result["verification_assessment"]
    .model_dump_json(indent=2)
)