from app.agents.operations_investigator import OperationsInvestigator
from app.agents.weather_investigator import WeatherInvestigator
from app.agents.verification_agent import VerificationAgent

from app.models.analysis import AnalysisAssessment


def main():

    airport = "KJFK"

    # Collect real evidence
    operations_agent = OperationsInvestigator()
    weather_agent = WeatherInvestigator()

    operations = operations_agent.investigate(airport)
    weather = weather_agent.investigate(airport)

    # ------------------------------------------------
    # Intentionally create an unsupported conclusion
    # ------------------------------------------------

    bad_analysis = AnalysisAssessment(
        airport=airport,

        observed_facts=[
            "Weather conditions were observed at the airport."
        ],

        potential_factors=[
            "Weather may affect aviation operations."
        ],

        overall_assessment=(
            "Severe weather caused significant disruption "
            "at JFK airport."
        ),

        confidence="high",

        limitations=[],
    )

    # Verify the intentionally bad analysis
    verification_agent = VerificationAgent()

    verification = verification_agent.verify(
        operations=operations,
        weather=weather,
        analysis=bad_analysis,
    )

    print("\n===== ADVERSARIAL VERIFICATION TEST =====\n")

    print(verification.model_dump_json(indent=2))


if __name__ == "__main__":
    main()