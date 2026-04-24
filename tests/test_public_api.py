"""Tests for the public SDK-style API."""

from innersafe_mas import MockGenerationModel, MockLLMClient, SecureService


def test_secure_service_preview_watermark() -> None:
    service = SecureService()
    service.build_mock_graph({"aspirin": 0.9, "doctor": 0.2})

    preview = service.preview_watermark("doctor recommend aspirin", context="medical")

    assert preview["before_text"] == "doctor recommend aspirin"
    assert "after_text" in preview
    assert "watermark_metadata" in preview
    assert "token_decisions" in preview


def test_secure_service_protect_generated_text() -> None:
    service = SecureService()
    client = MockLLMClient("patient ZhangSan needs aspirin")

    result = service.protect_generated_text("medical prompt", client)

    assert result.final_config
    assert result.text
    assert result.original_text == "patient ZhangSan needs aspirin"
    assert result.final_config["source_prompt"] == "medical prompt"


def test_secure_service_generate_with_huggingface() -> None:
    service = SecureService()
    service.build_mock_graph({"recommend": 0.1, "safe": 0.1})
    result = service.generate_with_huggingface(
        "prompt",
        model=MockGenerationModel(
            logits_sequence=[
                {"recommend": 0.2, "doctor": 0.1},
                {"safe": 0.3, "<eos>": 0.1},
                {"<eos>": 1.0},
            ]
        ),
    )

    assert result["generated_text"]
    assert result["watermarked_text"]
    assert result["generation_trace"]
