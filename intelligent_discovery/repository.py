from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .domain import (
    CaseLifecycleStatus,
    CaseRecord,
    CaseRevision,
    CaseTaskLink,
    CaseTaskRelation,
    CaseVerificationStatus,
    Category,
    Classification,
    ClassificationSource,
    ClassificationStatus,
    Concept,
    DataLifecycleStatus,
    DataVisibility,
    DiscoveryTask,
    Evidence,
    EvidenceRelation,
    EvidenceStatus,
    EvolutionExperiment,
    FeaturePerformance,
    FeedbackVerdict,
    Finding,
    FindingFeedback,
    FindingKind,
    GovernanceRecord,
    GraphNodeType,
    ImprovementProposal,
    ImprovementStatus,
    KnowledgeRecord,
    RecommendationRecord,
    ReflectionRecord,
    ReflectionStatus,
    Relationship,
    RelationshipType,
    ReviewRecord,
    SearchFeedback,
    SearchQuery,
    Source,
    SourceStatus,
    SourceType,
    SystemFeedback,
    Tag,
    TaskStatus,
    TrustLevel,
    VisibilityRecord,
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
                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY, origin_task_id TEXT NOT NULL, name TEXT NOT NULL, case_type TEXT NOT NULL,
                    background TEXT NOT NULL, problem TEXT NOT NULL, solution TEXT NOT NULL,
                    outcome TEXT NOT NULL, success_factors TEXT NOT NULL, failure_factors TEXT NOT NULL,
                    lessons_learned TEXT NOT NULL, applicability TEXT NOT NULL, limitations TEXT NOT NULL,
                    source_ids TEXT NOT NULL, evidence_ids TEXT NOT NULL, finding_ids TEXT NOT NULL,
                    license_info TEXT NOT NULL, lifecycle_status TEXT NOT NULL,
                    verification_status TEXT NOT NULL, credibility REAL NOT NULL, version INTEGER NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS case_revisions (
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL, version INTEGER NOT NULL,
                    summary TEXT NOT NULL, change_reason TEXT NOT NULL, changed_fields TEXT NOT NULL,
                    created_at TEXT NOT NULL, FOREIGN KEY(case_id) REFERENCES cases(id)
                );
                CREATE TABLE IF NOT EXISTS case_task_links (
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL, task_id TEXT NOT NULL,
                    relation TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(case_id, task_id, relation), FOREIGN KEY(case_id) REFERENCES cases(id),
                    FOREIGN KEY(task_id) REFERENCES tasks(id)
                );
                CREATE TABLE IF NOT EXISTS concepts (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, concept_type TEXT NOT NULL,
                    description TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(name, concept_type)
                );
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY, source_type TEXT NOT NULL, source_id TEXT NOT NULL,
                    target_type TEXT NOT NULL, target_id TEXT NOT NULL, relationship_type TEXT NOT NULL,
                    evidence_ids TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_relationship_source ON relationships(source_type, source_id);
                CREATE INDEX IF NOT EXISTS idx_relationship_target ON relationships(target_type, target_id);
                CREATE TABLE IF NOT EXISTS reflection_records (
                    id TEXT PRIMARY KEY, case_id TEXT NOT NULL, original_judgment TEXT NOT NULL,
                    actual_outcome TEXT NOT NULL, deviation TEXT NOT NULL, cause_analysis TEXT NOT NULL,
                    learning_update TEXT NOT NULL, evidence_ids TEXT NOT NULL, status TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, FOREIGN KEY(case_id) REFERENCES cases(id)
                );
                CREATE TABLE IF NOT EXISTS categories (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, category_type TEXT NOT NULL,
                    parent_id TEXT, created_at TEXT NOT NULL, UNIQUE(name, category_type)
                );
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS classifications (
                    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL,
                    category_id TEXT, tag_id TEXT, confidence REAL NOT NULL, source TEXT NOT NULL,
                    status TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS search_queries (
                    id TEXT PRIMARY KEY, query TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS search_feedback (
                    id TEXT PRIMARY KEY, search_query_id TEXT NOT NULL, result_type TEXT NOT NULL,
                    result_id TEXT NOT NULL, useful INTEGER NOT NULL, comment TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recommendation_records (
                    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL, reason TEXT NOT NULL,
                    evidence_ids TEXT NOT NULL, case_ids TEXT NOT NULL, feedback TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS governance_records (
                    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL, action TEXT NOT NULL,
                    reason TEXT NOT NULL, actor_reference TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS review_records (
                    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL,
                    reviewer_reference TEXT NOT NULL,
                    decision TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS visibility_records (
                    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL, visibility TEXT NOT NULL,
                    lifecycle_status TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(object_type, object_id)
                );
                CREATE TABLE IF NOT EXISTS system_feedback (
                    id TEXT PRIMARY KEY, feature TEXT NOT NULL, feedback_type TEXT NOT NULL, rating INTEGER,
                    description TEXT NOT NULL, related_action TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS improvement_proposals (
                    id TEXT PRIMARY KEY, problem TEXT NOT NULL, feedback_ids TEXT NOT NULL, proposal TEXT NOT NULL,
                    priority TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evolution_experiments (
                    id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL, objective TEXT NOT NULL,
                    change_description TEXT NOT NULL,
                    metrics TEXT NOT NULL, result TEXT NOT NULL, status TEXT NOT NULL
                );
            """)
            self._migrate_source_columns(conn)
            self._migrate_finding_columns(conn)
            self._migrate_case_columns(conn)

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

    @staticmethod
    def _migrate_case_columns(conn: sqlite3.Connection) -> None:
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(cases)")}
        if "origin_task_id" not in existing:
            conn.execute("ALTER TABLE cases ADD COLUMN origin_task_id TEXT NOT NULL DEFAULT ''")

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

    def save_case(self, case: CaseRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO cases (
                    id, origin_task_id, name, case_type, background, problem, solution, outcome, success_factors,
                    failure_factors, lessons_learned, applicability, limitations, source_ids, evidence_ids,
                    finding_ids, license_info, lifecycle_status, verification_status, credibility, version,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    case.id,
                    case.origin_task_id,
                    case.name,
                    case.case_type,
                    case.background,
                    case.problem,
                    case.solution,
                    case.outcome,
                    case.success_factors,
                    case.failure_factors,
                    case.lessons_learned,
                    case.applicability,
                    case.limitations,
                    json.dumps(case.source_ids),
                    json.dumps(case.evidence_ids),
                    json.dumps(case.finding_ids),
                    case.license_info,
                    case.lifecycle_status,
                    case.verification_status,
                    case.credibility,
                    case.version,
                    case.created_at.isoformat(),
                    case.updated_at.isoformat(),
                ),
            )

    def get_case(self, case_id: str) -> CaseRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        return self._case(row) if row else None

    def list_cases(self, task_id: str | None = None) -> list[CaseRecord]:
        with self.connect() as conn:
            if task_id:
                rows = conn.execute(
                    """SELECT cases.* FROM cases
                    INNER JOIN case_task_links ON cases.id = case_task_links.case_id
                    WHERE case_task_links.task_id = ? ORDER BY cases.updated_at DESC""",
                    (task_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM cases ORDER BY updated_at DESC").fetchall()
        return [self._case(row) for row in rows]

    def save_case_revision(self, revision: CaseRevision) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO case_revisions VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    revision.id,
                    revision.case_id,
                    revision.version,
                    revision.summary,
                    revision.change_reason,
                    json.dumps(revision.changed_fields),
                    revision.created_at.isoformat(),
                ),
            )

    def list_case_revisions(self, case_id: str) -> list[CaseRevision]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM case_revisions WHERE case_id = ? ORDER BY version", (case_id,)
            ).fetchall()
        return [self._case_revision(row) for row in rows]

    def save_case_task_link(self, link: CaseTaskLink) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO case_task_links VALUES (?, ?, ?, ?, ?, ?)",
                (link.id, link.case_id, link.task_id, link.relation, link.note, link.created_at.isoformat()),
            )

    def list_case_task_links(self, task_id: str) -> list[CaseTaskLink]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM case_task_links WHERE task_id = ?", (task_id,)).fetchall()
        return [self._case_task_link(row) for row in rows]

    def save_concept(self, concept: Concept) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO concepts VALUES (?, ?, ?, ?, ?, ?)",
                (
                    concept.id,
                    concept.name,
                    concept.concept_type,
                    concept.description,
                    concept.created_at.isoformat(),
                    concept.updated_at.isoformat(),
                ),
            )

    def get_concept(self, concept_id: str) -> Concept | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM concepts WHERE id = ?", (concept_id,)).fetchone()
        return self._concept(row) if row else None

    def list_concepts(self, query: str | None = None) -> list[Concept]:
        with self.connect() as conn:
            if query:
                pattern = f"%{query}%"
                rows = conn.execute(
                    "SELECT * FROM concepts WHERE name LIKE ? OR description LIKE ? ORDER BY name", (pattern, pattern)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM concepts ORDER BY name").fetchall()
        return [self._concept(row) for row in rows]

    def save_relationship(self, relationship: Relationship) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    relationship.id,
                    relationship.source_type,
                    relationship.source_id,
                    relationship.target_type,
                    relationship.target_id,
                    relationship.relationship_type,
                    json.dumps(relationship.evidence_ids),
                    relationship.description,
                    relationship.created_at.isoformat(),
                ),
            )

    def list_relationships(self, node_type: GraphNodeType, node_id: str) -> list[Relationship]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM relationships WHERE (source_type = ? AND source_id = ?)
                OR (target_type = ? AND target_id = ?) ORDER BY created_at""",
                (node_type, node_id, node_type, node_id),
            ).fetchall()
        return [self._relationship(row) for row in rows]

    def entity_exists(self, node_type: GraphNodeType, entity_id: str) -> bool:
        tables = {
            GraphNodeType.SOURCE: "sources",
            GraphNodeType.EVIDENCE: "evidence",
            GraphNodeType.FINDING: "findings",
            GraphNodeType.KNOWLEDGE: "knowledge_records",
            GraphNodeType.CASE: "cases",
            GraphNodeType.CONCEPT: "concepts",
        }
        with self.connect() as conn:
            return conn.execute(f"SELECT 1 FROM {tables[node_type]} WHERE id = ?", (entity_id,)).fetchone() is not None

    def save_reflection(self, reflection: ReflectionRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO reflection_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    reflection.id,
                    reflection.case_id,
                    reflection.original_judgment,
                    reflection.actual_outcome,
                    reflection.deviation,
                    reflection.cause_analysis,
                    reflection.learning_update,
                    json.dumps(reflection.evidence_ids),
                    reflection.status,
                    reflection.created_at.isoformat(),
                    reflection.updated_at.isoformat(),
                ),
            )

    def list_reflections(self, case_id: str) -> list[ReflectionRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM reflection_records WHERE case_id = ? ORDER BY created_at", (case_id,)
            ).fetchall()
        return [self._reflection(row) for row in rows]

    def save_category(self, category: Category) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO categories VALUES (?, ?, ?, ?, ?)",
                (
                    category.id,
                    category.name,
                    category.category_type,
                    category.parent_id,
                    category.created_at.isoformat(),
                ),
            )

    def list_categories(self) -> list[Category]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM categories ORDER BY category_type, name").fetchall()
        return [
            Category(
                id=row["id"],
                name=row["name"],
                category_type=row["category_type"],
                parent_id=row["parent_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def save_tag(self, tag: Tag) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO tags VALUES (?, ?, ?)", (tag.id, tag.name, tag.created_at.isoformat()))

    def list_tags(self) -> list[Tag]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
        return [
            Tag(id=row["id"], name=row["name"], created_at=datetime.fromisoformat(row["created_at"])) for row in rows
        ]

    def save_classification(self, classification: Classification) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO classifications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    classification.id,
                    classification.object_type,
                    classification.object_id,
                    classification.category_id,
                    classification.tag_id,
                    classification.confidence,
                    classification.source,
                    classification.status,
                    classification.created_at.isoformat(),
                ),
            )

    def list_classifications(self, object_type: GraphNodeType, object_id: str) -> list[Classification]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM classifications WHERE object_type = ? AND object_id = ? ORDER BY created_at",
                (object_type, object_id),
            ).fetchall()
        return [
            Classification(
                id=row["id"],
                object_type=GraphNodeType(row["object_type"]),
                object_id=row["object_id"],
                category_id=row["category_id"],
                tag_id=row["tag_id"],
                confidence=row["confidence"],
                source=ClassificationSource(row["source"]),
                status=ClassificationStatus(row["status"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def save_search_query(self, query: SearchQuery) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO search_queries VALUES (?, ?, ?)", (query.id, query.query, query.created_at.isoformat())
            )

    def save_search_feedback(self, feedback: SearchFeedback) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO search_feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feedback.id,
                    feedback.search_query_id,
                    feedback.result_type,
                    feedback.result_id,
                    feedback.useful,
                    feedback.comment,
                    feedback.created_at.isoformat(),
                ),
            )

    def save_recommendation(self, recommendation: RecommendationRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO recommendation_records VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    recommendation.id,
                    recommendation.object_type,
                    recommendation.object_id,
                    recommendation.reason,
                    json.dumps(recommendation.evidence_ids),
                    json.dumps(recommendation.case_ids),
                    recommendation.feedback,
                    recommendation.created_at.isoformat(),
                ),
            )

    def search_assets(self, query: str) -> list[dict[str, object]]:
        pattern = f"%{query}%"
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT 'concept' AS kind, id, name AS title, description AS summary
                FROM concepts WHERE name LIKE ? OR description LIKE ?
                UNION ALL SELECT 'case', id, name, lessons_learned
                FROM cases WHERE name LIKE ? OR lessons_learned LIKE ?
                UNION ALL SELECT 'finding', id, statement, rationale
                FROM findings WHERE statement LIKE ? OR rationale LIKE ?
                UNION ALL SELECT 'knowledge', id, title, summary
                FROM knowledge_records WHERE title LIKE ? OR summary LIKE ?""",
                (pattern, pattern, pattern, pattern, pattern, pattern, pattern, pattern),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_governance(self, record: GovernanceRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO governance_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.object_type,
                    record.object_id,
                    record.action,
                    record.reason,
                    record.actor_reference,
                    record.created_at.isoformat(),
                ),
            )

    def save_review(self, record: ReviewRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO review_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.object_type,
                    record.object_id,
                    record.reviewer_reference,
                    record.decision,
                    record.reason,
                    record.created_at.isoformat(),
                ),
            )

    def save_visibility(self, record: VisibilityRecord) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO visibility_records VALUES (?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.object_type,
                    record.object_id,
                    record.visibility,
                    record.lifecycle_status,
                    record.updated_at.isoformat(),
                ),
            )

    def get_visibility(self, object_type: GraphNodeType, object_id: str) -> VisibilityRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM visibility_records WHERE object_type = ? AND object_id = ?", (object_type, object_id)
            ).fetchone()
        return (
            VisibilityRecord(
                id=row["id"],
                object_type=GraphNodeType(row["object_type"]),
                object_id=row["object_id"],
                visibility=DataVisibility(row["visibility"]),
                lifecycle_status=DataLifecycleStatus(row["lifecycle_status"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            if row
            else None
        )

    def save_system_feedback(self, feedback: SystemFeedback) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO system_feedback VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    feedback.id,
                    feedback.feature,
                    feedback.feedback_type,
                    feedback.rating,
                    feedback.description,
                    feedback.related_action,
                    feedback.created_at.isoformat(),
                ),
            )

    def feature_performance(self, feature: str) -> FeaturePerformance:
        with self.connect() as conn:
            row = conn.execute(
                """SELECT COUNT(*) usage, COALESCE(SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END), 0) success,
                COALESCE(SUM(rating), 0) satisfaction, COUNT(rating) ratings FROM system_feedback WHERE feature = ?""",
                (feature,),
            ).fetchone()
            modes = conn.execute(
                "SELECT feedback_type FROM system_feedback WHERE feature = ? AND rating IS NOT NULL AND rating <= 2",
                (feature,),
            ).fetchall()
        return FeaturePerformance(
            feature=feature,
            usage_count=row["usage"],
            successful_count=row["success"],
            satisfaction_sum=row["satisfaction"],
            feedback_count=row["ratings"],
            failure_modes=[item["feedback_type"] for item in modes],
        )

    def save_improvement(self, proposal: ImprovementProposal) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO improvement_proposals VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    proposal.id,
                    proposal.problem,
                    json.dumps(proposal.feedback_ids),
                    proposal.proposal,
                    proposal.priority,
                    proposal.status,
                    proposal.created_at.isoformat(),
                ),
            )

    def get_improvement(self, proposal_id: str) -> ImprovementProposal | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM improvement_proposals WHERE id = ?", (proposal_id,)).fetchone()
        return (
            ImprovementProposal(
                id=row["id"],
                problem=row["problem"],
                feedback_ids=json.loads(row["feedback_ids"]),
                proposal=row["proposal"],
                priority=row["priority"],
                status=ImprovementStatus(row["status"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            if row
            else None
        )

    def save_experiment(self, experiment: EvolutionExperiment) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO evolution_experiments VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    experiment.id,
                    experiment.proposal_id,
                    experiment.objective,
                    experiment.change_description,
                    json.dumps(experiment.metrics),
                    experiment.result,
                    experiment.status,
                ),
            )

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

    @staticmethod
    def _case(row: sqlite3.Row) -> CaseRecord:
        return CaseRecord(
            id=row["id"],
            origin_task_id=row["origin_task_id"],
            name=row["name"],
            case_type=row["case_type"],
            background=row["background"],
            problem=row["problem"],
            solution=row["solution"],
            outcome=row["outcome"],
            success_factors=row["success_factors"],
            failure_factors=row["failure_factors"],
            lessons_learned=row["lessons_learned"],
            applicability=row["applicability"],
            limitations=row["limitations"],
            source_ids=json.loads(row["source_ids"]),
            evidence_ids=json.loads(row["evidence_ids"]),
            finding_ids=json.loads(row["finding_ids"]),
            license_info=row["license_info"],
            lifecycle_status=CaseLifecycleStatus(row["lifecycle_status"]),
            verification_status=CaseVerificationStatus(row["verification_status"]),
            credibility=row["credibility"],
            version=row["version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _case_revision(row: sqlite3.Row) -> CaseRevision:
        return CaseRevision(
            id=row["id"],
            case_id=row["case_id"],
            version=row["version"],
            summary=row["summary"],
            change_reason=row["change_reason"],
            changed_fields=json.loads(row["changed_fields"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _case_task_link(row: sqlite3.Row) -> CaseTaskLink:
        return CaseTaskLink(
            id=row["id"],
            case_id=row["case_id"],
            task_id=row["task_id"],
            relation=CaseTaskRelation(row["relation"]),
            note=row["note"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _concept(row: sqlite3.Row) -> Concept:
        return Concept(
            id=row["id"],
            name=row["name"],
            concept_type=row["concept_type"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _relationship(row: sqlite3.Row) -> Relationship:
        return Relationship(
            id=row["id"],
            source_type=GraphNodeType(row["source_type"]),
            source_id=row["source_id"],
            target_type=GraphNodeType(row["target_type"]),
            target_id=row["target_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            evidence_ids=json.loads(row["evidence_ids"]),
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _reflection(row: sqlite3.Row) -> ReflectionRecord:
        return ReflectionRecord(
            id=row["id"],
            case_id=row["case_id"],
            original_judgment=row["original_judgment"],
            actual_outcome=row["actual_outcome"],
            deviation=row["deviation"],
            cause_analysis=row["cause_analysis"],
            learning_update=row["learning_update"],
            evidence_ids=json.loads(row["evidence_ids"]),
            status=ReflectionStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
