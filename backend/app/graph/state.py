from typing import Optional, TypedDict

from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.analysis import AnalysisAssessment
from app.models.verification import VerificationAssessment


class InvestigationState(TypedDict):
    """
    Shared state passed between all AeroWatch
    investigation nodes.
    """

    query: str
    airport: str

    operations_assessment: Optional[OperationsAssessment]
    weather_assessment: Optional[WeatherAssessment]

    analysis_assessment: Optional[AnalysisAssessment]

    verification_assessment: Optional[VerificationAssessment]

    revision_count: int
    max_revisions: int

    investigation_complete: bool