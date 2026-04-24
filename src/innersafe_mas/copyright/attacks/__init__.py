"""Minimal attack simulators for robustness testing."""

from innersafe_mas.copyright.attacks.base import BaseAttack
from innersafe_mas.copyright.attacks.simple_attacks import (
    ParaphraseAttack,
    TruncationAttack,
    WordDeletionAttack,
)

__all__ = [
    "BaseAttack",
    "ParaphraseAttack",
    "TruncationAttack",
    "WordDeletionAttack",
]
