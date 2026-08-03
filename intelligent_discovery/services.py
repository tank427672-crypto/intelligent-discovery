from __future__ import annotations

from dataclasses import replace

from .domain import (
    AccessPolicy,
    CaseLifecycleStatus,
    CaseRecord,
    CaseRevision,
    CaseTaskLink,
    CaseTaskRelation,
    Category,
    Classification,
    Concept,
    DataRequest,
    DataVisibility,
    DiscoveryTask,
    Evidence,
    EvidenceRelation,
    EvidenceStatus,
    EvolutionExperiment,
    ExperimentStatus,
    FeaturePerformance,
    FeedbackVerdict,
    Finding,
    FindingFeedback,
    FindingKind,
    GovernanceRecord,
    GraphNodeType,
    ImprovementProposal,
    ImprovementStatus,
    KnowledgeRecord,
    RecommendationRecord,
    ReflectionRecord,
    Relationship,
    RelationshipType,
    ReviewRecord,
    SearchFeedback,
    SearchQuery,
    ShareRequest,
    ShareRequestStatus,
    Source,
    SourceStatus,
    SourceType,
    SystemFeedback,
    Tag,
    TaskStatus,
    TrustLevel,
    User,
    VisibilityRecord,
    utc_now,
)
from .ports import DiscoveryRepository


class NotFoundError(LookupError):
    pass


class CaseService:
    """Application service for verified, versioned case knowledge assets."""

    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def create_case(self, case: CaseRecord) -> CaseRecord:
        self._validate_case_links(case)
        self.repository.save_case(case)
        self.repository.save_case_revision(
            CaseRevision(
                case_id=case.id,
                version=case.version,
                summary="Initial case record",
                change_reason="case created",
                changed_fields=["initial_record"],
            )
        )
        self.link_case_to_task(case.id, case.origin_task_id, CaseTaskRelation.DISCOVERED_IN)
        return case

    def get_case(self, case_id: str) -> CaseRecord:
        case = self.repository.get_case(case_id)
        if not case:
            raise NotFoundError(f"case {case_id} was not found")
        return case

    def revise_case(self, case_id: str, change_reason: str, **changes: object) -> CaseRecord:
        current = self.get_case(case_id)
        if not change_reason.strip():
            raise ValueError("case change_reason is required")
        allowed = {
            "background",
            "problem",
            "solution",
            "outcome",
            "success_factors",
            "failure_factors",
            "lessons_learned",
            "applicability",
            "limitations",
            "license_info",
            "credibility",
            "verification_status",
        }
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"case fields cannot be revised: {', '.join(sorted(unknown))}")
        changed = {
            name: value for name, value in changes.items() if value is not None and value != getattr(current, name)
        }
        if not changed:
            raise ValueError("case revision must change at least one field")
        updated = replace(current, **changed, version=current.version + 1, updated_at=utc_now())
        self._validate_case_links(updated)
        self.repository.save_case(updated)
        self.repository.save_case_revision(
            CaseRevision(
                case_id=updated.id,
                version=updated.version,
                summary="Case record revised",
                change_reason=change_reason.strip(),
                changed_fields=sorted(changed),
            )
        )
        return updated

    def transition_case(self, case_id: str, status: CaseLifecycleStatus) -> CaseRecord:
        current = self.get_case(case_id)
        case = replace(current, version=current.version + 1, updated_at=utc_now())
        case.transition_to(status)
        self.repository.save_case(case)
        self.repository.save_case_revision(
            CaseRevision(
                case_id=case.id,
                version=case.version,
                summary=f"Lifecycle changed to {status}",
                change_reason="case lifecycle transition",
                changed_fields=["lifecycle_status"],
            )
        )
        return case

    def link_case_to_task(self, case_id: str, task_id: str, relation: CaseTaskRelation, note: str = "") -> CaseTaskLink:
        self.get_case(case_id)
        if not self.repository.get_task(task_id):
            raise NotFoundError(f"task {task_id} was not found")
        link = CaseTaskLink(case_id=case_id, task_id=task_id, relation=relation, note=note.strip())
        self.repository.save_case_task_link(link)
        return link

    def cases_for_task(self, task_id: str) -> list[CaseRecord]:
        if not self.repository.get_task(task_id):
            raise NotFoundError(f"task {task_id} was not found")
        return self.repository.list_cases(task_id)

    def revisions(self, case_id: str) -> list[CaseRevision]:
        self.get_case(case_id)
        return self.repository.list_case_revisions(case_id)

    def _validate_case_links(self, case: CaseRecord) -> None:
        if not self.repository.get_task(case.origin_task_id):
            raise NotFoundError(f"task {case.origin_task_id} was not found")
        sources = {source.id for source in self.repository.list_sources(case.origin_task_id)}
        evidence = {item.id for item in self.repository.list_evidence(case.origin_task_id)}
        findings = {item.id for item in self.repository.list_findings(case.origin_task_id)}
        if any(item not in sources for item in case.source_ids):
            raise ValueError("case source_ids must reference sources from its origin task")
        if any(item not in evidence for item in case.evidence_ids):
            raise ValueError("case evidence_ids must reference evidence from its origin task")
        if any(item not in findings for item in case.finding_ids):
            raise ValueError("case finding_ids must reference findings from its origin task")


