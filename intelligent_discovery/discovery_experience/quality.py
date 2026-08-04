"""Content quality is a transparent assessment, never a truth guarantee."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContentQualityLevel(StrEnum):
    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    TRUSTED = "trusted"
    FEATURED = "featured"


@dataclass(frozen=True, slots=True)
class ContentQualityAssessment:
    content_id: str
    source_quality: float
    evidence_strength: float
    completeness: float
    freshness: float
    expert_enhanced: bool
    user_feedback_summary: str
    level: ContentQualityLevel
    limitations: list[str]

    def __post_init__(self) -> None:
        if any(
            not 0 <= value <= 1
            for value in (self.source_quality, self.evidence_strength, self.completeness, self.freshness)
        ):
            raise ValueError("quality factors must be between 0 and 1")
        if self.level is ContentQualityLevel.FEATURED and not self.limitations:
            raise ValueError("featured content must still show limitations")
