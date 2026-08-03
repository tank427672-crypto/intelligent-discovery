from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, HttpUrl

from .domain import (
    CaseLifecycleStatus,
    CaseRecord,
    CaseTaskRelation,
    CaseVerificationStatus,
    Classification,
    ClassificationSource,
    ClassificationStatus,
    EvidenceRelation,
    EvidenceStatus,
    FeedbackVerdict,
    FindingKind,
    GraphNodeType,
    ReflectionRecord,
    ReflectionStatus,
    RelationshipType,
    SearchFeedback,
    SourceStatus,
    SourceType,
    TrustLevel,
)
from .repository import SQLiteRepository
from .services import (
    CaseService,
    DiscoveryIntelligenceService,
    DiscoveryService,
    KnowledgeGraphService,
    NotFoundError,
    ReportRenderer,
)

database_path = Path(os.getenv("ID_DATABASE_PATH", "data/intelligent_discovery.db"))
service = DiscoveryService(SQLiteRepository(database_path))
case_service = CaseService(service.repository)
graph_service = KnowledgeGraphService(service.repository)
discovery_intelligence = DiscoveryIntelligenceService(service.repository)
renderer = ReportRenderer()
app = FastAPI(
    title="Intelligent Discovery", version="0.5.0", description="Evidence-led discovery and decision support."
)


class TaskInput(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    context: str = Field(default="", max_length=5000)


class SourceInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    excerpt: str = Field(min_length=1, max_length=5000)
    credibility: float = Field(ge=0, le=1)
    source_type: SourceType = SourceType.USER_PROVIDED
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    status: SourceStatus = SourceStatus.UNVERIFIED
    license_info: str = Field(default="unknown", max_length=500)


class EvidenceInput(BaseModel):
    source_id: str
    claim: str = Field(min_length=1, max_length=5000)
    excerpt: str = Field(min_length=1, max_length=5000)
    locator: str = Field(min_length=1, max_length=1000)
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS
    status: EvidenceStatus = EvidenceStatus.EXTRACTED
    limitations: str = Field(default="", max_length=5000)


class FindingInput(BaseModel):
    statement: str = Field(min_length=1, max_length=5000)
    kind: FindingKind
    confidence: float = Field(ge=0, le=1)
    source_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(default="", max_length=5000)


class FeedbackInput(BaseModel):
    finding_id: str
    verdict: FeedbackVerdict
    comment: str = Field(min_length=1, max_length=5000)
    reviewer_label: str = Field(default="human", max_length=200)


class CaseInput(BaseModel):
    origin_task_id: str
    name: str = Field(min_length=1, max_length=500)
    case_type: str = Field(min_length=1, max_length=200)
    background: str = Field(default="", max_length=10000)
    problem: str = Field(default="", max_length=10000)
    solution: str = Field(default="", max_length=10000)
    outcome: str = Field(default="", max_length=10000)
    success_factors: str = Field(default="", max_length=10000)
    failure_factors: str = Field(default="", max_length=10000)
    lessons_learned: str = Field(default="", max_length=10000)
    applicability: str = Field(default="", max_length=10000)
    limitations: str = Field(default="", max_length=10000)
    source_ids: list[str] = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    finding_ids: list[str] = Field(default_factory=list)
    license_info: str = Field(default="unknown", max_length=500)
    verification_status: CaseVerificationStatus = CaseVerificationStatus.PENDING
    credibility: float = Field(default=0, ge=0, le=1)


class CaseUpdateInput(BaseModel):
    change_reason: str = Field(min_length=1, max_length=2000)
    background: str | None = Field(default=None, max_length=10000)
    problem: str | None = Field(default=None, max_length=10000)
    solution: str | None = Field(default=None, max_length=10000)
    outcome: str | None = Field(default=None, max_length=10000)
    success_factors: str | None = Field(default=None, max_length=10000)
    failure_factors: str | None = Field(default=None, max_length=10000)
    lessons_learned: str | None = Field(default=None, max_length=10000)
    applicability: str | None = Field(default=None, max_length=10000)
    limitations: str | None = Field(default=None, max_length=10000)
    license_info: str | None = Field(default=None, max_length=500)
    credibility: float | None = Field(default=None, ge=0, le=1)
    verification_status: CaseVerificationStatus | None = None


class CaseLinkInput(BaseModel):
    task_id: str
    relation: CaseTaskRelation
    note: str = Field(default="", max_length=2000)


class ConceptInput(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    concept_type: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)


class RelationshipInput(BaseModel):
    source_type: GraphNodeType
    source_id: str
    target_type: GraphNodeType
    target_id: str
    relationship_type: RelationshipType
    evidence_ids: list[str] = Field(default_factory=list)
    description: str = Field(default="", max_length=5000)


class ReflectionInput(BaseModel):
    case_id: str
    original_judgment: str = Field(min_length=1, max_length=5000)
    actual_outcome: str = Field(min_length=1, max_length=5000)
    deviation: str = Field(min_length=1, max_length=5000)
    cause_analysis: str = Field(min_length=1, max_length=5000)
    learning_update: str = Field(min_length=1, max_length=5000)
    evidence_ids: list[str] = Field(default_factory=list)
    status: ReflectionStatus = ReflectionStatus.OBSERVED


class CategoryInput(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    category_type: str = Field(min_length=1, max_length=200)
    parent_id: str | None = None


class TagInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ClassificationInput(BaseModel):
    object_type: GraphNodeType
    object_id: str
    category_id: str | None = None
    tag_id: str | None = None
    confidence: float = Field(ge=0, le=1)
    source: ClassificationSource = ClassificationSource.HUMAN
    status: ClassificationStatus = ClassificationStatus.PROPOSED


class SearchFeedbackInput(BaseModel):
    search_query_id: str
    result_type: GraphNodeType
    result_id: str
    useful: bool
    comment: str = Field(default="", max_length=2000)


def serialize(value: object) -> dict[str, object]:
    data = asdict(value)
    return {
        key: item.value if hasattr(item, "value") else item.isoformat() if hasattr(item, "isoformat") else item
        for key, item in data.items()
    }


def translate(action):
    try:
        return action()
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.5.0"}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskInput) -> dict[str, object]:
    return serialize(translate(lambda: service.create_task(payload.question, payload.context)))


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, object]:
    task, sources, evidence, findings, feedback = translate(lambda: service.snapshot(task_id))
    return {
        "task": serialize(task),
        "sources": [serialize(item) for item in sources],
        "evidence": [serialize(item) for item in evidence],
        "findings": [serialize(item) for item in findings],
        "feedback": [serialize(item) for item in feedback],
    }


@app.post("/tasks/{task_id}/sources", status_code=status.HTTP_201_CREATED)
def add_source(task_id: str, payload: SourceInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_source(
                task_id,
                payload.title,
                str(payload.url),
                payload.excerpt,
                payload.credibility,
                payload.source_type,
                payload.trust_level,
                payload.status,
                payload.license_info,
            )
        )
    )


