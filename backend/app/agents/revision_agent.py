from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.verification import VerificationAssessment


class RevisionAgent:
    """
    Revises an analysis when the Verification Agent identifies
    evidence-grounding or reasoning issues.
    """

    def revise(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
        analysis: AnalysisAssessment,
        verification: VerificationAssessment,
    ) -> AnalysisAssessment:
        """
        Produces a more conservative analysis based on
        verification feedback and available evidence.
        """

        observed_facts = []
        potential_factors = []
        limitations = []

        # Preserve evidence-grounded operational facts
        observed_facts.extend(
            analysis.observed_facts
        )

        # Preserve evidence-grounded weather facts
        for fact in analysis.potential_factors:
            potential_factors.append(fact)

        # Preserve limitations from source assessments
        limitations.extend(
            operations.limitations
        )

        limitations.extend(
            weather.limitations
        )

        # Add verification concerns as limitations
        for issue in verification.issues:
            limitations.append(
                f"Verification concern: {issue}"
            )

        # Generate a conservative revised assessment
        if operations.disruption_detected:
            overall_assessment = (
                "Available operational evidence indicates an active "
                "airport operational event. The available evidence "
                "supports identifying the event, but does not establish "
                "a direct causal relationship with weather conditions."
            )

            confidence = "medium"

        elif weather.weather_risk_detected:
            overall_assessment = (
                "Available weather evidence indicates conditions that "
                "may present operational risk. However, the available "
                "evidence does not establish that weather is directly "
                "causing an airport operational disruption."
            )

            confidence = "medium"

        else:
            overall_assessment = (
                "Available evidence does not currently establish a "
                "significant operational disruption or a direct causal "
                "relationship between weather conditions and airport "
                "operations."
            )

            confidence = "medium"

        return AnalysisAssessment(
            airport=analysis.airport,
            observed_facts=observed_facts,
            potential_factors=potential_factors,
            overall_assessment=overall_assessment,
            confidence=confidence,
            limitations=limitations,
        )