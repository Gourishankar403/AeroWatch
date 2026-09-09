from datetime import datetime, timezone

from app.agents.revision_agent import RevisionAgent
from app.agents.verification_agent import VerificationAgent

from app.models.analysis import AnalysisAssessment

from app.models.operations import (
    OperationsAssessment,
    OperationsEvidence,
)

from app.models.weather import (
    WeatherAssessment,
    WeatherEvidence,
)


def main():

    print("\n===== AEROWATCH LLM REVISION TEST =====\n")

    retrieved_at = datetime.now(timezone.utc)

    # --------------------------------------------------
    # Operational evidence
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
    # Weather evidence
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
    # Deliberately BAD analysis
    # --------------------------------------------------

    bad_analysis = AnalysisAssessment(
        airport="KJFK",

        observed_facts=[
            "No active FAA operational events were detected.",
            "Current flight category is VFR.",
        ],

        potential_factors=[
            "Weather conditions caused the airport disruption."
        ],

        overall_assessment=(
            "Poor weather caused an operational disruption "
            "at KJFK."
        ),

        confidence="high",

        limitations=[],
    )

    print("===== INITIAL BAD ANALYSIS =====\n")

    print(
        bad_analysis.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------
    # Run deterministic verification
    # --------------------------------------------------

    verifier = VerificationAgent()

    verification = verifier.verify(
        operations=operations,
        weather=weather,
        analysis=bad_analysis,
    )

    print("\n===== INITIAL VERIFICATION =====\n")

    print(
        verification.model_dump_json(
            indent=2
        )
    )

    assert verification.approved is False

    print("\nVerification correctly rejected the bad analysis.")

    # --------------------------------------------------
    # Run LLM Revision Agent
    # --------------------------------------------------

    reviser = RevisionAgent()

    print("\n===== RUNNING LLM REVISION =====\n")

    revised_analysis = reviser.revise(
        operations=operations,
        weather=weather,
        analysis=bad_analysis,
        verification=verification,
    )

    # --------------------------------------------------
    # Display revised analysis
    # --------------------------------------------------

    print("===== REVISED ANALYSIS =====\n")

    print(
        revised_analysis.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------
    # Verify revised analysis
    # --------------------------------------------------

    final_verification = verifier.verify(
        operations=operations,
        weather=weather,
        analysis=revised_analysis,
    )

    print("\n===== FINAL VERIFICATION =====\n")

    print(
        final_verification.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------
    # Final assertions
    # --------------------------------------------------

    assert revised_analysis.airport == "KJFK"

    assert final_verification.approved is True

    print(
        "\n===== ALL REVISION TESTS PASSED ====="
    )

    print(
        "\nThe LLM RevisionAgent successfully corrected "
        "the evidence-grounding failure."
    )


if __name__ == "__main__":
    main()