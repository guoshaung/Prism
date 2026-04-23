"""
Unit tests for privacy module.
"""

import pytest
from innersafe_mas.privacy import InformationBottleneckPrivacyGate


class TestInformationBottleneckPrivacyGate:
    """Test cases for SRPG privacy gate."""

    def test_initialization(self):
        """Test gate initialization."""
        gate = InformationBottleneckPrivacyGate()
        assert gate.placeholder_prefix == "[ANON_"
        assert len(gate._anonymization_map) == 0

    def test_split_streams_with_chinese_name(self):
        """Test PII detection for Chinese names."""
        gate = InformationBottleneckPrivacyGate()
        text = "患者张三服用阿司匹林"
        result = gate.split_streams(text)

        assert "[ANON_NAME_1]" in result["desensitized_stream"]
        assert "张三" not in result["desensitized_stream"]
        assert len(result["detected_entities"]) == 1

    def test_split_streams_with_id_number(self):
        """Test PII detection for ID numbers."""
        gate = InformationBottleneckPrivacyGate()
        text = "身份证号110101199001011234"
        result = gate.split_streams(text)

        assert "[ANON_ID_" in result["desensitized_stream"]
        assert "110101199001011234" not in result["desensitized_stream"]

    def test_calculate_loss(self):
        """Test information bottleneck loss calculation."""
        gate = InformationBottleneckPrivacyGate()
        loss, components = gate.calculate_loss(alpha=0.1, beta=1.0, cost=0.5)

        assert isinstance(loss, float)
        assert "privacy_leakage" in components
        assert "utility_gain" in components
        assert "regularization" in components
        assert components["total_loss"] == loss

    def test_reconstruct(self):
        """Test reconstruction of original text."""
        gate = InformationBottleneckPrivacyGate()
        original = "患者张三服用药物"
        result = gate.split_streams(original)
        reconstructed = gate.reconstruct(result["desensitized_stream"])

        assert "张三" in reconstructed

    def test_anonymization_map_consistency(self):
        """Test that same PII gets same placeholder."""
        gate = InformationBottleneckPrivacyGate()
        text1 = "患者张三"
        text2 = "医生建议张三"

        result1 = gate.split_streams(text1)
        result2 = gate.split_streams(text2)

        # Same name should get same placeholder
        placeholder1 = result1["desensitized_stream"].split()[0].split("患者")[1]
        placeholder2 = result2["desensitized_stream"].split("张三")[0].split("建议")[1]
        assert placeholder1 == placeholder2
