from pydantic import BaseModel, Field

from app.models.analysis import AnalysisAssessment
from app.models.verification import VerificationAssessment


class InvestigationRequest(BaseModel):
    """
    Request body for an AeroWatch investigation.
    """

    airport: str = Field(
        ...,
        min_length=4,
        max_length=4,
        description="ICAO airport code, e.g. KJFK",
    )

    query: str = Field(
        default="Investigate current operational conditions.",
        min_length=1,
        description="Question or objective for the investigation.",
    )


class InvestigationResponse(BaseModel):
    """
    Public API response for a completed AeroWatch
    investigation.
    """

    airport: str

    status: str

    analysis: AnalysisAssessment

    verification: VerificationAssessment

    revision_count: int