class DiscoveryService:
    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def create_task(self, question: str, context: str = "") -> DiscoveryTask:
        if not question.strip():
            raise ValueError("question is required")
        task = DiscoveryTask(question=question.strip(), context=context.strip())
        task.transition_to(TaskStatus.RESEARCHING)
        self.repository.save_task(task)
        return task

    def get_task(self, task_id: str) -> DiscoveryTask:
        task = self.repository.get_task(task_id)
        if not task:
            raise NotFoundError(f"task {task_id} was not found")
        return task

    def add_source(
        self,
        task_id: str,
        title: str,
        url: str,
        excerpt: str,
        credibility: float,
        source_type: SourceType = SourceType.USER_PROVIDED,
        trust_level: TrustLevel = TrustLevel.UNVERIFIED,
        status: SourceStatus = SourceStatus.UNVERIFIED,
        license_info: str = "unknown",
    ) -> Source:
        self.get_task(task_id)
        if not title.strip() or not url.strip() or not excerpt.strip():
            raise ValueError("title, url and excerpt are required")
        source = Source(
            task_id=task_id,
            title=title.strip(),
            url=url.strip(),
            excerpt=excerpt.strip(),
            credibility=credibility,
            source_type=source_type,
            trust_level=trust_level,
            status=status,
            license_info=license_info.strip() or "unknown",
        )
        self.repository.save_source(source)
        return source

    def add_evidence(
        self,
        task_id: str,
        source_id: str,
        claim: str,
        excerpt: str,
        locator: str,
        relation: EvidenceRelation = EvidenceRelation.SUPPORTS,
        status: EvidenceStatus = EvidenceStatus.EXTRACTED,
        limitations: str = "",
    ) -> Evidence:
        self.get_task(task_id)
        if source_id not in {source.id for source in self.repository.list_sources(task_id)}:
            raise ValueError("evidence source_id must belong to this task")
        if not claim.strip() or not excerpt.strip() or not locator.strip():
            raise ValueError("claim, excerpt and locator are required")
        evidence = Evidence(
            task_id=task_id,
            source_id=source_id,
            claim=claim.strip(),
            excerpt=excerpt.strip(),
            locator=locator.strip(),
            relation=relation,
            status=status,
            limitations=limitations.strip(),
        )
        self.repository.save_evidence(evidence)
        return evidence

    def add_finding(
        self,
        task_id: str,
        statement: str,
        kind: FindingKind,
        confidence: float,
        source_ids: list[str] | None = None,
        evidence_ids: list[str] | None = None,
        rationale: str = "",
    ) -> Finding:
        task = self.get_task(task_id)
        if task.status == TaskStatus.COMPLETED:
            raise ValueError("completed tasks cannot be changed")
        source_ids = source_ids or []
        evidence_ids = evidence_ids or []
        sources = {source.id for source in self.repository.list_sources(task_id)}
        if any(source_id not in sources for source_id in source_ids):
            raise ValueError("every source_id must belong to this task")
        evidence = {item.id for item in self.repository.list_evidence(task_id)}
        if any(evidence_id not in evidence for evidence_id in evidence_ids):
            raise ValueError("every evidence_id must belong to this task")
        finding = Finding(
            task_id=task_id,
            statement=statement.strip(),
            kind=kind,
            confidence=confidence,
            source_ids=source_ids,
            evidence_ids=evidence_ids,
            rationale=rationale.strip(),
        )
        self.repository.save_finding(finding)
        return finding

    def add_feedback(
        self,
        task_id: str,
        finding_id: str,
        verdict: FeedbackVerdict,
        comment: str,
        reviewer_label: str = "human",
    ) -> FindingFeedback:
        self.get_task(task_id)
        finding_ids = {finding.id for finding in self.repository.list_findings(task_id)}
        if finding_id not in finding_ids:
            raise ValueError("feedback finding_id must belong to this task")
        feedback = FindingFeedback(
            task_id=task_id,
            finding_id=finding_id,
            verdict=verdict,
            comment=comment.strip(),
            reviewer_label=reviewer_label.strip() or "human",
        )
        self.repository.save_feedback(feedback)
        return feedback

    def analyze(self, task_id: str) -> DiscoveryTask:
        task = self.get_task(task_id)
        if task.status != TaskStatus.RESEARCHING:
            raise ValueError("only researching tasks can be analyzed")
        if not self.repository.list_sources(task_id):
            raise ValueError("at least one source is required before analysis")
        task.transition_to(TaskStatus.ANALYZED)
        self.repository.save_task(task)
        return task

    def complete(self, task_id: str) -> KnowledgeRecord:
        task = self.get_task(task_id)
        if task.status != TaskStatus.ANALYZED:
            raise ValueError("only analyzed tasks can be completed")
        findings = self.repository.list_findings(task_id)
        if not findings:
            raise ValueError("at least one finding is required before completion")
        task.transition_to(TaskStatus.COMPLETED)
        self.repository.save_task(task)
        headline = next((f.statement for f in findings if f.kind == FindingKind.INSIGHT), findings[0].statement)
        record = KnowledgeRecord(task_id=task.id, title=task.question, summary=headline)
        self.repository.save_knowledge(record)
        return record

    def snapshot(
        self, task_id: str
    ) -> tuple[DiscoveryTask, list[Source], list[Evidence], list[Finding], list[FindingFeedback]]:
        return (
            self.get_task(task_id),
            self.repository.list_sources(task_id),
            self.repository.list_evidence(task_id),
            self.repository.list_findings(task_id),
            self.repository.list_feedback(task_id),
        )


