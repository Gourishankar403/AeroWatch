from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.analysis import AnalysisAssessment
from app.models.operations import (
    OperationalEvent,
    OperationsAssessment,
    OperationsEvidence,
)
from app.models.weather import (
    WeatherAssessment,
    WeatherEvidence,
)


@dataclass
class EvaluationCase:
    """
    Defines one controlled AeroWatch evaluation scenario.

    Each case contains:
    - deterministic operational evidence
    - deterministic weather evidence
    - expected system behavior
    """

    name: str
    description: str
    operations: OperationsAssessment
    weather: WeatherAssessment

    expected_disruption: bool
    expected_weather_risk: bool
    expected_causation_violation: bool = False


# ============================================================
# Helper functions
# ============================================================

def make_operations_assessment(
    airport: str,
    disruption_detected: bool,
    event_count: int,
    findings: list[str],
    limitations: list[str],
    events: list[OperationalEvent],
) -> OperationsAssessment:

    evidence = OperationsEvidence(
        airport=airport,
        source="FAA NAS",
        retrieved_at="2026-01-01T12:00:00Z",
        events=events,
        summary=(
            "Active FAA operational events found."
            if events
            else "No active FAA operational events found."
        ),
    )

    return OperationsAssessment(
        airport=airport,
        disruption_detected=disruption_detected,
        event_count=event_count,
        findings=findings,
        limitations=limitations,
        evidence=evidence,
    )


def make_weather_assessment(
    airport: str,
    weather_risk_detected: bool,
    risk_level: str,
    findings: list[str],
    limitations: list[str],
    flight_category: str | None,
    wind_speed_knots: float | None,
    visibility_meters: float | None,
) -> WeatherAssessment:

    evidence = WeatherEvidence(
        airport=airport,
        source="Aviation Weather Center",
        retrieved_at="2026-01-01T12:00:00Z",
        temperature_c=20.0,
        wind_speed_knots=wind_speed_knots,
        wind_gust_knots=None,
        visibility_meters=visibility_meters,
        visibility_raw=None,
        weather_conditions=[],
        flight_category=flight_category,
        raw_observation="CONTROLLED EVALUATION OBSERVATION",
    )

    return WeatherAssessment(
        airport=airport,
        weather_risk_detected=weather_risk_detected,
        risk_level=risk_level,
        findings=findings,
        limitations=limitations,
        evidence=evidence,
    )


# ============================================================
# Common limitations
# ============================================================

FAA_LIMITATIONS = [
    "This is controlled evaluation evidence.",
    "FAA operational status represents the available "
    "operational information at retrieval time.",
]

WEATHER_LIMITATIONS = [
    "This is controlled evaluation evidence.",
    "Weather observations represent conditions at the "
    "time of observation and may change.",
    "Potential weather risk does not establish that weather "
    "is the direct cause of an operational disruption.",
]


# ============================================================
# Evaluation cases
# ============================================================

