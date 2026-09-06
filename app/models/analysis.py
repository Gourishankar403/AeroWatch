from typing import Optional 
from pydantic import BaseModel,Field

class AnalysisAssessment(BaseModel):
    "Combined evidence based assessment produced from "
    "muliple investigation agents"


    airport:str=Field(
        ...,
        description="Airport being investigated"

    )

    observed_facts:list[str]=Field(
        default_factory=list,
        description="Facts direclty supported by collected evidence"

    )

    potential_factors:list[str]=Field(
        default_factory=list,
        description="Factors that may be relevant but are not proved"
    )

    overall_assessment:str=Field(
        ...,
        description="Evidence grounded summary of the investigation"

    )

    confidence:str=Field(
        ...,
        description="Confidence level based on available evidence"


    )


    limitations:list[str]=Field(
        default_factory=list,
        description="Important limitations and missing evidence"


    )