"""Module catalogue for the long-term ecosystem.

The catalogue intentionally describes planned modules without coupling v0.1 to
their implementation. A module becomes active only by registering a provider
for its declared capability.
"""

from __future__ import annotations

from dataclasses import dataclass

from .extensions import Capability


@dataclass(frozen=True, slots=True)
class ModuleDefinition:
    key: str
    name: str
    capability: Capability
    phase: str
    purpose: str


MODULE_CATALOGUE: tuple[ModuleDefinition, ...] = (
    ModuleDefinition(
        "discovery-core",
        "Discovery Core",
        Capability.RESEARCH,
        "v0.1",
        "Creates and coordinates evidence-led discovery tasks.",
    ),
    ModuleDefinition(
        "opportunity-radar",
        "Opportunity Radar",
        Capability.OPPORTUNITY_DISCOVERY,
        "future",
        "Detects relevant external change signals.",
    ),
    ModuleDefinition(
        "decision-engine",
        "Decision Analysis",
        Capability.DECISION_ANALYSIS,
        "future",
        "Evaluates options while preserving human judgment.",
    ),
    ModuleDefinition(
        "personal-intelligence",
        "Personal Intelligence",
        Capability.PERSONAL_INTELLIGENCE,
        "future",
        "Applies consented user context to discovery.",
    ),
    ModuleDefinition(
        "recommendation",
        "Recommendation",
        Capability.RECOMMENDATION,
        "future",
        "Surfaces contextual next-best information.",
    ),
    ModuleDefinition(
        "case-intelligence",
        "Case Intelligence",
        Capability.CASE_INTELLIGENCE,
        "future",
        "Learns structured lessons from cases.",
    ),
    ModuleDefinition(
        "community", "Community System", Capability.COMMUNITY, "future", "Supports review, sharing, and collaboration."
    ),
    ModuleDefinition(
        "contribution",
        "Contribution System",
        Capability.CONTRIBUTION,
        "future",
        "Recognizes verified community contributions.",
    ),
    ModuleDefinition(
        "enterprise",
        "Enterprise Services",
        Capability.ENTERPRISE,
        "future",
        "Provides governed organization-level workflows.",
    ),
    ModuleDefinition(
        "experimental",
        "Experimental Extensions",
        Capability.EXPERIMENTAL,
        "always",
        "Reserved for future unknown ideas under explicit review.",
    ),
)
