import json

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.verification import VerificationAssessment
from app.models.weather import WeatherAssessment
from app.providers.llm_provider import LLMProvider


class RevisionAgent:
    """
    Revises an analysis after deterministic verification
    identifies evidence-grounding or reasoning problems.
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

        prompt = f"""
You are the revision agent for AeroWatch.

Your task is to revise an aviation disruption analysis
after a deterministic verification process identified
one or more problems.

You must correct the identified problems while remaining
strictly grounded in the supplied operational and weather
evidence.

============================================================
OPERATIONAL EVIDENCE
============================================================

{operations.model_dump_json(indent=2)}

============================================================
WEATHER EVIDENCE
============================================================

{weather.model_dump_json(indent=2)}

============================================================
PREVIOUS ANALYSIS
============================================================

{analysis.model_dump_json(indent=2)}

============================================================
VERIFICATION RESULT
============================================================

{verification.model_dump_json(indent=2)}

============================================================
REVISION RULES
============================================================

1. USE ONLY PROVIDED EVIDENCE

Do not introduce external information.

Do not invent operational events.

Do not invent weather conditions.

Do not invent causes.

Do not invent timestamps or observations.

------------------------------------------------------------

2. CORRECT THE STRUCTURED DISRUPTION STATE

The revised field:

`disruption_detected`

MUST exactly match:

operations.disruption_detected

If the operational evidence reports no active
disruption, the revised value MUST be false.

If the operational evidence reports an active
disruption, the revised value MUST be true.

------------------------------------------------------------

3. CORRECT THE STRUCTURED WEATHER-RISK STATE

The revised field:

`weather_risk_detected`

MUST exactly match:

weather.weather_risk_detected

------------------------------------------------------------

4. AIRPORT

The revised:

`airport`

MUST exactly match:

{operations.airport}

------------------------------------------------------------

5. CAUSATION

Do not claim that weather caused an operational
disruption unless explicit causal evidence exists.

The simultaneous presence of:

- an operational disruption
- IFR/LIFR conditions
- reduced visibility
- strong winds
- precipitation
- thunderstorms

does NOT establish causation.

If causation is not established, explicitly preserve
that limitation.

Acceptable wording includes:

"The available evidence does not establish causation."

or:

"Weather may be a potential contributing factor, but
causation is not established."

Do NOT state:

"Weather caused the disruption."

unless the supplied evidence explicitly supports that claim.

------------------------------------------------------------

6. OBSERVED FACTS

`observed_facts` must contain only facts directly
supported by the evidence.

------------------------------------------------------------

7. POTENTIAL FACTORS

Potential factors may be included when relevant, but
they must not be presented as confirmed causes.

------------------------------------------------------------

8. LIMITATIONS

Preserve the existing evidence limitations.

If the verifier says that limitations are missing,
restore the appropriate limitations based only on the
supplied evidence.

Do not invent limitations unrelated to the evidence.

------------------------------------------------------------

9. CONFIDENCE

Use exactly one of:

- low
- medium
- high

Confidence must reflect the evidence available.

Do not use:

- certain
- definite
- guaranteed
- absolute
- 100%

------------------------------------------------------------

10. OVERALL ASSESSMENT

The revised overall assessment must:

- accurately represent operational status
- accurately represent weather risk
- avoid unsupported claims
- avoid unsupported causation
- preserve uncertainty
- distinguish facts from potential factors
- reflect the verifier's identified problems

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do not return Markdown.

Do not return code fences.

Do not include explanations outside the JSON.

Return exactly these fields:

{{
    "airport": "{operations.airport}",
    "disruption_detected": false,
    "weather_risk_detected": false,
    "observed_facts": [],
    "potential_factors": [],
    "overall_assessment": "",
    "confidence": "medium",
    "limitations": []
}}

============================================================
FINAL CHECK
============================================================

Before returning the result, verify all of the following:

1. airport exactly matches operations.airport
2. disruption_detected exactly matches
   operations.disruption_detected
3. weather_risk_detected exactly matches
   weather.weather_risk_detected
4. observed_facts contain only supported facts
5. potential_factors are not presented as confirmed causes
6. unsupported causal claims have been removed
7. limitations are preserved
8. confidence is low, medium, or high
9. the output contains only valid JSON
10. no additional fields are present
"""

        raw_response = self.llm.generate_json(
            prompt
        )

        # ----------------------------------------------------
        # JSON parsing
        # ----------------------------------------------------

        try:

            data = json.loads(
                raw_response
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "RevisionAgent returned invalid JSON."
            ) from error

        # ----------------------------------------------------
        # Pydantic validation
        # ----------------------------------------------------

        try:

            revised_analysis = (
                AnalysisAssessment.model_validate(
                    data
                )
            )

        except Exception as error:

            raise ValueError(
                "LLM revision does not match "
                "AnalysisAssessment schema."
            ) from error

        # ----------------------------------------------------
        # Deterministic consistency checks
        # ----------------------------------------------------

        if (
            revised_analysis.airport
            != operations.airport
        ):
            raise ValueError(
                "RevisionAgent returned an airport that "
                "does not match the operational evidence."
            )

        if (
            revised_analysis.disruption_detected
            != operations.disruption_detected
        ):
            raise ValueError(
                "RevisionAgent returned a disruption_detected "
                "value inconsistent with the operational evidence."
            )

        if (
            revised_analysis.weather_risk_detected
            != weather.weather_risk_detected
        ):
            raise ValueError(
                "RevisionAgent returned a weather_risk_detected "
                "value inconsistent with the weather evidence."
            )

        valid_confidence_levels = {
            "low",
            "medium",
            "high",
        }

        if (
            revised_analysis.confidence.lower()
            not in valid_confidence_levels
        ):
            raise ValueError(
                "RevisionAgent returned an invalid confidence level."
            )

        if not revised_analysis.limitations:
            raise ValueError(
                "RevisionAgent failed to preserve "
                "evidence limitations."
            )

        if not revised_analysis.observed_facts:
            raise ValueError(
                "RevisionAgent returned no observed facts."
            )

        return revised_analysis