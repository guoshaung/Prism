"""High-level public API for using innersafe-mas from other projects."""

from __future__ import annotations

from typing import Any

from innersafe_mas.copyright import (
    HuggingFaceWrapper,
    KnowledgeGraphAdapter,
    MockGenerationModel,
    MockKnowledgeGraph,
)
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark
from innersafe_mas.governance import GameTheoryRouter
from innersafe_mas.llm import BaseLLMClient
from innersafe_mas.pipeline import (
    CopyrightAgent,
    PrivacyAgent,
    SecureInferencePipeline,
    SecurityContext,
)
from innersafe_mas.privacy import InformationBottleneckPrivacyGate


class SecureService:
    """
    SDK-style facade for external projects.

    This class exposes a stable set of methods for:
    - secure text protection
    - watermark preview
    - knowledge-graph configuration
    - HuggingFace-style model interception
    - generic LLM output protection
    """

    def __init__(
        self,
        privacy_gate: InformationBottleneckPrivacyGate | None = None,
        watermark: AdaptiveKGWWatermark | None = None,
        graph: KnowledgeGraphAdapter | None = None,
        router: GameTheoryRouter | None = None,
    ) -> None:
        self.privacy_gate = privacy_gate or InformationBottleneckPrivacyGate()
        self.watermark = watermark or AdaptiveKGWWatermark()
        self.graph = graph or MockKnowledgeGraph()
        self.router = router or GameTheoryRouter()
        self.pipeline = SecureInferencePipeline(
            privacy_agent=PrivacyAgent(self.privacy_gate),
            copyright_agent=CopyrightAgent(self.watermark, self.graph),
            router=self.router,
        )

    def set_graph(self, graph: KnowledgeGraphAdapter) -> None:
        """Replace the current knowledge graph backend."""
        self.graph = graph
        self.pipeline.copyright_agent.graph = graph

    def build_mock_graph(self, centrality_map: dict[str, float]) -> MockKnowledgeGraph:
        """Convenience helper for quickly building a toy knowledge graph."""
        graph = MockKnowledgeGraph(centrality_map)
        self.set_graph(graph)
        return graph

    def protect_text(self, text: str) -> SecurityContext:
        """Run the full privacy -> governance -> watermark pipeline."""
        return self.pipeline.run(text)

    def preview_watermark(
        self,
        text: str,
        context: str = "",
    ) -> dict[str, Any]:
        """
        Return a before/after watermark preview for UI display.
        """
        result = self.watermark.inject_watermark(text, self.graph, context=context)
        return {
            "before_text": text,
            "after_text": result["watermarked_text"],
            "watermark_metadata": result["watermark_metadata"],
            "token_decisions": result["token_decisions"],
        }

    def protect_generated_text(
        self,
        prompt: str,
        client: BaseLLMClient,
        **kwargs: object,
    ) -> SecurityContext:
        """
        Call any external LLM client, then run the secure pipeline on its output.
        """
        generated_text = client.generate(prompt, **kwargs)
        context = self.protect_text(generated_text)
        context.final_config["source_prompt"] = prompt
        return context

    def generate_with_huggingface(
        self,
        prompt: str,
        model: MockGenerationModel | None = None,
        max_new_tokens: int = 8,
    ) -> dict[str, Any]:
        """
        Demonstrate decoder-side KGW interception with a HuggingFace-style wrapper.
        """
        wrapper = HuggingFaceWrapper(
            model=model or MockGenerationModel(),
            watermark=self.watermark,
            graph=self.graph,
        )
        return wrapper.generate(prompt, max_new_tokens=max_new_tokens)
