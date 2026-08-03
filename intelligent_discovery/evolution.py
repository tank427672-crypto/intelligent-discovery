"""Controlled evolution queue: candidates require experiment and human approval."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
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


class EvolutionService:
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
        return c
