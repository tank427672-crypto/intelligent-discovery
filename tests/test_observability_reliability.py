import pytest

from intelligent_discovery.observability import (
    EventRecord,
    HealthSnapshot,
    MetricRecord,
    ObservabilityService,
    SQLiteObservabilityAdapter,
)
from intelligent_discovery.reliability import AnomalyRecord, CorrectionAction, ReliabilityService


def test_observability_is_queryable_and_excludes_private_content(tmp_path):
    service = ObservabilityService(SQLiteObservabilityAdapter(tmp_path / "telemetry.db"))
    event = service.emit(EventRecord("ShareRequested", "user-1", "finding-1", {"visibility": "shared"}))
    assert service.store.list_events("ShareRequested")[0].id == event.id
    assert service.metric(MetricRecord("error_rate", 0.1, "system", "api")).value == 0.1
    assert service.health(HealthSnapshot(1, 0.8, 1, 0.7)).privacy_health == 1
    with pytest.raises(ValueError, match="private content"):
        EventRecord("Bad", "user", "target", {"content": "secret"})


def test_reliability_corrections_remain_pending_human_review():
    reliability = ReliabilityService()
    assert (
        reliability.assess(AnomalyRecord("KNOWLEDGE", "medium", "finding-1", "missing evidence")).status == "assessed"
    )
    assert reliability.correction(CorrectionAction("a", "review", "ask reviewer")).result == "pending_human_review"
    with pytest.raises(ValueError):
        reliability.correction(CorrectionAction("a", "delete", "no automatic delete"))
