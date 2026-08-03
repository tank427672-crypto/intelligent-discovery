"""Privacy-safe observability domain and SQLite adapter; it never records private content."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class EventRecord:
    event_type: str
    actor: str
    target: str
    metadata: dict[str, str] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if any(key.lower() in {"content", "excerpt", "private_text"} for key in self.metadata):
            raise ValueError("events must not contain private content")


@dataclass(slots=True)
class MetricRecord:
    metric_name: str
    value: float
    scope: str
    source: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


@dataclass(slots=True)
class HealthSnapshot:
    system_health: float
    knowledge_health: float
    privacy_health: float
    ecosystem_health: float
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


@dataclass(slots=True)
class AlertRecord:
    alert_type: str
    severity: str
    source: str
    description: str
    status: str = "open"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


@dataclass(slots=True)
class IncidentRecord:
    title: str
    impact: str
    cause: str
    resolution: str
    prevention: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)


class ObservabilityStore(Protocol):
    def save_event(self, value: EventRecord) -> None: ...
    def list_events(self, event_type: str | None = None) -> list[EventRecord]: ...
    def save_metric(self, value: MetricRecord) -> None: ...
    def save_health(self, value: HealthSnapshot) -> None: ...
    def save_alert(self, value: AlertRecord) -> None: ...
    def save_incident(self, value: IncidentRecord) -> None: ...


class ObservabilityService:
    def __init__(self, store: ObservabilityStore) -> None:
        self.store = store

    def emit(self, event: EventRecord) -> EventRecord:
        self.store.save_event(event)
        return event

    def metric(self, metric: MetricRecord) -> MetricRecord:
        self.store.save_metric(metric)
        return metric

    def health(self, snapshot: HealthSnapshot) -> HealthSnapshot:
        if any(
            not 0 <= value <= 1
            for value in (
                snapshot.system_health,
                snapshot.knowledge_health,
                snapshot.privacy_health,
                snapshot.ecosystem_health,
            )
        ):
            raise ValueError("health values must be between 0 and 1")
        self.store.save_health(snapshot)
        return snapshot

    def alert(self, alert: AlertRecord) -> AlertRecord:
        self.store.save_alert(alert)
        return alert

    def incident(self, incident: IncidentRecord) -> IncidentRecord:
        self.store.save_incident(incident)
        return incident


class SQLiteObservabilityAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, type TEXT, actor TEXT, target TEXT, metadata TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS metrics (id TEXT PRIMARY KEY, name TEXT, value REAL, scope TEXT, source TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS health (id TEXT PRIMARY KEY, system REAL, knowledge REAL, privacy REAL, ecosystem REAL, created TEXT);
            CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, type TEXT, severity TEXT, source TEXT, description TEXT, status TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, title TEXT, impact TEXT, cause TEXT, resolution TEXT, prevention TEXT, created TEXT);""")

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def save_event(self, v: EventRecord) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)",
                (v.id, v.event_type, v.actor, v.target, json.dumps(v.metadata), v.created_at.isoformat()),
            )

    def list_events(self, event_type: str | None = None) -> list[EventRecord]:
        with self.connect() as c:
            rows = c.execute(
                "SELECT * FROM events WHERE type = ?" if event_type else "SELECT * FROM events",
                (event_type,) if event_type else (),
            ).fetchall()
        return [
            EventRecord(
                id=r["id"],
                event_type=r["type"],
                actor=r["actor"],
                target=r["target"],
                metadata=json.loads(r["metadata"]),
                created_at=datetime.fromisoformat(r["created"]),
            )
            for r in rows
        ]

    def save_metric(self, v: MetricRecord) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?)",
                (v.id, v.metric_name, v.value, v.scope, v.source, v.created_at.isoformat()),
            )

    def save_health(self, v: HealthSnapshot) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO health VALUES (?, ?, ?, ?, ?, ?)",
                (
                    v.id,
                    v.system_health,
                    v.knowledge_health,
                    v.privacy_health,
                    v.ecosystem_health,
                    v.created_at.isoformat(),
                ),
            )

    def save_alert(self, v: AlertRecord) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?)",
                (v.id, v.alert_type, v.severity, v.source, v.description, v.status, v.created_at.isoformat()),
            )

    def save_incident(self, v: IncidentRecord) -> None:
        with self.connect() as c:
            c.execute(
                "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?)",
                (v.id, v.title, v.impact, v.cause, v.resolution, v.prevention, v.created_at.isoformat()),
            )
