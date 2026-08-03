"""Future-facing contracts for case intelligence providers; no provider is bundled."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .domain import CaseRecord, Evidence, Source


@dataclass(frozen=True, slots=True)
class CaseCandidate:
    name: str
    case_type: str
    source: Source
    rationale: str


@dataclass(slots=True)
class CaseProviderResponse:
    candidates: list[CaseCandidate] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


class CaseDiscoveryProvider(Protocol):
    """Returns candidates and limitations; it does not create verified cases."""

    name: str

    def discover(self, topic: str, task_id: str) -> CaseProviderResponse: ...


class CaseVerificationProvider(Protocol):
    name: str

    def verify(self, candidate: CaseCandidate) -> CaseProviderResponse: ...


class CaseAnalysisProvider(Protocol):
    """Produces traceable analysis drafts for human review, not final judgments."""

    name: str

    def analyze(self, case: CaseRecord) -> CaseProviderResponse: ...


class CaseUpdateProvider(Protocol):
    name: str

    def track(self, case: CaseRecord) -> CaseProviderResponse: ...
