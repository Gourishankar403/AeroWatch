from app.models.operations import OperationsAssessment
from app.tools.operations_tool import OperationsTool


class OperationsInvestigator:

    """
    Investigates airport operational conditions using
    collected FAA operational evidence.
    """

    def __init__(self):
        self.operations_tool = OperationsTool()

    def investigate(
        self,
        airport: str
    ) -> OperationsAssessment:

        evidence = self.operations_tool.investigate_airport(
            airport
        )

        findings = []
        limitations = []

        if evidence.events:

            findings.append(
                f"{len(evidence.events)} active FAA operational "
                f"event(s) detected for {evidence.airport}."
            )

            for event in evidence.events:

                finding = (
                    f"{event.event_type.replace('_', ' ').title()}: "
                    f"{event.description}"
                )

                if event.cause:
                    finding += f" Reason reported: {event.cause}"

                findings.append(finding)

            disruption_detected = True

        else:

            findings.append(
                f"No active FAA operational events were found "
                f"for {evidence.airport}."
            )

            disruption_detected = False

        limitations.append(
            "This assessment reflects active events available "
            "from the FAA NAS status source."
        )

        limitations.append(
            "Absence of an active FAA event does not prove "
            "that the airport has no operational disruption."
        )

        return OperationsAssessment(
            airport=evidence.airport,
            disruption_detected=disruption_detected,
            event_count=len(evidence.events),
            findings=findings,
            limitations=limitations,
            evidence=evidence
        )