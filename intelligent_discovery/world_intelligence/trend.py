"""Trend signals describe observed change signals, not predictions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class TrendSignal:
    topic: str
    growth_signal: str
    confidence: float
    sources: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    detected_time: datetime = field(default_factory=now)
    limitation: str = "Observed signal only; it is not a prediction."

    def __post_init__(self) -> None:
        if not self.topic.strip() or not self.growth_signal.strip() or not self.sources:
            raise ValueError("trend signal requires topic, signal and sources")
        if not 0 <= self.confidence <= 1:
            raise ValueError("trend confidence must be between 0 and 1")
