from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment


class AnalysisAgent:
    """
    Combines evidence from multiple investigation agents
    into an evidence-grounded assessment.
    """

    def analyze(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
    ) -> AnalysisAssessment:

        observed_facts = []
        potential_factors = []
        limitations = []

        # -------------------------
        # Operations evidence
        # -------------------------

        if operations.disruption_detected:
            observed_facts.append(
                f"{operations.event_count} active FAA operational "
                f"event(s) were detected for {operations.airport}."
            )

            for finding in operations.findings[1:]:
                observed_facts.append(finding)

        else:
            observed_facts.append(
                f"No active FAA operational events were found "
                f"for {operations.airport}."
            )

        limitations.extend(operations.limitations)

        # -------------------------
        # Weather evidence
        # -------------------------

        if weather.evidence.flight_category:
            observed_facts.append(
                f"Current flight category is "
                f"{weather.evidence.flight_category}."
            )

        if weather.evidence.wind_speed_knots is not None:
            observed_facts.append(
                f"Observed wind speed is "
                f"{weather.evidence.wind_speed_knots} knots."
            )

        if weather.weather_risk_detected:
            potential_factors.append(
                f"Current weather conditions may contribute to "
                f"aviation operational constraints "
                f"(risk level: {weather.risk_level})."
            )

        else:
            potential_factors.append(
                "Available weather evidence does not currently "
                "indicate elevated weather-related operational risk."
            )

        limitations.extend(weather.limitations)

        # -------------------------
        # Overall assessment
        # -------------------------

        if (
            operations.disruption_detected
            and weather.weather_risk_detected
        ):
            overall_assessment = (
                "An active operational disruption is reported, and "
                "weather conditions represent a potential contributing "
                "factor. The available evidence does not establish "
                "direct causation."
            )

            confidence = "medium"

        elif operations.disruption_detected:
            overall_assessment = (
                "An active operational disruption is reported. "
                "Available weather evidence does not currently indicate "
                "elevated weather-related operational risk."
            )

            confidence = "medium"

        elif weather.weather_risk_detected:
            overall_assessment = (
                "No active FAA operational event was detected, but "
                "current weather conditions may present an operational "
                "risk."
            )

            confidence = "low"

        else:
            overall_assessment = (
                "Available evidence does not currently indicate a "
                "significant operational disruption or elevated "
                "weather-related risk."
            )

            confidence = "medium"

        return AnalysisAssessment(
            airport=operations.airport,
            observed_facts=observed_facts,
            potential_factors=potential_factors,
            overall_assessment=overall_assessment,
            confidence=confidence,
            limitations=limitations,
        )