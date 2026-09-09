import json

from app.models.analysis import AnalysisAssessment
from app.models.operations import OperationsAssessment
from app.models.weather import WeatherAssessment
from app.providers.llm_provider import LLMProvider


class AnalysisAgent:
    """
    Produces an evidence-grounded combined assessment from
    operational and weather investigation results.
    """

    def __init__(self):
        self.llm = LLMProvider()

    def analyze(
        self,
        operations: OperationsAssessment,
        weather: WeatherAssessment,
    ) -> AnalysisAssessment:

        prompt = f"""
You are the analysis agent for AeroWatch, an aviation
disruption investigation system.

Your task is to produce an evidence-grounded assessment
using ONLY the operational and weather evidence provided
below.

Do not invent facts.
Do not infer facts that are not supported by the evidence.
Do not introduce external knowledge.

============================================================
OPERATIONAL EVIDENCE
============================================================

{operations.model_dump_json(indent=2)}

============================================================
WEATHER EVIDENCE
============================================================

{weather.model_dump_json(indent=2)}

============================================================
ANALYSIS RULES
============================================================

1. OPERATIONAL DISRUPTION

The field `disruption_detected` must be TRUE only when the
operational evidence indicates an active operational
disruption.

Use:

operations.disruption_detected

as the authoritative source for this field.

If the operational evidence says there is no active
disruption, `disruption_detected` MUST be false.

Do not infer an operational disruption merely because
weather conditions are poor.

------------------------------------------------------------

2. WEATHER RISK

The field `weather_risk_detected` must be TRUE only when
the weather assessment indicates potentially disruptive
weather conditions.

Use:

weather.weather_risk_detected

as the authoritative source for this field.

Do not create weather risk that is not present in the
weather evidence.

------------------------------------------------------------

3. CAUSATION

Do NOT claim that weather caused an operational disruption
unless explicit causal evidence is provided.

The following are NOT sufficient to establish causation:

- IFR conditions
- LIFR conditions
- low visibility
- strong winds
- thunderstorms
- precipitation
- poor weather
- simultaneous occurrence of weather and disruption

When both operational disruption and adverse weather are
present, clearly distinguish:

- what is observed
- what may be a potential factor
- what is NOT established

For example, it is acceptable to say:

"Weather conditions may be a potential contributing factor,
but the available evidence does not establish causation."

It is NOT acceptable to say:

"Weather caused the disruption."

unless explicit causal evidence is supplied.

------------------------------------------------------------

4. OBSERVED FACTS

`observed_facts` must contain facts directly supported by
the supplied evidence.

Do not put speculation into `observed_facts`.

------------------------------------------------------------

5. POTENTIAL FACTORS

`potential_factors` may contain factors that could be
relevant but are not proven to have caused the disruption.

Potential factors MUST NOT be presented as confirmed causes.

------------------------------------------------------------

6. OVERALL ASSESSMENT

`overall_assessment` must summarize the evidence.

It must:

- accurately represent the operational state
- accurately represent the weather state
- avoid unsupported claims
- avoid unsupported causation
- preserve important uncertainty
- distinguish observations from possibilities

------------------------------------------------------------

7. LIMITATIONS

Preserve important limitations from the underlying evidence.

Do not remove limitations merely to make the answer sound
more confident.

------------------------------------------------------------

8. CONFIDENCE

Use only one of:

- low
- medium
- high

Confidence must reflect the quality and completeness of the
available evidence.

------------------------------------------------------------

9. AIRPORT

The `airport` field MUST exactly match:

{operations.airport}

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do not return:

- Markdown
- code fences
- explanations outside the JSON
- additional fields

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

The boolean fields must be derived directly from the
corresponding evidence assessments.

============================================================
FINAL CHECK
============================================================

Before returning the JSON, verify:

- airport matches the operational evidence
- disruption_detected matches operations.disruption_detected
- weather_risk_detected matches weather.weather_risk_detected
- observed_facts are evidence-supported
- potential_factors are not presented as confirmed causes
- no unsupported causal claim is made
- limitations are preserved
- confidence is low, medium, or high
- output contains ONLY valid JSON
"""

        raw_response = self.llm.generate_json(prompt)

        try:
            data = json.loads(raw_response)

        except json.JSONDecodeError as error:
            raise ValueError(
                "AnalysisAgent returned invalid JSON."
            ) from error

        try:
            assessment = AnalysisAssessment.model_validate(
                data
            )

        except Exception as error:
            raise ValueError(
                "AnalysisAgent returned JSON that does not "
                "match the AnalysisAssessment schema."
            ) from error

        # ----------------------------------------------------
        # Deterministic consistency checks
        # ----------------------------------------------------

        if assessment.airport != operations.airport:
            raise ValueError(
                "AnalysisAgent returned an airport that does "
                "not match the operational evidence."
            )

        if (
            assessment.disruption_detected
            != operations.disruption_detected
        ):
            raise ValueError(
                "AnalysisAgent returned a disruption_detected "
                "value inconsistent with the operational evidence."
            )

        if (
            assessment.weather_risk_detected
            != weather.weather_risk_detected
        ):
            raise ValueError(
                "AnalysisAgent returned a weather_risk_detected "
                "value inconsistent with the weather evidence."
            )

        return assessment