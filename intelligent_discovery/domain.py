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


class CaseLifecycleStatus(StrEnum):
    CANDIDATE = "candidate"
    TRACKED = "tracked"
    VERIFIED = "verified"
    MATURE = "mature"
    HISTORICAL = "historical"


class CaseVerificationStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    REJECTED = "rejected"


class CaseTaskRelation(StrEnum):
    DISCOVERED_IN = "discovered_in"
    REFERENCED_BY = "referenced_by"
    APPLIED_TO = "applied_to"


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


@dataclass(slots=True)
class CaseRecord:
    origin_task_id: str
    name: str
    case_type: str
    background: str
    problem: str
    solution: str
    outcome: str
    success_factors: str
    failure_factors: str
    lessons_learned: str
    applicability: str
    limitations: str
    source_ids: list[str]
    evidence_ids: list[str] = field(default_factory=list)
    finding_ids: list[str] = field(default_factory=list)
    license_info: str = "unknown"
    lifecycle_status: CaseLifecycleStatus = CaseLifecycleStatus.CANDIDATE
    verification_status: CaseVerificationStatus = CaseVerificationStatus.PENDING
    credibility: float = 0.0
    id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.case_type.strip():
            raise ValueError("case name and type are required")
        if not self.source_ids:
            raise ValueError("cases must reference at least one source")
        if not 0 <= self.credibility <= 1:
            raise ValueError("case credibility must be between 0 and 1")

    def transition_to(self, status: CaseLifecycleStatus) -> None:
        allowed = {
            CaseLifecycleStatus.CANDIDATE: {CaseLifecycleStatus.TRACKED},
            CaseLifecycleStatus.TRACKED: {CaseLifecycleStatus.VERIFIED},
            CaseLifecycleStatus.VERIFIED: {CaseLifecycleStatus.MATURE},
            CaseLifecycleStatus.MATURE: {CaseLifecycleStatus.HISTORICAL},
            CaseLifecycleStatus.HISTORICAL: set(),
        }
        if status not in allowed[self.lifecycle_status]:
            raise ValueError(f"Cannot transition case from {self.lifecycle_status} to {status}")
        if status in {CaseLifecycleStatus.VERIFIED, CaseLifecycleStatus.MATURE} and (
            self.verification_status != CaseVerificationStatus.VERIFIED
        ):
            raise ValueError("verified lifecycle states require verified case evidence")
        self.lifecycle_status = status
        self.updated_at = utc_now()


@dataclass(slots=True)
class CaseRevision:
    case_id: str
    version: int
    summary: str
    change_reason: str
    changed_fields: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class CaseTaskLink:
    case_id: str
    task_id: str
    relation: CaseTaskRelation
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
