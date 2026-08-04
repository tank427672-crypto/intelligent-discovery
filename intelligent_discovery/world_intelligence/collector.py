"""Candidate collector that keeps connector output separate from evidence and publication."""

from __future__ import annotations

from .connector import SourceConnector
from .event_candidate import WorldEventCandidate
from .source_registry import SourceRecord, SourceRegistryStatus


class CandidateCollector:
    def collect(self, connector: SourceConnector, source: SourceRecord) -> list[WorldEventCandidate]:
        if source.status is not SourceRegistryStatus.VERIFIED:
            raise ValueError("only verified source records may be collected")
        return [
            WorldEventCandidate(
                item.title, "Unverified candidate from registered source.", "uncategorized", [item.url], 0, 0
            )
            for item in connector.discover(source)
        ]
