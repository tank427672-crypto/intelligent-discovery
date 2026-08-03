from intelligent_discovery.research import ResearchFailure, ResearchFailureKind, ResearchResponse, SearchRequest


def test_research_failure_is_explicit_and_never_represented_as_a_source() -> None:
    request = SearchRequest(query="不完整资料", task_id="task-1")
    response = ResearchResponse(
        failures=[
            ResearchFailure(
                kind=ResearchFailureKind.INSUFFICIENT_DATA,
                message="可信资料不足，不能形成结论。",
                retryable=True,
            )
        ]
    )
    assert request.limit == 10
    assert response.sources == []
    assert response.failures[0].kind == ResearchFailureKind.INSUFFICIENT_DATA
