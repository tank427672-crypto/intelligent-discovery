"""Developer contact gateway that creates structured CommunicationRecords."""

from __future__ import annotations

from enum import StrEnum

from ..communication import CommunicationPriority, CommunicationRecord, CommunicationService, CommunicationType


class DeveloperContactType(StrEnum):
    PRODUCT_FEEDBACK = "product_feedback"
    BUG_REPORT = "bug_report"
    SECURITY_REPORT = "security_report"
    CASE_CONTRIBUTION = "case_contribution"
    PARTNERSHIP_REQUEST = "partnership_request"


class CommunicationGateway:
    def __init__(self, communication: CommunicationService) -> None:
        self.communication = communication

    def submit(
        self, sender_id: str, contact_type: DeveloperContactType, related_type: str, related_id: str, purpose: str
    ) -> CommunicationRecord:
        communication_type = (
            CommunicationType.SECURITY_REPORT
            if contact_type is DeveloperContactType.SECURITY_REPORT
            else CommunicationType.FEEDBACK
        )
        priority = (
            CommunicationPriority.P0
            if contact_type is DeveloperContactType.SECURITY_REPORT
            else CommunicationPriority.P2
        )
        return self.communication.create(
            CommunicationRecord(
                "user",
                sender_id,
                "developer",
                "maintainers",
                communication_type,
                related_type,
                related_id,
                purpose,
                priority=priority,
            )
        )
