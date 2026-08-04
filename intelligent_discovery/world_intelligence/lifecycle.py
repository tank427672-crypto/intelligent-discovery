"""World-event lifecycle after verification; it records evolution, not certainty."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class WorldEventLifecycleStatus(StrEnum):
    DETECTED = "detected"
    EMERGING = "emerging"
    ACTIVE = "active"
    DEVELOPING = "developing"
    RESOLVED = "resolved"
    HISTORICAL = "historical"


@dataclass(slots=True)
class WorldEventLifecycle:
    event_id: str
    status: WorldEventLifecycleStatus = WorldEventLifecycleStatus.DETECTED
    source_changes: list[str] = field(default_factory=list)
    evidence_references: list[str] = field(default_factory=list)
    historical_versions: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))


class WorldEventLifecycleService:
    FLOW = {
        WorldEventLifecycleStatus.DETECTED: {WorldEventLifecycleStatus.EMERGING},
        WorldEventLifecycleStatus.EMERGING: {WorldEventLifecycleStatus.ACTIVE},
        WorldEventLifecycleStatus.ACTIVE: {WorldEventLifecycleStatus.DEVELOPING, WorldEventLifecycleStatus.RESOLVED},
        WorldEventLifecycleStatus.DEVELOPING: {WorldEventLifecycleStatus.RESOLVED},
        WorldEventLifecycleStatus.RESOLVED: {WorldEventLifecycleStatus.HISTORICAL},
        WorldEventLifecycleStatus.HISTORICAL: set(),
    }

    def transition(self, lifecycle: WorldEventLifecycle, target: WorldEventLifecycleStatus) -> WorldEventLifecycle:
        if target not in self.FLOW[lifecycle.status]:
            raise ValueError("invalid world event lifecycle transition")
        lifecycle.status = target
        return lifecycle
