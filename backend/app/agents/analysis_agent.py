import json

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.providers.llm_provider import LLMProvider


class AnalysisAgent:

    """
    Uses an LLM to produce an evidence-grounded assessment
    from operational and weather investigation results.
    """

    def __init__(self):

        self.llm = LLMProvider()

    def analyze(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
    ) -> AnalysisAssessment:

        """
        Generates an evidence-grounded analysis using the LLM.
        """

        # --------------------------------------------------
        # Serialize structured evidence
        # --------------------------------------------------

        evidence = {
            "operations": operations.model_dump(),
            "weather": weather.model_dump(),
        }

        evidence_json = json.dumps(
            evidence,
            indent=2,
            default=str,
        )

        # --------------------------------------------------
        # Analysis prompt
        # --------------------------------------------------

        prompt = f"""
You are the Analysis Agent for AeroWatch.

Your task is to analyze structured aviation investigation
evidence and produce an evidence-grounded assessment.

STRICT RULES:

1. Use ONLY the evidence provided below.

2. Do NOT invent FAA events, weather observations,
   operational conditions, or other facts.

3. Clearly distinguish between:
   - observed facts
   - potential factors
   - unsupported assumptions

4. NEVER claim that weather CAUSED an operational disruption
   unless the provided evidence explicitly establishes causation.

5. Weather conditions may be described as a potential factor,
   but correlation must NOT be presented as causation.

6. If no FAA operational disruption was detected,
   DO NOT claim that an operational disruption is occurring.

7. Preserve important limitations from the source evidence.

8. Confidence must reflect the strength and completeness
   of the available evidence.

9. The airport field MUST exactly match the airport from
   the operational evidence.

10. observed_facts must contain ONLY facts directly supported
    by the supplied evidence.

11. potential_factors must contain ONLY possible factors that
    are supported by the supplied evidence but are NOT proven.

12. Do not introduce information from outside the evidence.

13. Return ONLY valid JSON.

14. Do not use markdown or code fences.

The JSON MUST contain exactly these fields:

{{
    "airport": "airport code",

    "observed_facts": [
        "directly supported fact"
    ],

    "potential_factors": [
        "potential but unproven factor"
    ],

    "overall_assessment": "evidence-grounded summary",

    "confidence": "low, medium, or high",

    "limitations": [
        "important limitation"
    ]
}}

INVESTIGATION EVIDENCE:

{evidence_json}
"""

        # --------------------------------------------------
        # Call LLM
        # --------------------------------------------------

        raw_response = self.llm.generate_json(prompt)

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            result = json.loads(raw_response)

        except json.JSONDecodeError as exc:

            raise ValueError(
                "AnalysisAgent received invalid JSON from the LLM."
            ) from exc

        # --------------------------------------------------
        # Validate Pydantic schema
        # --------------------------------------------------

        try:

            assessment = AnalysisAssessment.model_validate(result)

        except Exception as exc:

            raise ValueError(
                "LLM response does not match "
                "AnalysisAssessment schema."
            ) from exc

        # --------------------------------------------------
        # Deterministic airport validation
        # --------------------------------------------------

        if assessment.airport != operations.airport:

            raise ValueError(
                "LLM returned an airport that does not match "
                "the investigated airport."
            )

        return assessment