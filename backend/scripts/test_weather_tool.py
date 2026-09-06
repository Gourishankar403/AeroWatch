from app.tools.weather_tool import WeatherTool


tool = WeatherTool()

result = tool.get_weather("KJFK")

print(result.model_dump_json(indent=2))