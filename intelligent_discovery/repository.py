from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .domain import (
    DiscoveryTask,
    Evidence,
    EvidenceRelation,
    EvidenceStatus,
    FeedbackVerdict,
    Finding,
    FindingFeedback,
    FindingKind,
    KnowledgeRecord,
    Source,
    SourceStatus,
    SourceType,
    TaskStatus,
    TrustLevel,
)


class SQLiteRepository:
    def __init__(self, database_path: str | Path = "data/intelligent_discovery.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY, question TEXT NOT NULL, context TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, title TEXT NOT NULL,
                    url TEXT NOT NULL, excerpt TEXT NOT NULL, credibility REAL NOT NULL,
                    source_type TEXT NOT NULL DEFAULT 'user_provided',
                    trust_level TEXT NOT NULL DEFAULT 'unverified',
                    status TEXT NOT NULL DEFAULT 'unverified', license_info TEXT NOT NULL DEFAULT 'unknown',
                    published_at TEXT, updated_at TEXT, collected_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, source_id TEXT NOT NULL,
                    claim TEXT NOT NULL, excerpt TEXT NOT NULL, locator TEXT NOT NULL,
                    relation TEXT NOT NULL, status TEXT NOT NULL, limitations TEXT NOT NULL,
                    created_at TEXT NOT NULL, FOREIGN KEY(task_id) REFERENCES tasks(id),
                    FOREIGN KEY(source_id) REFERENCES sources(id)
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, statement TEXT NOT NULL,
                    kind TEXT NOT NULL, confidence REAL NOT NULL, source_ids TEXT NOT NULL,
                    evidence_ids TEXT NOT NULL DEFAULT '[]', rationale TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, finding_id TEXT NOT NULL,
                    verdict TEXT NOT NULL, comment TEXT NOT NULL, reviewer_label TEXT NOT NULL,
                    created_at TEXT NOT NULL, FOREIGN KEY(task_id) REFERENCES tasks(id),
                    FOREIGN KEY(finding_id) REFERENCES findings(id)
                );
                CREATE TABLE IF NOT EXISTS knowledge_records (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, title TEXT NOT NULL,
                    summary TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
            """)
            self._migrate_source_columns(conn)
            self._migrate_finding_columns(conn)

    @staticmethod
    def _migrate_source_columns(conn: sqlite3.Connection) -> None:
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(sources)")}
        migrations = {
            "source_type": "TEXT NOT NULL DEFAULT 'user_provided'",
            "trust_level": "TEXT NOT NULL DEFAULT 'unverified'",
            "status": "TEXT NOT NULL DEFAULT 'unverified'",
            "license_info": "TEXT NOT NULL DEFAULT 'unknown'",
            "published_at": "TEXT",
            "updated_at": "TEXT",
        }
        for column, definition in migrations.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE sources ADD COLUMN {column} {definition}")

    @staticmethod
    def _migrate_finding_columns(conn: sqlite3.Connection) -> None:
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(findings)")}
        if "evidence_ids" not in existing:
            conn.execute("ALTER TABLE findings ADD COLUMN evidence_ids TEXT NOT NULL DEFAULT '[]'")

    def save_task(self, task: DiscoveryTask) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?)",
                (
                    task.id,
                    task.question,
                    task.context,
                    task.status,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                ),
            )

    def get_task(self, task_id: str) -> DiscoveryTask | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._task(row) if row else None

    def save_source(self, source: Source) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO sources (
                    id, task_id, title, url, excerpt, credibility, source_type, trust_level,
                    status, license_info, published_at, updated_at, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source.id,
                    source.task_id,
                    source.title,
                    source.url,
                    source.excerpt,
                    source.credibility,
                    source.source_type,
                    source.trust_level,
                    source.status,
                    source.license_info,
                    source.published_at.isoformat() if source.published_at else None,
                    source.updated_at.isoformat() if source.updated_at else None,
                    source.collected_at.isoformat(),
                ),
            )

    def list_sources(self, task_id: str) -> list[Source]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM sources WHERE task_id = ? ORDER BY collected_at", (task_id,)).fetchall()
        return [self._source(row) for row in rows]

    def save_evidence(self, evidence: Evidence) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    evidence.id,
                    evidence.task_id,
                    evidence.source_id,
                    evidence.claim,
                    evidence.excerpt,
                    evidence.locator,
                    evidence.relation,
                    evidence.status,
                    evidence.limitations,
                    evidence.created_at.isoformat(),
                ),
            )

    def list_evidence(self, task_id: str) -> list[Evidence]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM evidence WHERE task_id = ? ORDER BY created_at", (task_id,)).fetchall()
        return [self._evidence(row) for row in rows]

    def save_finding(self, finding: Finding) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO findings (
                    id, task_id, statement, kind, confidence, source_ids, evidence_ids, rationale, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    finding.id,
                    finding.task_id,
                    finding.statement,
                    finding.kind,
                    finding.confidence,
                    json.dumps(finding.source_ids),
                    json.dumps(finding.evidence_ids),
                    finding.rationale,
                    finding.created_at.isoformat(),
                ),
            )

    def list_findings(self, task_id: str) -> list[Finding]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM findings WHERE task_id = ? ORDER BY created_at", (task_id,)).fetchall()
        return [self._finding(row) for row in rows]

    def save_feedback(self, feedback: FindingFeedback) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feedback.id,
                    feedback.task_id,
                    feedback.finding_id,
                    feedback.verdict,
                    feedback.comment,
                    feedback.reviewer_label,
                    feedback.created_at.isoformat(),
                ),
            )

    def list_feedback(self, task_id: str) -> list[FindingFeedback]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM feedback WHERE task_id = ? ORDER BY created_at", (task_id,)).fetchall()
        return [self._feedback(row) for row in rows]

    def save_knowledge(self, record: KnowledgeRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO knowledge_records VALUES (?, ?, ?, ?, ?)",
                (record.id, record.task_id, record.title, record.summary, record.created_at.isoformat()),
            )

    def list_knowledge(self) -> list[KnowledgeRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM knowledge_records ORDER BY created_at DESC").fetchall()
        return [
            KnowledgeRecord(
                id=r["id"],
                task_id=r["task_id"],
                title=r["title"],
                summary=r["summary"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    @staticmethod
    def _task(row: sqlite3.Row) -> DiscoveryTask:
        return DiscoveryTask(
            id=row["id"],
            question=row["question"],
            context=row["context"],
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _source(row: sqlite3.Row) -> Source:
        return Source(
            id=row["id"],
            task_id=row["task_id"],
            title=row["title"],
            url=row["url"],
            excerpt=row["excerpt"],
            credibility=row["credibility"],
            source_type=SourceType(row["source_type"]),
            trust_level=TrustLevel(row["trust_level"]),
            status=SourceStatus(row["status"]),
            license_info=row["license_info"],
            published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            collected_at=datetime.fromisoformat(row["collected_at"]),
        )

    @staticmethod
    def _evidence(row: sqlite3.Row) -> Evidence:
        return Evidence(
            id=row["id"],
            task_id=row["task_id"],
            source_id=row["source_id"],
            claim=row["claim"],
            excerpt=row["excerpt"],
            locator=row["locator"],
            relation=EvidenceRelation(row["relation"]),
            status=EvidenceStatus(row["status"]),
            limitations=row["limitations"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _finding(row: sqlite3.Row) -> Finding:
        return Finding(
            id=row["id"],
            task_id=row["task_id"],
            statement=row["statement"],
            kind=FindingKind(row["kind"]),
            confidence=row["confidence"],
            source_ids=json.loads(row["source_ids"]),
            evidence_ids=json.loads(row["evidence_ids"]),
            rationale=row["rationale"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _feedback(row: sqlite3.Row) -> FindingFeedback:
        return FindingFeedback(
            id=row["id"],
            task_id=row["task_id"],
            finding_id=row["finding_id"],
            verdict=FeedbackVerdict(row["verdict"]),
            comment=row["comment"],
            reviewer_label=row["reviewer_label"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
