from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    DataRequest,
    DataRequestType,
    DataVisibility,
    FindingKind,
    GraphNodeType,
    PermissionName,
    ShareRequest,
    User,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import DiscoveryService, IdentityLocalNetworkService


def test_user_owned_sharing_is_explicit_and_auditable(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "identity.db")
    discovery, identity = DiscoveryService(repository), IdentityLocalNetworkService(repository)
    user = identity.create_user(User("测试用户"))
    task = discovery.create_task("私人研究")
    source = discovery.add_source(task.id, "来源", "https://example.com", "摘录", 0.8)
    evidence = discovery.add_evidence(task.id, source.id, "主张", "摘录", "section")
    finding = discovery.add_finding(task.id, "发现", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id])
    request = identity.request_share(
        ShareRequest(user.id, GraphNodeType.FINDING, finding.id, DataVisibility.SHARED, PermissionName.READ)
    )
    assert identity.approve_share(request.id).status.value == "approved"
    assert (
        identity.request_data_right(
            DataRequest(user.id, DataRequestType.EXPORT, GraphNodeType.FINDING, finding.id)
        ).owner_id
        == user.id
    )
    with pytest.raises(ValueError, match="share target"):
        identity.request_share(
            ShareRequest(user.id, GraphNodeType.FINDING, finding.id, DataVisibility.PRIVATE, PermissionName.READ)
        )