class ReportRenderer:
    def render(
        self,
        task: DiscoveryTask,
        sources: list[Source],
        evidence: list[Evidence],
        findings: list[Finding],
        feedback: list[FindingFeedback],
        cases: list[CaseRecord] | None = None,
    ) -> str:
        by_kind = {kind: [f for f in findings if f.kind == kind] for kind in FindingKind}
        lines = [
            f"# {task.question}",
            "",
            "## 背景",
            task.context or "未提供。",
            "",
            "## 任务状态",
            task.status,
            "",
            "## 资料来源",
        ]
        lines.extend(
            [
                f"- [{source.title}]({source.url}) — {source.source_type}/{source.trust_level}/"
                f"{source.status}；可信度 {source.credibility:.0%}；许可：{source.license_info}；{source.excerpt}"
                for source in sources
            ]
            or ["- 尚无资料来源。"]
        )
        labels = {
            FindingKind.INSIGHT: "关键发现",
            FindingKind.RISK: "风险",
            FindingKind.RECOMMENDATION: "建议",
            FindingKind.UNKNOWN: "未知问题",
        }
        for kind in FindingKind:
            lines.extend(["", f"## {labels[kind]}"])
            entries = by_kind[kind]
            if entries:
                for finding in entries:
                    citations = ", ".join(f"[^e-{item}]" for item in finding.evidence_ids)
                    citations = citations or ", ".join(f"[^s-{item}]" for item in finding.source_ids) or "待研究"
                    detail = f"；依据：{finding.rationale}" if finding.rationale else ""
                    lines.append(f"- {finding.statement}（置信度 {finding.confidence:.0%}；证据：{citations}{detail}）")
            else:
                lines.append("- 暂无。")
        lines.extend(["", "## 证据链"])
        if evidence:
            source_titles = {source.id: source.title for source in sources}
            lines.extend(
                f"- [^e-{item.id}] {source_titles.get(item.source_id, item.source_id)}，定位：{item.locator}；"
                f"关系：{item.relation}；状态：{item.status}；限制：{item.limitations or '未注明'}"
                for item in evidence
            )
        else:
            lines.append("- 尚无独立证据条目；现有结论仅关联 v0.1 来源。")
        lines.extend(["", "## 人工复核反馈"])
        lines.extend(f"- {item.verdict}：{item.comment}（{item.reviewer_label}）" for item in feedback)
        if not feedback:
            lines.append("- 尚无人工复核反馈。")
        lines.extend(["", "## 关联案例"])
        if cases:
            lines.extend(
                f"- {item.name}（{item.case_type}；状态：{item.lifecycle_status}/"
                f"{item.verification_status}；可信度 {item.credibility:.0%}；版本 {item.version}）"
                for item in cases
            )
        else:
            lines.append("- 尚无关联案例。")
        lines.extend(["", "## 下一步", "- 复核关键来源，补充未知项，并由用户基于证据作出决策。", ""])
        return "\n".join(lines)


