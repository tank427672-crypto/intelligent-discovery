import pytest

from intelligent_discovery.extensions import Capability, ExtensionRegistry
from intelligent_discovery.modules import MODULE_CATALOGUE


def test_module_catalogue_covers_planned_ecosystem_and_unknown_space() -> None:
    capabilities = {module.capability for module in MODULE_CATALOGUE}
    assert {
        Capability.OPPORTUNITY_DISCOVERY,
        Capability.DECISION_ANALYSIS,
        Capability.PERSONAL_INTELLIGENCE,
        Capability.RECOMMENDATION,
        Capability.CASE_INTELLIGENCE,
        Capability.COMMUNITY,
        Capability.CONTRIBUTION,
        Capability.ENTERPRISE,
        Capability.EXPERIMENTAL,
    } <= capabilities


def test_extension_registry_prevents_ambiguous_capability_replacement() -> None:
    registry = ExtensionRegistry()
    provider = object()
    registry.register(Capability.EXPERIMENTAL, provider)
    assert registry.get(Capability.EXPERIMENTAL) is provider
    with pytest.raises(ValueError, match="already registered"):
        registry.register(Capability.EXPERIMENTAL, object())
