from app.agents.operations_investigator import OperationsInvestigator
from app.agents.weather_investigator import WeatherInvestigator
from app.graph.state import InvestigationState
from app.agents.verification_agent import VerificationAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.revision_agent import RevisionAgent


def investigate_operations(
    state: InvestigationState,
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
    state: InvestigationState,
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


def analyze_evidence(
    state: InvestigationState,
) -> dict:
    """
    Combines operations and weather assessments
    into a single evidence-grounded analysis.
    """

    analyst = AnalysisAgent()

    assessment = analyst.analyze(
        operations=state["operations_assessment"],
        weather=state["weather_assessment"],
    )

    return {
        "analysis_assessment": assessment
    }


def verify_analysis(
    state: InvestigationState,
) -> dict:
    """
    Verifies whether the generated analysis is
    adequately supported by the available evidence.
    """

    verifier = VerificationAgent()

    assessment = verifier.verify(
        operations=state["operations_assessment"],
        weather=state["weather_assessment"],
        analysis=state["analysis_assessment"],
    )

    return {
        "verification_assessment": assessment
    }


def revise_analysis(
    state: InvestigationState,
) -> dict:
    """
    Revises the analysis when verification identifies
    evidence-grounding or reasoning issues.
    """

    reviser = RevisionAgent()

    revised_assessment = reviser.revise(
        operations=state["operations_assessment"],
        weather=state["weather_assessment"],
        analysis=state["analysis_assessment"],
        verification=state["verification_assessment"],
    )

    return {
        "analysis_assessment": revised_assessment,
        "revision_count": state["revision_count"] + 1,
    }