class KnowledgeGraphService:
    """Evidence-bound graph operations; it does not infer or fabricate relationships."""

    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def create_concept(self, name: str, concept_type: str, description: str = "") -> Concept:
        concept = Concept(name=name.strip(), concept_type=concept_type.strip(), description=description.strip())
        self.repository.save_concept(concept)
        return concept

    def relate(
        self,
        source_type: GraphNodeType,
        source_id: str,
        target_type: GraphNodeType,
        target_id: str,
        relationship_type: RelationshipType,
        evidence_ids: list[str] | None = None,
        description: str = "",
    ) -> Relationship:
        if not self.repository.entity_exists(source_type, source_id):
            raise ValueError("relationship source must exist")
        if not self.repository.entity_exists(target_type, target_id):
            raise ValueError("relationship target must exist")
        evidence_ids = evidence_ids or []
        for evidence_id in evidence_ids:
            if not self.repository.entity_exists(GraphNodeType.EVIDENCE, evidence_id):
                raise ValueError("relationship evidence must exist")
        relationship = Relationship(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type,
            evidence_ids=evidence_ids,
            description=description.strip(),
        )
        self.repository.save_relationship(relationship)
        return relationship

    def relationships_for(self, node_type: GraphNodeType, node_id: str) -> list[Relationship]:
        if not self.repository.entity_exists(node_type, node_id):
            raise NotFoundError(f"graph node {node_type}:{node_id} was not found")
        return self.repository.list_relationships(node_type, node_id)

    def similar_cases(self, case_id: str) -> list[CaseRecord]:
        if not self.repository.get_case(case_id):
            raise NotFoundError(f"case {case_id} was not found")
        concepts = {
            relationship.target_id
            for relationship in self.repository.list_relationships(GraphNodeType.CASE, case_id)
            if relationship.target_type == GraphNodeType.CONCEPT
        }
        scores: dict[str, int] = {}
        for concept_id in concepts:
            for relationship in self.repository.list_relationships(GraphNodeType.CONCEPT, concept_id):
                if relationship.source_type == GraphNodeType.CASE and relationship.source_id != case_id:
                    scores[relationship.source_id] = scores.get(relationship.source_id, 0) + 1
        records = {record.id: record for record in self.repository.list_cases()}
        return [records[item] for item in sorted(scores, key=lambda item: (-scores[item], item)) if item in records]

    def add_reflection(self, reflection: ReflectionRecord) -> ReflectionRecord:
        case = self.repository.get_case(reflection.case_id)
        if not case:
            raise NotFoundError(f"case {reflection.case_id} was not found")
        valid_evidence = {item.id for item in self.repository.list_evidence(case.origin_task_id)}
        if any(item not in valid_evidence for item in reflection.evidence_ids):
            raise ValueError("reflection evidence must belong to the case origin task")
        self.repository.save_reflection(reflection)
        return reflection


class DiscoveryIntelligenceService:
    """Explores existing assets with explicit evidence boundaries, never web search or black-box ranking."""

    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def create_category(self, name: str, category_type: str, parent_id: str | None = None) -> Category:
        if parent_id and not any(item.id == parent_id for item in self.repository.list_categories()):
            raise ValueError("category parent must exist")
        category = Category(name=name.strip(), category_type=category_type.strip(), parent_id=parent_id)
        self.repository.save_category(category)
        return category

    def create_tag(self, name: str) -> Tag:
        tag = Tag(name=name.strip())
        self.repository.save_tag(tag)
        return tag

    def classify(self, classification: Classification) -> Classification:
        if not self.repository.entity_exists(classification.object_type, classification.object_id):
            raise ValueError("classified object must exist")
        if classification.category_id and not any(
            item.id == classification.category_id for item in self.repository.list_categories()
        ):
            raise ValueError("classification category must exist")
        if classification.tag_id and not any(item.id == classification.tag_id for item in self.repository.list_tags()):
            raise ValueError("classification tag must exist")
        self.repository.save_classification(classification)
        return classification

    def search(self, text: str) -> tuple[SearchQuery, list[dict[str, object]]]:
        if not text.strip():
            raise ValueError("search query is required")
        query = SearchQuery(query=text.strip())
        self.repository.save_search_query(query)
        results = self.repository.search_assets(query.query)
        for result in results:
            result["relationships"] = self.repository.list_relationships(
                GraphNodeType(result["kind"]), str(result["id"])
            )
            result["classifications"] = self.repository.list_classifications(
                GraphNodeType(result["kind"]), str(result["id"])
            )
            result["limitations"] = "仅检索本地已记录资产；不代表完整世界信息。"
        return query, results

    def add_search_feedback(self, feedback: SearchFeedback) -> SearchFeedback:
        if not self.repository.entity_exists(feedback.result_type, feedback.result_id):
            raise ValueError("search feedback result must exist")
        self.repository.save_search_feedback(feedback)
        return feedback

    def record_recommendation(self, recommendation: RecommendationRecord) -> RecommendationRecord:
        if not self.repository.entity_exists(recommendation.object_type, recommendation.object_id):
            raise ValueError("recommendation object must exist")
        if not recommendation.reason.strip():
            raise ValueError("recommendation reason is required")
        self.repository.save_recommendation(recommendation)
        return recommendation


