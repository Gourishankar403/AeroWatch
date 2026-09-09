from app.graph.state import InvestigationState
from app.graph.workflow import build_investigation_graph
from app.models.analysis import AnalysisAssessment
from app.models.verification import VerificationAssessment


class InvestigationService:
    """
    Application service responsible for executing
    a complete AeroWatch investigation.
    """

    def __init__(self, max_revisions: int = 2):
        self.max_revisions = max_revisions
        self.graph = build_investigation_graph()

    def investigate(
        self,
        airport: str,
        query: str,
    ) -> tuple[
        AnalysisAssessment,
        VerificationAssessment,
        int,
    ]:
        """
        Execute the complete AeroWatch investigation
        and return the final verified assessment.
        """

        initial_state: InvestigationState = {
            "query": query,
            "airport": airport,
            "operations_assessment": None,
            "weather_assessment": None,
            "analysis_assessment": None,
            "verification_assessment": None,
            "revision_count": 0,
            "max_revisions": self.max_revisions,
            "investigation_complete": False,
        }

        result = self.graph.invoke(initial_state)

        analysis = result.get("analysis_assessment")
        verification = result.get("verification_assessment")

        if analysis is None:
            raise RuntimeError(
                "Investigation completed without an analysis assessment."
            )

        if verification is None:
            raise RuntimeError(
                "Investigation completed without a verification assessment."
            )

        return (
            analysis,
            verification,
            result.get("revision_count", 0),
        )