from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaskStatus(StrEnum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    ANALYZED = "analyzed"
    COMPLETED = "completed"


class FindingKind(StrEnum):
    INSIGHT = "insight"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    UNKNOWN = "unknown"


class SourceType(StrEnum):
    WEB = "web"
    DATABASE = "database"
    API = "api"
    OPEN_SOURCE = "open_source"
    DOCUMENT = "document"
    USER_PROVIDED = "user_provided"


class TrustLevel(StrEnum):
    PRIMARY = "primary"
    CURATED = "curated"
    SECONDARY = "secondary"
    UNVERIFIED = "unverified"


class SourceStatus(StrEnum):
    ACCESSIBLE = "accessible"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    UNVERIFIED = "unverified"


class EvidenceRelation(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT = "context"


class EvidenceStatus(StrEnum):
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    FAILED = "failed"


class FeedbackVerdict(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass(slots=True)
class DiscoveryTask:
    question: str
    context: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.DRAFT
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def transition_to(self, status: TaskStatus) -> None:
        allowed = {
            TaskStatus.DRAFT: {TaskStatus.RESEARCHING},
            TaskStatus.RESEARCHING: {TaskStatus.ANALYZED},
            TaskStatus.ANALYZED: {TaskStatus.COMPLETED},
            TaskStatus.COMPLETED: set(),
        }
        if status not in allowed[self.status]:
            raise ValueError(f"Cannot transition from {self.status} to {status}")
        self.status = status
        self.updated_at = utc_now()


@dataclass(slots=True)
class Source:
    task_id: str
    title: str
    url: str
    excerpt: str
    credibility: float
    source_type: SourceType = SourceType.USER_PROVIDED
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    status: SourceStatus = SourceStatus.UNVERIFIED
    license_info: str = "unknown"
    published_at: datetime | None = None
    updated_at: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    collected_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not 0 <= self.credibility <= 1:
            raise ValueError("credibility must be between 0 and 1")


@dataclass(slots=True)
class Evidence:
    task_id: str
    source_id: str
    claim: str
    excerpt: str
    locator: str
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS
    status: EvidenceStatus = EvidenceStatus.EXTRACTED
    limitations: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Finding:
    task_id: str
    statement: str
    kind: FindingKind
    confidence: float
    source_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    rationale: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.kind != FindingKind.UNKNOWN and not (self.source_ids or self.evidence_ids):
            raise ValueError("findings must reference at least one source or evidence item")


@dataclass(slots=True)
class FindingFeedback:
    task_id: str
    finding_id: str
    verdict: FeedbackVerdict
    comment: str
    reviewer_label: str = "human"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.comment.strip():
            raise ValueError("feedback comment is required")


@dataclass(slots=True)
class KnowledgeRecord:
    task_id: str
    title: str
    summary: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
