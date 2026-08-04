"""World Intelligence Acquisition foundation; all acquired items remain candidates until verified."""

from .event_candidate import WorldEventCandidate, WorldEventStatus
from .source_registry import SourceRecord, WorldSourceType

__all__ = ["SourceRecord", "WorldEventCandidate", "WorldEventStatus", "WorldSourceType"]
