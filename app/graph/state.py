from typing import Optional, TypedDict

from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment


class InvestigationState(TypedDict):
    """
    Shared state passed between all AeroWatch
    investigation nodes.
    """

    query: str
    airport: str

    operations_assessment: Optional[OperationsAssessment]
    weather_assessment: Optional[WeatherAssessment]

    investigation_complete: bool