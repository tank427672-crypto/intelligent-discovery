"""Source registry domain. A registered source is not evidence or knowledge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from uuid import uuid4

from ..domain import TrustLevel


def now() -> datetime:
    return datetime.now(UTC)


class WorldSourceType(StrEnum):
    OFFICIAL = "official"
    OPEN_SOURCE = "open_source"
    RESEARCH = "research"
    DATASET = "dataset"
    NEWS = "news"
    COMMUNITY = "community"


class SourceRegistryStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
    RETIRED = "retired"


@dataclass(slots=True)
class SourceRecord:
    name: str
    source_type: WorldSourceType
    url: str
    license: str
    trust_level: TrustLevel
    update_frequency: str
    status: SourceRegistryStatus = SourceRegistryStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.url.startswith(("https://", "http://")):
            raise ValueError("source requires a name and public URL")
        if not self.license.strip() or not self.update_frequency.strip():
            raise ValueError("source license and update frequency are required")


class SourceRegistryPort(Protocol):
    def save_source_record(self, record: SourceRecord) -> None: ...
    def get_source_record(self, source_id: str) -> SourceRecord | None: ...


class SourceRegistryService:
    def __init__(self, store: SourceRegistryPort) -> None:
        self.store = store

    def register(self, record: SourceRecord) -> SourceRecord:
        self.store.save_source_record(record)
        return record

    def verify(self, source_id: str) -> SourceRecord:
        record = self.store.get_source_record(source_id)
        if record is None:
            raise ValueError("source record not found")
        record.status = SourceRegistryStatus.VERIFIED
        self.store.save_source_record(record)
        return record


class InMemorySourceRegistryAdapter:
    def __init__(self) -> None:
        self.records: dict[str, SourceRecord] = {}

    def save_source_record(self, record: SourceRecord) -> None:
        self.records[record.id] = record

    def get_source_record(self, source_id: str) -> SourceRecord | None:
        return self.records.get(source_id)
