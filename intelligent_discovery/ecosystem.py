"""Future ecosystem contracts, feature flags and permission boundaries.

No provider here can modify core knowledge, permissions, reputation or rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class EcosystemCapability(StrEnum):
    MOBILE_APP = "mobile_app"
    COMMUNITY = "community"
    EXPERT = "expert"
    CONTRIBUTION = "contribution"
    ENTERPRISE = "enterprise"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    AI_PROVIDER = "ai_provider"


@dataclass(slots=True)
class FeatureFlag:
    capability: EcosystemCapability
    enabled: bool = False
    beta_only: bool = True
    approved_by: str = ""

    def __post_init__(self) -> None:
        if self.enabled and not self.approved_by:
            raise ValueError("enabling an ecosystem capability requires human approval")


@dataclass(frozen=True, slots=True)
class PermissionBoundary:
    capability: EcosystemCapability
    allowed_actions: tuple[str, ...]
    prohibited_actions: tuple[str, ...] = (
        "modify_knowledge",
        "modify_permissions",
        "modify_reputation",
        "modify_rules",
    )


class CommunityPort(Protocol):
    def propose_discussion(self, topic_id: str, summary: str) -> str: ...


class ExpertNetworkPort(Protocol):
    def request_enhancement(self, object_id: str, evidence_references: list[str]) -> str: ...


class ContributionPort(Protocol):
    def submit(self, contribution_type: str, source_references: list[str]) -> str: ...


class NotificationPort(Protocol):
    def notify(self, recipient_id: str, notification_type: str, reference_id: str) -> None: ...


class AIProviderPort(Protocol):
    def propose(self, operation: str, evidence_references: list[str]) -> dict[str, object]: ...


class EnterpriseServicePort(Protocol):
    def propose_analysis(self, request_id: str) -> dict[str, object]: ...


class BillingPort(Protocol):
    def prepare_checkout(self, plan_id: str) -> str: ...


class EcosystemExtensionRegistry:
    """Disabled by default; a registered provider is not automatically activated."""

    def __init__(self) -> None:
        self.flags = {capability: FeatureFlag(capability) for capability in EcosystemCapability}
        self.providers: dict[EcosystemCapability, object] = {}

    def register(self, capability: EcosystemCapability, provider: object) -> None:
        if capability in self.providers:
            raise ValueError("capability provider already registered")
        self.providers[capability] = provider

    def enable(self, capability: EcosystemCapability, approver: str) -> FeatureFlag:
        flag = FeatureFlag(capability, enabled=True, beta_only=True, approved_by=approver)
        self.flags[capability] = flag
        return flag

    def available(self, capability: EcosystemCapability) -> bool:
        return self.flags[capability].enabled and capability in self.providers