@app.post("/tasks/{task_id}/evidence", status_code=status.HTTP_201_CREATED)
def add_evidence(task_id: str, payload: EvidenceInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_evidence(
                task_id,
                payload.source_id,
                payload.claim,
                payload.excerpt,
                payload.locator,
                payload.relation,
                payload.status,
                payload.limitations,
            )
        )
    )


@app.post("/tasks/{task_id}/findings", status_code=status.HTTP_201_CREATED)
def add_finding(task_id: str, payload: FindingInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_finding(
                task_id,
                payload.statement,
                payload.kind,
                payload.confidence,
                source_ids=payload.source_ids,
                evidence_ids=payload.evidence_ids,
                rationale=payload.rationale,
            )
        )
    )


@app.post("/tasks/{task_id}/feedback", status_code=status.HTTP_201_CREATED)
def add_feedback(task_id: str, payload: FeedbackInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_feedback(
                task_id, payload.finding_id, payload.verdict, payload.comment, payload.reviewer_label
            )
        )
    )


@app.post("/cases", status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseInput) -> dict[str, object]:
    case = CaseRecord(**payload.model_dump())
    return serialize(translate(lambda: case_service.create_case(case)))


@app.get("/cases")
def list_cases(task_id: str | None = None) -> list[dict[str, object]]:
    return [serialize(item) for item in service.repository.list_cases(task_id)]


@app.get("/cases/{case_id}")
def get_case(case_id: str) -> dict[str, object]:
    case = translate(lambda: case_service.get_case(case_id))
    return {
        "case": serialize(case),
        "revisions": [serialize(item) for item in case_service.revisions(case_id)],
    }


@app.patch("/cases/{case_id}")
def revise_case(case_id: str, payload: CaseUpdateInput) -> dict[str, object]:
    changes = payload.model_dump(exclude={"change_reason"}, exclude_none=True)
    return serialize(translate(lambda: case_service.revise_case(case_id, payload.change_reason, **changes)))


