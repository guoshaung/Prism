"""Simple text attacks used for watermark robustness experiments."""

from __future__ import annotations

import math

from innersafe_mas.copyright.attacks.base import BaseAttack


class ParaphraseAttack(BaseAttack):
    """
    Mock paraphrase attack based on deterministic token substitution.

    This is intentionally simple: good enough for research demos without
    pretending to be a strong paraphrase model.
    """

    name = "paraphrase"

    def __init__(self, replacements: dict[str, str] | None = None) -> None:
        self.replacements = replacements or {
            "recommend": "suggest",
            "safe": "secure",
            "helps": "supports",
            "doctor": "clinician",
        }

    def apply(self, text: str) -> str:
        tokens = text.split()
        return " ".join(self.replacements.get(token, token) for token in tokens)


class TruncationAttack(BaseAttack):
    """Drop the tail of the sequence to simulate clipping/truncation."""

    name = "truncation"

    def __init__(self, keep_ratio: float = 0.7) -> None:
        if not 0.0 < keep_ratio <= 1.0:
            raise ValueError("keep_ratio must be in (0.0, 1.0]")
        self.keep_ratio = keep_ratio

    def apply(self, text: str) -> str:
        tokens = text.split()
        keep = max(1, math.ceil(len(tokens) * self.keep_ratio))
        return " ".join(tokens[:keep])


class WordDeletionAttack(BaseAttack):
    """Remove every n-th token to simulate lightweight corruption."""

    name = "word_deletion"

    def __init__(self, drop_every: int = 3) -> None:
        if drop_every < 2:
            raise ValueError("drop_every must be >= 2")
        self.drop_every = drop_every

    def apply(self, text: str) -> str:
        tokens = text.split()
        kept = [
            token
            for index, token in enumerate(tokens, start=1)
            if index % self.drop_every != 0
        ]
        return " ".join(kept)
