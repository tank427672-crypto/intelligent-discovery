from datetime import UTC, datetime

import pytest

from intelligent_discovery.communication import (
    CommunicationPriority,
    CommunicationService,
    CommunicationType,
    InMemoryCommunicationAdapter,
)
from intelligent_discovery.discovery_experience.content import ContentFreshness, DiscoveryContent, DiscoveryContentType
from intelligent_discovery.discovery_experience.following import FollowRelation, FollowTargetType
from intelligent_discovery.discovery_experience.gateway import CommunicationGateway, DeveloperContactType
from intelligent_discovery.discovery_experience.personal import (
    InterestProfile,
    InterestProfileStore,
    InterestTrend,
    RecommendationExplanation,
)
from intelligent_discovery.discovery_experience.stream import DiscoveryScope, StreamService


def content() -> DiscoveryContent:
    return DiscoveryContent(
        DiscoveryContentType.EVENT, "Public change", "A verified public update.", ["source-1"], ["evidence-1"]
    )


def test_content_types_and_freshness_are_explicit() -> None:
    value = content()
    freshness = ContentFreshness(value.id, datetime.now(UTC), True, "review source", ["revision-1"])
    assert value.content_type is DiscoveryContentType.EVENT
    assert freshness.source_changed is True
    with pytest.raises(ValueError):
        DiscoveryContent(DiscoveryContentType.CASE, "", "summary", ["source"], [])


def test_world_and_personal_discovery_scopes_are_separated() -> None:
    service, value = StreamService(), content()
    world = service.world_item(value, 0.7, 0.8, 0.9)
    assert world.scope is DiscoveryScope.WORLD
    with pytest.raises(ValueError):
        service.personal_item(value, "related interest", False)
    personal = service.personal_item(value, "you explicitly follow this topic", True)
    assert personal.scope is DiscoveryScope.PERSONAL


def test_interest_is_owner_controlled_and_recommendations_are_explained() -> None:
    store = InterestProfileStore()
    profile = store.save(InterestProfile("user-1", "open source", 0.8, 0.9, InterestTrend.RISING, True))
    explanation = RecommendationExplanation(
        "content-1", ["you confirmed interest"], ["source-1"], ["coverage is incomplete"]
    )
    assert explanation.reasons
    with pytest.raises(PermissionError):
        store.delete(profile.id, "another-user")
    store.delete(profile.id, "user-1")


def test_following_rejects_private_targets() -> None:
    assert FollowRelation("user-1", FollowTargetType.TOPIC, "topic-1", True).target_is_public
    with pytest.raises(ValueError):
        FollowRelation("user-1", FollowTargetType.EXPERT, "expert-1", False)


def test_developer_connection_creates_a_private_structured_communication() -> None:
    gateway = CommunicationGateway(CommunicationService(InMemoryCommunicationAdapter()))
    record = gateway.submit("user-1", DeveloperContactType.SECURITY_REPORT, "report", "r1", "security concern")
    assert record.communication_type is CommunicationType.SECURITY_REPORT
    assert record.priority is CommunicationPriority.P0
