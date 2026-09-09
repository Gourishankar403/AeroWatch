from fastapi import APIRouter, HTTPException

from app.api.models import (
    InvestigationRequest,
    InvestigationResponse,
)

from app.graph.state import InvestigationState
from app.graph.workflow import build_investigation_graph


router = APIRouter()


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

    # --------------------------------------------------
    # Basic airport validation
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Initial LangGraph state
    # --------------------------------------------------

    initial_state: InvestigationState = {
        "query": query,
        "airport": airport,

        "operations_assessment": None,
        "weather_assessment": None,
        "analysis_assessment": None,
        "verification_assessment": None,

        "revision_count": 0,
        "max_revisions": 2,

        "investigation_complete": False,
    }

    # --------------------------------------------------
    # Execute investigation graph
    # --------------------------------------------------

    try:

        graph = build_investigation_graph()

        result = graph.invoke(
            initial_state
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "AeroWatch investigation failed."
            ),
        ) from error

    # --------------------------------------------------
    # Extract final results
    # --------------------------------------------------

    analysis = result.get(
        "analysis_assessment"
    )

    verification = result.get(
        "verification_assessment"
    )

    if analysis is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation completed without "
                "an analysis assessment."
            ),
        )

    if verification is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation completed without "
                "a verification assessment."
            ),
        )

    # --------------------------------------------------
    # API response
    # --------------------------------------------------

    return InvestigationResponse(
        airport=airport,
        status="completed",
        analysis=analysis,
        verification=verification,
        revision_count=result.get(
            "revision_count",
            0,
        ),
    )