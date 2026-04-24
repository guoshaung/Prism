"""Unified secure inference pipeline for the research prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter, MockKnowledgeGraph
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark
from innersafe_mas.privacy import InformationBottleneckPrivacyGate, SensitiveSpan


@dataclass
class SecurityContext:
    """
    Shared state passed across privacy, copyright, and governance modules.
    """

    text: str
    privacy_entities: list[SensitiveSpan] = field(default_factory=list)
    kg_weights: dict[str, float] = field(default_factory=dict)
    final_config: dict[str, Any] = field(default_factory=dict)
    original_text: str = ""
    logic_stream: str = ""
    desensitized_text: str = ""
    watermarked_text: str = ""
    watermark_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.original_text:
            self.original_text = self.text


class PrivacyAgent:
    """
    Privacy execution agent driven by a SecurityContext.
    """

    def __init__(self, gate: InformationBottleneckPrivacyGate | None = None) -> None:
        self.gate = gate or InformationBottleneckPrivacyGate()

    def analyze(self, context: SecurityContext) -> SecurityContext:
        context.privacy_entities = self.gate.recognizer.analyze(context.text)
        return context

    def execute(self, context: SecurityContext) -> SecurityContext:
        mode = context.final_config.get("anonymization_level", "standard")
        if mode == "none":
            context.desensitized_text = context.text
            context.logic_stream = context.text
            return context

        if context.privacy_entities:
            desensitized = context.text
            for span in context.privacy_entities:
                placeholder = self.gate._placeholder_for(span.text, span.entity_type)
                desensitized = desensitized.replace(span.text, placeholder)
            context.desensitized_text = desensitized
            context.logic_stream = self.gate._extract_logic_tokens(desensitized)
        else:
            split = self.gate.split_streams(context.text)
            context.desensitized_text = split["desensitized_stream"]
            context.logic_stream = split["logic_stream"]

        context.text = context.desensitized_text

        # A "strong" mode can append a coarse indicator for downstream agents.
        if mode == "strong":
            context.logic_stream = f"{context.logic_stream} [STRICT_PRIVACY]".strip()

        return context


class CopyrightAgent:
    """
    Copyright execution agent driven by a SecurityContext.
    """

    def __init__(
        self,
        watermark: AdaptiveKGWWatermark | None = None,
        graph: KnowledgeGraphAdapter | None = None,
    ) -> None:
        self.watermark = watermark or AdaptiveKGWWatermark()
        self.graph = graph or MockKnowledgeGraph()

    def analyze(self, context: SecurityContext) -> SecurityContext:
        tokens = self.watermark._tokenize(context.text, self.graph)
        context.kg_weights = {
            token: self.graph.get_semantic_centrality(token)
            for token in tokens
        }
        return context

    def execute(self, context: SecurityContext) -> SecurityContext:
        strength = context.final_config.get("watermark_strength", "medium")
        scale = {
            "weak": 0.5,
            "medium": 1.0,
            "strong": 1.5,
        }.get(strength, 1.0)

        tuned_watermark = AdaptiveKGWWatermark(
            base_delta=self.watermark.base_delta * scale,
            secret_key=self.watermark.secret_key,
            green_list_ratio=self.watermark.green_list_ratio,
        )
        result = tuned_watermark.inject_watermark(
            context.text,
            self.graph,
            context.logic_stream or context.original_text,
        )
        context.watermarked_text = result["watermarked_text"]
        context.watermark_metadata = result["watermark_metadata"]
        context.text = context.watermarked_text
        return context


class SecureInferencePipeline:
    """
    Main orchestration flow:
    context -> analyze -> optimize -> execute -> output
    """

    def __init__(
        self,
        privacy_agent: PrivacyAgent,
        copyright_agent: CopyrightAgent,
        router: Any,
    ) -> None:
        self.privacy_agent = privacy_agent
        self.copyright_agent = copyright_agent
        self.router = router

    def run(self, text: str) -> SecurityContext:
        context = SecurityContext(text=text)
        self.privacy_agent.analyze(context)
        self.copyright_agent.analyze(context)
        self.router.optimize_strategy(context)
        self.privacy_agent.execute(context)
        self.copyright_agent.execute(context)
        return context
