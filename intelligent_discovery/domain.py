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


class GraphNodeType(StrEnum):
    SOURCE = "source"
    EVIDENCE = "evidence"
    FINDING = "finding"
    KNOWLEDGE = "knowledge"
    CASE = "case"
    CONCEPT = "concept"


class RelationshipType(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    USES = "uses"
    BELONGS_TO = "belongs_to"
    SOLVES = "solves"
    HAS_SUCCESS_FACTOR = "has_success_factor"
    HAS_FAILURE_FACTOR = "has_failure_factor"
    INFLUENCES = "influences"
    RELATED_TO = "related_to"


class ReflectionStatus(StrEnum):
    OBSERVED = "observed"
    REVIEWED = "reviewed"


class ClassificationStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ClassificationSource(StrEnum):
    HUMAN = "human"
    AI_SUGGESTION = "ai_suggestion"
    RULE = "rule"


class HelpRequestStatus(StrEnum):
    OPEN = "open"
    IN_RESEARCH = "in_research"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DataVisibility(StrEnum):
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class DataLifecycleStatus(StrEnum):
    CREATED = "created"
    UNDER_REVIEW = "under_review"
    PUBLISHED = "published"
    REVISED = "revised"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ReviewDecision(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ImprovementStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class ExperimentStatus(StrEnum):
    PLANNED = "planned"
    REVIEWED = "reviewed"
    COMPLETED = "completed"


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


@dataclass(slots=True)
class Concept:
    name: str
    concept_type: str
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.concept_type.strip():
            raise ValueError("concept name and type are required")


@dataclass(slots=True)
class Relationship:
    source_type: GraphNodeType
    source_id: str
    target_type: GraphNodeType
    target_id: str
    relationship_type: RelationshipType
    evidence_ids: list[str] = field(default_factory=list)
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.source_type == self.target_type and self.source_id == self.target_id:
            raise ValueError("relationships cannot self-reference")


@dataclass(slots=True)
class DecisionContext:
    question: str
    goal: str
    constraints: list[str]
    options: list[str]
    evidence_ids: list[str] = field(default_factory=list)
    case_ids: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.question.strip() or not self.goal.strip() or not self.options:
            raise ValueError("decision question, goal and at least one option are required")


@dataclass(slots=True)
class ReflectionRecord:
    case_id: str
    original_judgment: str
    actual_outcome: str
    deviation: str
    cause_analysis: str
    learning_update: str
    evidence_ids: list[str] = field(default_factory=list)
    status: ReflectionStatus = ReflectionStatus.OBSERVED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        required = (
            self.original_judgment,
            self.actual_outcome,
            self.deviation,
            self.cause_analysis,
            self.learning_update,
        )
        if not all(value.strip() for value in required):
            raise ValueError("reflection requires judgment, outcome, deviation, cause analysis and learning update")


@dataclass(slots=True)
class Category:
    name: str
    category_type: str
    parent_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.category_type.strip():
            raise ValueError("category name and type are required")


@dataclass(slots=True)
class Tag:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("tag name is required")


@dataclass(slots=True)
class Classification:
    object_type: GraphNodeType
    object_id: str
    category_id: str | None = None
    tag_id: str | None = None
    confidence: float = 0.0
    source: ClassificationSource = ClassificationSource.HUMAN
    status: ClassificationStatus = ClassificationStatus.PROPOSED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not (self.category_id or self.tag_id):
            raise ValueError("classification requires a category or tag")
        if not 0 <= self.confidence <= 1:
            raise ValueError("classification confidence must be between 0 and 1")


@dataclass(slots=True)
class SearchQuery:
    query: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class SearchFeedback:
    search_query_id: str
    result_type: GraphNodeType
    result_id: str
    useful: bool
    comment: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class RecommendationRecord:
    object_type: GraphNodeType
    object_id: str
    reason: str
    evidence_ids: list[str] = field(default_factory=list)
    case_ids: list[str] = field(default_factory=list)
    feedback: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class PersonalDiscoverySpace:
    owner_reference: str
    consented: bool
    focus_category_ids: list[str] = field(default_factory=list)
    saved_object_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.consented:
            raise ValueError("personal discovery space requires explicit consent")


@dataclass(slots=True)
class HelpRequest:
    question: str
    background: str
    goal: str
    constraints: str
    category_ids: list[str] = field(default_factory=list)
    tag_ids: list[str] = field(default_factory=list)
    status: HelpRequestStatus = HelpRequestStatus.OPEN
    attention_count: int = 0
    resolution: str = ""
    related_knowledge_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class CommunityContribution:
    contributor_reference: str
    content_summary: str
    source_url: str
    evidence_excerpt: str = ""
    verification_status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class GovernanceRecord:
    object_type: GraphNodeType
    object_id: str
    action: str
    reason: str
    actor_reference: str = "human"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ReviewRecord:
    object_type: GraphNodeType
    object_id: str
    reviewer_reference: str
    decision: ReviewDecision
    reason: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("review reason is required")


@dataclass(slots=True)
class VisibilityRecord:
    object_type: GraphNodeType
    object_id: str
    visibility: DataVisibility
    lifecycle_status: DataLifecycleStatus = DataLifecycleStatus.CREATED
    id: str = field(default_factory=lambda: str(uuid4()))
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class SystemFeedback:
    feature: str
    feedback_type: str
    rating: int | None
    description: str
    related_action: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.rating is not None and not 1 <= self.rating <= 5:
            raise ValueError("feedback rating must be between 1 and 5")


@dataclass(slots=True)
class FeaturePerformance:
    feature: str
    usage_count: int = 0
    successful_count: int = 0
    satisfaction_sum: int = 0
    feedback_count: int = 0
    failure_modes: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ImprovementProposal:
    problem: str
    feedback_ids: list[str]
    proposal: str
    priority: str
    status: ImprovementStatus = ImprovementStatus.PROPOSED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class EvolutionExperiment:
    proposal_id: str
    objective: str
    change_description: str
    metrics: list[str]
    result: str = ""
    status: ExperimentStatus = ExperimentStatus.PLANNED
    id: str = field(default_factory=lambda: str(uuid4()))
