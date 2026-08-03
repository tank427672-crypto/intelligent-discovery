from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    DataVisibility,
    EvolutionExperiment,
    ExperimentStatus,
    FindingKind,
    GraphNodeType,
    ImprovementProposal,
    ImprovementStatus,
    SystemFeedback,
    VisibilityRecord,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import DiscoveryService, TrustGovernanceService


def test_visibility_feedback_and_evolution_require_human_control(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "trust.db")
    discovery, trust = DiscoveryService(repository), TrustGovernanceService(repository)
    task = discovery.create_task("治理测试")
    source = discovery.add_source(task.id, "来源", "https://example.com", "摘录", 0.8)
    evidence = discovery.add_evidence(task.id, source.id, "主张", "摘录", "section")
    finding = discovery.add_finding(task.id, "发现", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id])
    private = trust.set_visibility(VisibilityRecord(GraphNodeType.FINDING, finding.id, DataVisibility.PRIVATE))
    assert private.visibility == DataVisibility.PRIVATE
    with pytest.raises(ValueError, match="explicitly shared"):
        trust.set_visibility(VisibilityRecord(GraphNodeType.FINDING, finding.id, DataVisibility.PUBLIC))
    feedback = trust.add_feedback(SystemFeedback("search", "poor_relevance", 2, "结果不够相关"))
    performance = trust.performance("search")
    assert feedback.id and performance.usage_count == 1 and performance.failure_modes == ["poor_relevance"]
    proposal = trust.propose_improvement(ImprovementProposal("相关性不足", [feedback.id], "增加人工评估", "high"))
    with pytest.raises(ValueError, match="approved"):
        trust.start_experiment(EvolutionExperiment(proposal.id, "验证", "修改", ["satisfaction"]))
    proposal.status = ImprovementStatus.APPROVED
    repository.save_improvement(proposal)
    experiment = trust.start_experiment(EvolutionExperiment(proposal.id, "验证", "修改", ["satisfaction"]))
    assert experiment.status == ExperimentStatus.PLANNED
