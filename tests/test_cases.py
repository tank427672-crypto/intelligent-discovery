from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    CaseLifecycleStatus,
    CaseRecord,
    CaseTaskRelation,
    CaseVerificationStatus,
    FindingKind,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import CaseService, DiscoveryService, ReportRenderer


def make_case(task_id: str, source_id: str, evidence_id: str, finding_id: str) -> CaseRecord:
    return CaseRecord(
        origin_task_id=task_id,
        name="可验证的迁移案例",
        case_type="technology_adoption",
        background="团队需要迁移遗留系统。",
        problem="现有系统无法满足扩展需求。",
        solution="分阶段迁移并保留回滚机制。",
        outcome="迁移完成，恢复时间下降。",
        success_factors="小范围试点和明确回滚。",
        failure_factors="初期范围估计不足。",
        lessons_learned="先验证依赖关系。",
        applicability="适用于可分阶段替换的系统。",
        limitations="单一来源，尚需持续跟踪。",
        source_ids=[source_id],
        evidence_ids=[evidence_id],
        finding_ids=[finding_id],
        license_info="summary under source terms",
        credibility=0.7,
    )


def test_case_is_versioned_verified_and_reusable_across_tasks(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "case.db")
    discovery = DiscoveryService(repository)
    cases = CaseService(repository)
    first = discovery.create_task("迁移经验")
    second = discovery.create_task("另一迁移方案")
    source = discovery.add_source(first.id, "官方复盘", "https://example.com/case", "复盘摘要", 0.8)
    evidence = discovery.add_evidence(first.id, source.id, "分阶段迁移", "采用分阶段迁移", "section 2")
    finding = discovery.add_finding(
        first.id, "分阶段迁移降低风险", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id]
    )

    case = cases.create_case(make_case(first.id, source.id, evidence.id, finding.id))
    cases.link_case_to_task(case.id, second.id, CaseTaskRelation.REFERENCED_BY, "用于方案比较")
    verified = cases.revise_case(
        case.id, "完成来源复核", verification_status=CaseVerificationStatus.VERIFIED, credibility=0.85
    )
    assert verified.version == 2
    assert cases.transition_case(case.id, CaseLifecycleStatus.TRACKED).lifecycle_status == CaseLifecycleStatus.TRACKED
    assert cases.transition_case(case.id, CaseLifecycleStatus.VERIFIED).lifecycle_status == CaseLifecycleStatus.VERIFIED
    assert len(cases.revisions(case.id)) == 4
    assert cases.cases_for_task(second.id)[0].id == case.id

    task, sources, evidence_items, findings, feedback = discovery.snapshot(first.id)
    report = ReportRenderer().render(task, sources, evidence_items, findings, feedback, cases.cases_for_task(first.id))
    assert "可验证的迁移案例" in report


def test_case_rejects_cross_task_evidence_and_unverified_maturity(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "case-invalid.db")
    discovery = DiscoveryService(repository)
    cases = CaseService(repository)
    first = discovery.create_task("任务一")
    second = discovery.create_task("任务二")
    source = discovery.add_source(first.id, "来源", "https://example.com", "摘要", 0.8)
    evidence = discovery.add_evidence(first.id, source.id, "主张", "摘录", "section")
    finding = discovery.add_finding(first.id, "发现", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id])
    invalid = make_case(second.id, source.id, evidence.id, finding.id)
    with pytest.raises(ValueError, match="origin task"):
        cases.create_case(invalid)

    case = cases.create_case(make_case(first.id, source.id, evidence.id, finding.id))
    cases.transition_case(case.id, CaseLifecycleStatus.TRACKED)
    with pytest.raises(ValueError, match="verified case evidence"):
        cases.transition_case(case.id, CaseLifecycleStatus.VERIFIED)
