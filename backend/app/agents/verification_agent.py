from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.verification import VerificationAssessment


class VerificationAgent:
    """
    Verifies whether an AeroWatch analysis is adequately
    supported by the collected investigation evidence.
    """

    def verify(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
        analysis: AnalysisAssessment,
    ) -> VerificationAssessment:

        issues = []
        missing_evidence = []

        assessment_text = analysis.overall_assessment.lower()

        # -----------------------------------
        # Check for unsupported disruption claims
        # -----------------------------------

        positive_disruption_claims = [
            "significant operational disruption is occurring",
            "active disruption is occurring",
            "airport is experiencing disruption",
            "operations are significantly disrupted",
        ]

        if operations.disruption_detected is False:
            for claim in positive_disruption_claims:
                if claim in assessment_text:
                    issues.append(
                        "The analysis claims an operational disruption, "
                        "but no active FAA operational event was detected."
                    )
                    break

        # -----------------------------------
        # Check for unsupported weather causation
        # -----------------------------------

        causal_terms = [
            "caused",
            "cause of",
            "due to",
            "resulted in",
        ]

        for term in causal_terms:
            if term in assessment_text:
                issues.append(
                    "The analysis may imply direct causation without "
                    "sufficient evidence."
                )
                break

        # -----------------------------------
        # Check evidence coverage
        # -----------------------------------

        if operations.evidence is None:
            missing_evidence.append(
                "Operational evidence is missing."
            )

        if weather.evidence is None:
            missing_evidence.append(
                "Weather evidence is missing."
            )

        # -----------------------------------
        # Check limitations
        # -----------------------------------

        if not analysis.limitations:
            issues.append(
                "The analysis does not preserve evidence limitations."
            )

        # -----------------------------------
        # Determine verification result
        # -----------------------------------

        approved = len(issues) == 0

        if approved:
            verification_summary = (
                "The analysis is adequately supported by the "
                "available operational and weather evidence."
            )
        else:
            verification_summary = (
                "The analysis contains reasoning or evidence "
                "grounding issues that should be reviewed."
            )

        return VerificationAssessment(
            approved=approved,
            issues=issues,
            missing_evidence=missing_evidence,
            verification_summary=verification_summary,
        )