"""Stable, frontend-neutral case showcase contracts.

Case seed cards are candidates until their source, evidence and licence are
reviewed and linked into the evidence chain.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CaseCardContract:
    name: str
    case_type: str
    credibility: float
    source_count: int
    evidence_count: int
    updated_at: str
    related_problem: str
    verification_status: str = "candidate"


@dataclass(frozen=True, slots=True)
class CaseDetailContract:
    sections: tuple[str, ...] = (
        "background",
        "problem",
        "solution",
        "outcome",
        "lessons",
        "failure_factors",
        "limitations",
        "evidence_chain",
        "graph_relationships",
        "feedback",
    )

