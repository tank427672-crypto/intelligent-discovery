"""Private-Beta Experience Intelligence, based on consented metadata only.

This module detects friction and routes it to human review.  It never inspects
private bodies, changes knowledge, changes rules, or releases code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from .communication import CommunicationPriority


def now() -> datetime:
    return datetime.now(UTC)


SAFE_SIGNAL_FIELDS = frozenset({"feature", "action", "outcome", "duration_bucket", "error_code", "consented"})


@dataclass(slots=True)
class ExperienceSignal:
    user_id: str
    scenario: str
    metadata: dict[str, str]
    consented: bool
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.consented:
            raise ValueError("experience signals require explicit consent")
        if not set(self.metadata).issubset(SAFE_SIGNAL_FIELDS):
            raise ValueError("experience signals may only contain approved metadata")
        if any(key.lower() in {"content", "body", "message", "query", "private_text"} for key in self.metadata):
            raise ValueError("experience signals must not contain private content")


@dataclass(slots=True)
class BetaInsight:
    signal_ids: list[str]
    category: str
    impact_scope: int
    severity: int
    frequency: int
    security_risk: bool
    priority: CommunicationPriority
    summary: str
    human_review_required: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))


# Compatibility name for earlier design notes.
ExperienceInsight = BetaInsight


@dataclass(slots=True)
class UserFeedbackWorkflow:
    """Connects a structured communication to analysis and controlled evolution."""

    communication_id: str
    signal_ids: list[str]
    insight_id: str = ""
    improvement_proposal_id: str = ""
    evolution_candidate_id: str = ""
    evolution_experiment_id: str = ""
    human_approved_by: str = ""
    released_version: str = ""
    user_revalidated: bool = False

    def can_release(self) -> bool:
        return bool(self.evolution_experiment_id and self.human_approved_by)


@dataclass(slots=True)
class ImprovementLink:
    insight_id: str
    improvement_proposal_id: str
    evolution_candidate_id: str = ""
    experiment_id: str = ""
    approved_by: str = ""
    user_revalidation_requested: bool = False

    def ready_for_release(self) -> bool:
        return bool(self.experiment_id and self.approved_by)


@dataclass(slots=True)
class ExpertEnhancementRequest:
    expert_id: str
    related_object_type: str
    related_object_id: str
    requested_kind: str
    evidence_references: list[str]
    status: str = "submitted"
    id: str = field(default_factory=lambda: str(uuid4()))

    def can_change_knowledge(self) -> bool:
        return False


@dataclass(slots=True)
class ExpertFeedbackReview:
    request_id: str
    helpfulness: int
    explanation_quality: int
    communication_quality: int
    long_term_value: int
    reviewer_id: str

    def __post_init__(self) -> None:
        if any(not 1 <= value <= 5 for value in self.scores):
            raise ValueError("expert feedback values must be between 1 and 5")

    @property
    def scores(self) -> tuple[int, int, int, int]:
        return self.helpfulness, self.explanation_quality, self.communication_quality, self.long_term_value


@dataclass(slots=True)
class TrustProfile:
    """Four separate review inputs; no rank, privilege, or automatic reward."""

    subject_id: str
    contribution_value: float = 0
    community_reputation: float = 0
    professional_reputation: float = 0
    review_reputation: float = 0


class ExperienceStore(Protocol):
    def save_signal(self, signal: ExperienceSignal) -> None: ...
    def save_insight(self, insight: BetaInsight) -> None: ...
    def save_link(self, link: ImprovementLink) -> None: ...


class BetaExperienceService:
    """A classifier and routing layer; human review is always retained."""

    def __init__(self, store: ExperienceStore) -> None:
        self.store = store

    def record(self, signal: ExperienceSignal) -> ExperienceSignal:
        self.store.save_signal(signal)
        return signal

    @staticmethod
    def priority(impact_scope: int, severity: int, frequency: int, security_risk: bool) -> CommunicationPriority:
        if security_risk or severity >= 4:
            return CommunicationPriority.P0
        if severity >= 3 or impact_scope >= 20:
            return CommunicationPriority.P1
        if frequency >= 3 or impact_scope >= 5:
            return CommunicationPriority.P2
        return CommunicationPriority.P3

    def analyze(
        self,
        signal_ids: list[str],
        category: str,
        summary: str,
        impact_scope: int,
        severity: int,
        frequency: int,
        security_risk: bool,
    ) -> BetaInsight:
        if not summary.strip() or not signal_ids:
            raise ValueError("analysis requires a summary and at least one signal")
        insight = BetaInsight(
            signal_ids,
            category,
            impact_scope,
            severity,
            frequency,
            security_risk,
            self.priority(impact_scope, severity, frequency, security_risk),
            summary,
        )
        self.store.save_insight(insight)
        return insight

    def link_improvement(self, link: ImprovementLink) -> ImprovementLink:
        self.store.save_link(link)
        return link


class InMemoryExperienceAdapter:
    def __init__(self) -> None:
        self.signals: list[ExperienceSignal] = []
        self.insights: list[BetaInsight] = []
        self.links: list[ImprovementLink] = []

    def save_signal(self, signal: ExperienceSignal) -> None:
        self.signals.append(signal)

    def save_insight(self, insight: BetaInsight) -> None:
        self.insights.append(insight)

    def save_link(self, link: ImprovementLink) -> None:
        self.links.append(link)
