from app.models.weather import WeatherAssessment
from app.tools.weather_tool import WeatherTool


class WeatherInvestigator:

    """
    Investigates whether current aviation weather conditions
    may be contributing to operational disruption.
    """

    def __init__(self):
        self.weather_tool = WeatherTool()

    def investigate(
        self,
        airport: str
    ) -> WeatherAssessment:

        evidence = self.weather_tool.get_weather(
            airport
        )

        findings = []
        limitations = []

        risk_level = "low"
        weather_risk_detected = False

        # Check flight category
        if evidence.flight_category == "LIFR":

            findings.append(
                "LIFR conditions are currently reported, "
                "indicating significantly restricted flight conditions."
            )

            risk_level = "high"
            weather_risk_detected = True

        elif evidence.flight_category == "IFR":

            findings.append(
                "IFR conditions are currently reported, "
                "which may contribute to reduced airport capacity."
            )

            risk_level = "moderate"
            weather_risk_detected = True

        elif evidence.flight_category == "MVFR":

            findings.append(
                "MVFR conditions are currently reported, "
                "indicating marginal visual flight conditions."
            )

        elif evidence.flight_category == "VFR":

            findings.append(
                "VFR conditions are currently reported."
            )

        # Check wind speed
        if evidence.wind_speed_knots is not None:

            if evidence.wind_speed_knots >= 30:

                findings.append(
                    f"Strong sustained winds of "
                    f"{evidence.wind_speed_knots} knots detected."
                )

                weather_risk_detected = True

                if risk_level == "low":
                    risk_level = "moderate"

            else:

                findings.append(
                    f"Wind speed is {evidence.wind_speed_knots} knots."
                )

        # Check wind gusts
        if evidence.wind_gust_knots is not None:

            if evidence.wind_gust_knots >= 40:

                findings.append(
                    f"Strong wind gusts of "
                    f"{evidence.wind_gust_knots} knots detected."
                )

                weather_risk_detected = True
                risk_level = "high"

        limitations.append(
            "This assessment is based on the latest available "
            "METAR observation."
        )

        limitations.append(
            "Potential weather risk does not establish that weather "
            "is the direct cause of an operational disruption."
        )

        return WeatherAssessment(
            airport=evidence.airport,
            weather_risk_detected=weather_risk_detected,
            risk_level=risk_level,
            findings=findings,
            limitations=limitations,
            evidence=evidence
        )