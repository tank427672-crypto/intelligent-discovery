"""Unified content abstraction; it preserves different questions each content type answers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


class DiscoveryContentType(StrEnum):
    EVENT = "event"
    STORY = "story"
    EXPERIENCE = "experience"
    CASE = "case"
    TREND = "trend"
    KNOWLEDGE = "knowledge"
    OPEN_SOURCE = "open_source"


CONTENT_PURPOSE = {
    DiscoveryContentType.EVENT: "what happened",
    DiscoveryContentType.STORY: "why it happened",
    DiscoveryContentType.EXPERIENCE: "what someone experienced",
    DiscoveryContentType.CASE: "why it succeeded or failed",
    DiscoveryContentType.TREND: "what change is forming",
    DiscoveryContentType.KNOWLEDGE: "what the foundational understanding is",
    DiscoveryContentType.OPEN_SOURCE: "what an open-source project enables",
}


@dataclass(slots=True)
class DiscoveryContent:
    content_type: DiscoveryContentType
    title: str
    summary: str
    source_references: list[str]
    evidence_references: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.summary.strip():
            raise ValueError("content title and summary are required")
        if not self.source_references:
            raise ValueError("content needs at least one source reference")


@dataclass(slots=True)
class ContentFreshness:
    content_id: str
    updated_at: datetime
    source_changed: bool = False
    update_suggestion: str = ""
    historical_versions: list[str] = field(default_factory=list)