def build_evaluation_cases() -> list[EvaluationCase]:
    """
    Build the complete controlled AeroWatch evaluation suite.
    """

    cases: list[EvaluationCase] = []

    # --------------------------------------------------------
    # CASE 1 — Normal conditions
    # --------------------------------------------------------

    cases.append(
        EvaluationCase(
            name="normal_conditions",
            description=(
                "No FAA operational disruption and normal "
                "VFR weather conditions."
            ),
            operations=make_operations_assessment(
                airport="KJFK",
                disruption_detected=False,
                event_count=0,
                findings=[
                    "No active FAA operational events "
                    "were found for KJFK."
                ],
                limitations=FAA_LIMITATIONS,
                events=[],
            ),
            weather=make_weather_assessment(
                airport="KJFK",
                weather_risk_detected=False,
                risk_level="low",
                findings=[
                    "Current flight category is VFR.",
                    "Wind speed is 8 knots.",
                    "Visibility is 10,000 meters.",
                ],
                limitations=WEATHER_LIMITATIONS,
                flight_category="VFR",
                wind_speed_knots=8.0,
                visibility_meters=10000.0,
            ),
            expected_disruption=False,
            expected_weather_risk=False,
        )
    )

    # --------------------------------------------------------
    # CASE 2 — Operational disruption
    # --------------------------------------------------------

    cases.append(
        EvaluationCase(
            name="operational_disruption",
            description=(
                "FAA reports an active ground delay while "
                "weather remains normal."
            ),
            operations=make_operations_assessment(
                airport="KJFK",
                disruption_detected=True,
                event_count=1,
                findings=[
                    "An active FAA ground delay is reported "
                    "for KJFK."
                ],
                limitations=FAA_LIMITATIONS,
                events=[
                    OperationalEvent(
                        event_type="ground_delay",
                        description=(
                            "Ground delay program is active."
                        ),
                        cause=None,
                        severity="medium",
                    )
                ],
            ),
            weather=make_weather_assessment(
                airport="KJFK",
                weather_risk_detected=False,
                risk_level="low",
                findings=[
                    "Current flight category is VFR.",
                    "Wind speed is 8 knots.",
                ],
                limitations=WEATHER_LIMITATIONS,
                flight_category="VFR",
                wind_speed_knots=8.0,
                visibility_meters=10000.0,
            ),
            expected_disruption=True,
            expected_weather_risk=False,
        )
    )

    # --------------------------------------------------------
    # CASE 3 — Weather risk
    # --------------------------------------------------------

    cases.append(
        EvaluationCase(
            name="weather_risk",
            description=(
                "No FAA operational event exists, but weather "
                "conditions indicate elevated operational risk."
            ),
            operations=make_operations_assessment(
                airport="KJFK",
                disruption_detected=False,
                event_count=0,
                findings=[
                    "No active FAA operational events "
                    "were found for KJFK."
                ],
                limitations=FAA_LIMITATIONS,
                events=[],
            ),
            weather=make_weather_assessment(
                airport="KJFK",
                weather_risk_detected=True,
                risk_level="high",
                findings=[
                    "Current flight category is LIFR.",
                    "Visibility is significantly reduced.",
                    "Low visibility may affect airport operations."
                ],
                limitations=WEATHER_LIMITATIONS,
                flight_category="LIFR",
                wind_speed_knots=18.0,
                visibility_meters=800.0,
            ),
            expected_disruption=False,
            expected_weather_risk=True,
        )
    )

    # --------------------------------------------------------
    # CASE 4 — Operational disruption + weather risk
    # --------------------------------------------------------

    cases.append(
        EvaluationCase(
            name="combined_disruption_and_weather",
            description=(
                "FAA reports an operational event while "
                "weather simultaneously presents elevated risk."
            ),
            operations=make_operations_assessment(
                airport="KJFK",
                disruption_detected=True,
                event_count=1,
                findings=[
                    "An active FAA ground delay is reported "
                    "for KJFK."
                ],
                limitations=FAA_LIMITATIONS,
                events=[
                    OperationalEvent(
                        event_type="ground_delay",
                        description=(
                            "Ground delay program is active."
                        ),
                        cause=None,
                        severity="high",
                    )
                ],
            ),
            weather=make_weather_assessment(
                airport="KJFK",
                weather_risk_detected=True,
                risk_level="high",
                findings=[
                    "Current flight category is IFR.",
                    "Visibility is reduced.",
                    "Weather conditions may present "
                    "operational risk."
                ],
                limitations=WEATHER_LIMITATIONS,
                flight_category="IFR",
                wind_speed_knots=20.0,
                visibility_meters=2000.0,
            ),
            expected_disruption=True,
            expected_weather_risk=True,
        )
    )

    # --------------------------------------------------------
    # CASE 5 — Causation trap
    # --------------------------------------------------------

    cases.append(
        EvaluationCase(
            name="causation_trap",
            description=(
                "FAA disruption and adverse weather are both "
                "present, but the evidence does not establish "
                "that weather caused the disruption."
            ),
            operations=make_operations_assessment(
                airport="KJFK",
                disruption_detected=True,
                event_count=1,
                findings=[
                    "An active FAA ground delay is reported "
                    "for KJFK."
                ],
                limitations=FAA_LIMITATIONS,
                events=[
                    OperationalEvent(
                        event_type="ground_delay",
                        description=(
                            "Ground delay program is active."
                        ),
                        cause=None,
                        severity="high",
                    )
                ],
            ),
            weather=make_weather_assessment(
                airport="KJFK",
                weather_risk_detected=True,
                risk_level="high",
                findings=[
                    "Current flight category is IFR.",
                    "Visibility is reduced."
                ],
                limitations=WEATHER_LIMITATIONS,
                flight_category="IFR",
                wind_speed_knots=25.0,
                visibility_meters=1500.0,
            ),
            expected_disruption=True,
            expected_weather_risk=True,
            expected_causation_violation=True,
        )
    )

    return cases


# ============================================================
# Public accessor
# ============================================================

def get_evaluation_cases() -> list[EvaluationCase]:
    """
    Return all controlled AeroWatch evaluation cases.
    """

    return build_evaluation_cases()