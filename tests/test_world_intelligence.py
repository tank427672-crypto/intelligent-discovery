from datetime import timedelta

import pytest

from intelligent_discovery.domain import TrustLevel
from intelligent_discovery.world_intelligence.collector import CandidateCollector
from intelligent_discovery.world_intelligence.connector import ConnectorItem
from intelligent_discovery.world_intelligence.event_candidate import (
    WorldEventCandidate,
    WorldEventService,
    WorldEventStatus,
)
from intelligent_discovery.world_intelligence.feed import WorldFeedService
from intelligent_discovery.world_intelligence.freshness import FreshnessRecord, FreshnessService, FreshnessStatus, now
from intelligent_discovery.world_intelligence.source_registry import (
    InMemorySourceRegistryAdapter,
    SourceRecord,
    SourceRegistryService,
    SourceRegistryStatus,
    WorldSourceType,
)
from intelligent_discovery.world_intelligence.trend import TrendSignal
from intelligent_discovery.world_intelligence.verification import VerificationResult, WorldVerificationService


class FakeConnector:
    name = "fake"

    def discover(self, source: SourceRecord) -> list[ConnectorItem]:
        return [ConnectorItem("one", "Release candidate", "https://example.org/release")]

    def fetch(self, item: ConnectorItem) -> ConnectorItem:
        return item

    def parse(self, item: ConnectorItem) -> ConnectorItem:
        return item

    def verify(self, item: ConnectorItem) -> bool:
        return True


def registered_source() -> SourceRecord:
    return SourceRecord(
        "Official project", WorldSourceType.OFFICIAL, "https://example.org", "terms", TrustLevel.PRIMARY, "daily"
    )


def test_source_registry_and_connector_are_adapter_isolated() -> None:
    registry = SourceRegistryService(InMemorySourceRegistryAdapter())
    source = registry.register(registered_source())
    with pytest.raises(ValueError):
        CandidateCollector().collect(FakeConnector(), source)
    source = registry.verify(source.id)
    candidates = CandidateCollector().collect(FakeConnector(), source)
    assert source.status is SourceRegistryStatus.VERIFIED
    assert candidates[0].verification_status is WorldEventStatus.DISCOVERED


def test_candidate_requires_ordered_verification_and_publication() -> None:
    candidate = WorldEventCandidate("Change", "Potential change", "technology", ["https://example.org"], 0.5, 0.2)
    service = WorldEventService()
    with pytest.raises(ValueError):
        service.transition(candidate, WorldEventStatus.PUBLISHED)
    service.transition(candidate, WorldEventStatus.CHECKING)
    WorldVerificationService().verify(
        candidate, VerificationResult(candidate.id, ["evidence-1"], "reviewer", True, ["early report"])
    )
    service.transition(candidate, WorldEventStatus.PUBLISHED)
    assert WorldFeedService().from_candidate(candidate, TrustLevel.PRIMARY).title == "Change"


def test_freshness_detects_update_and_archive_thresholds() -> None:
    current = now()
    stale = FreshnessRecord("event-1", current, current - timedelta(days=31), None, 0.3)
    archived = FreshnessRecord("event-2", current, current - timedelta(days=61), None, 0.1)
    assert FreshnessService().evaluate(stale).status is FreshnessStatus.NEEDS_UPDATE
    assert FreshnessService().evaluate(archived).status is FreshnessStatus.ARCHIVED


def test_trend_signal_is_explicitly_not_a_prediction() -> None:
    signal = TrendSignal("open tooling", "repository activity increased", 0.6, ["source-1"])
    assert "not a prediction" in signal.limitation
