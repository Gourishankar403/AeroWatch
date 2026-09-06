from app.graph.workflow import build_investigation_graph


graph = build_investigation_graph()

initial_state = {
    "query": "Investigate current operational conditions at JFK airport",
    "airport": "KJFK",
    "operations_assessment": None,
    "weather_assessment": None,
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