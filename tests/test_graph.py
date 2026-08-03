from pathlib import Path

import pytest

from intelligent_discovery.domain import (
    CaseRecord,
    FindingKind,
    GraphNodeType,
    ReflectionRecord,
    RelationshipType,
)
from intelligent_discovery.repository import SQLiteRepository
from intelligent_discovery.services import CaseService, DiscoveryService, KnowledgeGraphService


def make_case(task_id: str, source_id: str, evidence_id: str, finding_id: str, name: str) -> CaseRecord:
    return CaseRecord(
        origin_task_id=task_id,
        name=name,
        case_type="migration",
        background="background",
        problem="problem",
        solution="solution",
        outcome="outcome",
        success_factors="factor",
        failure_factors="failure",
        lessons_learned="lesson",
        applicability="scope",
        limitations="limits",
        source_ids=[source_id],
        evidence_ids=[evidence_id],
        finding_ids=[finding_id],
        credibility=0.7,
    )


def test_graph_links_cases_concepts_and_reflections_without_inference(tmp_path: Path) -> None:
    repository = SQLiteRepository(tmp_path / "graph.db")
    discovery, cases, graph = DiscoveryService(repository), CaseService(repository), KnowledgeGraphService(repository)
    task = discovery.create_task("迁移案例")
    source = discovery.add_source(task.id, "来源", "https://example.com", "摘录", 0.8)
    evidence = discovery.add_evidence(task.id, source.id, "分阶段迁移", "摘录", "section")
    finding = discovery.add_finding(task.id, "风险下降", FindingKind.INSIGHT, 0.8, evidence_ids=[evidence.id])
    first = cases.create_case(make_case(task.id, source.id, evidence.id, finding.id, "案例一"))
    second = cases.create_case(make_case(task.id, source.id, evidence.id, finding.id, "案例二"))
    concept = graph.create_concept("分阶段迁移", "strategy", "降低迁移风险的策略")
    graph.relate(GraphNodeType.CASE, first.id, GraphNodeType.CONCEPT, concept.id, RelationshipType.USES, [evidence.id])
    graph.relate(GraphNodeType.CASE, second.id, GraphNodeType.CONCEPT, concept.id, RelationshipType.USES, [evidence.id])
    assert graph.similar_cases(first.id)[0].id == second.id
    reflection = graph.add_reflection(
        ReflectionRecord(
            case_id=first.id,
            original_judgment="风险可控",
            actual_outcome="按计划完成",
            deviation="低于预期",
            cause_analysis="试点提前暴露依赖",
            learning_update="保留试点阶段",
            evidence_ids=[evidence.id],
        )
    )
    assert repository.list_reflections(first.id)[0].id == reflection.id
    with pytest.raises(ValueError, match="relationship target must exist"):
        graph.relate(GraphNodeType.CASE, first.id, GraphNodeType.CONCEPT, "missing", RelationshipType.USES)
