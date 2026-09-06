from datetime import datetime, timezone

import httpx

from app.models.weather import WeatherEvidence


class WeatherProvider:

    """
    Retrieves aviation weather observations from the
    NOAA Aviation Weather Center API.
    """

    BASE_URL = "https://aviationweather.gov/api/data/metar"

    def get_weather(
        self,
        airport: str
    ) -> WeatherEvidence:

        airport = airport.upper()

        params = {
            "ids": airport,
            "format": "json"
        }

        response = httpx.get(
            self.BASE_URL,
            params=params,
            timeout=10.0,
            headers={
                "User-Agent": "AeroWatch/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        # API may return an empty list when no observation exists
        if not data:
            return WeatherEvidence(
                airport=airport,
                source="NOAA Aviation Weather Center",
                retrieved_at=datetime.now(timezone.utc),
                weather_conditions=[],
                raw_observation=None
            )

        observation = data[0]

        return WeatherEvidence(
            airport=observation.get("icaoId", airport),
            source="NOAA Aviation Weather Center",
            retrieved_at=datetime.now(timezone.utc),

            temperature_c=observation.get("temp"),

            wind_speed_knots=observation.get("wspd"),

            wind_gust_knots=observation.get("wgst"),

            visibility_raw=observation.get("visib"),

            weather_conditions=[],

            flight_category=observation.get("fltCat"),

            raw_observation=observation.get("rawOb")
        )