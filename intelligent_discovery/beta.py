"""Beta-release contracts and services.

This module deliberately contains no production identity provider, no automatic
publication, and no automatic governance action.  It turns beta activity into
reviewable records and privacy-safe observability events.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from .observability import EventRecord


class BetaRole(StrEnum):
    OBSERVER = "observer"
    TESTER = "tester"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"


class BetaFeedbackType(StrEnum):
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    CASE = "case"
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"


class ReleaseStage(StrEnum):
    INTERNAL_ALPHA = "internal_alpha"
    PRIVATE_BETA = "private_beta"
    PUBLIC_BETA = "public_beta"


@dataclass(slots=True)
class CaseLicense:
    """A source-use declaration, not a legal determination."""

    source: str
    license_type: str
    usage_permission: str
    citation_required: bool = True

    def __post_init__(self) -> None:
        if not self.source.startswith(("https://", "http://")):
            raise ValueError("case license source must be a public URL")
        if not self.license_type or not self.usage_permission:
            raise ValueError("license type and usage permission are required")


@dataclass(slots=True)
class BetaUser:
    role: BetaRole
    permissions: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    feedback_score: float = 0

    def allows(self, permission: str) -> bool:
        return permission in self.permissions


@dataclass(slots=True)
class BetaFeedback:
    user_id: str
    target: str
    feedback_type: BetaFeedbackType
    content: str
    priority: str = "normal"
    status: str = "open"
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("feedback content cannot be empty")
        if self.priority not in {"low", "normal", "high", "critical"}:
            raise ValueError("unsupported feedback priority")


@dataclass(slots=True)
class ReleaseCandidate:
    version: str
    stage: ReleaseStage
    test_scope: str
    issues: list[str]
    risks: list[str]
    approved: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ReleaseChecklist:
    functionality: bool
    security: bool
    privacy: bool
    copyright: bool
    governance: bool
    recovery: bool

    def ready(self) -> bool:
        return all(
            (self.functionality, self.security, self.privacy, self.copyright, self.governance, self.recovery)
        )


@dataclass(slots=True)
class ContributionScorePreview:
    """An explainable preview only; it grants neither points nor privileges."""

    contribution_quality: float
    feedback_value: float
    case_verification: float

    def score(self) -> float:
        return round((self.contribution_quality + self.feedback_value + self.case_verification) / 3, 2)


class AbuseDetectionProvider(Protocol):
    """Future contract. Signals must be reviewed; it cannot impose sanctions."""

    def assess(self, preview: ContributionScorePreview) -> list[str]: ...


class BetaStore(Protocol):
    def save_user(self, user: BetaUser) -> None: ...
    def get_user(self, user_id: str) -> BetaUser | None: ...
    def save_feedback(self, feedback: BetaFeedback) -> None: ...
    def list_feedback(self) -> list[BetaFeedback]: ...


class EventEmitter(Protocol):
    def emit(self, event: EventRecord) -> EventRecord: ...


class BetaFeedbackService:
    """Captures feedback and provides a review route, without making changes."""

    def __init__(self, store: BetaStore, events: EventEmitter | None = None) -> None:
        self.store = store
        self.events = events

    def register_user(self, user: BetaUser) -> BetaUser:
        self.store.save_user(user)
        return user

    def submit(self, feedback: BetaFeedback) -> BetaFeedback:
        user = self.store.get_user(feedback.user_id)
        if user is None or not user.allows("feedback:submit"):
            raise PermissionError("beta user is not allowed to submit feedback")
        self.store.save_feedback(feedback)
        if self.events:
            self.events.emit(
                EventRecord(
                    event_type="FeedbackSubmitted",
                    actor=feedback.user_id,
                    target=feedback.target,
                    metadata={"feedback_type": feedback.feedback_type, "priority": feedback.priority},
                )
            )
        return feedback

    @staticmethod
    def route(feedback: BetaFeedback) -> str:
        """Return a review queue, never an automated incident or evolution change."""
        if feedback.feedback_type is BetaFeedbackType.BUG and feedback.priority in {"high", "critical"}:
            return "incident_triage"
        return "periodic_governance_review"


class BetaReleaseService:
    """Evaluates readiness evidence; a human approval remains mandatory."""

    @staticmethod
    def can_progress(candidate: ReleaseCandidate, checklist: ReleaseChecklist) -> bool:
        return candidate.approved and checklist.ready()


class SQLiteBetaAdapter:
    """A replaceable beta adapter; SQLite is local development storage only."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(
                "CREATE TABLE IF NOT EXISTS beta_users "
                "(id TEXT PRIMARY KEY, role TEXT, permissions TEXT, feedback_score REAL);"
                "CREATE TABLE IF NOT EXISTS beta_feedback "
                "(id TEXT PRIMARY KEY, user_id TEXT, target TEXT, type TEXT, content TEXT, priority TEXT, status TEXT);"
            )

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save_user(self, user: BetaUser) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO beta_users VALUES (?, ?, ?, ?)",
                (user.id, user.role, ",".join(user.permissions), user.feedback_score),
            )

    def get_user(self, user_id: str) -> BetaUser | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM beta_users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return BetaUser(
            id=row["id"],
            role=BetaRole(row["role"]),
            permissions=row["permissions"].split(","),
            feedback_score=row["feedback_score"],
        )

    def save_feedback(self, feedback: BetaFeedback) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO beta_feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feedback.id, feedback.user_id, feedback.target, feedback.feedback_type, feedback.content,
                    feedback.priority, feedback.status,
                ),
            )

    def list_feedback(self) -> list[BetaFeedback]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM beta_feedback ORDER BY id").fetchall()
        return [
            BetaFeedback(
                id=row["id"], user_id=row["user_id"], target=row["target"], feedback_type=BetaFeedbackType(row["type"]),
                content=row["content"], priority=row["priority"], status=row["status"],
            )
            for row in rows
        ]
