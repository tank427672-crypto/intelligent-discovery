"""Contracts for research providers. No network provider is bundled in v0.2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from .domain import Evidence, Source


class ResearchFailureKind(StrEnum):
    SOURCE_UNAVAILABLE = "source_unavailable"
    INSUFFICIENT_DATA = "insufficient_data"
    CONFLICTING_INFORMATION = "conflicting_information"
    VERIFICATION_FAILED = "verification_failed"
    UNSUPPORTED_LICENSE = "unsupported_license"


@dataclass(frozen=True, slots=True)
class ResearchFailure:
    kind: ResearchFailureKind
    message: str
    retryable: bool
    source_url: str | None = None


@dataclass(frozen=True, slots=True)
class SearchRequest:
    query: str
    task_id: str
    limit: int = 10


@dataclass(slots=True)
class ResearchResponse:
    sources: list[Source] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    failures: list[ResearchFailure] = field(default_factory=list)


class ResearchProvider(Protocol):
    """A provider reports uncertainty as structured failures, never fabricated data."""

    name: str

    def search(self, request: SearchRequest) -> ResearchResponse: ...
    def fetch(self, source: Source) -> ResearchResponse: ...
    def parse(self, source: Source) -> ResearchResponse: ...
    def verify(self, evidence: Evidence) -> ResearchResponse: ...
