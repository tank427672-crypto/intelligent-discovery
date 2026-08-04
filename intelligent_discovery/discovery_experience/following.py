"""Following only tracks explicitly public targets and never exposes private activity."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class FollowTargetType(StrEnum):
    PERSON = "person"
    EXPERT = "expert"
    CREATOR = "creator"
    PROJECT = "project"
    COMPANY = "company"
    TOPIC = "topic"


@dataclass(frozen=True, slots=True)
class FollowRelation:
    user_id: str
    target_type: FollowTargetType
    target_id: str
    target_is_public: bool
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.target_is_public:
            raise ValueError("only public targets may be followed")


@dataclass(frozen=True, slots=True)
class FollowingUpdate:
    relation_id: str
    public_object_id: str
    update_summary: str
