from datetime import datetime, timezone

from app.agents.analysis_agent import AnalysisAgent

from app.models.operations import (
    OperationsAssessment,
    OperationsEvidence,
)

from app.models.weather import (
    WeatherAssessment,
    WeatherEvidence,
)


def main():

    print("\n===== AEROWATCH LLM ANALYSIS TEST =====\n")

    retrieved_at = datetime.now(timezone.utc)

    # --------------------------------------------------
    # Controlled operational evidence
    # --------------------------------------------------

    operations_evidence = OperationsEvidence(
        airport="KJFK",
        source="FAA NAS",
        retrieved_at=retrieved_at,
        events=[],
        summary="No active FAA operational events detected."
    )

    operations = OperationsAssessment(
        airport="KJFK",
        disruption_detected=False,
        event_count=0,
        findings=[
            "No active FAA operational events were detected."
        ],
        limitations=[
            "FAA operational status represents the available "
            "operational information at retrieval time."
        ],
        evidence=operations_evidence,
    )

    # --------------------------------------------------
    # Controlled weather evidence
    # --------------------------------------------------

    weather_evidence = WeatherEvidence(
        airport="KJFK",
        source="NOAA Aviation Weather Center",
        retrieved_at=retrieved_at,
        temperature_c=22.0,
        wind_speed_knots=8.0,
        wind_gust_knots=None,
        visibility_meters=10000.0,
        visibility_raw="10SM",
        weather_conditions=[],
        flight_category="VFR",
        raw_observation=(
            "KJFK 091951Z 18008KT 10SM CLR 22/12 A3012"
        ),
    )

    weather = WeatherAssessment(
        airport="KJFK",
        weather_risk_detected=False,
        risk_level="low",
        findings=[
            "Current flight category is VFR.",
            "Observed wind speed is 8 knots.",
            "No elevated weather-related operational risk "
            "was detected."
        ],
        limitations=[
            "Weather observations represent conditions at "
            "the time of observation and may change."
        ],
        evidence=weather_evidence,
    )

    # --------------------------------------------------
    # Run Analysis Agent
    # --------------------------------------------------

    agent = AnalysisAgent()

    print("Running LLM-powered AnalysisAgent...\n")

    result = agent.analyze(
        operations=operations,
        weather=weather,
    )

    # --------------------------------------------------
    # Display result
    # --------------------------------------------------

    print("===== ANALYSIS RESULT =====\n")

    print(
        result.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    print("\n===== VALIDATION =====")

    assert result.airport == "KJFK"

    assert isinstance(
        result.observed_facts,
        list
    )

    assert isinstance(
        result.potential_factors,
        list
    )

    assert isinstance(
        result.overall_assessment,
        str
    )

    assert isinstance(
        result.confidence,
        str
    )

    assert isinstance(
        result.limitations,
        list
    )

    print("Result type:", type(result).__name__)
    print("Airport:", result.airport)
    print("Confidence:", result.confidence)

    print("\nObserved facts:")

    for fact in result.observed_facts:
        print("-", fact)

    print("\nPotential factors:")

    for factor in result.potential_factors:
        print("-", factor)

    print("\nLimitations:")

    for limitation in result.limitations:
        print("-", limitation)

    print("\nOverall assessment:")
    print(result.overall_assessment)

    print("\n===== ALL VALIDATION CHECKS PASSED =====")


if __name__ == "__main__":
    main()