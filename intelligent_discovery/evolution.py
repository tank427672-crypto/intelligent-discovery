"""Controlled evolution queue: candidates require experiment and human approval."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from .observability import now


class EvolutionStatus(StrEnum):
    OBSERVED = "observed"
    COLLECTED = "collected"
    EVALUATING = "evaluating"
    EXPERIMENTING = "experimenting"
    APPROVED = "approved"
    RELEASED = "released"
    REJECTED = "rejected"


@dataclass(slots=True)
class EvolutionCandidate:
    source_incident: str
    problem_summary: str
    impact: float
    frequency: int
    priority: float
    suggested_change: str
    status: EvolutionStatus = EvolutionStatus.OBSERVED
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: object = field(default_factory=now)

    @classmethod
    def prioritized(
        cls,
        source_incident: str,
        problem_summary: str,
        impact: float,
        frequency: int,
        severity: float,
        suggested_change: str,
    ) -> EvolutionCandidate:
        return cls(
            source_incident, problem_summary, impact, frequency, impact * severity * max(frequency, 1), suggested_change
        )


class EvolutionService:
    def __init__(self, store: EvolutionStore | None = None, cooldown_days: int = 7) -> None:
        self.store, self.cooldown_days = store, cooldown_days

    def transition(
        self,
        c: EvolutionCandidate,
        next_status: EvolutionStatus,
        experiment_verified: bool = False,
        human_approved: bool = False,
    ) -> EvolutionCandidate:
        if next_status == EvolutionStatus.APPROVED and not (experiment_verified and human_approved):
            raise ValueError("approval requires verified experiment and human approval")
        if next_status == EvolutionStatus.RELEASED and c.status != EvolutionStatus.APPROVED:
            raise ValueError("release requires approval")
        c.status = next_status
        if self.store:
            self.store.save(c)
        return c

    def trigger(self, candidate: EvolutionCandidate, major_incident: bool = False) -> EvolutionCandidate:
        candidate.status = EvolutionStatus.EVALUATING if major_incident else EvolutionStatus.COLLECTED
        if self.store:
            self.store.save(candidate)
        return candidate


class EvolutionStore(Protocol):
    def save(self, value: EvolutionCandidate) -> None: ...
    def recent_release_exists(self, cooldown_days: int) -> bool: ...


class SQLiteEvolutionAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS evolution_candidates (id TEXT PRIMARY KEY, incident TEXT, summary TEXT, impact REAL, frequency INTEGER, priority REAL, suggested TEXT, status TEXT, created TEXT)"
            )

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save(self, v: EvolutionCandidate) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT OR REPLACE INTO evolution_candidates VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    v.id,
                    v.source_incident,
                    v.problem_summary,
                    v.impact,
                    v.frequency,
                    v.priority,
                    v.suggested_change,
                    v.status,
                    v.created_at.isoformat(),
                ),
            )

    def recent_release_exists(self, cooldown_days: int) -> bool:
        return False
