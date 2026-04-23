"""
Adaptive KGW (Knowledge Graph Watermark) for Copyright Protection.

This module implements a dynamic watermarking scheme that adapts to the
semantic importance of words in domain-specific knowledge graphs.

Theoretical Foundation:
    Traditional watermarking methods (e.g., fixed-bias token selection) distort
    all words equally, which degrades the quality of domain-critical knowledge.

    The KGW approach introduces adaptive bias:
        δ_dynamic(i) = δ_base × (1 - S(i))

    Where:
    - δ_base: Base watermark strength (e.g., 2.0 for logit bias)
    - S(i): Semantic centrality of word i in knowledge graph [0, 1]
    - δ_dynamic(i): Actual watermark bias applied to word i

    Key Properties:
    1. When S(i) = 1 (core concept): δ_dynamic = 0 → no distortion
    2. When S(i) = 0 (peripheral word): δ_dynamic = δ_base → full watermark
    3. Smooth interpolation for intermediate centrality values

    This ensures copyright traceability while preserving domain knowledge fidelity.
"""

import hashlib
import random
import re
from typing import Optional

from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter


class AdaptiveKGWWatermark:
    """
    Adaptive watermark injector based on knowledge graph centrality.

    This class implements a simplified watermarking scheme. In production,
    this would integrate with LLM generation APIs to bias token probabilities
    during sampling. Here we use text-level simulation for demonstration.

    Attributes:
        base_delta: Base watermark strength (higher = stronger but more distortion)
        secret_key: Secret key for watermark generation (must be kept private)
        green_list_ratio: Ratio of vocabulary to mark as "green" tokens
    """

    def __init__(
        self,
        base_delta: float = 2.0,
        secret_key: str = "innersafe-default-key",
        green_list_ratio: float = 0.5,
    ):
        """
        Initialize the adaptive watermark injector.

        Args:
            base_delta: Base watermark bias strength (typical range: 1.0 - 5.0)
            secret_key: Secret key for deterministic watermark generation
            green_list_ratio: Fraction of vocabulary to bias toward (0.0 - 1.0)
        """
        if not 0.0 < green_list_ratio < 1.0:
            raise ValueError("green_list_ratio must be in (0.0, 1.0)")

        self.base_delta = base_delta
        self.secret_key = secret_key
        self.green_list_ratio = green_list_ratio
        self._rng = random.Random(self._hash_key(secret_key))

    def _hash_key(self, key: str) -> int:
        """Generate deterministic seed from secret key."""
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**32)

    def inject_watermark(
        self,
        text: str,
        graph: KnowledgeGraphAdapter,
        context: Optional[str] = None,
    ) -> dict[str, any]:
        """
        Inject adaptive watermark into generated text.

        This method simulates watermark injection by:
        1. Tokenizing the text (mock: split by spaces)
        2. For each token, compute adaptive bias: δ_dynamic = δ_base × (1 - S(token))
        3. Decide whether to apply watermark based on green list membership
        4. Return watermarked text and metadata

        In a real LLM integration, this would:
        - Hook into the model's logit processor
        - Apply δ_dynamic as additive bias to green-list token logits
        - Sample from the biased distribution

        Args:
            text: Generated text to watermark (from LLM output)
            graph: Knowledge graph adapter for centrality lookup
            context: Optional context for contextual watermarking

        Returns:
            Dictionary containing:
            - "watermarked_text": Text with watermark applied
            - "watermark_metadata": Metadata for verification
            - "token_decisions": Per-token watermark decisions
        """
        tokens = self._tokenize(text, graph)
        watermarked_tokens = []
        token_decisions = []

        for i, token in enumerate(tokens):
            # Step 1: Get semantic centrality from knowledge graph
            centrality = graph.get_semantic_centrality(token)

            # Step 2: Compute adaptive watermark bias
            # Formula: δ_dynamic(i) = δ_base × (1 - S(i))
            adaptive_delta = self.base_delta * (1.0 - centrality)

            # Step 3: Determine if token is in green list (deterministic)
            is_green = self._is_green_token(token, context or "", i)

            # Step 4: Apply watermark decision
            # In real implementation, this would bias logits during generation
            # Here we simulate by marking tokens (no actual text modification)
            watermarked_tokens.append(token)

            token_decisions.append({
                "token": token,
                "position": i,
                "centrality": centrality,
                "adaptive_delta": adaptive_delta,
                "is_green": is_green,
                "watermarked": is_green and adaptive_delta > 0.1,  # Threshold
            })

        watermarked_text = " ".join(watermarked_tokens)

        # Compute watermark strength (for verification)
        watermark_strength = sum(
            d["adaptive_delta"] for d in token_decisions if d["watermarked"]
        ) / max(len(token_decisions), 1)

        metadata = {
            "watermark_strength": watermark_strength,
            "num_watermarked_tokens": sum(d["watermarked"] for d in token_decisions),
            "total_tokens": len(tokens),
            "base_delta": self.base_delta,
            "secret_key_hash": hashlib.sha256(self.secret_key.encode()).hexdigest()[:16],
        }

        return {
            "watermarked_text": watermarked_text,
            "watermark_metadata": metadata,
            "token_decisions": token_decisions,
        }

    def _tokenize(self, text: str, graph: KnowledgeGraphAdapter) -> list[str]:
        """
        Tokenize text for demonstration purposes.

        - If whitespace exists, split on whitespace (English-like tokens).
        - Otherwise, attempt a lightweight CJK segmentation:
          * Greedy longest-match over graph concepts (when available)
          * Fallback to 2-char chunks for CJK runs, 1-char for the remainder
        """
        if re.search(r"\s", text):
            return [t for t in text.split() if t]

        # Try to extract a concept vocabulary from mock adapters.
        vocab: list[str] = []
        centrality_map = getattr(graph, "centrality_map", None)
        if isinstance(centrality_map, dict):
            vocab = sorted((str(k) for k in centrality_map.keys()), key=len, reverse=True)

        tokens: list[str] = []
        i = 0
        while i < len(text):
            # Skip pure punctuation / whitespace-like chars.
            ch = text[i]
            if ch.isspace():
                i += 1
                continue

            # Greedy concept match.
            matched = None
            for term in vocab:
                if term and text.startswith(term, i):
                    matched = term
                    break
            if matched is not None:
                tokens.append(matched)
                i += len(matched)
                continue

            # CJK fallback chunking.
            if "\u4e00" <= ch <= "\u9fff":
                if i + 2 <= len(text):
                    tokens.append(text[i : i + 2])
                    i += 2
                else:
                    tokens.append(ch)
                    i += 1
                continue

            # ASCII word/number fallback.
            m = re.match(r"[A-Za-z0-9_]+", text[i:])
            if m:
                tokens.append(m.group(0))
                i += len(m.group(0))
            else:
                tokens.append(ch)
                i += 1

        return tokens

    def _is_green_token(self, token: str, context: str, position: int) -> bool:
        """
        Determine if a token belongs to the green list.

        Uses deterministic hashing based on:
        - Token content
        - Context (for contextual watermarking)
        - Position (for positional diversity)

        Args:
            token: The token to check
            context: Surrounding context
            position: Token position in sequence

        Returns:
            True if token is in green list, False otherwise
        """
        # Create deterministic hash from token, context, and position
        hash_input = f"{self.secret_key}:{token}:{context}:{position}"
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)

        # Map hash to [0, 1] and compare with green_list_ratio
        normalized_hash = (hash_value % 10000) / 10000.0
        return normalized_hash < self.green_list_ratio

    def verify_watermark(
        self,
        text: str,
        graph: KnowledgeGraphAdapter,
        context: Optional[str] = None,
        threshold: float = 0.5,
    ) -> dict[str, any]:
        """
        Verify if text contains the watermark.

        This method checks if the text exhibits statistical patterns consistent
        with watermark injection. In production, this would use hypothesis testing
        (e.g., z-test on green token ratio).

        Args:
            text: Text to verify
            graph: Knowledge graph adapter (same as used for injection)
            context: Optional context used during injection
            threshold: Detection threshold (higher = stricter)

        Returns:
            Dictionary containing:
            - "is_watermarked": Boolean detection result
            - "confidence": Detection confidence score [0, 1]
            - "statistics": Detailed statistics
        """
        tokens = self._tokenize(text, graph)
        green_count = 0
        total_weight = 0.0

        for i, token in enumerate(tokens):
            centrality = graph.get_semantic_centrality(token)
            adaptive_delta = self.base_delta * (1.0 - centrality)
            is_green = self._is_green_token(token, context or "", i)

            if is_green and adaptive_delta > 0.1:
                green_count += 1
                total_weight += adaptive_delta

        # Compute detection statistics
        green_ratio = green_count / max(len(tokens), 1)
        expected_ratio = self.green_list_ratio
        z_score = (green_ratio - expected_ratio) / (expected_ratio * 0.1 + 1e-6)

        # Simple threshold-based detection (in production, use proper hypothesis test)
        is_watermarked = z_score > threshold
        confidence = min(max(z_score / 3.0, 0.0), 1.0)  # Normalize to [0, 1]

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
