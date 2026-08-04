"""Continuous Discovery data contracts. They do not optimize attention or implement a UI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .content import DiscoveryContent, DiscoveryContentType


class DiscoveryScope(StrEnum):
    WORLD = "world"
    PERSONAL = "personal"


@dataclass(frozen=True, slots=True)
class DiscoveryStreamItem:
    content_id: str
    content_type: DiscoveryContentType
    title: str
    summary: str
    importance: float
    freshness: float
    trust_score: float
    recommendation_reason: str
    source_count: int
    scope: DiscoveryScope


@dataclass(frozen=True, slots=True)
class DiscoveryValue:
    content_id: str
    helped_understanding: bool
    saved: bool
    prompted_exploration: bool
    solved_problem: bool
    prompted_contribution: bool

    def score(self) -> int:
        return sum(
            (
                self.helped_understanding,
                self.saved,
                self.prompted_exploration,
                self.solved_problem,
                self.prompted_contribution,
            )
        )


@dataclass(frozen=True, slots=True)
class FeaturedDiscovery:
    content_id: str
    curator_id: str
    curation_reason: str
    verified: bool = False


class StreamService:
    def world_item(
        self, content: DiscoveryContent, importance: float, freshness: float, trust_score: float
    ) -> DiscoveryStreamItem:
        return DiscoveryStreamItem(
            content.id,
            content.content_type,
            content.title,
            content.summary,
            importance,
            freshness,
            trust_score,
            "World relevance and source quality.",
            len(content.source_references),
            DiscoveryScope.WORLD,
        )

    def personal_item(self, content: DiscoveryContent, reason: str, interest_confirmed: bool) -> DiscoveryStreamItem:
        if not interest_confirmed:
            raise ValueError("personal discovery requires an explicit interest signal")
        return DiscoveryStreamItem(
            content.id,
            content.content_type,
            content.title,
            content.summary,
            0,
            0,
            0,
            reason,
            len(content.source_references),
            DiscoveryScope.PERSONAL,
        )
