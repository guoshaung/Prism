"""
Unit tests for copyright module.
"""

import pytest
from innersafe_mas.copyright import AdaptiveKGWWatermark
from innersafe_mas.copyright.graph_adapter import MockKnowledgeGraph


class TestMockKnowledgeGraph:
    """Test cases for mock knowledge graph."""

    def test_initialization(self):
        """Test graph initialization."""
        graph = MockKnowledgeGraph({"aspirin": 0.9, "headache": 0.5})
        assert graph.get_semantic_centrality("aspirin") == 0.9
        assert graph.get_semantic_centrality("headache") == 0.5

    def test_unknown_word(self):
        """Test handling of unknown words."""
        graph = MockKnowledgeGraph()
        assert graph.get_semantic_centrality("unknown") == 0.0

    def test_add_concept(self):
        """Test adding concepts dynamically."""
        graph = MockKnowledgeGraph()
        graph.add_concept("test", 0.7)
        assert graph.get_semantic_centrality("test") == 0.7

    def test_invalid_centrality(self):
        """Test validation of centrality range."""
        graph = MockKnowledgeGraph()
        with pytest.raises(ValueError):
            graph.add_concept("invalid", 1.5)


class TestAdaptiveKGWWatermark:
    """Test cases for adaptive KGW watermark."""

    def test_initialization(self):
        """Test watermark initialization."""
        watermark = AdaptiveKGWWatermark(base_delta=2.0)
        assert watermark.base_delta == 2.0
        assert 0.0 < watermark.green_list_ratio < 1.0

    def test_inject_watermark(self):
        """Test watermark injection."""
        graph = MockKnowledgeGraph({"阿司匹林": 0.95, "建议": 0.2})
        watermark = AdaptiveKGWWatermark(base_delta=2.0)

        text = "建议服用阿司匹林"
        result = watermark.inject_watermark(text, graph)

        assert "watermarked_text" in result
        assert "watermark_metadata" in result
        assert "token_decisions" in result
        assert len(result["token_decisions"]) == 3

    def test_adaptive_bias_calculation(self):
        """Test that adaptive bias respects centrality."""
        graph = MockKnowledgeGraph({"core": 1.0, "peripheral": 0.0})
        watermark = AdaptiveKGWWatermark(base_delta=2.0)

        result = watermark.inject_watermark("core peripheral", graph)

        # Find decisions for each token
        core_decision = next(d for d in result["token_decisions"] if d["token"] == "core")
        peripheral_decision = next(d for d in result["token_decisions"] if d["token"] == "peripheral")

        # Core concept should have near-zero bias
        assert core_decision["adaptive_delta"] < 0.1
        # Peripheral should have full bias
        assert peripheral_decision["adaptive_delta"] == pytest.approx(2.0, rel=0.01)

    def test_verify_watermark(self):
        """Test watermark verification."""
        graph = MockKnowledgeGraph({"test": 0.5})
        watermark = AdaptiveKGWWatermark(base_delta=2.0, secret_key="test-key")

        text = "test " * 100  # Repeat to get statistical significance
        result = watermark.inject_watermark(text, graph)
        verification = watermark.verify_watermark(result["watermarked_text"], graph)

        assert "is_watermarked" in verification
        assert "confidence" in verification
        assert "statistics" in verification

    def test_invalid_green_list_ratio(self):
        """Test validation of green list ratio."""
        with pytest.raises(ValueError):
            AdaptiveKGWWatermark(green_list_ratio=1.5)
