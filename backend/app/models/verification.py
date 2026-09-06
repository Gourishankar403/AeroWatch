from pydantic import BaseModel,Field

class VerificationAssessment(BaseModel):
    """

    Result of verifying whether an AeroWatch analysis
    is adequately supported by collected evidence
    """

    approved:bool=Field(
        ...,
        description="Whether the analysis is adequately supported"

    )

    issues:list[str]=Field(
        default_factory=list,
        description="Unsupported claims or reasoning issues detected"

    )


    missing_evidence:list[str]=Field(
        default_factory=list,
        description="Evidence that would improve the investigation"

    )

    verification_summary:str=Field(
        ...,
        description="Summary of the verification result"

    )


    