from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .domain import DiscoveryTask, Finding, FindingKind, KnowledgeRecord, Source, TaskStatus


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
                    collected_at TEXT NOT NULL, FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, statement TEXT NOT NULL,
                    kind TEXT NOT NULL, confidence REAL NOT NULL, source_ids TEXT NOT NULL,
                    rationale TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS knowledge_records (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, title TEXT NOT NULL,
                    summary TEXT NOT NULL, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
            """)

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
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    source.id,
                    source.task_id,
                    source.title,
                    source.url,
                    source.excerpt,
                    source.credibility,
                    source.collected_at.isoformat(),
                ),
            )

    def list_sources(self, task_id: str) -> list[Source]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM sources WHERE task_id = ? ORDER BY collected_at", (task_id,)).fetchall()
        return [self._source(row) for row in rows]

    def save_finding(self, finding: Finding) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    finding.id,
                    finding.task_id,
                    finding.statement,
                    finding.kind,
                    finding.confidence,
                    json.dumps(finding.source_ids),
                    finding.rationale,
                    finding.created_at.isoformat(),
                ),
            )

    def list_findings(self, task_id: str) -> list[Finding]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM findings WHERE task_id = ? ORDER BY created_at", (task_id,)).fetchall()
        return [self._finding(row) for row in rows]

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
            collected_at=datetime.fromisoformat(row["collected_at"]),
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
            rationale=row["rationale"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
