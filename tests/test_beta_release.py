from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from intelligent_discovery.api import app
from intelligent_discovery.beta import (
    BetaFeedback,
    BetaFeedbackService,
    BetaFeedbackType,
    BetaReleaseService,
    BetaRole,
    BetaUser,
    CaseLicense,
    ReleaseCandidate,
    ReleaseChecklist,
    ReleaseStage,
    SQLiteBetaAdapter,
)
from intelligent_discovery.case_seed import load_case_seeds
from intelligent_discovery.case_view import CaseCardContract, CaseDetailContract
from intelligent_discovery.observability import ObservabilityService, SQLiteObservabilityAdapter


def test_case_seed_import_has_twenty_public_candidates() -> None:
    seeds = load_case_seeds(Path("case_seed/cases.json"))
    assert len(seeds) >= 20
    assert {seed.category for seed in seeds} >= {"AI与科技", "开源生态", "商业生态", "创业与失败案例", "社区生态"}
    assert all(seed.source.startswith("https://") for seed in seeds)


def test_case_license_requires_public_source_and_declaration() -> None:
    license_record = CaseLicense("https://example.org/source", "CC BY 4.0", "structured summary only")
    assert license_record.citation_required is True
    with pytest.raises(ValueError):
        CaseLicense("local-file", "", "")


def test_case_display_contract_exposes_required_evidence_and_feedback_sections() -> None:
    card = CaseCardContract("案例", "community", 0, 1, 0, "seed-candidate", "协作")
    assert card.verification_status == "candidate"
    assert {"evidence_chain", "graph_relationships", "feedback"} <= set(CaseDetailContract().sections)


def test_beta_feedback_permission_and_incident_routing(tmp_path: Path) -> None:
    service = BetaFeedbackService(SQLiteBetaAdapter(tmp_path / "beta.db"))
    user = service.register_user(BetaUser(role=BetaRole.TESTER, permissions=["feedback:submit"]))
    feedback = service.submit(
        BetaFeedback(user.id, "case:seed", BetaFeedbackType.BUG, "evidence link is unavailable", priority="critical")
    )
    assert service.route(feedback) == "incident_triage"
    with pytest.raises(PermissionError):
        service.submit(BetaFeedback("unknown", "case:seed", BetaFeedbackType.CASE, "check license"))


def test_release_checklist_requires_human_approval_and_every_gate() -> None:
    candidate = ReleaseCandidate("0.9.1-beta.1", ReleaseStage.PRIVATE_BETA, "invited testers", [], [], approved=False)
    checklist = ReleaseChecklist(True, True, True, True, True, True)
    assert BetaReleaseService.can_progress(candidate, checklist) is False
    candidate.approved = True
    assert BetaReleaseService.can_progress(candidate, checklist) is True
    assert BetaReleaseService.can_progress(candidate, ReleaseChecklist(True, True, True, False, True, True)) is False


def test_beta_feedback_event_tracking_excludes_feedback_body(tmp_path: Path) -> None:
    events = ObservabilityService(SQLiteObservabilityAdapter(tmp_path / "events.db"))
    service = BetaFeedbackService(SQLiteBetaAdapter(tmp_path / "beta.db"), events)
    user = service.register_user(BetaUser(role=BetaRole.CONTRIBUTOR, permissions=["feedback:submit"]))
    service.submit(BetaFeedback(user.id, "case:seed", BetaFeedbackType.CASE, "citation is useful"))
    tracked = events.store.list_events("FeedbackSubmitted")
    assert tracked[0].metadata == {"feedback_type": "case", "priority": "normal"}


def test_beta_api_exposes_candidates_and_feedback_loop() -> None:
    client = TestClient(app)
    featured = client.get("/beta/featured-discoveries")
    assert featured.status_code == 200
    assert len(featured.json()) >= 20
    assert featured.json()[0]["verification_status"] == "candidate"
    user = client.post("/beta/users", json={"role": "tester"})
    feedback = client.post(
        "/beta/feedback",
        json={
            "user_id": user.json()["id"],
            "target": "case:seed",
            "feedback_type": "experience",
            "content": "展示结构清晰",
        },
    )
    assert user.status_code == 201
    assert feedback.status_code == 201
    assert feedback.json()["review_route"] == "periodic_governance_review"
