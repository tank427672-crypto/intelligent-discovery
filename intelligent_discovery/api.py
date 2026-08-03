from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, HttpUrl

from .domain import FindingKind
from .repository import SQLiteRepository
from .services import DiscoveryService, NotFoundError, ReportRenderer

database_path = Path(os.getenv("ID_DATABASE_PATH", "data/intelligent_discovery.db"))
service = DiscoveryService(SQLiteRepository(database_path))
renderer = ReportRenderer()
app = FastAPI(
    title="Intelligent Discovery", version="0.1.0", description="Evidence-led discovery and decision support."
)


class TaskInput(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    context: str = Field(default="", max_length=5000)


class SourceInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    excerpt: str = Field(min_length=1, max_length=5000)
    credibility: float = Field(ge=0, le=1)


class FindingInput(BaseModel):
    statement: str = Field(min_length=1, max_length=5000)
    kind: FindingKind
    confidence: float = Field(ge=0, le=1)
    source_ids: list[str] = Field(default_factory=list)
    rationale: str = Field(default="", max_length=5000)


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
    return {"status": "ok", "version": "0.1.0"}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskInput) -> dict[str, object]:
    return serialize(translate(lambda: service.create_task(payload.question, payload.context)))


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, object]:
    task, sources, findings = translate(lambda: service.snapshot(task_id))
    return {
        "task": serialize(task),
        "sources": [serialize(item) for item in sources],
        "findings": [serialize(item) for item in findings],
    }


@app.post("/tasks/{task_id}/sources", status_code=status.HTTP_201_CREATED)
def add_source(task_id: str, payload: SourceInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_source(task_id, payload.title, str(payload.url), payload.excerpt, payload.credibility)
        )
    )


@app.post("/tasks/{task_id}/findings", status_code=status.HTTP_201_CREATED)
def add_finding(task_id: str, payload: FindingInput) -> dict[str, object]:
    return serialize(
        translate(
            lambda: service.add_finding(
                task_id, payload.statement, payload.kind, payload.confidence, payload.source_ids, payload.rationale
            )
        )
    )


@app.post("/tasks/{task_id}/analyze")
def analyze(task_id: str) -> dict[str, object]:
    return serialize(translate(lambda: service.analyze(task_id)))


@app.post("/tasks/{task_id}/complete", status_code=status.HTTP_201_CREATED)
def complete(task_id: str) -> dict[str, object]:
    return serialize(translate(lambda: service.complete(task_id)))


@app.get("/tasks/{task_id}/report", response_class=Response)
def report(task_id: str) -> Response:
    task, sources, findings = translate(lambda: service.snapshot(task_id))
    return Response(renderer.render(task, sources, findings), media_type="text/markdown; charset=utf-8")


@app.get("/knowledge")
def list_knowledge() -> list[dict[str, object]]:
    return [serialize(record) for record in service.repository.list_knowledge()]
