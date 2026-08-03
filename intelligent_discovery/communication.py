"""Communication Intelligence core: private-by-default, auditable, human-governed.

No transport, database, model SDK, or community platform is imported here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from uuid import uuid4

from .domain import DataVisibility


def now() -> datetime:
    return datetime.now(UTC)


class CommunicationType(StrEnum):
    FEEDBACK = "feedback"
    HELP_REQUEST = "help_request"
    DISCUSSION = "discussion"
    REVIEW = "review"
    APPEAL = "appeal"
    NOTIFICATION = "notification"
    SECURITY_REPORT = "security_report"
    FEATURE_REQUEST = "feature_request"


class CommunicationStatus(StrEnum):
    CREATED = "created"
    RECEIVED = "received"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    WAITING_FOR_USER = "waiting_for_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CommunicationPriority(StrEnum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


@dataclass(slots=True)
class CommunicationRecord:
    sender_type: str
    sender_id: str
    receiver_type: str
    receiver_id: str
    communication_type: CommunicationType
    related_object_type: str
    related_object_id: str
    purpose: str
    visibility: DataVisibility = DataVisibility.PRIVATE
    status: CommunicationStatus = CommunicationStatus.CREATED
    priority: CommunicationPriority = CommunicationPriority.P3
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.purpose.strip():
            raise ValueError("communication purpose is required")


@dataclass(slots=True)
class CommunicationHistory:
    communication_id: str
    from_status: CommunicationStatus
    to_status: CommunicationStatus
    actor_id: str
    reason: str
    created_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class FeedbackResolution:
    communication_id: str
    owner_id: str
    outcome: str
    improvement_proposal_id: str = ""
    user_notified: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class HelpRequestWorkflow:
    """Controlled beta flow; answers never update knowledge directly."""

    communication_id: str
    review_required: bool = True
    invited_participants: list[str] = field(default_factory=list)
    evidence_reviewed: bool = False
    knowledge_update_approved: bool = False


@dataclass(slots=True)
class ContributorCommunication:
    communication_id: str
    proposal_kind: str
    evidence_reviewed: bool = False
    reviewer_id: str = ""
    approved: bool = False

    def can_update_knowledge(self) -> bool:
        return self.evidence_reviewed and bool(self.reviewer_id) and self.approved


@dataclass(slots=True)
class AIInteractionExplanation:
    communication_id: str
    information_used: list[str]
    source_references: list[str]
    assumptions: list[str]
    uncertainties: list[str]
    human_review_required: bool = True


@dataclass(slots=True)
class CommunicationRiskAssessment:
    communication_id: str
    risk_signals: list[str]
    risk_level: CommunicationPriority
    metadata_only: bool = True
    human_review_required: bool = True

    def __post_init__(self) -> None:
        if not self.metadata_only or not self.human_review_required:
            raise ValueError("communication risk assessment must be metadata-only and human-reviewed")


class CommunicationStore(Protocol):
    def save(self, record: CommunicationRecord) -> None: ...
    def get(self, communication_id: str) -> CommunicationRecord | None: ...
    def save_history(self, history: CommunicationHistory) -> None: ...
    def list_history(self, communication_id: str) -> list[CommunicationHistory]: ...
    def save_resolution(self, resolution: FeedbackResolution) -> None: ...


class CommunicationService:
    FLOW = {
        CommunicationStatus.CREATED: {CommunicationStatus.RECEIVED},
        CommunicationStatus.RECEIVED: {CommunicationStatus.ASSIGNED},
        CommunicationStatus.ASSIGNED: {CommunicationStatus.PROCESSING},
        CommunicationStatus.PROCESSING: {CommunicationStatus.WAITING_FOR_USER, CommunicationStatus.RESOLVED},
        CommunicationStatus.WAITING_FOR_USER: {CommunicationStatus.PROCESSING},
        CommunicationStatus.RESOLVED: {CommunicationStatus.CLOSED},
        CommunicationStatus.CLOSED: set(),
    }

    def __init__(self, store: CommunicationStore) -> None:
        self.store = store

    def create(self, record: CommunicationRecord) -> CommunicationRecord:
        self.store.save(record)
        return record

    def transition(
        self, record: CommunicationRecord, next_status: CommunicationStatus, actor_id: str, reason: str
    ) -> CommunicationRecord:
        if next_status not in self.FLOW[record.status]:
            raise ValueError("invalid communication status transition")
        history = CommunicationHistory(record.id, record.status, next_status, actor_id, reason)
        record.status, record.updated_at = next_status, now()
        self.store.save(record)
        self.store.save_history(history)
        return record

    def resolve_feedback(self, resolution: FeedbackResolution, actor_id: str) -> FeedbackResolution:
        record = self.store.get(resolution.communication_id)
        if record is None or record.communication_type not in {
            CommunicationType.FEEDBACK,
            CommunicationType.FEATURE_REQUEST,
        }:
            raise ValueError("resolution must relate to feedback or feature request")
        if record.status is not CommunicationStatus.PROCESSING:
            raise ValueError("feedback must be processing before resolution")
        self.transition(record, CommunicationStatus.RESOLVED, actor_id, "resolution recorded")
        self.store.save_resolution(resolution)
        return resolution


class InMemoryCommunicationAdapter:
    """Test adapter. Production adapters must keep communication bodies outside telemetry."""

    def __init__(self) -> None:
        self.records: dict[str, CommunicationRecord] = {}
        self.history: list[CommunicationHistory] = []
        self.resolutions: list[FeedbackResolution] = []

    def save(self, record: CommunicationRecord) -> None:
        self.records[record.id] = record

    def get(self, communication_id: str) -> CommunicationRecord | None:
        return self.records.get(communication_id)

    def save_history(self, history: CommunicationHistory) -> None:
        self.history.append(history)

    def list_history(self, communication_id: str) -> list[CommunicationHistory]:
        return [item for item in self.history if item.communication_id == communication_id]

    def save_resolution(self, resolution: FeedbackResolution) -> None:
        self.resolutions.append(resolution)
