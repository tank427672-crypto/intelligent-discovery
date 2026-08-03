"""Stable contracts for modules planned after v0.1, without implementing them."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from .domain import DiscoveryTask, Source


class Capability(StrEnum):
    RESEARCH = "research"
    OPPORTUNITY_DISCOVERY = "opportunity_discovery"
    DECISION_ANALYSIS = "decision_analysis"
    PERSONAL_INTELLIGENCE = "personal_intelligence"
    RECOMMENDATION = "recommendation"
    CASE_INTELLIGENCE = "case_intelligence"
    COMMUNITY = "community"
    CONTRIBUTION = "contribution"
    ENTERPRISE = "enterprise"
    EXPERIMENTAL = "experimental"


class ResearchProvider(Protocol):
    name: str

    def collect(self, task: DiscoveryTask) -> list[Source]: ...


class OpportunitySignalProvider(Protocol):
    name: str

    def detect(self) -> list[dict[str, object]]: ...


class DecisionAssessmentProvider(Protocol):
    name: str

    def assess(self, subject: dict[str, object]) -> dict[str, object]: ...


class PersonalizationProvider(Protocol):
    name: str

    def personalize(
        self, user_profile: dict[str, object], discoveries: list[dict[str, object]]
    ) -> list[dict[str, object]]: ...


class RecommendationProvider(Protocol):
    name: str

    def recommend(self, subject: dict[str, object], context: dict[str, object]) -> list[dict[str, object]]: ...


class CaseIntelligenceProvider(Protocol):
    name: str

    def learn(self, case: dict[str, object]) -> dict[str, object]: ...


class CommunityProvider(Protocol):
    name: str

    def publish(self, contribution: dict[str, object]) -> dict[str, object]: ...


class ContributionProvider(Protocol):
    name: str

    def evaluate(self, contribution: dict[str, object]) -> dict[str, object]: ...


class EnterpriseProvider(Protocol):
    name: str

    def execute(self, request: dict[str, object]) -> dict[str, object]: ...


@dataclass
class ExtensionRegistry:
    """Capability registry. Implementations remain outside the core service."""

    providers: dict[Capability, object] = field(default_factory=dict)

    def register(self, capability: Capability, provider: object) -> None:
        if capability in self.providers:
            raise ValueError(f"capability already registered: {capability}")
        self.providers[capability] = provider

    def get(self, capability: Capability) -> object | None:
        return self.providers.get(capability)
