from __future__ import annotations

from .domain import (
    DiscoveryTask,
    Evidence,
    EvidenceRelation,
    EvidenceStatus,
    FeedbackVerdict,
    Finding,
    FindingFeedback,
    FindingKind,
    KnowledgeRecord,
    Source,
    SourceStatus,
    SourceType,
    TaskStatus,
    TrustLevel,
)
from .ports import DiscoveryRepository


class NotFoundError(LookupError):
    pass


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
        lines.extend(["", "## 下一步", "- 复核关键来源，补充未知项，并由用户基于证据作出决策。", ""])
        return "\n".join(lines)
