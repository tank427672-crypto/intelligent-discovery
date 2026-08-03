import pytest

from intelligent_discovery.evolution import EvolutionCandidate, EvolutionService, EvolutionStatus
from intelligent_discovery.response import IncidentStatus, ResponseEvaluation, ResponseService


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
