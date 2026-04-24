"""Tests for the minimal copyright attack-defense-detection loop."""

from innersafe_mas.copyright import (
    HuggingFaceWrapper,
    MockCopyrightPolicy,
    MockForensicRecorder,
    MockGenerationModel,
    MockKeyManager,
    MockKnowledgeGraph,
    ParaphraseAttack,
    TruncationAttack,
    WordDeletionAttack,
    AdaptiveKGWWatermark,
    run_generation_attack_loop,
    run_robustness_suite,
)


def test_huggingface_wrapper_intercepts_logits() -> None:
    graph = MockKnowledgeGraph(
        {
            "doctor": 0.9,
            "recommend": 0.1,
            "helps": 0.3,
            "safe": 0.1,
        }
    )
    watermark = AdaptiveKGWWatermark(base_delta=3.0, secret_key="demo")
    model = MockGenerationModel(
        logits_sequence=[
            {"doctor": 0.6, "recommend": 0.25},
            {"helps": 0.3, "safe": 0.28},
            {"<eos>": 1.0},
        ]
    )
    wrapper = HuggingFaceWrapper(model=model, watermark=watermark, graph=graph)

    result = wrapper.generate("medical prompt", max_new_tokens=3)

    assert result["generated_text"] == "recommend safe"
    assert len(result["generation_trace"]) == 3
    assert result["generation_trace"][0]["biased_logits"]["recommend"] > 0.25
    assert result["generation_trace"][0]["biased_logits"]["doctor"] == 0.6


def test_robustness_suite_reports_retention() -> None:
    graph = MockKnowledgeGraph({"recommend": 0.1, "safe": 0.1, "doctor": 0.9})
    watermark = AdaptiveKGWWatermark(base_delta=3.0, secret_key="kgw-demo")
    injected = watermark.inject_watermark("recommend safe recommend", graph, context="prompt")

    report = run_robustness_suite(
        protected_text=injected["watermarked_text"],
        watermark=watermark,
        graph=graph,
        attacks=[ParaphraseAttack(), TruncationAttack(keep_ratio=0.8), WordDeletionAttack(2)],
        context="prompt",
    )

    assert "baseline" in report
    assert "attack_results" in report
    assert len(report["attack_results"]) == 3
    assert 0.0 <= report["retention_rate"] <= 1.0


def test_generation_attack_loop_and_mock_placeholders() -> None:
    graph = MockKnowledgeGraph({"recommend": 0.1, "safe": 0.1, "doctor": 0.8})
    watermark = AdaptiveKGWWatermark(base_delta=2.5, secret_key="kgw-demo")
    wrapper = HuggingFaceWrapper(MockGenerationModel(), watermark, graph)

    loop = run_generation_attack_loop("clinical prompt", wrapper, max_new_tokens=4)

    key_manager = MockKeyManager()
    policy = MockCopyrightPolicy(base_delta=2.0)
    recorder = MockForensicRecorder()
    event = recorder.record(
        "evaluation_finished",
        {
            "retention_rate": loop["robustness"]["retention_rate"],
            "issued_key": key_manager.issue_key("demo"),
            "resolved_delta": policy.resolve_delta("strict"),
        },
    )

    assert "generation" in loop
    assert "robustness" in loop
    assert event["payload"]["resolved_delta"] > 2.0
    assert len(recorder.events) == 1
