from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.verification import VerificationAssessment


def _phrase_is_negated(
    text: str,
    phrase: str,
) -> bool:
    """
    Check whether a phrase occurs in a clearly negated
    context.

    This is intentionally lightweight and deterministic.
    It is not intended to be a full NLP parser.
    """

    index = text.find(phrase)

    if index == -1:
        return False

    context_start = max(0, index - 100)
    context = text[context_start:index]

    negation_patterns = [
        "no ",
        "not ",
        "does not ",
        "do not ",
        "did not ",
        "without ",
        "never ",
        "neither ",
        "cannot ",
        "can't ",
        "isn't ",
        "is not ",
        "wasn't ",
        "was not ",
        "were not ",
        "are not ",
        "there is no ",
        "there was no ",
        "doesn't ",
        "didn't ",
    ]

    return any(
        negation in context
        for negation in negation_patterns
    )


def _contains_positive_disruption_claim(
    text: str,
) -> bool:
    """
    Detect whether the analysis positively claims that
    an operational disruption exists.
    """

    positive_patterns = [
        "operational disruption is occurring",
        "an operational disruption is occurring",
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
        "active faa ground delay",
        "active faa ground delay program",
    ]

    for pattern in positive_patterns:

        if pattern not in text:
            continue

        if not _phrase_is_negated(
            text,
            pattern,
        ):
            return True

    return False


def _contains_positive_weather_risk_claim(
    text: str,
) -> bool:
    """
    Detect whether the analysis positively claims that
    weather-related operational risk exists.
    """

    positive_patterns = [
        "high weather risk",
        "high operational risk",
        "elevated weather risk",
        "elevated operational risk",
        "significant weather risk",
        "severe weather risk",
        "hazardous weather",
        "hazardous weather conditions",
        "weather conditions are hazardous",
        "potentially disruptive weather",
        "weather conditions are potentially disruptive",
        "reduced visibility",
        "lifr",
        "ifr conditions",
    ]

    for pattern in positive_patterns:

        if pattern not in text:
            continue

        if not _phrase_is_negated(
            text,
            pattern,
        ):
            return True

    return False


class VerificationAgent:
    """
    Deterministic verification layer for AeroWatch.

    The verifier checks:

    1. Airport consistency
    2. Structured operational consistency
    3. Structured weather-risk consistency
    4. Textual grounding
    5. Unsupported causal claims
    6. Excessive certainty
    7. Required evidence
    8. Required analysis fields
    9. Confidence validity
    """

    def verify(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
        analysis: AnalysisAssessment,
    ) -> VerificationAssessment:

        issues: list[str] = []
        missing_evidence: list[str] = []

        assessment_text = (
            analysis.overall_assessment.lower()
        )

        # ====================================================
        # 1. Airport consistency
        # ====================================================

        if analysis.airport != operations.airport:
            issues.append(
                "The analysis airport does not match "
                "the investigated airport."
            )

        if analysis.airport != weather.airport:
            issues.append(
                "The analysis airport does not match "
                "the weather evidence airport."
            )

        # ====================================================
        # 2. Structured operational consistency
        # ====================================================

        if (
            analysis.disruption_detected
            != operations.disruption_detected
        ):
            issues.append(
                "The analysis disruption_detected value does "
                "not match the operational evidence."
            )

        # ====================================================
        # 3. Structured weather-risk consistency
        # ====================================================

        if (
            analysis.weather_risk_detected
            != weather.weather_risk_detected
        ):
            issues.append(
                "The analysis weather_risk_detected value does "
                "not match the weather evidence."
            )

        # ====================================================
        # 4. Textual operational grounding
        # ====================================================

        if not operations.disruption_detected:

            if _contains_positive_disruption_claim(
                assessment_text
            ):
                issues.append(
                    "The analysis claims or implies an "
                    "operational disruption, but no active "
                    "FAA operational event was detected."
                )

        # ====================================================
        # 5. Textual weather-risk grounding
        # ====================================================

        if not weather.weather_risk_detected:

            if _contains_positive_weather_risk_claim(
                assessment_text
            ):
                issues.append(
                    "The analysis claims or implies elevated "
                    "weather risk, but the weather assessment "
                    "does not indicate weather risk."
                )

        # ====================================================
        # 6. Unsupported causation
        # ====================================================

        causal_patterns = [
            "weather caused",
            "weather conditions caused",
            "weather directly caused",
            "poor weather caused",
            "bad weather caused",
            "low visibility caused",
            "strong winds caused",
            "wind caused",
            "storm caused",
            "thunderstorms caused",
            "fog caused",
            "weather resulted in",
            "weather led to",
            "weather was responsible for",
            "weather is responsible for",
            "weather directly resulted in",
            "weather directly led to",
            "the disruption was caused by weather",
            "the disruption was caused by the weather",
            "the operational disruption was caused by weather",
            "the operational disruption was caused by the weather",
            "the delay was caused by weather",
            "the delay was caused by the weather",
            "the ground delay was caused by weather",
            "the ground delay was caused by the weather",
            "the disruption resulted from weather",
            "the disruption resulted from the weather",
            "the operational disruption resulted from weather",
            "the operational disruption resulted from the weather",
            "the disruption was due to weather",
            "the disruption was due to the weather",
            "the operational disruption was due to weather",
            "the operational disruption was due to the weather",
            "the delay was due to weather",
            "the delay was due to the weather",
            "the ground delay was due to weather",
            "the ground delay was due to the weather",
        ]

        causal_violation = False

        for pattern in causal_patterns:

            if pattern not in assessment_text:
                continue

            if _phrase_is_negated(
                assessment_text,
                pattern,
            ):
                continue

            causal_violation = True
            break

        if causal_violation:

            issues.append(
                "The analysis may imply direct causation "
                "without sufficient evidence."
            )

            issues.append(
                "The analysis attributes an operational "
                "disruption directly to weather without "
                "explicit causal evidence."
            )

        # ====================================================
        # 7. Strong certainty language
        # ====================================================

        certainty_patterns = [
            "definitely",
            "certainly",
            "proves that",
            "proven that",
            "confirmed that",
            "without doubt",
            "undoubtedly",
        ]

        if any(
            pattern in assessment_text
            for pattern in certainty_patterns
        ):
            issues.append(
                "The analysis uses strong certainty language "
                "that may exceed the available evidence."
            )

        # ====================================================
        # 8. Required evidence
        # ====================================================

        if operations.evidence is None:
            missing_evidence.append(
                "Operational evidence is missing."
            )

        if weather.evidence is None:
            missing_evidence.append(
                "Weather evidence is missing."
            )

        # ====================================================
        # 9. Required analysis fields
        # ====================================================

        if not analysis.limitations:
            issues.append(
                "The analysis does not preserve evidence "
                "limitations."
            )

        if not analysis.observed_facts:
            issues.append(
                "The analysis does not contain any observed facts."
            )

        # ====================================================
        # 10. Confidence validation
        # ====================================================

        valid_confidence_levels = {
            "low",
            "medium",
            "high",
        }

        if (
            analysis.confidence.lower()
            not in valid_confidence_levels
        ):
            issues.append(
                "The analysis contains an invalid "
                "confidence level."
            )

        # ====================================================
        # 11. Final decision
        # ====================================================

        approved = (
            len(issues) == 0
            and len(missing_evidence) == 0
        )

        if approved:

            verification_summary = (
                "The analysis is adequately supported by "
                "the available operational and weather "
                "evidence."
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