class TrustGovernanceService:
    """Human-controlled visibility, review and product-evolution records."""

    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def set_visibility(self, record: VisibilityRecord) -> VisibilityRecord:
        if not self.repository.entity_exists(record.object_type, record.object_id):
            raise ValueError("visibility object must exist")
        existing = self.repository.get_visibility(record.object_type, record.object_id)
        if existing and existing.visibility == DataVisibility.PRIVATE and record.visibility == DataVisibility.PUBLIC:
            raise ValueError("private data must be explicitly shared and reviewed before public visibility")
        self.repository.save_visibility(record)
        self.repository.save_governance(
            GovernanceRecord(record.object_type, record.object_id, "visibility_changed", record.visibility)
        )
        return record

    def review(self, record: ReviewRecord) -> ReviewRecord:
        if not self.repository.entity_exists(record.object_type, record.object_id):
            raise ValueError("review object must exist")
        self.repository.save_review(record)
        self.repository.save_governance(
            GovernanceRecord(
                record.object_type, record.object_id, "reviewed", record.decision, record.reviewer_reference
            )
        )
        return record

    def add_feedback(self, feedback: SystemFeedback) -> SystemFeedback:
        if not feedback.feature.strip() or not feedback.description.strip():
            raise ValueError("feedback feature and description are required")
        self.repository.save_system_feedback(feedback)
        return feedback

    def performance(self, feature: str) -> FeaturePerformance:
        return self.repository.feature_performance(feature)

    def propose_improvement(self, proposal: ImprovementProposal) -> ImprovementProposal:
        if not proposal.problem.strip() or not proposal.proposal.strip():
            raise ValueError("improvement problem and proposal are required")
        self.repository.save_improvement(proposal)
        return proposal

    def start_experiment(self, experiment: EvolutionExperiment) -> EvolutionExperiment:
        proposal = self.repository.get_improvement(experiment.proposal_id)
        if not proposal or proposal.status != ImprovementStatus.APPROVED:
            raise ValueError("experiments require an approved improvement proposal")
        if experiment.status != ExperimentStatus.PLANNED:
            raise ValueError("experiments must start in planned status")
        self.repository.save_experiment(experiment)
        return experiment


class IdentityLocalNetworkService:
    """Identity and rights records; no authentication or automatic publication is implemented."""

    def __init__(self, repository: DiscoveryRepository) -> None:
        self.repository = repository

    def create_user(self, user: User) -> User:
        if not user.name.strip():
            raise ValueError("user name is required")
        self.repository.save_user(user)
        return user

    def grant(self, policy: AccessPolicy) -> AccessPolicy:
        if not self.repository.get_user(policy.subject_id):
            raise ValueError("policy subject must be an existing user")
        if not self.repository.entity_exists(policy.resource_type, policy.resource_id):
            raise ValueError("policy resource must exist")
        self.repository.save_access_policy(policy)
        return policy

    def request_share(self, request: ShareRequest) -> ShareRequest:
        if not self.repository.get_user(request.owner_id):
            raise ValueError("share owner must be an existing user")
        if not self.repository.entity_exists(request.object_type, request.object_id):
            raise ValueError("shared object must exist")
        if request.target_visibility == DataVisibility.PRIVATE:
            raise ValueError("share target must be shared or public")
        self.repository.save_share_request(request)
        return request

    def approve_share(self, request_id: str) -> ShareRequest:
        request = self.repository.get_share_request(request_id)
        if not request or request.status != ShareRequestStatus.REQUESTED:
            raise ValueError("only requested shares can be approved")
        request.status = ShareRequestStatus.APPROVED
        self.repository.save_share_request(request)
        return request

    def request_data_right(self, request: DataRequest) -> DataRequest:
        if not self.repository.get_user(request.owner_id):
            raise ValueError("data request owner must be an existing user")
        self.repository.save_data_request(request)
        return request
