"""Explicit, editable personal-interest signals; no hidden profile inference."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class InterestTrend(StrEnum):
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass(slots=True)
class InterestProfile:
    user_id: str
    topic: str
    interest_level: float
    confidence: float
    trend: InterestTrend
    user_confirmed: bool
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.topic.strip() or not 0 <= self.interest_level <= 1 or not 0 <= self.confidence <= 1:
            raise ValueError("interest profile requires topic and bounded scores")


@dataclass(frozen=True, slots=True)
class RecommendationExplanation:
    content_id: str
    reasons: list[str]
    evidence_references: list[str]
    limitations: list[str]

    def __post_init__(self) -> None:
        if not self.reasons or not self.limitations:
            raise ValueError("recommendations require reasons and limitations")


class InterestProfileStore:
    def __init__(self) -> None:
        self.values: dict[str, InterestProfile] = {}

    def save(self, profile: InterestProfile) -> InterestProfile:
        self.values[profile.id] = profile
        return profile

    def delete(self, profile_id: str, user_id: str) -> None:
        profile = self.values.get(profile_id)
        if profile is None or profile.user_id != user_id:
            raise PermissionError("only the profile owner may delete an interest signal")
        del self.values[profile_id]
