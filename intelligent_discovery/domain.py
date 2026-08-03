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
    id: str = field(default_factory=lambda: str(uuid4()))
    collected_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not 0 <= self.credibility <= 1:
            raise ValueError("credibility must be between 0 and 1")


@dataclass(slots=True)
class Finding:
    task_id: str
    statement: str
    kind: FindingKind
    confidence: float
    source_ids: list[str] = field(default_factory=list)
    rationale: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.kind != FindingKind.UNKNOWN and not self.source_ids:
            raise ValueError("findings must reference at least one source")


@dataclass(slots=True)
class KnowledgeRecord:
    task_id: str
    title: str
    summary: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
