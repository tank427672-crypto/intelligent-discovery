import pytest

from intelligent_discovery.communication import CommunicationPriority
from intelligent_discovery.experience import (
    BetaExperienceService,
    ExperienceSignal,
    ExpertEnhancementRequest,
    ExpertFeedbackReview,
    ImprovementLink,
    InMemoryExperienceAdapter,
    UserFeedbackWorkflow,
)


def test_experience_signal_requires_consent_and_rejects_private_content() -> None:
    with pytest.raises(ValueError):
        ExperienceSignal("u1", "search", {"action": "completed"}, False)
    with pytest.raises(ValueError):
        ExperienceSignal("u1", "search", {"query": "private question"}, True)
    signal = ExperienceSignal("u1", "case_view", {"action": "opened", "outcome": "success"}, True)
    assert signal.metadata["action"] == "opened"


def test_priority_routes_security_and_repeated_friction() -> None:
    service = BetaExperienceService(InMemoryExperienceAdapter())
    assert service.priority(1, 1, 1, True) is CommunicationPriority.P0
    assert service.priority(25, 2, 1, False) is CommunicationPriority.P1
    assert service.priority(2, 1, 3, False) is CommunicationPriority.P2
    assert service.priority(1, 1, 1, False) is CommunicationPriority.P3


def test_feedback_analysis_and_evolution_link_stay_human_controlled() -> None:
    store, service = InMemoryExperienceAdapter(), BetaExperienceService(InMemoryExperienceAdapter())
    service = BetaExperienceService(store)
    signal = service.record(ExperienceSignal("u1", "feedback", {"feature": "search", "outcome": "failed"}, True))
    insight = service.analyze([signal.id], "functional_friction", "search result flow needs review", 5, 2, 3, False)
    workflow = UserFeedbackWorkflow("communication-1", [signal.id], insight.id, "proposal-1", "candidate-1")
    link = service.link_improvement(ImprovementLink(insight.id, "proposal-1", "candidate-1"))
    assert insight.priority is CommunicationPriority.P2
    assert workflow.can_release() is False
    assert link.ready_for_release() is False


def test_expert_enhancement_and_feedback_do_not_grant_automatic_authority() -> None:
    request = ExpertEnhancementRequest("expert-1", "case", "case-1", "evidence_boundary", ["evidence-1"])
    review = ExpertFeedbackReview(request.id, 5, 4, 5, 5, "user-1")
    assert request.can_change_knowledge() is False
    assert review.scores == (5, 4, 5, 5)
