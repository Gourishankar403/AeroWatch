from app.models.weather import WeatherEvidence
from app.providers.weather_provider import WeatherProvider


class WeatherTool:

    """
    Tool for retrieving current aviation weather
    evidence for an airport.
    """

    def __init__(self):
        self.weather_provider = WeatherProvider()

    def get_weather(
        self,
        airport: str
    ) -> WeatherEvidence:

        return self.weather_provider.get_weather(
            airport
        )