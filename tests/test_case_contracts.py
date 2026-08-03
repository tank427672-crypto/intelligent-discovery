from intelligent_discovery.case_extensions import CaseCandidate, CaseProviderResponse
from intelligent_discovery.domain import Source


def test_case_provider_response_preserves_limitations_without_claiming_verification() -> None:
    source = Source(task_id="task-1", title="候选来源", url="https://example.com", excerpt="摘要", credibility=0.4)
    candidate = CaseCandidate(name="候选案例", case_type="example", source=source, rationale="与研究主题相关")
    response = CaseProviderResponse(candidates=[candidate], limitations=["尚未验证来源真实性"])
    assert response.candidates[0].name == "候选案例"
    assert response.limitations == ["尚未验证来源真实性"]
