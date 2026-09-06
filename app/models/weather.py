from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherEvidence(BaseModel):

    """
    Normalized weather observation
    collected for a specific airport.
    """

    airport: str = Field(
        ...,
        description="ICAO airport code"
    )

    source: str = Field(
        ...,
        description="Source of weather information"
    )

    retrieved_at: datetime = Field(
        ...,
        description="Time when the weather data was retrieved"
    )

    temperature_c: Optional[float] = Field(
        default=None,
        description="Observed temperature in Celsius"
    )

    wind_speed_knots: Optional[float] = Field(
        default=None,
        description="Observed wind speed in knots"
    )

    wind_gust_knots: Optional[float] = Field(
        default=None,
        description="Observed wind gust speed in knots"
    )

    visibility_meters: Optional[float] = Field(
        default=None,
        description="Normalized visibility in meters when available"
    )

    visibility_raw: Optional[str] = Field(
        default=None,
        description="Original visibility value reported by the source"
    )

    weather_conditions: list[str] = Field(
        default_factory=list,
        description="Reported weather conditions"
    )

    flight_category: Optional[str] = Field(
        default=None,
        description="Aviation flight category such as VFR, MVFR, IFR, or LIFR"
    )

    raw_observation: Optional[str] = Field(
        default=None,
        description="Original METAR observation for traceability"
    )



class WeatherAssessment(BaseModel):
    """
    Assessment derived from aviation weather evidence.
    """

    airport: str = Field(
        ...,
        description="Airport being investigated"
    )

    weather_risk_detected: bool = Field(
        ...,
        description="Whether potentially disruptive weather conditions were detected"
    )

    risk_level: str = Field(
        ...,
        description="Overall weather-related operational risk level"
    )

    findings: list[str] = Field(
        default_factory=list,
        description="Evidence-grounded weather findings"
    )

    limitations: list[str] = Field(
        default_factory=list,
        description="Important limitations of this assessment"
    )

    evidence: WeatherEvidence = Field(
        ...,
        description="Underlying weather evidence supporting the assessment"
    )