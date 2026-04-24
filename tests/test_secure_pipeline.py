"""Tests for the unified secure inference pipeline."""

from innersafe_mas import (
    AdaptiveKGWWatermark,
    CopyrightAgent,
    GameTheoryRouter,
    MockKnowledgeGraph,
    PrivacyAgent,
    SecureInferencePipeline,
    SecurityContext,
)
from innersafe_mas.privacy import SensitiveSpan


class StubPrivacyAgent(PrivacyAgent):
    def analyze(self, context: SecurityContext) -> SecurityContext:
        context.privacy_entities = [
            SensitiveSpan("PERSON", 2, 4, "张三"),
            SensitiveSpan("ID", 9, 27, "110101199001011234"),
        ]
        return context


def test_router_optimize_strategy_high_privacy_and_high_semantics() -> None:
    router = GameTheoryRouter()
    context = SecurityContext(
        text="患者张三使用 aspirin 治疗",
        privacy_entities=[
            SensitiveSpan("PERSON", 2, 4, "张三"),
            SensitiveSpan("ID", 0, 0, "110101199001011234"),
        ],
        kg_weights={"aspirin": 0.95, "治疗": 0.8},
    )

    router.optimize_strategy(context)

    assert context.final_config["anonymization_level"] == "strong"
    assert context.final_config["watermark_strength"] == "weak"


def test_pipeline_runs_analyze_decide_execute() -> None:
    graph = MockKnowledgeGraph({"aspirin": 0.95, "治疗": 0.8, "患者": 0.2})
    pipeline = SecureInferencePipeline(
        privacy_agent=StubPrivacyAgent(),
        copyright_agent=CopyrightAgent(
            watermark=AdaptiveKGWWatermark(base_delta=2.0, secret_key="demo"),
            graph=graph,
        ),
        router=GameTheoryRouter(),
    )

    context = pipeline.run("患者张三使用 aspirin 治疗，身份证号110101199001011234")

    assert context.final_config["anonymization_level"] == "strong"
    assert context.final_config["watermark_strength"] == "weak"
    assert context.desensitized_text
    assert context.watermarked_text
    assert context.watermark_metadata["base_delta"] == 1.0
    assert "[ANON_" in context.desensitized_text
