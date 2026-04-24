"""Mock copyright-side components used as architecture placeholders."""

from __future__ import annotations

import hashlib
from typing import Any


class MockKeyManager:
    """Tiny stand-in for future key lifecycle management."""

    def issue_key(self, namespace: str) -> str:
        return hashlib.sha256(namespace.encode()).hexdigest()[:16]


class MockCopyrightPolicy:
    """Minimal policy object for future watermark strategy expansion."""

    def __init__(self, base_delta: float = 2.0) -> None:
        self.base_delta = base_delta

    def resolve_delta(self, sensitivity: str = "balanced") -> float:
        mapping = {
            "strict": self.base_delta * 1.5,
            "balanced": self.base_delta,
            "gentle": self.base_delta * 0.5,
        }
        return mapping.get(sensitivity, self.base_delta)


class MockForensicRecorder:
    """Simple in-memory placeholder for future evidence recording."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {"event_type": event_type, "payload": payload}
        self.events.append(event)
        return event
