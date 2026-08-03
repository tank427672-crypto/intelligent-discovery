"""Response workflow records. High-impact actions always remain human-governed."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from .observability import now


class IncidentStatus(StrEnum):
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    REVIEWED = "reviewed"
    LEARNED = "learned"


class ResponseActionType(StrEnum):
    NOTIFY = "notify"
    REVIEW = "review"
    RETRY = "retry"
    PAUSE = "pause"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    ARCHIVE = "archive"


@dataclass(slots=True)
class ResponseIncident:
    title: str
    severity: str
    status: IncidentStatus = IncidentStatus.DETECTED
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ResponsePlan:
    trigger_type: str
    severity: str
    actions: list[ResponseActionType]
    approval_required: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ResponseAction:
    incident_id: str
    action_type: ResponseActionType
    description: str
    result: str = "pending_human_review"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: object = field(default_factory=now)


@dataclass(slots=True)
class ResponseEvaluation:
    response_id: str
    before_state: str
    after_state: str
    effectiveness: float
    review: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if not 0 <= self.effectiveness <= 1:
            raise ValueError("effectiveness must be between 0 and 1")


class ResponseService:
    def __init__(self, store: ResponseStore | None = None) -> None:
        self.store = store

    def create_incident(self, incident: ResponseIncident) -> ResponseIncident:
        if self.store:
            self.store.save_incident(incident)
        return incident

    def transition(self, status: IncidentStatus, next_status: IncidentStatus) -> IncidentStatus:
        flow = {
            IncidentStatus.DETECTED: IncidentStatus.ACKNOWLEDGED,
            IncidentStatus.ACKNOWLEDGED: IncidentStatus.INVESTIGATING,
            IncidentStatus.INVESTIGATING: IncidentStatus.MITIGATING,
            IncidentStatus.MITIGATING: IncidentStatus.RESOLVED,
            IncidentStatus.RESOLVED: IncidentStatus.REVIEWED,
            IncidentStatus.REVIEWED: IncidentStatus.LEARNED,
        }
        if flow.get(status) != next_status:
            raise ValueError("invalid incident transition")
        return next_status

    def transition_incident(self, incident: ResponseIncident, next_status: IncidentStatus) -> ResponseIncident:
        incident.status = self.transition(incident.status, next_status)
        if self.store:
            self.store.update_incident_status(incident.id, incident.status)
        return incident

    def record_action(self, action: ResponseAction) -> ResponseAction:
        if self.store:
            self.store.save_action(action)
        return action


class ResponseStore(Protocol):
    def save_incident(self, value: ResponseIncident) -> None: ...
    def update_incident_status(self, incident_id: str, new: IncidentStatus) -> None: ...
    def save_action(self, value: ResponseAction) -> None: ...


class SQLiteResponseAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.executescript(
                "CREATE TABLE IF NOT EXISTS response_incidents (id TEXT PRIMARY KEY,title TEXT,severity TEXT,status TEXT); CREATE TABLE IF NOT EXISTS response_actions (id TEXT PRIMARY KEY,incident_id TEXT,type TEXT,description TEXT,result TEXT,created TEXT);"
            )

    def connect(self):
        return sqlite3.connect(self.path)

    def save_incident(self, v: ResponseIncident) -> None:
        with self.connect() as c:
            c.execute("INSERT INTO response_incidents VALUES (?,?,?,?)", (v.id, v.title, v.severity, v.status))

    def update_incident_status(self, incident_id: str, new: IncidentStatus) -> None:
        with self.connect() as c:
            c.execute("UPDATE response_incidents SET status=? WHERE id=?", (new, incident_id))

    def save_action(self, v: ResponseAction) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO response_actions VALUES (?,?,?,?,?,?)",
                (v.id, v.incident_id, v.action_type, v.description, v.result, v.created_at.isoformat()),
            )
