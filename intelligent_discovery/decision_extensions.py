"""Decision contracts reserve explainable assistance without automatic decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .domain import DecisionContext, Evidence


@dataclass(slots=True)
class DecisionDraft:
    options: list[str]
    evidence: list[Evidence] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    requires_human_review: bool = True


class DecisionAnalysisProvider(Protocol):
    name: str

    def compare(self, context: DecisionContext) -> DecisionDraft: ...
