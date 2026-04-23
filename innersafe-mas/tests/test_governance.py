"""
Unit tests for governance module.
"""

import pytest
from innersafe_mas.governance import GameTheoryRouter


class TestGameTheoryRouter:
    """Test cases for game-theoretic router."""

    def test_initialization(self):
        """Test router initialization."""
        router = GameTheoryRouter(lambda_1=1.0, lambda_2=0.5)
        assert router.lambda_1 == 1.0
        assert router.lambda_2 == 0.5

    def test_invalid_weights(self):
        """Test validation of weight parameters."""
        with pytest.raises(ValueError):
            GameTheoryRouter(lambda_1=-1.0)

    def test_evaluate_and_route_basic(self):
        """Test basic routing with valid candidates."""
        router = GameTheoryRouter(lambda_1=1.0, lambda_2=1.0)

        candidates = [
            {
                "agent_id": "agent_1",
                "response": "Response 1",
                "quality": 0.8,
                "privacy_risk": 0.2,
                "copyright_loss": 0.1,
            },
            {
                "agent_id": "agent_2",
                "response": "Response 2",
                "quality": 0.9,
                "privacy_risk": 0.5,
                "copyright_loss": 0.3,
            },
        ]

        result = router.evaluate_and_route(candidates)

        assert "selected_response" in result
        assert "utility_scores" in result
        assert "pareto_frontier" in result
        assert len(result["utility_scores"]) == 2

    def test_utility_calculation(self):
        """Test utility calculation formula."""
        router = GameTheoryRouter(lambda_1=1.0, lambda_2=1.0, quality_weight=1.0)

        # U = Q - λ₁·R_priv - λ₂·L_copy
        # U = 0.8 - 1.0*0.2 - 1.0*0.1 = 0.5
        utility = router._compute_utility(
            quality=0.8,
            privacy_risk=0.2,
            copyright_loss=0.1,
        )

        assert utility == pytest.approx(0.5, rel=0.01)

    def test_pareto_frontier(self):
        """Test Pareto frontier identification."""
        router = GameTheoryRouter()

        candidates = [
            {
                "agent_id": "dominated",
                "response": "Dominated",
                "quality": 0.5,
                "privacy_risk": 0.8,
                "copyright_loss": 0.8,
            },
            {
                "agent_id": "pareto_optimal_1",
                "response": "Optimal 1",
                "quality": 0.9,
                "privacy_risk": 0.2,
                "copyright_loss": 0.3,
            },
            {
                "agent_id": "pareto_optimal_2",
                "response": "Optimal 2",
                "quality": 0.7,
                "privacy_risk": 0.1,
                "copyright_loss": 0.1,
            },
        ]

        result = router.evaluate_and_route(candidates)
        pareto_indices = result["pareto_frontier"]

        # First candidate should be dominated
        assert 0 not in pareto_indices
        # Other two should be on frontier
        assert len(pareto_indices) >= 1

    def test_empty_candidates(self):
        """Test handling of empty candidate list."""
        router = GameTheoryRouter()
        with pytest.raises(ValueError):
            router.evaluate_and_route([])

    def test_missing_fields(self):
        """Test validation of candidate format."""
        router = GameTheoryRouter()
        invalid_candidates = [
            {
                "agent_id": "incomplete",
                "response": "Missing fields",
                "quality": 0.8,
                # Missing privacy_risk and copyright_loss
            }
        ]

        with pytest.raises(ValueError):
            router.evaluate_and_route(invalid_candidates)

    def test_update_weights(self):
        """Test dynamic weight updates."""
        router = GameTheoryRouter(lambda_1=1.0, lambda_2=1.0)

        router.update_weights(lambda_1=2.0, lambda_2=0.5)
        weights = router.get_weights()

        assert weights["lambda_1"] == 2.0
        assert weights["lambda_2"] == 0.5

    def test_privacy_prioritization(self):
        """Test that higher lambda_1 prioritizes privacy."""
        candidates = [
            {
                "agent_id": "high_quality_risky",
                "response": "High quality but risky",
                "quality": 0.95,
                "privacy_risk": 0.8,
                "copyright_loss": 0.1,
            },
            {
                "agent_id": "lower_quality_safe",
                "response": "Lower quality but safe",
                "quality": 0.75,
                "privacy_risk": 0.1,
                "copyright_loss": 0.1,
            },
        ]

        # Low privacy penalty - should prefer high quality
        router_low = GameTheoryRouter(lambda_1=0.1, lambda_2=1.0)
        result_low = router_low.evaluate_and_route(candidates)
        assert result_low["selected_response"]["agent_id"] == "high_quality_risky"

        # High privacy penalty - should prefer safe option
        router_high = GameTheoryRouter(lambda_1=5.0, lambda_2=1.0)
        result_high = router_high.evaluate_and_route(candidates)
        assert result_high["selected_response"]["agent_id"] == "lower_quality_safe"
