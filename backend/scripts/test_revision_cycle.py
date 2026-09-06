from app.agents.revision_agent import RevisionAgent
from app.agents.verification_agent import VerificationAgent

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment


def main():

    # -----------------------------------
    # Create test operational evidence
    # -----------------------------------

    operations = OperationsAssessment(
        airport="KJFK",
        disruption_detected=False,
        event_count=0,
        findings=[
            "No active FAA operational events were found for KJFK."
        ],
        limitations=[
            "This assessment reflects test operational evidence."
        ],
        evidence={
            "airport": "KJFK",
            "source": "test",
            "retrieved_at": "2026-09-06T12:00:00Z",
            "events": [],
            "summary": "No active operational events."
        },
    )

    # -----------------------------------
    # Create test weather evidence
    # -----------------------------------

    weather = WeatherAssessment(
        airport="KJFK",
        weather_risk_detected=False,
        risk_level="low",
        findings=[
            "VFR conditions are currently reported.",
            "Wind speed is 5 knots."
        ],
        limitations=[
            "This assessment reflects test weather evidence."
        ],
        evidence={
            "airport": "KJFK",
            "source": "test",
            "retrieved_at": "2026-09-06T12:00:00Z",
            "temperature_c": 20.0,
            "wind_speed_knots": 5.0,
            "wind_gust_knots": None,
            "visibility_meters": 10000,
            "visibility_raw": "10SM",
            "weather_conditions": [],
            "flight_category": "VFR",
            "raw_observation": "TEST METAR",
        },
    )

    # -----------------------------------
    # Create intentionally bad analysis
    #
    # This should fail verification because
    # it claims unsupported causation.
    # -----------------------------------

    bad_analysis = AnalysisAssessment(
        airport="KJFK",
        observed_facts=[
            "No active FAA operational events were found."
        ],
        potential_factors=[
            "Weather conditions may influence operations."
        ],
        overall_assessment=(
            "Weather caused a significant operational disruption "
            "at KJFK."
        ),
        confidence="high",
        limitations=[],
    )

    # -----------------------------------
    # Verify the bad analysis
    # -----------------------------------

    verifier = VerificationAgent()

    verification_result = verifier.verify(
        operations=operations,
        weather=weather,
        analysis=bad_analysis,
    )

    print("\n===== INITIAL VERIFICATION =====\n")

    print(
        verification_result.model_dump_json(
            indent=2
        )
    )

    # -----------------------------------
    # Revise the analysis
    # -----------------------------------

    reviser = RevisionAgent()

    revised_analysis = reviser.revise(
        operations=operations,
        weather=weather,
        analysis=bad_analysis,
        verification=verification_result,
    )

    print("\n===== REVISED ANALYSIS =====\n")

    print(
        revised_analysis.model_dump_json(
            indent=2
        )
    )

    # -----------------------------------
    # Verify revised analysis again
    # -----------------------------------

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


if __name__ == "__main__":
    main()