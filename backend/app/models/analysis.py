from pydantic import BaseModel, Field


class AnalysisAssessment(BaseModel):
    """
    Combined evidence-based assessment produced from
    multiple investigation agents.
    """

    airport: str = Field(
        ...,
        description="Airport being investigated",
    )

    disruption_detected: bool = Field(
        ...,
        description=(
            "Whether the available operational evidence "
            "indicates an active operational disruption"
        ),
    )

    weather_risk_detected: bool = Field(
        ...,
        description=(
            "Whether the available weather evidence "
            "indicates potentially disruptive weather risk"
        ),
    )

    observed_facts: list[str] = Field(
        default_factory=list,
        description=(
            "Facts directly supported by collected evidence"
        ),
    )

    potential_factors: list[str] = Field(
        default_factory=list,
        description=(
            "Factors that may be relevant but are not proved"
        ),
    )

    overall_assessment: str = Field(
        ...,
        description=(
            "Evidence-grounded summary of the investigation"
        ),
    )

    confidence: str = Field(
        ...,
        description=(
            "Confidence level based on available evidence"
        ),
    )

    limitations: list[str] = Field(
        default_factory=list,
        description=(
            "Important limitations and missing evidence"
        ),
    )