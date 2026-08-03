from pathlib import Path

import pytest

from intelligent_discovery.domain import FindingKind, TaskStatus
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import DiscoveryService, ReportRenderer


@pytest.fixture
def service(tmp_path: Path) -> DiscoveryService:
    return DiscoveryService(SQLiteRepository(tmp_path / "test.db"))


def test_evidence_led_discovery_lifecycle(service: DiscoveryService) -> None:
    task = service.create_task("旧 Mac 上哪些 AI 工具不能使用？", "比较硬件与系统要求。")
    assert task.status == TaskStatus.RESEARCHING

    source = service.add_source(
        task.id, "官方系统要求", "https://example.com/requirements", "工具需要 macOS 14 与 Apple Silicon。", 0.9
    )
    finding = service.add_finding(
        task.id,
        "部分工具不支持 Intel Mac。",
        FindingKind.INSIGHT,
        0.85,
        [source.id],
        "官方系统要求限制 Apple Silicon。",
    )
    service.add_finding(task.id, "具体兼容性需逐个产品核验。", FindingKind.UNKNOWN, 0.5, [])

    analyzed = service.analyze(task.id)
    assert analyzed.status == TaskStatus.ANALYZED
    record = service.complete(task.id)
    assert record.task_id == task.id
    completed, sources, findings = service.snapshot(task.id)
    report = ReportRenderer().render(completed, sources, findings)

    assert completed.status == TaskStatus.COMPLETED
    assert finding.id in {item.id for item in findings}
    assert "官方系统要求" in report
    assert "未知问题" in report
    assert service.repository.list_knowledge()[0].id == record.id


def test_non_unknown_finding_requires_own_source(service: DiscoveryService) -> None:
    task = service.create_task("测试问题")
    source = service.add_source(task.id, "来源", "https://example.com/source", "摘录", 0.8)
    with pytest.raises(ValueError, match="belong to this task"):
        service.add_finding(task.id, "不应通过", FindingKind.RISK, 0.7, ["not-a-source"])
    with pytest.raises(ValueError, match="reference at least one source"):
        service.add_finding(task.id, "不应通过", FindingKind.RISK, 0.7, [])
    assert source.task_id == task.id


def test_analysis_requires_sources_and_valid_state(service: DiscoveryService) -> None:
    task = service.create_task("测试问题")
    with pytest.raises(ValueError, match="at least one source"):
        service.analyze(task.id)
    service.add_source(task.id, "来源", "https://example.com/source", "摘录", 0.8)
    service.analyze(task.id)
    with pytest.raises(ValueError, match="only researching"):
        service.analyze(task.id)
