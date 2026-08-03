"""Private-Beta release operations with human approval and local recovery drills.

These are domain/application contracts. They do not authenticate users, publish
data, release software, or change knowledge automatically.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


class ReleaseStatus(StrEnum):
    DRAFT = "draft"
    TESTING = "testing"
    SECURITY_REVIEW = "security_review"
    GOVERNANCE_REVIEW = "governance_review"
    APPROVED = "approved"
    RELEASED = "released"
    MONITORING = "monitoring"


class RiskLevel(StrEnum):
    LEVEL_0 = "level_0"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


@dataclass(slots=True)
class ReleaseCandidate:
    version: str
    release_notes: str
    risk_summary: str
    test_summary: str
    security_summary: str
    migration_summary: str
    rollback_summary: str
    status: ReleaseStatus = ReleaseStatus.DRAFT
    scheduled_at: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ReleaseEvidence:
    candidate_id: str
    evidence_type: str
    reference: str
    summary: str
    verified_by: str
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ReleaseRiskAssessment:
    candidate_id: str
    risk: str
    likelihood: float
    impact: float
    mitigation: str
    reviewed_by: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not 0 <= self.likelihood <= 1 or not 0 <= self.impact <= 1:
            raise ValueError("risk likelihood and impact must be between 0 and 1")


@dataclass(slots=True)
class ReleaseRollbackPlan:
    candidate_id: str
    trigger_conditions: list[str]
    steps: list[str]
    data_considerations: str
    tested: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class ReleaseApproval:
    candidate_id: str
    approver: str
    role: str
    decision: str
    rationale: str
    created_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.decision not in {"approved", "rejected"}:
            raise ValueError("release approval decision must be approved or rejected")


@dataclass(slots=True)
class TrustChecklist:
    default_private: bool
    explicit_owner: bool
    export_available: bool
    delete_available: bool
    revocation_available: bool
    access_reason_recorded: bool
    access_audited: bool
    ai_private_data_boundary_checked: bool
    explainability_checked: bool

    def complete(self) -> bool:
        return all(asdict(self).values())


@dataclass(slots=True)
class DataAccessAudit:
    owner_id: str
    action: str
    reason: str
    actor: str
    created_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class DataAsset:
    owner_id: str
    asset_type: str
    payload: dict[str, str]
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class BackupTestRecord:
    source_path: str
    backup_path: str
    source_hash: str
    restored_hash: str
    integrity_verified: bool
    failure_simulated: bool
    consistency_verified: bool
    created_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class BetaAgreement:
    user_id: str
    version: str
    purpose: str
    data_processing_summary: str
    permission_scope: str
    exit_method: str
    accepted_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class BetaConsent:
    user_id: str
    scope: str
    granted: bool
    created_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class BetaExit:
    user_id: str
    reason: str
    requested_at: datetime = field(default_factory=now)
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class EvolutionCalendar:
    weekly_review: bool = True
    monthly_review: bool = True
    quarterly_architecture_review: bool = True
    next_review_at: datetime = field(default_factory=now)


@dataclass(slots=True)
class BetaMetrics:
    consent_completion_rate: float
    delete_request_success_rate: float
    export_success_rate: float
    user_satisfaction: float
    issue_response_hours: float
    error_rate: float
    recovery_time_hours: float
    security_incident_count: int
    case_review_quality: float
    evidence_completeness: float
    feedback_value: float


@dataclass(slots=True)
class CaseReleaseChecklist:
    source_reviewed: bool
    license_reviewed: bool
    evidence_reviewed: bool
    human_approved: bool

    def verified(self) -> bool:
        return all(asdict(self).values())


class PrivateDataStore(Protocol):
    def save_asset(self, asset: DataAsset) -> None: ...
    def list_assets(self, owner_id: str) -> list[DataAsset]: ...
    def delete_assets(self, owner_id: str) -> int: ...
    def save_audit(self, audit: DataAccessAudit) -> None: ...
    def list_audits(self, owner_id: str) -> list[DataAccessAudit]: ...


class DataProtectionCenter:
    """User-controlled local data actions. Every action is auditable."""

    def __init__(self, store: PrivateDataStore) -> None:
        self.store = store

    def view(self, owner_id: str, actor: str, reason: str) -> list[DataAsset]:
        self.store.save_audit(DataAccessAudit(owner_id, "view", reason, actor))
        return self.store.list_assets(owner_id)

    def export(self, owner_id: str, actor: str, reason: str) -> list[dict[str, object]]:
        assets = self.view(owner_id, actor, reason)
        self.store.save_audit(DataAccessAudit(owner_id, "export", reason, actor))
        return [asdict(asset) for asset in assets]

    def delete(self, owner_id: str, actor: str, reason: str) -> int:
        deleted = self.store.delete_assets(owner_id)
        self.store.save_audit(DataAccessAudit(owner_id, "delete", reason, actor))
        return deleted

    def history(self, owner_id: str) -> list[DataAccessAudit]:
        return self.store.list_audits(owner_id)


class BackupVerificationService:
    """Copies, hashes, isolates and restores a file without damaging the source."""

    @staticmethod
    def _digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def exercise(self, source: str | Path, workdir: str | Path) -> BackupTestRecord:
        source_path, workdir_path = Path(source), Path(workdir)
        if not source_path.is_file():
            raise ValueError("backup source must be an existing file")
        workdir_path.mkdir(parents=True, exist_ok=True)
        backup = workdir_path / f"{source_path.name}.backup"
        restored = workdir_path / f"{source_path.name}.restored"
        shutil.copy2(source_path, backup)
        source_hash = self._digest(source_path)
        integrity = source_hash == self._digest(backup)
        restored.write_bytes(b"simulated_failure")
        failure_simulated = restored.read_bytes() == b"simulated_failure"
        shutil.copy2(backup, restored)
        restored_hash = self._digest(restored)
        return BackupTestRecord(
            str(source_path),
            str(backup),
            source_hash,
            restored_hash,
            integrity,
            failure_simulated,
            source_hash == restored_hash,
        )


class ReleaseService:
    """Valid transitions and evidence requirements; never deploys anything."""

    FLOW = {
        ReleaseStatus.DRAFT: ReleaseStatus.TESTING,
        ReleaseStatus.TESTING: ReleaseStatus.SECURITY_REVIEW,
        ReleaseStatus.SECURITY_REVIEW: ReleaseStatus.GOVERNANCE_REVIEW,
        ReleaseStatus.GOVERNANCE_REVIEW: ReleaseStatus.APPROVED,
        ReleaseStatus.APPROVED: ReleaseStatus.RELEASED,
        ReleaseStatus.RELEASED: ReleaseStatus.MONITORING,
    }

    def transition(
        self,
        candidate: ReleaseCandidate,
        next_status: ReleaseStatus,
        trust: TrustChecklist | None = None,
        approval: ReleaseApproval | None = None,
    ) -> ReleaseCandidate:
        if self.FLOW.get(candidate.status) is not next_status:
            raise ValueError("invalid release transition")
        if next_status is ReleaseStatus.APPROVED and (
            trust is None or not trust.complete() or approval is None or approval.decision != "approved"
        ):
            raise ValueError("approval requires completed trust checklist and human approval")
        candidate.status = next_status
        return candidate


class OperationsRouting:
    """Maps observed risk to a human-controlled operational queue."""

    @staticmethod
    def route(level: RiskLevel) -> str:
        return {
            RiskLevel.LEVEL_0: "periodic_observation",
            RiskLevel.LEVEL_1: "governance_queue",
            RiskLevel.LEVEL_2: "human_approval_required",
            RiskLevel.LEVEL_3: "major_incident_response",
        }[level]


class SQLitePrivateDataAdapter:
    """Local replacement adapter; production storage must add encryption and retention controls."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(
                "CREATE TABLE IF NOT EXISTS protected_assets "
                "(id TEXT PRIMARY KEY, owner_id TEXT, asset_type TEXT, payload TEXT);"
                "CREATE TABLE IF NOT EXISTS data_access_audit "
                "(id TEXT PRIMARY KEY, owner_id TEXT, action TEXT, reason TEXT, actor TEXT, created_at TEXT);"
            )

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save_asset(self, asset: DataAsset) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO protected_assets VALUES (?, ?, ?, ?)",
                (asset.id, asset.owner_id, asset.asset_type, json.dumps(asset.payload)),
            )

    def list_assets(self, owner_id: str) -> list[DataAsset]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM protected_assets WHERE owner_id = ?", (owner_id,)).fetchall()
        return [DataAsset(row["owner_id"], row["asset_type"], json.loads(row["payload"]), row["id"]) for row in rows]

    def delete_assets(self, owner_id: str) -> int:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM protected_assets WHERE owner_id = ?", (owner_id,))
        return cursor.rowcount

    def save_audit(self, audit: DataAccessAudit) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO data_access_audit VALUES (?, ?, ?, ?, ?, ?)",
                (audit.id, audit.owner_id, audit.action, audit.reason, audit.actor, audit.created_at.isoformat()),
            )

    def list_audits(self, owner_id: str) -> list[DataAccessAudit]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM data_access_audit WHERE owner_id = ?", (owner_id,)).fetchall()
        return [
            DataAccessAudit(
                row["owner_id"],
                row["action"],
                row["reason"],
                row["actor"],
                datetime.fromisoformat(row["created_at"]),
                row["id"],
            )
            for row in rows
        ]
