import pytest

from intelligent_discovery.beta_operations import WebBetaReleaseChecklist
from intelligent_discovery.discovery_experience.content import DiscoveryContent, DiscoveryContentType
from intelligent_discovery.discovery_experience.graph import DiscoveryRelation, DiscoveryRelationType
from intelligent_discovery.discovery_experience.quality import ContentQualityAssessment, ContentQualityLevel
from intelligent_discovery.discovery_experience.stream import StreamService
from intelligent_discovery.ecosystem import (
    EcosystemCapability,
    EcosystemExtensionRegistry,
    FeatureFlag,
    PermissionBoundary,
)
from intelligent_discovery.world_intelligence.lifecycle import (
    WorldEventLifecycle,
    WorldEventLifecycleService,
    WorldEventLifecycleStatus,
)


def test_discovery_feed_and_quality_keep_limitations_visible() -> None:
    content = DiscoveryContent(DiscoveryContentType.STORY, "Why", "Context", ["source"], ["evidence"])
    item = StreamService().world_item(content, 0.7, 0.8, 0.9)
    quality = ContentQualityAssessment(
        content.id, 0.8, 0.8, 0.7, 0.9, True, "useful", ContentQualityLevel.FEATURED, ["coverage limited"]
    )
    assert item.source_count == 1
    assert quality.level is ContentQualityLevel.FEATURED
    with pytest.raises(ValueError):
        ContentQualityAssessment(content.id, 1, 1, 1, 1, False, "", ContentQualityLevel.FEATURED, [])


def test_world_lifecycle_is_ordered_and_preserves_update_links() -> None:
    lifecycle, service = (
        WorldEventLifecycle("event-1", source_changes=["source update"], evidence_references=["evidence-1"]),
        WorldEventLifecycleService(),
    )
    with pytest.raises(ValueError):
        service.transition(lifecycle, WorldEventLifecycleStatus.ACTIVE)
    service.transition(lifecycle, WorldEventLifecycleStatus.EMERGING)
    service.transition(lifecycle, WorldEventLifecycleStatus.ACTIVE)
    assert lifecycle.evidence_references == ["evidence-1"]


def test_discovery_graph_requires_evidence_for_verified_relations() -> None:
    assert DiscoveryRelation("a", "b", DiscoveryRelationType.RELATED_TO, [], False).verified is False
    with pytest.raises(ValueError):
        DiscoveryRelation("a", "b", DiscoveryRelationType.CONTRADICTS, [], True)


def test_extensions_default_off_and_require_approval_to_enable() -> None:
    registry = EcosystemExtensionRegistry()
    assert registry.available(EcosystemCapability.COMMUNITY) is False
    registry.register(EcosystemCapability.COMMUNITY, object())
    assert registry.available(EcosystemCapability.COMMUNITY) is False
    registry.enable(EcosystemCapability.COMMUNITY, "governance-owner")
    assert registry.available(EcosystemCapability.COMMUNITY) is True
    with pytest.raises(ValueError):
        FeatureFlag(EcosystemCapability.PAYMENT, enabled=True)
    boundary = PermissionBoundary(EcosystemCapability.COMMUNITY, ("propose_discussion",))
    assert "modify_knowledge" in boundary.prohibited_actions


def test_web_beta_release_requires_all_gates_and_human_approval() -> None:
    checklist = WebBetaReleaseChecklist(True, True, True, True, True, True, True, True, True)
    assert checklist.release_ready() is False
    checklist.approved_by = "release-owner"
    assert checklist.release_ready() is True
