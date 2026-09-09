from dataclasses import dataclass

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment

from scripts.evaluation.test_cases import (
    get_evaluation_cases,
)


@dataclass
class AdversarialCase:
    """
    Defines an intentionally flawed analysis that should be
    rejected by the VerificationAgent and corrected by the
    RevisionAgent.
    """

    name: str
    description: str

    operations: OperationsAssessment
    weather: WeatherAssessment

    bad_analysis: AnalysisAssessment

    expected_verifier_rejection: bool = True


def get_adversarial_cases() -> list[AdversarialCase]:
    """
    Return the controlled adversarial evaluation cases.
    """

    evaluation_cases = get_evaluation_cases()

    normal_case = evaluation_cases[0]
    disruption_case = evaluation_cases[1]
    combined_case = evaluation_cases[3]

    cases: list[AdversarialCase] = []

    # ========================================================
    # Case 1
    # Hallucinated operational disruption
    # ========================================================

    cases.append(
        AdversarialCase(
            name="hallucinated_disruption",
            description=(
                "FAA evidence reports no active operational "
                "event, but the analysis incorrectly claims "
                "that an operational disruption is occurring."
            ),
            operations=normal_case.operations,
            weather=normal_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KJFK",
                disruption_detected=True,
                weather_risk_detected=False,
                observed_facts=[
                    "VFR weather conditions are present."
                ],
                potential_factors=[],
                overall_assessment=(
                    "KJFK is experiencing an operational "
                    "disruption despite no active FAA "
                    "operational event being reported."
                ),
                confidence="high",
                limitations=[
                    "The available operational evidence "
                    "contains no active FAA event."
                ],
            ),
        )
    )

    # ========================================================
    # Case 2
    # Unsupported weather causation
    # ========================================================

    cases.append(
        AdversarialCase(
            name="unsupported_weather_causation",
            description=(
                "An FAA ground delay and adverse weather are "
                "both present, but the analysis incorrectly "
                "claims that weather caused the disruption."
            ),
            operations=combined_case.operations,
            weather=combined_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KJFK",
                disruption_detected=True,
                weather_risk_detected=True,
                observed_facts=[
                    "An FAA ground delay is active.",
                    "IFR weather conditions are present.",
                    "Visibility is reduced.",
                ],
                potential_factors=[],
                overall_assessment=(
                    "Poor weather caused the active FAA ground "
                    "delay at KJFK."
                ),
                confidence="high",
                limitations=[
                    "The available evidence does not provide "
                    "explicit causal attribution."
                ],
            ),
        )
    )

    # ========================================================
    # Case 3
    # Missing limitations
    # ========================================================

    cases.append(
        AdversarialCase(
            name="missing_limitations",
            description=(
                "The analysis otherwise appears reasonable but "
                "fails to preserve evidence limitations."
            ),
            operations=disruption_case.operations,
            weather=disruption_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KJFK",
                disruption_detected=True,
                weather_risk_detected=False,
                observed_facts=[
                    "An FAA ground delay is active."
                ],
                potential_factors=[],
                overall_assessment=(
                    "An active FAA ground delay is present at KJFK."
                ),
                confidence="high",
                limitations=[],
            ),
        )
    )

    # ========================================================
    # Case 4
    # Wrong airport
    # ========================================================

    cases.append(
        AdversarialCase(
            name="wrong_airport",
            description=(
                "The evidence concerns KJFK, but the analysis "
                "incorrectly identifies the airport as KLAX."
            ),
            operations=disruption_case.operations,
            weather=disruption_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KLAX",
                disruption_detected=True,
                weather_risk_detected=False,
                observed_facts=[
                    "An FAA ground delay is active."
                ],
                potential_factors=[],
                overall_assessment=(
                    "An active FAA ground delay is present "
                    "at KLAX."
                ),
                confidence="medium",
                limitations=[
                    "The available evidence does not establish "
                    "the cause of the operational event."
                ],
            ),
        )
    )

    # ========================================================
    # Case 5
    # Invalid confidence
    # ========================================================

    cases.append(
        AdversarialCase(
            name="invalid_confidence",
            description=(
                "The analysis uses a confidence value outside "
                "the allowed confidence levels."
            ),
            operations=normal_case.operations,
            weather=normal_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KJFK",
                disruption_detected=False,
                weather_risk_detected=False,
                observed_facts=[
                    "No active FAA operational disruption "
                    "is reported.",
                    "Weather conditions are VFR.",
                ],
                potential_factors=[],
                overall_assessment=(
                    "No operational disruption or significant "
                    "weather risk is detected at KJFK."
                ),
                confidence="certain",
                limitations=[
                    "The assessment is limited to the "
                    "available operational and weather evidence."
                ],
            ),
        )
    )

    # ========================================================
    # Case 6
    # Hallucinated weather risk
    # ========================================================

    cases.append(
        AdversarialCase(
            name="hallucinated_weather_risk",
            description=(
                "Weather evidence indicates low risk, but the "
                "analysis incorrectly claims severe weather risk."
            ),
            operations=normal_case.operations,
            weather=normal_case.weather,
            bad_analysis=AnalysisAssessment(
                airport="KJFK",
                disruption_detected=False,
                weather_risk_detected=True,
                observed_facts=[
                    "VFR weather conditions are observed."
                ],
                potential_factors=[],
                overall_assessment=(
                    "Severe weather risk is affecting "
                    "operations at KJFK."
                ),
                confidence="high",
                limitations=[
                    "The available evidence is limited to "
                    "the current weather observation."
                ],
            ),
        )
    )

    return cases