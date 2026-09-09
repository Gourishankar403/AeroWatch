import json

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.models.verification import VerificationAssessment
from app.providers.llm_provider import LLMProvider


class RevisionAgent:
    """
    Uses an LLM to revise an analysis when the Verification Agent
    identifies evidence-grounding or reasoning issues.
    """

    def __init__(self):

        self.llm = LLMProvider()

    def revise(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
        analysis: AnalysisAssessment,
        verification: VerificationAssessment,
    ) -> AnalysisAssessment:

        """
        Revises the analysis using the original evidence,
        verification feedback, and the previous analysis.
        """

        # --------------------------------------------------
        # Serialize investigation state
        # --------------------------------------------------

        investigation_data = {
            "operations": operations.model_dump(),
            "weather": weather.model_dump(),
            "previous_analysis": analysis.model_dump(),
            "verification": verification.model_dump(),
        }

        investigation_json = json.dumps(
            investigation_data,
            indent=2,
            default=str,
        )

        # --------------------------------------------------
        # Revision prompt
        # --------------------------------------------------

        prompt = f"""
You are the Revision Agent for AeroWatch.

Your task is to revise an aviation disruption analysis
after a deterministic Verification Agent has identified
reasoning or evidence-grounding problems.

The revised analysis MUST be more evidence-grounded
than the previous analysis.

STRICT RULES:

1. Use ONLY the supplied investigation evidence.

2. Do NOT invent FAA events, weather observations,
   operational conditions, or other facts.

3. Preserve facts that are directly supported by
   the investigation evidence.

4. Remove or rewrite unsupported claims.

5. NEVER claim that weather CAUSED an operational
   disruption unless the evidence explicitly establishes
   causation.

6. A weather condition may be described as a potential
   contributing factor, but it must NOT be presented
   as a proven cause unless explicitly supported.

7. If no active FAA operational event exists, the revised
   analysis MUST NOT claim that an operational disruption
   is occurring.

8. Preserve important source limitations.

9. Address EVERY issue raised by the Verification Agent.

10. Do not blindly preserve statements from the previous
    analysis if they conflict with the evidence.

11. observed_facts must contain only directly supported facts.

12. potential_factors must contain only possible factors
    supported by the evidence and must not be presented
    as proven causes.

13. Confidence must reflect the strength and limitations
    of the available evidence.

14. The airport MUST exactly match the airport in the
    operational evidence.

15. Return ONLY valid JSON.

16. Do not use markdown or code fences.

The revised JSON MUST contain exactly these fields:

{{
    "airport": "airport code",

    "observed_facts": [
        "directly supported fact"
    ],

    "potential_factors": [
        "potential but unproven factor"
    ],

    "overall_assessment": "revised evidence-grounded summary",

    "confidence": "low, medium, or high",

    "limitations": [
        "important limitation"
    ]
}}

INVESTIGATION DATA:

{investigation_json}
"""

        # --------------------------------------------------
        # Call Groq
        # --------------------------------------------------

        raw_response = self.llm.generate_json(prompt)

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            result = json.loads(raw_response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "RevisionAgent received invalid JSON from the LLM."
            ) from exc

        # --------------------------------------------------
        # Validate Pydantic schema
        # --------------------------------------------------

        try:

            revised_assessment = (
                AnalysisAssessment.model_validate(result)
            )

        except Exception as exc:

            raise ValueError(
                "LLM revision does not match "
                "AnalysisAssessment schema."
            ) from exc

        # --------------------------------------------------
        # Deterministic airport validation
        # --------------------------------------------------

        if revised_assessment.airport != operations.airport:

            raise ValueError(
                "LLM revision returned an airport that does not "
                "match the investigated airport."
            )

        return revised_assessment