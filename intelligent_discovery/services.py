from __future__ import annotations

from .domain import DiscoveryTask, Finding, FindingKind, KnowledgeRecord, Source, TaskStatus
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

    def add_source(self, task_id: str, title: str, url: str, excerpt: str, credibility: float) -> Source:
        self.get_task(task_id)
        if not title.strip() or not url.strip() or not excerpt.strip():
            raise ValueError("title, url and excerpt are required")
        source = Source(
            task_id=task_id, title=title.strip(), url=url.strip(), excerpt=excerpt.strip(), credibility=credibility
        )
        self.repository.save_source(source)
        return source

    def add_finding(
        self,
        task_id: str,
        statement: str,
        kind: FindingKind,
        confidence: float,
        source_ids: list[str],
        rationale: str = "",
    ) -> Finding:
        task = self.get_task(task_id)
        if task.status == TaskStatus.COMPLETED:
            raise ValueError("completed tasks cannot be changed")
        sources = {source.id for source in self.repository.list_sources(task_id)}
        if any(source_id not in sources for source_id in source_ids):
            raise ValueError("every source_id must belong to this task")
        finding = Finding(
            task_id=task_id,
            statement=statement.strip(),
            kind=kind,
            confidence=confidence,
            source_ids=source_ids,
            rationale=rationale.strip(),
        )
        self.repository.save_finding(finding)
        return finding

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

    def snapshot(self, task_id: str) -> tuple[DiscoveryTask, list[Source], list[Finding]]:
        return self.get_task(task_id), self.repository.list_sources(task_id), self.repository.list_findings(task_id)


class ReportRenderer:
    def render(self, task: DiscoveryTask, sources: list[Source], findings: list[Finding]) -> str:
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
                f"- [{source.title}]({source.url}) — 可信度 {source.credibility:.0%}；{source.excerpt}"
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
                    evidence = ", ".join(finding.source_ids) if finding.source_ids else "待研究"
                    detail = f"；依据：{finding.rationale}" if finding.rationale else ""
                    lines.append(f"- {finding.statement}（置信度 {finding.confidence:.0%}；证据：{evidence}{detail}）")
            else:
                lines.append("- 暂无。")
        lines.extend(["", "## 下一步", "- 复核关键来源，补充未知项，并由用户基于证据作出决策。", ""])
        return "\n".join(lines)
