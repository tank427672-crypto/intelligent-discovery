import pytest

from intelligent_discovery.evolution import (
    EvolutionCandidate,
    EvolutionService,
    EvolutionStatus,
    SQLiteEvolutionAdapter,
)
from intelligent_discovery.response import (
    IncidentStatus,
    ResponseEvaluation,
    ResponseIncident,
    ResponseService,
    SQLiteResponseAdapter,
)


def test_response_and_controlled_evolution():
    assert (
        ResponseService().transition(IncidentStatus.DETECTED, IncidentStatus.ACKNOWLEDGED)
        == IncidentStatus.ACKNOWLEDGED
    )
    with pytest.raises(ValueError):
        ResponseEvaluation("r", "a", "b", 2, "review")
    c = EvolutionCandidate("i", "problem", 1, 2, 3, "change")
    with pytest.raises(ValueError):
        EvolutionService().transition(c, EvolutionStatus.APPROVED)
    assert EvolutionService().transition(c, EvolutionStatus.APPROVED, True, True).status == EvolutionStatus.APPROVED


def test_response_persistence_and_event_driven_evolution(tmp_path):
    response = ResponseService(SQLiteResponseAdapter(tmp_path / "response.db"))
    incident = response.create_incident(ResponseIncident("private access anomaly", "high"))
    assert response.transition_incident(incident, IncidentStatus.ACKNOWLEDGED).status == IncidentStatus.ACKNOWLEDGED
    evolution = EvolutionService(SQLiteEvolutionAdapter(tmp_path / "evolution.db"))
    candidate = EvolutionCandidate.prioritized(incident.id, "review access patterns", 1, 3, 1, "add review")
    assert evolution.trigger(candidate, major_incident=True).status == EvolutionStatus.EVALUATING
