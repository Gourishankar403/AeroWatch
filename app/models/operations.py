from datetime import datetime
from typing import Optional

from pydantic import BaseModel,Field

class OperationalEvent(BaseModel):

    """Represents a single aviation operational 
     event affecting an airport"""

    event_type:str=Field(
        ...,
        description="Type of operational event , eg .ground_delay"
    )


    description:str=Field(
        ...,
        description="Human-readable description of the event"

    )

    cause:Optional[str]=Field(
        default=None,
        description="Reported cause of the operational event"

    )

    severity:Optional[str]=Field(
        default=None,
        description="Severity level if available"
    )

    start_time:Optional[datetime]=Field(
        default=None,
        description="Event start time"

    )


    end_time:Optional[datetime]=Field(
        default=None,
        description="Event end time"

    )




class OperationsEvidence(BaseModel):
    """Normalised operational evidence collected
    
    for a specific airport"""

    airport:str=Field(
        ...,
        description="ICAO or IATA airport code"

    )

    source:str=Field(
        default="FAA NAS",
        description="Source of operational information"

    )


    retrieved_at:datetime=Field(
        ...,
        description="Time when the information was retrieved"

    )

    events:list[OperationalEvent]=Field(
        default_factory=list,
        description="Operational events affecting the airport"

    )


    summary:Optional[str]=Field(
        default=None,
        description="Brief  summary of operational status"

    )




class OperationsAssessment(BaseModel):

    """Assesment derived form collected operational evidence"""

    airport:str=Field(
        ...,
        description="Airport being investigated"

    )

    disruption_detected:bool=Field(
        ...,
        description="Whether active FAA operational events were detected"

    )

    event_count:int=Field(
        ...,
        description="Number of active operational events found"

    )

    findings:list[str]=Field(
        deafult_factory=list,
        description="Evidence-grounded operational findings"

    )


    limitations:list[str]=Field(
        default_factory=list,
        description="Important limitations of this assessment"

    )

    evidence:OperationsEvidence=Field(
        ...,
        description="Underlying operational evidence supporting the assessment  "

    )