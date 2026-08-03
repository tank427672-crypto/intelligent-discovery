"""Validation and loading of reviewed-before-import case seed candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CaseSeed:
    name: str
    case_type: str
    category: str
    source: str
    license: str
    summary: str


def load_case_seeds(path: str | Path) -> list[CaseSeed]:
    """Load structured candidates; this deliberately does not create CaseRecords."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("case seed file must contain a list")
    seeds = [
        CaseSeed(
            name=item["name"],
            case_type=item.get("case_type", item.get("type", "unknown")),
            category=item["category"],
            source=item["source"],
            license=item["license"],
            summary=item["summary"],
        )
        for item in raw
    ]
    for seed in seeds:
        if not seed.name or not seed.summary or not seed.source.startswith(("https://", "http://")):
            raise ValueError("case seeds need a name, summary and public source URL")
        if not seed.license:
            raise ValueError("case seeds need a license declaration")
    return seeds
