from pathlib import Path

import pytest

from intelligent_discovery.beta_operations import (
    BackupVerificationService,
    BetaAgreement,
    BetaConsent,
    BetaExit,
    CaseReleaseChecklist,
    DataAsset,
    DataProtectionCenter,
    OperationsRouting,
    ReleaseApproval,
    ReleaseCandidate,
    ReleaseService,
    ReleaseStatus,
    RiskLevel,
    SQLitePrivateDataAdapter,
    TrustChecklist,
)


def complete_trust() -> TrustChecklist:
    return TrustChecklist(True, True, True, True, True, True, True, True, True)


def test_release_candidate_requires_ordered_reviews_and_human_approval() -> None:
    candidate = ReleaseCandidate(
        "0.9.2-rc.1", "trust controls", "local beta only", "all tests pass", "reviewed", "none", "restore backup"
    )
    service = ReleaseService()
    for expected in (ReleaseStatus.TESTING, ReleaseStatus.SECURITY_REVIEW, ReleaseStatus.GOVERNANCE_REVIEW):
        assert service.transition(candidate, expected).status is expected
    with pytest.raises(ValueError):
        service.transition(candidate, ReleaseStatus.APPROVED, complete_trust())
    approval = ReleaseApproval(candidate.id, "release-owner", "owner", "approved", "private beta accepted")
    assert (
        service.transition(candidate, ReleaseStatus.APPROVED, complete_trust(), approval).status
        is ReleaseStatus.APPROVED
    )
    assert service.transition(candidate, ReleaseStatus.RELEASED).status is ReleaseStatus.RELEASED
    assert service.transition(candidate, ReleaseStatus.MONITORING).status is ReleaseStatus.MONITORING


def test_data_protection_center_exports_deletes_and_audits(tmp_path: Path) -> None:
    store = SQLitePrivateDataAdapter(tmp_path / "private.db")
    store.save_asset(DataAsset("user-1", "knowledge", {"title": "private note"}))
    center = DataProtectionCenter(store)
    assert center.export("user-1", "user-1", "user requested export")[0]["payload"]["title"] == "private note"
    assert center.delete("user-1", "user-1", "user requested deletion") == 1
    assert center.view("user-1", "user-1", "confirm deletion") == []
    assert [record.action for record in center.history("user-1")] == ["view", "export", "delete", "view"]


def test_backup_recovery_drill_verifies_a_non_destructive_restore(tmp_path: Path) -> None:
    source = tmp_path / "beta.db"
    source.write_bytes(b"trusted beta data")
    record = BackupVerificationService().exercise(source, tmp_path / "drill")
    assert record.integrity_verified and record.failure_simulated and record.consistency_verified
    assert source.read_bytes() == b"trusted beta data"


def test_beta_agreement_consent_and_exit_disclose_control_boundaries() -> None:
    agreement = BetaAgreement("user-1", "0.9.2", "private beta", "local data only", "feedback", "request exit")
    consent = BetaConsent("user-1", "feedback processing", True)
    exit_request = BetaExit("user-1", "testing complete")
    assert agreement.exit_method == "request exit"
    assert consent.granted is True
    assert exit_request.completed is False


def test_case_release_and_risk_routing_require_review() -> None:
    assert CaseReleaseChecklist(True, True, True, True).verified() is True
    assert CaseReleaseChecklist(True, False, True, True).verified() is False
    assert OperationsRouting.route(RiskLevel.LEVEL_3) == "major_incident_response"
