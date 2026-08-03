import pytest

from intelligent_discovery.communication import (
    AIInteractionExplanation,
    CommunicationPriority,
    CommunicationRecord,
    CommunicationRiskAssessment,
    CommunicationService,
    CommunicationStatus,
    CommunicationType,
    ContributorCommunication,
    FeedbackResolution,
    HelpRequestWorkflow,
    InMemoryCommunicationAdapter,
)
from intelligent_discovery.domain import DataVisibility


def move_to_processing(service: CommunicationService, record: CommunicationRecord) -> None:
    service.transition(record, CommunicationStatus.RECEIVED, "triage", "received")
    service.transition(record, CommunicationStatus.ASSIGNED, "triage", "assigned")
    service.transition(record, CommunicationStatus.PROCESSING, "owner", "working")


def test_communication_lifecycle_is_ordered_and_audited() -> None:
    store, service = InMemoryCommunicationAdapter(), CommunicationService(InMemoryCommunicationAdapter())
    # Service and store need the same port instance.
    service = CommunicationService(store)
    record = service.create(
        CommunicationRecord(
            "user", "u1", "system", "triage", CommunicationType.FEEDBACK, "case", "c1", "correct source"
        )
    )
    with pytest.raises(ValueError):
        service.transition(record, CommunicationStatus.RESOLVED, "owner", "skip")
    move_to_processing(service, record)
    service.transition(record, CommunicationStatus.RESOLVED, "owner", "resolved")
    service.transition(record, CommunicationStatus.CLOSED, "owner", "notified")
    assert record.status is CommunicationStatus.CLOSED
    assert len(store.list_history(record.id)) == 5


def test_private_by_default_and_risk_assessment_never_reads_body() -> None:
    record = CommunicationRecord(
        "user", "u1", "system", "triage", CommunicationType.SECURITY_REPORT, "data", "d1", "report"
    )
    risk = CommunicationRiskAssessment(record.id, ["rapid_repeat"], CommunicationPriority.P0)
    assert record.visibility is DataVisibility.PRIVATE
    assert risk.metadata_only and risk.human_review_required
    with pytest.raises(ValueError):
        CommunicationRiskAssessment(record.id, [], CommunicationPriority.P3, metadata_only=False)


def test_feedback_closure_records_owner_and_user_result() -> None:
    service = CommunicationService(InMemoryCommunicationAdapter())
    record = service.create(
        CommunicationRecord(
            "user", "u1", "system", "triage", CommunicationType.FEATURE_REQUEST, "feature", "f1", "add export"
        )
    )
    move_to_processing(service, record)
    resolution = service.resolve_feedback(
        FeedbackResolution(record.id, "owner", "planned", "proposal-1", True), "owner"
    )
    assert record.status is CommunicationStatus.RESOLVED
    assert resolution.improvement_proposal_id == "proposal-1"


def test_help_and_contributor_workflows_do_not_auto_update_knowledge() -> None:
    help_flow = HelpRequestWorkflow("comm-1")
    contribution = ContributorCommunication("comm-2", "case_correction")
    assert help_flow.review_required and not help_flow.knowledge_update_approved
    assert contribution.can_update_knowledge() is False
    contribution.evidence_reviewed, contribution.reviewer_id, contribution.approved = True, "reviewer-1", True
    assert contribution.can_update_knowledge() is True


def test_ai_explanations_keep_assumptions_and_unknowns_visible() -> None:
    explanation = AIInteractionExplanation(
        "comm-1", ["case record"], ["source-1"], ["similarity heuristic"], ["coverage incomplete"]
    )
    assert explanation.human_review_required
    assert explanation.uncertainties == ["coverage incomplete"]
