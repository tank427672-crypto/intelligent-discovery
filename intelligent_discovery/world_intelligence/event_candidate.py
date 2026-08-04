"""Candidate state machine. Candidate items cannot be published knowledge by themselves."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


class WorldEventStatus(StrEnum):
    DISCOVERED = "discovered"
    CHECKING = "checking"
    VERIFIED = "verified"
    PUBLISHED = "published"
    REJECTED = "rejected"


@dataclass(slots=True)
class WorldEventCandidate:
    title: str
    summary: str
    category: str
    source_links: list[str]
    impact_score: float
    confidence: float
    verification_status: WorldEventStatus = WorldEventStatus.DISCOVERED
    id: str = field(default_factory=lambda: str(uuid4()))
    detected_time: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.summary.strip() or not self.source_links:
            raise ValueError("candidate needs title, summary and source links")
        if not all(link.startswith(("https://", "http://")) for link in self.source_links):
            raise ValueError("candidate source links must be public URLs")
        if not 0 <= self.impact_score <= 1 or not 0 <= self.confidence <= 1:
            raise ValueError("impact score and confidence must be between 0 and 1")


class WorldEventService:
    FLOW = {
        WorldEventStatus.DISCOVERED: {WorldEventStatus.CHECKING, WorldEventStatus.REJECTED},
        WorldEventStatus.CHECKING: {WorldEventStatus.VERIFIED, WorldEventStatus.REJECTED},
        WorldEventStatus.VERIFIED: {WorldEventStatus.PUBLISHED},
        WorldEventStatus.PUBLISHED: set(),
        WorldEventStatus.REJECTED: set(),
    }

    def transition(self, candidate: WorldEventCandidate, target: WorldEventStatus) -> WorldEventCandidate:
        if target not in self.FLOW[candidate.verification_status]:
            raise ValueError("invalid world event candidate transition")
        candidate.verification_status = target
        return candidate
