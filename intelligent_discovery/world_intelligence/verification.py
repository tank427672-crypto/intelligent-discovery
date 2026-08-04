"""Human verification boundary from source links to evidence, never direct publication."""

from __future__ import annotations

from dataclasses import dataclass

from .event_candidate import WorldEventCandidate, WorldEventStatus


@dataclass(frozen=True, slots=True)
class VerificationResult:
    candidate_id: str
    evidence_references: list[str]
    reviewer_id: str
    approved: bool
    limitations: list[str]


class WorldVerificationService:
    def verify(self, candidate: WorldEventCandidate, result: VerificationResult) -> WorldEventCandidate:
        if candidate.id != result.candidate_id or not result.reviewer_id:
            raise ValueError("verification must identify candidate and human reviewer")
        if result.approved and not result.evidence_references:
            raise ValueError("approval requires evidence references")
        candidate.verification_status = WorldEventStatus.VERIFIED if result.approved else WorldEventStatus.REJECTED
        return candidate
