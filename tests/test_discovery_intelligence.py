from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    Classification,
    ClassificationSource,
    ClassificationStatus,
    FindingKind,
    GraphNodeType,
    SearchFeedback,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import DiscoveryIntelligenceService, DiscoveryService


def test_catalog_classification_search_and_feedback_are_explicit(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "discovery.db")
    discovery = DiscoveryService(repository)
    intelligence = DiscoveryIntelligenceService(repository)
    task = discovery.create_task("旧 Mac 兼容性")
    source = discovery.add_source(task.id, "官方来源", "https://example.com", "系统要求", 0.9)
    evidence = discovery.add_evidence(task.id, source.id, "要求 Apple Silicon", "Apple Silicon", "requirements")
    finding = discovery.add_finding(task.id, "部分设备受限", FindingKind.RISK, 0.8, evidence_ids=[evidence.id])
    category = intelligence.create_category("硬件兼容性", "technology")
    tag = intelligence.create_tag("Apple Silicon")
    classification = intelligence.classify(
        Classification(
            object_type=GraphNodeType.FINDING,
            object_id=finding.id,
            category_id=category.id,
            tag_id=tag.id,
            confidence=0.8,
            source=ClassificationSource.HUMAN,
            status=ClassificationStatus.CONFIRMED,
        )
    )
    query, results = intelligence.search("设备")
    assert classification.status == ClassificationStatus.CONFIRMED
    assert results[0]["kind"] == "finding"
    assert "limitations" in results[0]
    feedback = intelligence.add_search_feedback(
        SearchFeedback(query.id, GraphNodeType.FINDING, finding.id, True, "有帮助")
    )
    assert feedback.useful is True
    with pytest.raises(ValueError, match="classified object"):
        intelligence.classify(
            Classification(object_type=GraphNodeType.CASE, object_id="missing", category_id=category.id)
        )
