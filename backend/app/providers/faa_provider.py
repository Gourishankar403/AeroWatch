from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import httpx

from app.models.operations import OperationalEvent, OperationsEvidence


class FAAProvider:

    BASE_URL = "https://nasstatus.faa.gov/api/airport-status-information"

    def get_airport_status(self, airport: str) -> OperationsEvidence:
        """
        Fetch active FAA operational events for a specific airport.
        """

        airport = airport.upper()

        response = httpx.get(
            self.BASE_URL,
            timeout=10.0
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

        # We'll improve FAA-specific time parsing later.
        # For now, preserve safety by returning None
        # if parsing isn't reliable.
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