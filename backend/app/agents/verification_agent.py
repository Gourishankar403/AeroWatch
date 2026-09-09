from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.verification import VerificationAssessment


def _contains_positive_disruption_claim(text: str) -> bool:
    """
    Detect whether the analysis positively claims that
    an operational disruption exists.

    This intentionally avoids flagging negated statements such as:
    - no operational disruption
    - no evidence of an operational disruption
    - no active operational disruption
    - no disruption detected
    - does not indicate an operational disruption
    """

    negative_patterns = [
        "no operational disruption",
        "no evidence of an operational disruption",
        "no active operational disruption",
        "no airport disruption",
        "no evidence of an airport disruption",
        "no disruption is occurring",
        "no disruption detected",
        "does not indicate an operational disruption",
        "does not indicate an airport disruption",
        "without an operational disruption",
        "without operational disruption",
        "not experiencing an operational disruption",
        "not operationally disrupted",
        "no evidence of disruption",
        "no active disruption",
    ]

    for pattern in negative_patterns:
        if pattern in text:
            return False

    positive_patterns = [
        "operational disruption is occurring",
        "an operational disruption is occurring",
        "operational disruption is occurring",
        "airport disruption is occurring",
        "the airport is disrupted",
        "operations are disrupted",
        "operationally disrupted",
        "significant disruption",
        "experiencing disruption",
        "undergoing disruption",
        "disruption is occurring",
        "significant delays are occurring",
        "flight delays are occurring",
        "ground delay is active",
        "ground stop is active",
    ]

    return any(pattern in text for pattern in positive_patterns)


class VerificationAgent:
    """
    Deterministically verifies whether an AeroWatch analysis
    is adequately supported by the collected evidence.

    The verifier does NOT generate new conclusions.
    It checks whether the existing analysis is consistent
    with the evidence collected from the investigation agents.
    """

    def verify(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
        analysis: AnalysisAssessment,
    ) -> VerificationAssessment:

        issues: list[str] = []
        missing_evidence: list[str] = []

        assessment_text = analysis.overall_assessment.lower()

        # ---------------------------------------------------------
        # 1. Operational disruption grounding
        # ---------------------------------------------------------
        #
        # If FAA reports no active operational event, the analysis
        # must not positively claim that a disruption exists.
        #
        if not operations.disruption_detected:
            if _contains_positive_disruption_claim(assessment_text):
                issues.append(
                    "The analysis claims or implies an operational "
                    "disruption, but no active FAA operational event "
                    "was detected."
                )

        # ---------------------------------------------------------
        # 2. Unsupported causal claims
        # ---------------------------------------------------------
        #
        # AeroWatch should distinguish correlation from causation.
        # The available evidence generally does not prove that
        # weather caused an operational event.
        #
        causal_patterns = [
            "caused by",
            "caused the",
            "caused an",
            "caused a",
            "causes",
            "caused",
            "due to",
            "resulted from",
            "resulted in",
            "led to",
            "responsible for",
            "direct cause",
            "directly caused",
        ]

        for pattern in causal_patterns:
            if pattern in assessment_text:
                issues.append(
                    "The analysis may imply direct causation "
                    "without sufficient evidence."
                )
                break

        # ---------------------------------------------------------
        # 3. Explicit weather-causation claims
        # ---------------------------------------------------------
        #
        # This is intentionally stricter than the generic causal
        # check because weather is one of AeroWatch's evidence
        # sources.
        #
        weather_causal_patterns = [
            "weather caused",
            "weather conditions caused",
            "weather is causing",
            "weather directly caused",
            "weather resulted in",
            "weather led to",
            "poor weather caused",
            "bad weather caused",
            "low visibility caused",
            "strong winds caused",
            "wind caused",
            "storm caused",
            "thunderstorms caused",
            "fog caused",
        ]

        for pattern in weather_causal_patterns:
            if pattern in assessment_text:
                issue = (
                    "The analysis attributes an operational "
                    "disruption directly to weather without "
                    "explicit causal evidence."
                )

                if issue not in issues:
                    issues.append(issue)

                break

        # ---------------------------------------------------------
        # 4. Excessive certainty
        # ---------------------------------------------------------
        #
        # Strong certainty language can exceed what the available
        # evidence supports.
        #
        certainty_patterns = [
            "definitely",
            "certainly",
            "proves that",
            "proven that",
            "confirmed that",
            "without doubt",
            "undoubtedly",
        ]

        for pattern in certainty_patterns:
            if pattern in assessment_text:
                issues.append(
                    "The analysis uses strong certainty language "
                    "that may exceed the available evidence."
                )
                break

        # ---------------------------------------------------------
        # 5. Required evidence checks
        # ---------------------------------------------------------

        if operations.evidence is None:
            missing_evidence.append(
                "Operational evidence is missing."
            )

        if weather.evidence is None:
            missing_evidence.append(
                "Weather evidence is missing."
            )

        # ---------------------------------------------------------
        # 6. Limitations preservation
        # ---------------------------------------------------------

        if not analysis.limitations:
            issues.append(
                "The analysis does not preserve evidence limitations."
            )

        # ---------------------------------------------------------
        # 7. Airport consistency
        # ---------------------------------------------------------

        if analysis.airport != operations.airport:
            issues.append(
                "The analysis airport does not match the "
                "investigated airport."
            )

        if analysis.airport != weather.airport:
            issues.append(
                "The analysis airport does not match the "
                "weather evidence airport."
            )

        # ---------------------------------------------------------
        # 8. Observed facts requirement
        # ---------------------------------------------------------

        if not analysis.observed_facts:
            issues.append(
                "The analysis does not contain any observed facts."
            )

        # ---------------------------------------------------------
        # 9. Confidence validation
        # ---------------------------------------------------------

        valid_confidence_levels = {
            "low",
            "medium",
            "high",
        }

        if analysis.confidence.lower() not in valid_confidence_levels:
            issues.append(
                "The analysis contains an invalid confidence level."
            )

        # ---------------------------------------------------------
        # 10. Final verification decision
        # ---------------------------------------------------------

        approved = (
            len(issues) == 0
            and len(missing_evidence) == 0
        )

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