@app.post("/cases/{case_id}/lifecycle/{lifecycle_status}")
def transition_case(case_id: str, lifecycle_status: CaseLifecycleStatus) -> dict[str, object]:
    return serialize(translate(lambda: case_service.transition_case(case_id, lifecycle_status)))


@app.post("/cases/{case_id}/links", status_code=status.HTTP_201_CREATED)
def link_case(case_id: str, payload: CaseLinkInput) -> dict[str, object]:
    return serialize(
        translate(lambda: case_service.link_case_to_task(case_id, payload.task_id, payload.relation, payload.note))
    )


@app.post("/concepts", status_code=status.HTTP_201_CREATED)
def create_concept(payload: ConceptInput) -> dict[str, object]:
    return serialize(
        translate(lambda: graph_service.create_concept(payload.name, payload.concept_type, payload.description))
    )


@app.get("/concepts")
def list_concepts(query: str | None = None) -> list[dict[str, object]]:
    return [serialize(item) for item in service.repository.list_concepts(query)]


@app.post("/relationships", status_code=status.HTTP_201_CREATED)
def create_relationship(payload: RelationshipInput) -> dict[str, object]:
    return serialize(translate(lambda: graph_service.relate(**payload.model_dump())))


@app.get("/graph/{node_type}/{node_id}")
def graph_neighbors(node_type: GraphNodeType, node_id: str) -> list[dict[str, object]]:
    return [serialize(item) for item in translate(lambda: graph_service.relationships_for(node_type, node_id))]


@app.get("/cases/{case_id}/similar")
def similar_cases(case_id: str) -> list[dict[str, object]]:
    return [serialize(item) for item in translate(lambda: graph_service.similar_cases(case_id))]


@app.post("/reflections", status_code=status.HTTP_201_CREATED)
def create_reflection(payload: ReflectionInput) -> dict[str, object]:
    return serialize(translate(lambda: graph_service.add_reflection(ReflectionRecord(**payload.model_dump()))))


@app.get("/cases/{case_id}/reflections")
def list_reflections(case_id: str) -> list[dict[str, object]]:
    translate(lambda: case_service.get_case(case_id))
    return [serialize(item) for item in service.repository.list_reflections(case_id)]


@app.post("/catalog/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: discovery_intelligence.create_category(payload.name, payload.category_type, payload.parent_id)
        )
    )


@app.get("/catalog/categories")
def list_categories() -> list[dict[str, object]]:
    return [serialize(item) for item in service.repository.list_categories()]


@app.post("/catalog/tags", status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagInput) -> dict[str, object]:
    return serialize(translate(lambda: discovery_intelligence.create_tag(payload.name)))


@app.post("/classifications", status_code=status.HTTP_201_CREATED)
def create_classification(payload: ClassificationInput) -> dict[str, object]:
    return serialize(translate(lambda: discovery_intelligence.classify(Classification(**payload.model_dump()))))


@app.get("/search")
def search(query: str) -> dict[str, object]:
    search_query, results = translate(lambda: discovery_intelligence.search(query))
    return {
        "query": serialize(search_query),
        "results": [
            {
                **result,
                "relationships": [serialize(item) for item in result["relationships"]],
                "classifications": [serialize(item) for item in result["classifications"]],
            }
            for result in results
        ],
    }


@app.post("/search/feedback", status_code=status.HTTP_201_CREATED)
def search_feedback(payload: SearchFeedbackInput) -> dict[str, object]:
    return serialize(
        translate(lambda: discovery_intelligence.add_search_feedback(SearchFeedback(**payload.model_dump())))
    )


@app.post("/tasks/{task_id}/analyze")
def analyze(task_id: str) -> dict[str, object]:
    return serialize(translate(lambda: service.analyze(task_id)))


@app.post("/tasks/{task_id}/complete", status_code=status.HTTP_201_CREATED)
def complete(task_id: str) -> dict[str, object]:
    return serialize(translate(lambda: service.complete(task_id)))


@app.get("/tasks/{task_id}/report", response_class=Response)
def report(task_id: str) -> Response:
    task, sources, evidence, findings, feedback = translate(lambda: service.snapshot(task_id))
    return Response(
        renderer.render(task, sources, evidence, findings, feedback, case_service.cases_for_task(task_id)),
        media_type="text/markdown; charset=utf-8",
    )


@app.get("/knowledge")
def list_knowledge() -> list[dict[str, object]]:
    return [serialize(record) for record in service.repository.list_knowledge()]
