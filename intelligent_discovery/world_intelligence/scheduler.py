"""Scheduling contract only; no background worker is bundled."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CollectionSchedule:
    source_id: str
    interval_minutes: int
    enabled: bool = False


class CollectionScheduler(Protocol):
    def schedule(self, value: CollectionSchedule) -> None: ...
