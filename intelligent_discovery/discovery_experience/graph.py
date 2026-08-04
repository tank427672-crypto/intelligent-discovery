"""Discovery exploration relations. Relations are candidates until governance links evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class DiscoveryRelationType(StrEnum):
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"
    CAUSED_BY = "caused_by"
    INFLUENCED_BY = "influenced_by"
    FOLLOW_UP = "follow_up"
    CONTRADICTS = "contradicts"


@dataclass(frozen=True, slots=True)
class DiscoveryRelation:
    source_content_id: str
    target_content_id: str
    relation_type: DiscoveryRelationType
    evidence_references: list[str]
    verified: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.verified and not self.evidence_references:
            raise ValueError("verified discovery relations require evidence references")
