"""Shared interfaces for robustness attacks."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAttack(ABC):
    """Abstract base class for text attacks."""

    name = "base_attack"

    @abstractmethod
    def apply(self, text: str) -> str:
        """Return the attacked text."""

