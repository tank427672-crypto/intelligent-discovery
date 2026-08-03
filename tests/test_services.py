from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    FeedbackVerdict,
    FindingKind,
    SourceStatus,
    SourceType,
    TaskStatus,
    TrustLevel,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import DiscoveryService, ReportRenderer


@pytest.fixture
def service(tmp_path: Path) -> DiscoveryService:
    return DiscoveryService(SQLiteRepository(tmp_path / "test.db"))


def test_evidence_led_discovery_lifecycle(service: DiscoveryService) -> None:
    task = service.create_task("旧 Mac 上哪些 AI 工具不能使用？", "比较硬件与系统要求。")
    source = service.add_source(
        task.id,
        "官方系统要求",
        "https://example.com/requirements",
        "工具需要 macOS 14 与 Apple Silicon。",
        0.9,
        SourceType.WEB,
        TrustLevel.PRIMARY,
        SourceStatus.ACCESSIBLE,
        "official terms",
    )
    evidence = service.add_evidence(
        task.id,
        source.id,
        "工具要求 Apple Silicon",
        "需要 macOS 14 与 Apple Silicon。",
        "Requirements > Hardware",
        limitations="仅适用于该版本。",
    )
    finding = service.add_finding(
        task.id,
        "部分工具不支持 Intel Mac。",
        FindingKind.INSIGHT,
        0.85,
        evidence_ids=[evidence.id],
        rationale="官方系统要求限制 Apple Silicon。",
    )
    service.add_finding(task.id, "具体兼容性需逐个产品核验。", FindingKind.UNKNOWN, 0.5)
    feedback = service.add_feedback(task.id, finding.id, FeedbackVerdict.NEEDS_REVISION, "需补充产品版本范围。")

    assert service.analyze(task.id).status == TaskStatus.ANALYZED
    record = service.complete(task.id)
    completed, sources, evidence_items, findings, feedback_items = service.snapshot(task.id)
    report = ReportRenderer().render(completed, sources, evidence_items, findings, feedback_items)

    assert completed.status == TaskStatus.COMPLETED
    assert finding.id in {item.id for item in findings}
    assert feedback.id in {item.id for item in feedback_items}
    assert "Requirements > Hardware" in report
    assert "需补充产品版本范围" in report
    assert service.repository.list_knowledge()[0].id == record.id


def test_non_unknown_finding_requires_own_source_or_evidence(service: DiscoveryService) -> None:
    task = service.create_task("测试问题")
    source = service.add_source(task.id, "来源", "https://example.com/source", "摘录", 0.8)
    with pytest.raises(ValueError, match="belong to this task"):
        service.add_finding(task.id, "不应通过", FindingKind.RISK, 0.7, source_ids=["not-a-source"])
    with pytest.raises(ValueError, match="reference at least one source or evidence"):
        service.add_finding(task.id, "不应通过", FindingKind.RISK, 0.7)
    assert source.task_id == task.id


def test_evidence_and_feedback_cannot_cross_task_boundaries(service: DiscoveryService) -> None:
    first = service.create_task("第一个问题")
    second = service.create_task("第二个问题")
    source = service.add_source(first.id, "来源", "https://example.com/source", "摘录", 0.8)
    with pytest.raises(ValueError, match="evidence source_id"):
        service.add_evidence(second.id, source.id, "主张", "摘录", "section")
    evidence = service.add_evidence(first.id, source.id, "主张", "摘录", "section")
    finding = service.add_finding(first.id, "发现", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id])
    with pytest.raises(ValueError, match="feedback finding_id"):
        service.add_feedback(second.id, finding.id, FeedbackVerdict.ACCEPTED, "不应通过")


def test_analysis_requires_sources_and_valid_state(service: DiscoveryService) -> None:
    task = service.create_task("测试问题")
    with pytest.raises(ValueError, match="at least one source"):
        service.analyze(task.id)
    service.add_source(task.id, "来源", "https://example.com/source", "摘录", 0.8)
    service.analyze(task.id)
    with pytest.raises(ValueError, match="only researching"):
        service.analyze(task.id)
