from app.agents.weather_investigator import WeatherInvestigator


investigator = WeatherInvestigator()

result = investigator.investigate("KJFK")

print(result.model_dump_json(indent=2))