"""Robustness evaluation helpers for the KGW research prototype."""

from __future__ import annotations

from typing import Any

from innersafe_mas.copyright.attacks import (
    ParaphraseAttack,
    TruncationAttack,
    WordDeletionAttack,
)
from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter
from innersafe_mas.copyright.integrations.huggingface_wrapper import HuggingFaceWrapper
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark


def run_robustness_suite(
    protected_text: str,
    watermark: AdaptiveKGWWatermark,
    graph: KnowledgeGraphAdapter,
    attacks: list | None = None,
    context: str | None = None,
) -> dict[str, Any]:
    """Apply attacks and measure watermark retention."""
    attacks = attacks or [
        ParaphraseAttack(),
        TruncationAttack(),
        WordDeletionAttack(),
    ]

    baseline = watermark.verify_watermark(protected_text, graph, context=context)
    attack_results = []
    retained_count = 0

    for attack in attacks:
        attacked_text = attack.apply(protected_text)
        verification = watermark.verify_watermark(attacked_text, graph, context=context)
        retained_count += int(verification["is_watermarked"])
        attack_results.append(
            {
                "attack": attack.name,
                "attacked_text": attacked_text,
                "verification": verification,
            }
        )

    retention_rate = retained_count / max(len(attack_results), 1)
    return {
        "baseline": baseline,
        "attack_results": attack_results,
        "retention_rate": retention_rate,
    }


def run_generation_attack_loop(
    prompt: str,
    wrapper: HuggingFaceWrapper,
    attacks: list | None = None,
    max_new_tokens: int = 8,
) -> dict[str, Any]:
    """
    End-to-end loop: generate -> attack -> detect.
    """
    generation = wrapper.generate(prompt, max_new_tokens=max_new_tokens)
    robustness = run_robustness_suite(
        protected_text=generation["watermarked_text"],
        watermark=wrapper.watermark,
        graph=wrapper.graph,
        attacks=attacks,
        context=prompt,
    )
    return {
        "generation": generation,
        "robustness": robustness,
    }
