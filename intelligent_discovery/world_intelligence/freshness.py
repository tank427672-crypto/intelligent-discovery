"""Freshness model for detected world items; it never asserts current truth."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


class FreshnessStatus(StrEnum):
    ACTIVE = "active"
    NEEDS_UPDATE = "needs_update"
    ARCHIVED = "archived"


@dataclass(slots=True)
class FreshnessRecord:
    object_id: str
    created_at: datetime
    updated_at: datetime
    last_verified_at: datetime | None
    freshness_score: float
    status: FreshnessStatus = FreshnessStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not 0 <= self.freshness_score <= 1:
            raise ValueError("freshness score must be between 0 and 1")


class FreshnessService:
    def evaluate(self, record: FreshnessRecord, max_age_days: int = 30) -> FreshnessRecord:
        reference = record.last_verified_at or record.updated_at
        if now() - reference > timedelta(days=max_age_days * 2):
            record.status = FreshnessStatus.ARCHIVED
        elif now() - reference > timedelta(days=max_age_days):
            record.status = FreshnessStatus.NEEDS_UPDATE
        else:
            record.status = FreshnessStatus.ACTIVE
        return record
