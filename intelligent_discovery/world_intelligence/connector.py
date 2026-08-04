"""Replaceable acquisition connector contract. No live connector is implemented."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .source_registry import SourceRecord


@dataclass(frozen=True, slots=True)
class ConnectorItem:
    external_id: str
    title: str
    url: str
    metadata: dict[str, str] = field(default_factory=dict)


class SourceConnector(Protocol):
    name: str

    def discover(self, source: SourceRecord) -> list[ConnectorItem]: ...
    def fetch(self, item: ConnectorItem) -> ConnectorItem: ...
    def parse(self, item: ConnectorItem) -> ConnectorItem: ...
    def verify(self, item: ConnectorItem) -> bool: ...
