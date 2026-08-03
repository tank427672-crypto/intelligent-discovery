"""Reliability workflow records; corrections are proposals for humans, never automatic changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from .observability import now


@dataclass(slots=True)
class AnomalyRecord:
    anomaly_type: str
    severity: str
    related_object: str
    description: str
    status: str = "detected"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


@dataclass(slots=True)
class CorrectionAction:
    anomaly_id: str
    action_type: str
    description: str
    result: str = "pending_human_review"
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class EvolutionLesson:
    incident_id: str
    lesson: str
    prevention_rule: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


class ReliabilityService:
    def assess(self, anomaly: AnomalyRecord) -> AnomalyRecord:
        anomaly.status = "assessed"
        return anomaly

    def correction(self, action: CorrectionAction) -> CorrectionAction:
        if action.action_type not in {"downgrade", "review", "archive", "retry", "restore"}:
            raise ValueError("unsupported correction action")
        return action
