"""Unit tests for privacy module."""

from innersafe_mas.privacy import (
    InformationBottleneckPrivacyGate,
    PresidioPrivacyAdapter,
    SensitiveSpan,
)


class StubRecognizer:
    """Deterministic recognizer for SRPG tests."""

    engine_mode = "stub"

    def analyze(self, text: str) -> list[SensitiveSpan]:
        return [
            SensitiveSpan("PERSON", 2, 4, "张三"),
            SensitiveSpan("ID", 14, 32, "110101199001011234"),
        ]


class TestPresidioPrivacyAdapter:
    def test_adapter_exposes_backend_mode(self):
        adapter = PresidioPrivacyAdapter()
        assert adapter.engine_mode in {"presidio", "regex-fallback"}

    def test_regex_fallback_detects_phone(self):
        adapter = PresidioPrivacyAdapter()
        spans = adapter.analyze("请联系13800138000获取结果")
        assert any(span.entity_type == "PHONE_NUMBER" for span in spans)


class TestInformationBottleneckPrivacyGate:
    def test_initialization(self):
        gate = InformationBottleneckPrivacyGate()
        assert gate.placeholder_prefix == "[ANON_"
        assert len(gate.get_anonymization_map()) == 0

    def test_split_streams_uses_recognition_layer(self):
        gate = InformationBottleneckPrivacyGate(recognizer=StubRecognizer())
        text = "患者张三的身份证号是110101199001011234，建议aspirin治疗"
        result = gate.split_streams(text)

        assert "[ANON_PERSON_1]" in result["desensitized_stream"]
        assert "[ANON_ID_2]" in result["desensitized_stream"]
        assert "张三" not in result["desensitized_stream"]
        assert "110101199001011234" not in result["desensitized_stream"]
        assert result["recognizer_backend"] == "stub"
        assert "[ANON_PERSON_1]" in result["logic_stream"]
        assert "aspirin" in result["logic_stream"]

    def test_calculate_loss(self):
        gate = InformationBottleneckPrivacyGate()
        loss, components = gate.calculate_loss(alpha=0.1, beta=1.0, cost=0.5)

        assert isinstance(loss, float)
        assert components["total_loss"] == loss
        assert "privacy_leakage" in components
        assert "utility_gain" in components

    def test_reconstruct(self):
        gate = InformationBottleneckPrivacyGate(recognizer=StubRecognizer())
        original = "患者张三的身份证号是110101199001011234"
        result = gate.split_streams(original)
        reconstructed = gate.reconstruct(result["desensitized_stream"])

        assert "张三" in reconstructed
        assert "110101199001011234" in reconstructed

    def test_anonymization_map_consistency(self):
        gate = InformationBottleneckPrivacyGate()
        first = gate.split_streams("患者张三需要复诊")
        second = gate.split_streams("医生建议张三继续观察")

        assert "[ANON_PERSON_1]" in first["desensitized_stream"]
        assert "[ANON_PERSON_1]" in second["desensitized_stream"]
