"""Feed and recommendation inputs; these are data contracts, not a UI or ranking algorithm."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain import TrustLevel
from .event_candidate import WorldEventCandidate, WorldEventStatus


@dataclass(frozen=True, slots=True)
class WorldFeedItem:
    title: str
    summary: str
    category: str
    importance: float
    trust_level: TrustLevel
    sources: list[str]
    updated_time: datetime


@dataclass(frozen=True, slots=True)
class RecommendationSignal:
    source_kind: str
    source_id: str
    explanation: str
    evidence_references: list[str]
    limitations: list[str]


class WorldFeedService:
    def from_candidate(self, candidate: WorldEventCandidate, trust_level: TrustLevel) -> WorldFeedItem:
        if candidate.verification_status is not WorldEventStatus.PUBLISHED:
            raise ValueError("only published, verified world events may enter the discovery feed")
        return WorldFeedItem(
            candidate.title,
            candidate.summary,
            candidate.category,
            candidate.impact_score,
            trust_level,
            candidate.source_links,
            candidate.detected_time,
        )
