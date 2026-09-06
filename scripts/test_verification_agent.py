from app.agents.operations_investigator import OperationsInvestigator
from app.agents.weather_investigator import WeatherInvestigator
from app.agents.analysis_agent import AnalysisAgent
from app.agents.verification_agent import VerificationAgent


def main():

    airport = "KJFK"

    # Collect assessments
    operations_agent = OperationsInvestigator()
    weather_agent = WeatherInvestigator()

    operations = operations_agent.investigate(airport)
    weather = weather_agent.investigate(airport)

    # Generate analysis
    analysis_agent = AnalysisAgent()

    analysis = analysis_agent.analyze(
        operations=operations,
        weather=weather,
    )

    # Verify analysis
    verification_agent = VerificationAgent()

    verification = verification_agent.verify(
        operations=operations,
        weather=weather,
        analysis=analysis,
    )

    print("\n===== VERIFICATION RESULT =====\n")

    print(verification.model_dump_json(indent=2))


if __name__ == "__main__":
    main()