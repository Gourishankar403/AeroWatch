from app.agents.operations_investigator import OperationsInvestigator
from app.agents.weather_investigator import WeatherInvestigator
from app.graph.state import InvestigationState


def investigate_operations(
    state: InvestigationState
) -> dict:
    """
    LangGraph node that investigates airport
    operational conditions.
    """

    investigator = OperationsInvestigator()

    assessment = investigator.investigate(
        state["airport"]
    )

    return {
        "operations_assessment": assessment
    }


def investigate_weather(
    state: InvestigationState
) -> dict:
    """
    LangGraph node that investigates current
    aviation weather conditions.
    """

    investigator = WeatherInvestigator()

    assessment = investigator.investigate(
        state["airport"]
    )

    return {
        "weather_assessment": assessment
    }