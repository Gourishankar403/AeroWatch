import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import httpx

from app.models.operations import OperationalEvent, OperationsEvidence
from app.core.config import settings


class FAAProvider:
    """
    Provider responsible for retrieving aviation operations
    status from the FAA NAS API.
    
    Reliability responsibilities:
    - HTTP timeout handling
    - Retry transient failures
    - Exponential backoff
    - Clear provider-level errors
    """

    BASE_URL = "https://nasstatus.faa.gov/api/airport-status-information"

    def __init__(self):
        # Use existing centralized retry configurations for external APIs
        self.timeout = settings.WEATHER_TIMEOUT
        self.max_retries = settings.WEATHER_MAX_RETRIES
        self.base_retry_delay = settings.WEATHER_RETRY_DELAY

    def _wait_before_retry(self, attempt: int) -> None:
        """
        Exponential backoff.
        """
        delay = self.base_retry_delay * (2 ** attempt)
        print(f"[FAAProvider] Temporary FAA API failure. Retrying in {delay:.1f}s...")
        time.sleep(delay)

    def get_airport_status(self, airport: str) -> OperationsEvidence:
        """
        Fetch active FAA operational events for a specific airport.
        """
        airport = airport.upper()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.get(
                    self.BASE_URL,
                    timeout=self.timeout
                )
                response.raise_for_status()

                root = ET.fromstring(response.text)
                events = []

                for delay_type in root.findall("Delay_type"):
                    event_name = delay_type.findtext("Name")

                    for airport_element in delay_type.iter("Airport"):
                        airport_code = airport_element.findtext("ARPT")

                        if airport_code != airport:
                            continue

                        event = OperationalEvent(
                            event_type=self._normalize_event_type(event_name),
                            description=self._build_description(
                                event_name,
                                airport
                            ),
                            cause=airport_element.findtext("Reason"),
                            start_time=self._parse_time(
                                airport_element.findtext("Start")
                            ),
                            end_time=self._parse_time(
                                airport_element.findtext("Reopen")
                            )
                        )
                        events.append(event)

                return OperationsEvidence(
                    airport=airport,
                    retrieved_at=datetime.now(timezone.utc),
                    events=events,
                    summary=self._build_summary(airport, events)
                )

            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as error:
                last_error = error
                if attempt >= self.max_retries:
                    break
                self._wait_before_retry(attempt)

            except httpx.HTTPStatusError as error:
                last_error = error
                status_code = error.response.status_code
                
                # Retry only temporary server/rate-limit errors.
                if status_code not in {429, 500, 502, 503, 504}:
                    raise RuntimeError(
                        f"FAA API returned a non-retryable "
                        f"HTTP {status_code} error."
                    ) from error
                    
                if attempt >= self.max_retries:
                    break
                self._wait_before_retry(attempt)
                
            except ET.ParseError:
                # Invalid XML is not retryable.
                raise
                
            except Exception as error:
                raise RuntimeError(
                    f"Unexpected FAA provider failure: {error}"
                ) from error

        raise RuntimeError(
            f"FAA API request failed after "
            f"{self.max_retries + 1} attempt(s): "
            f"{last_error}"
        )

    @staticmethod
    def _normalize_event_type(event_name: str | None) -> str:
        if not event_name:
            return "unknown"
        return (
            event_name
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

    @staticmethod
    def _build_description(
        event_name: str | None,
        airport: str
    ) -> str:
        if event_name:
            return f"{event_name} affecting {airport}"
        return f"Operational event affecting {airport}"

    @staticmethod
    def _parse_time(
        time_string: str | None
    ) -> datetime | None:
        return None

    @staticmethod
    def _build_summary(
        airport: str,
        events: list[OperationalEvent]
    ) -> str:
        if not events:
            return f"No active FAA operational events found for {airport}."
        return (
            f"{len(events)} active FAA operational event(s) "
            f"found for {airport}."
        )
