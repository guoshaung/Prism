"""Minimal HuggingFace-style generation wrapper for KGW demonstrations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark


class MockGenerationModel:
    """
    Scripted logits provider used to demonstrate decoder-side interception.

    Each generation step returns a token->logit dictionary.
    """

    def __init__(self, logits_sequence: list[dict[str, float]] | None = None) -> None:
        self.logits_sequence = logits_sequence or [
            {"doctor": 0.2, "recommend": 0.3, "aspirin": 0.1},
            {"helps": 0.4, "treats": 0.2, "safe": 0.1},
            {"safe": 0.3, "effective": 0.2, "<eos>": 0.1},
            {"<eos>": 1.0},
        ]

    def next_token_logits(
        self,
        prompt: str,
        generated_tokens: list[str],
    ) -> dict[str, float]:
        step = len(generated_tokens)
        if step >= len(self.logits_sequence):
            return {"<eos>": 1.0}
        return deepcopy(self.logits_sequence[step])


class HuggingFaceWrapper:
    """
    Lightweight wrapper that mimics intercepting logits inside generate().

    The wrapper does not depend on transformers. It only demonstrates the
    research architecture: get logits -> apply KGW bias -> decode next token.
    """

    def __init__(
        self,
        model: MockGenerationModel,
        watermark: AdaptiveKGWWatermark,
        graph: KnowledgeGraphAdapter,
    ) -> None:
        self.model = model
        self.watermark = watermark
        self.graph = graph

    def generate(self, prompt: str, max_new_tokens: int = 8) -> dict[str, Any]:
        generated_tokens: list[str] = []
        trace: list[dict[str, Any]] = []

        for position in range(max_new_tokens):
            raw_logits = self.model.next_token_logits(prompt, generated_tokens)
            biased_logits = {
                token: self.watermark.bias_logit(
                    token=token,
                    logit=logit,
                    graph=self.graph,
                    context=prompt,
                    position=position,
                )
                for token, logit in raw_logits.items()
            }
            next_token = max(biased_logits, key=biased_logits.get)
            trace.append(
                {
                    "position": position,
                    "raw_logits": raw_logits,
                    "biased_logits": biased_logits,
                    "selected_token": next_token,
                }
            )
            if next_token == "<eos>":
                break
            generated_tokens.append(next_token)

        generated_text = " ".join(generated_tokens)
        watermark_result = self.watermark.inject_watermark(
            generated_text,
            self.graph,
            context=prompt,
        )
        return {
            "prompt": prompt,
            "generated_text": generated_text,
            "watermarked_text": watermark_result["watermarked_text"],
            "watermark_metadata": watermark_result["watermark_metadata"],
            "generation_trace": trace,
        }
