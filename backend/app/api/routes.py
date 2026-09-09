from fastapi import APIRouter, HTTPException

from app.api.models import (
    InvestigationRequest,
    InvestigationResponse,
)
from app.services.investigation_service import InvestigationService


router = APIRouter()

investigation_service = InvestigationService(
    max_revisions=2,
)


@router.post(
    "/investigate",
    response_model=InvestigationResponse,
)
def investigate(
    request: InvestigationRequest,
):
    """
    Run a complete AeroWatch investigation.
    """

    airport = request.airport.strip().upper()
    query = request.query.strip()

    if len(airport) != 4:
        raise HTTPException(
            status_code=422,
            detail="Airport must be a 4-letter ICAO code.",
        )

    if not airport.isalpha():
        raise HTTPException(
            status_code=422,
            detail="Airport code must contain only letters.",
        )

    try:
        (
            analysis,
            verification,
            revision_count,
        ) = investigation_service.investigate(
            airport=airport,
            query=query,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="AeroWatch investigation failed.",
        ) from error

    return InvestigationResponse(
        airport=airport,
        status="completed",
        analysis=analysis,
        verification=verification,
        revision_count=revision_count,
    )