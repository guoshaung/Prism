"""
Adaptive KGW watermarking primitives.

This module keeps the implementation intentionally lightweight so the project
can focus on the KGW innovation itself while still exposing enough hooks to
demonstrate a full attack-defense-detection loop.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Optional

from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter


class AdaptiveKGWWatermark:
    """
    Minimal KGW watermark implementation.

    The core idea is unchanged: semantically central concepts receive less
    watermark bias, while peripheral content can carry stronger signals.
    """

    def __init__(
        self,
        base_delta: float = 2.0,
        secret_key: str = "innersafe-default-key",
        green_list_ratio: float = 0.5,
    ) -> None:
        if not 0.0 < green_list_ratio < 1.0:
            raise ValueError("green_list_ratio must be in (0.0, 1.0)")

        self.base_delta = base_delta
        self.secret_key = secret_key
        self.green_list_ratio = green_list_ratio

    def inject_watermark(
        self,
        text: str,
        graph: KnowledgeGraphAdapter,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Simulate watermark injection over an existing text.

        This does not rewrite the text. Instead, it records the token-level KGW
        decisions so the same logic can later be reused in a decoder wrapper.
        """
        tokens = self._tokenize(text, graph)
        token_decisions = []

        for position, token in enumerate(tokens):
            adaptive_delta = self.compute_adaptive_delta(token, graph)
            is_green = self._is_green_token(token, context or "", position)
            token_decisions.append(
                {
                    "token": token,
                    "position": position,
                    "centrality": graph.get_semantic_centrality(token),
                    "adaptive_delta": adaptive_delta,
                    "is_green": is_green,
                    "watermarked": is_green and adaptive_delta > 0.1,
                }
            )

        watermark_strength = sum(
            decision["adaptive_delta"]
            for decision in token_decisions
            if decision["watermarked"]
        ) / max(len(token_decisions), 1)

        return {
            "watermarked_text": " ".join(tokens),
            "watermark_metadata": {
                "watermark_strength": watermark_strength,
                "num_watermarked_tokens": sum(
                    decision["watermarked"] for decision in token_decisions
                ),
                "total_tokens": len(tokens),
                "base_delta": self.base_delta,
                "secret_key_hash": self._secret_key_hash(),
            },
            "token_decisions": token_decisions,
        }

    def compute_adaptive_delta(
        self,
        token: str,
        graph: KnowledgeGraphAdapter,
    ) -> float:
        """Compute KGW bias strength for a token."""
        centrality = graph.get_semantic_centrality(token)
        return self.base_delta * (1.0 - centrality)

    def bias_logit(
        self,
        token: str,
        logit: float,
        graph: KnowledgeGraphAdapter,
        context: str = "",
        position: int = 0,
    ) -> float:
        """
        Apply KGW bias to one candidate token logit.

        This is the key hook used by the HuggingFace-style integration wrapper.
        """
        if not self._is_green_token(token, context, position):
            return logit
        return logit + self.compute_adaptive_delta(token, graph)

    def verify_watermark(
        self,
        text: str,
        graph: KnowledgeGraphAdapter,
        context: Optional[str] = None,
        threshold: float = 0.5,
    ) -> dict[str, Any]:
        """
        Verify whether the text still exhibits the KGW watermark pattern.
        """
        tokens = self._tokenize(text, graph)
        green_count = 0
        total_weight = 0.0

        for position, token in enumerate(tokens):
            adaptive_delta = self.compute_adaptive_delta(token, graph)
            is_green = self._is_green_token(token, context or "", position)
            if is_green and adaptive_delta > 0.1:
                green_count += 1
                total_weight += adaptive_delta

        green_ratio = green_count / max(len(tokens), 1)
        expected_ratio = self.green_list_ratio
        z_score = (green_ratio - expected_ratio) / (expected_ratio * 0.1 + 1e-6)
        is_watermarked = z_score > threshold
        confidence = min(max(z_score / 3.0, 0.0), 1.0)

        return {
            "is_watermarked": is_watermarked,
            "confidence": confidence,
            "statistics": {
                "green_token_count": green_count,
                "total_tokens": len(tokens),
                "green_ratio": green_ratio,
                "expected_ratio": expected_ratio,
                "z_score": z_score,
                "total_weight": total_weight,
            },
        }

    def _is_green_token(self, token: str, context: str, position: int) -> bool:
        hash_input = f"{self.secret_key}:{token}:{context}:{position}"
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        normalized_hash = (hash_value % 10000) / 10000.0
        return normalized_hash < self.green_list_ratio

    def _tokenize(self, text: str, graph: KnowledgeGraphAdapter) -> list[str]:
        """
        Lightweight tokenizer for tests and demonstrations.
        """
        if re.search(r"\s", text):
            return [token for token in text.split() if token]

        vocab: list[str] = []
        centrality_map = getattr(graph, "centrality_map", None)
        if isinstance(centrality_map, dict):
            vocab = sorted((str(key) for key in centrality_map.keys()), key=len, reverse=True)

        tokens: list[str] = []
        index = 0
        while index < len(text):
            char = text[index]
            if char.isspace():
                index += 1
                continue

            matched = next(
                (term for term in vocab if term and text.startswith(term, index)),
                None,
            )
            if matched:
                tokens.append(matched)
                index += len(matched)
                continue

            if "\u4e00" <= char <= "\u9fff":
                if index + 2 <= len(text):
                    tokens.append(text[index : index + 2])
                    index += 2
                else:
                    tokens.append(char)
                    index += 1
                continue

            match = re.match(r"[A-Za-z0-9_]+", text[index:])
            if match:
                tokens.append(match.group(0))
                index += len(match.group(0))
            else:
                tokens.append(char)
                index += 1

        return tokens

    def _secret_key_hash(self) -> str:
        return hashlib.sha256(self.secret_key.encode()).hexdigest()[:16]
