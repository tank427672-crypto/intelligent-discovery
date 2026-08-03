"""Contracts for future classification, recommendation, personal and community capabilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .domain import Classification, CommunityContribution, HelpRequest, PersonalDiscoverySpace, RecommendationRecord


@dataclass(slots=True)
class ClassificationSuggestion:
    classification: Classification
    rationale: str
    requires_human_confirmation: bool = True


class AutoClassificationProvider(Protocol):
    name: str

    def suggest(self, object_type: str, object_id: str) -> list[ClassificationSuggestion]: ...


class RecommendationProvider(Protocol):
    name: str

    def recommend(self, context: dict[str, object]) -> list[RecommendationRecord]: ...


class PersonalDiscoveryProvider(Protocol):
    name: str

    def build_space(self, space: PersonalDiscoverySpace) -> dict[str, object]: ...


class CommunityDiscoveryProvider(Protocol):
    name: str

    def accept_help_request(self, request: HelpRequest) -> dict[str, object]: ...
    def intake_contribution(self, contribution: CommunityContribution) -> dict[str, object]: ...
