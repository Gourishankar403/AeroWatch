from datetime import datetime, timezone

from app.agents.revision_agent import RevisionAgent
from app.agents.verification_agent import VerificationAgent

from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.analysis import AnalysisAssessment


def main():

    # --------------------------------------------------
    # Create controlled test evidence
    # --------------------------------------------------

    operations = OperationsAssessment(
        airport="TEST",
        disruption_detected=False,
        event_count=0,
        findings=[
            "No operational disruption detected."
        ],
        limitations=[
            "This assessment reflects controlled test operational evidence."
        ],
        evidence={
            "airport": "TEST",
            "source": "test",
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "events": [],
            "summary": "No operational events detected."
        },
    )

    weather = WeatherAssessment(
        airport="TEST",
        weather_risk_detected=False,
        risk_level="low",
        findings=[
            "No significant weather risk detected."
        ],
        limitations=[
            "This assessment reflects controlled test weather evidence."
        ],
        evidence={
            "airport": "TEST",
            "source": "test",
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "temperature_c": 20.0,
            "wind_speed_knots": 5.0,
            "wind_gust_knots": None,
            "visibility_meters": None,
            "visibility_raw": "10+",
            "weather_conditions": [],
            "flight_category": "VFR",
            "raw_observation": "TEST METAR"
        },
    )

    # --------------------------------------------------
    # Deliberately create flawed analysis
    # --------------------------------------------------

    analysis = AnalysisAssessment(
        airport="TEST",
        observed_facts=[
            "No operational disruption detected."
        ],
        potential_factors=[
            "Weather conditions may influence operations."
        ],
        overall_assessment=(
            "Weather conditions caused a significant "
            "operational disruption at the airport."
        ),
        confidence="high",
        limitations=[],
    )

    verifier = VerificationAgent()
    revision_agent = RevisionAgent()

    revision_count = 0
    max_revisions = 2

    # --------------------------------------------------
    # Initial verification
    # --------------------------------------------------

    verification = verifier.verify(
        operations=operations,
        weather=weather,
        analysis=analysis,
    )

    print("\n===== INITIAL VERIFICATION =====\n")

    print(
        verification.model_dump_json(
            indent=2
        )
    )

    # --------------------------------------------------
    # Revision loop
    # --------------------------------------------------

    while (
        not verification.approved
        and revision_count < max_revisions
    ):

        revision_count += 1

        print(
            f"\n===== REVISION ATTEMPT "
            f"{revision_count} =====\n"
        )

        analysis = revision_agent.revise(
            operations=operations,
            weather=weather,
            analysis=analysis,
            verification=verification,
        )

        print(
            analysis.model_dump_json(
                indent=2
            )
        )

        verification = verifier.verify(
            operations=operations,
            weather=weather,
            analysis=analysis,
        )

        print(
            "\n===== VERIFICATION AFTER REVISION =====\n"
        )

        print(
            verification.model_dump_json(
                indent=2
            )
        )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    print("\n===== FINAL RESULT =====\n")

    print(
        f"Total revisions performed: "
        f"{revision_count}"
    )

    print(
        f"Final approval status: "
        f"{verification.approved}"
    )

    if verification.approved:
        print(
            "\nRevision loop successfully "
            "produced an evidence-grounded analysis."
        )
    else:
        print(
            "\nMaximum revision limit reached "
            "without approval."
        )


if __name__ == "__main__":
    main()