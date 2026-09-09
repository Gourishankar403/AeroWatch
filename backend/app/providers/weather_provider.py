import os
import time
from datetime import datetime, timezone

import httpx

from app.models.weather import WeatherEvidence


class WeatherProvider:
    """
    Provider responsible for retrieving aviation weather
    observations from the Aviation Weather Center.

    Reliability responsibilities:
    - HTTP timeout handling
    - Retry transient failures
    - Exponential backoff
    - Clear provider-level errors
    """

    BASE_URL = "https://aviationweather.gov/api/data/metar"

    def __init__(self):
        self.timeout = float(
            os.getenv("WEATHER_TIMEOUT", "10")
        )

        self.max_retries = int(
            os.getenv("WEATHER_MAX_RETRIES", "3")
        )

        self.base_retry_delay = float(
            os.getenv("WEATHER_RETRY_DELAY", "1")
        )

    # ---------------------------------------------------------
    # Retry helpers
    # ---------------------------------------------------------

    def _wait_before_retry(self, attempt: int) -> None:
        """
        Exponential backoff.

        Attempt 0 -> base delay
        Attempt 1 -> 2x base delay
        Attempt 2 -> 4x base delay
        """

        delay = self.base_retry_delay * (2 ** attempt)

        print(
            f"[WeatherProvider] Temporary weather API "
            f"failure. Retrying in {delay:.1f}s..."
        )

        time.sleep(delay)

    # ---------------------------------------------------------
    # Weather retrieval
    # ---------------------------------------------------------

    def get_weather(self, airport: str) -> WeatherEvidence:
        """
        Retrieve the latest METAR observation for an airport.

        The provider normalizes the external API response into
        WeatherEvidence so downstream agents never need to
        understand the external API format.
        """

        params = {
            "ids": airport,
            "format": "json",
        }

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:

                response = httpx.get(
                    self.BASE_URL,
                    params=params,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                data = response.json()

                if not data:
                    raise ValueError(
                        f"No weather observation returned for "
                        f"airport {airport}."
                    )

                observation = data[0]

                return self._normalize_observation(
                    airport=airport,
                    observation=observation,
                )

            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as error:

                last_error = error

                if attempt >= self.max_retries:
                    break

                self._wait_before_retry(attempt)

            except httpx.HTTPStatusError as error:

                last_error = error

                status_code = (
                    error.response.status_code
                )

                # Retry only temporary server/rate-limit errors.
                if status_code not in {
                    429,
                    500,
                    502,
                    503,
                    504,
                }:
                    raise RuntimeError(
                        "Weather API returned a non-retryable "
                        f"HTTP {status_code} error."
                    ) from error

                if attempt >= self.max_retries:
                    break

                self._wait_before_retry(attempt)

            except ValueError:
                # Invalid JSON / missing observation is not
                # automatically retryable.
                raise

            except Exception as error:

                raise RuntimeError(
                    "Unexpected weather provider failure: "
                    f"{error}"
                ) from error

        raise RuntimeError(
            "Weather API request failed after "
            f"{self.max_retries + 1} attempt(s): "
            f"{last_error}"
        )

    # ---------------------------------------------------------
    # Response normalization
    # ---------------------------------------------------------

    def _normalize_observation(
        self,
        airport: str,
        observation: dict,
    ) -> WeatherEvidence:
        """
        Convert Aviation Weather Center METAR JSON into
        AeroWatch WeatherEvidence.
        """

        temperature_c = observation.get("temp")

        wind_speed_knots = observation.get(
            "wspd"
        )

        wind_gust_knots = observation.get(
            "wgst"
        )

        visibility_raw = observation.get(
            "visib"
        )

        visibility_meters = (
            self._normalize_visibility(
                visibility_raw
            )
        )

        weather_conditions = []

        raw_wx = observation.get("wx_string")

        if raw_wx:
            weather_conditions = [
                condition.strip()
                for condition in raw_wx.split()
                if condition.strip()
            ]

        flight_category = observation.get(
            "fltcat"
        )

        raw_observation = observation.get(
            "rawOb"
        )

        return WeatherEvidence(
            airport=airport,
            source="Aviation Weather Center",
            retrieved_at=datetime.now(
                timezone.utc
            ),
            temperature_c=temperature_c,
            wind_speed_knots=wind_speed_knots,
            wind_gust_knots=wind_gust_knots,
            visibility_meters=visibility_meters,
            visibility_raw=(
                str(visibility_raw)
                if visibility_raw is not None
                else None
            ),
            weather_conditions=weather_conditions,
            flight_category=flight_category,
            raw_observation=raw_observation,
        )

    # ---------------------------------------------------------
    # Visibility normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_visibility(
        visibility
    ) -> float | None:
        """
        Normalize the Aviation Weather Center visibility
        representation into meters.

        The API may return visibility in statute miles,
        numeric form, or special values.
        """

        if visibility is None:
            return None

        if isinstance(
            visibility,
            (int, float),
        ):
            # Aviation Weather Center visibility is commonly
            # reported in statute miles.
            return float(visibility) * 1609.344

        value = str(visibility).strip().upper()

        if value in {
            "10+",
            "P6SM",
            "6+",
        }:
            return 16093.44

        try:
            return float(value) * 1609.344

        except ValueError:
            return None