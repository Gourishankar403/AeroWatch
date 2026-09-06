from app.providers.weather_provider import WeatherProvider


provider = WeatherProvider()

result = provider.get_weather("KJFK")

print(result.model_dump_json(indent=2))