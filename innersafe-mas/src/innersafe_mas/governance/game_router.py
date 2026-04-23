"""
Game-Theoretic Utility Router for Multi-Agent Governance.

This module implements a Pareto-optimal routing mechanism that balances
privacy protection, copyright enforcement, and response quality in LLM-MAS.

Theoretical Foundation:
    In a multi-agent system, different agents may generate candidate responses
    with varying trade-offs between:
    - Q(π): Response quality (accuracy, relevance, coherence)
    - R_priv: Privacy risk (potential PII leakage)
    - L_copy: Copyright loss (watermark strength, attribution)

    The global utility function is:
        U_total(π) = Q(π) - λ₁ · R_priv(π) - λ₂ · L_copy(π)

    Where:
    - λ₁: Privacy risk tolerance (higher = prioritize quality over privacy)
    - λ₂: Copyright risk tolerance (higher = prioritize quality over attribution)

    The router selects the strategy π* that maximizes U_total:
        π* = argmax_π U_total(π)

    This achieves a Pareto equilibrium where no agent can improve one objective
    without degrading another, given the system's risk tolerance parameters.
"""

from typing import List, Dict, Optional, Tuple


class GameTheoryRouter:
    """
    Game-theoretic router for selecting optimal agent responses.

    This class evaluates candidate responses from multiple agents and selects
    the one that maximizes global utility under privacy and copyright constraints.

    Attributes:
        lambda_1: Privacy risk tolerance weight (typical range: 0.1 - 2.0)
        lambda_2: Copyright risk tolerance weight (typical range: 0.1 - 2.0)
        quality_weight: Weight for response quality normalization
    """

    def __init__(
        self,
        lambda_1: float = 1.0,
        lambda_2: float = 1.0,
        quality_weight: float = 1.0,
    ):
        """
        Initialize the game-theoretic router.

        Args:
            lambda_1: Privacy risk penalty weight
                     - Higher values → prioritize privacy over quality
                     - Lower values → tolerate more privacy risk for better responses
            lambda_2: Copyright risk penalty weight
                     - Higher values → enforce stronger watermarking
                     - Lower values → tolerate weaker attribution for quality
            quality_weight: Scaling factor for quality scores (for normalization)

        Raises:
            ValueError: If weights are negative
        """
        if lambda_1 < 0 or lambda_2 < 0 or quality_weight <= 0:
            raise ValueError("All weights must be non-negative (quality_weight > 0)")

        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.quality_weight = quality_weight

    def evaluate_and_route(
        self, candidates: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Evaluate candidate responses and select the optimal one.

        This method implements the core routing logic:
        1. For each candidate, compute U_total = Q - λ₁·R_priv - λ₂·L_copy
        2. Select candidate with maximum U_total
        3. Return selected candidate with utility breakdown

        Args:
            candidates: List of candidate response dictionaries, each containing:
                - "response": The generated text
                - "quality": Quality score Q(π) in [0, 1]
                - "privacy_risk": Privacy risk R_priv in [0, 1]
                - "copyright_loss": Copyright loss L_copy in [0, 1]
                - "agent_id": Identifier of the generating agent
                - (optional) "metadata": Additional agent-specific metadata

        Returns:
            Dictionary containing:
            - "selected_response": The optimal candidate
            - "utility_scores": Utility scores for all candidates
            - "pareto_frontier": Candidates on the Pareto frontier
            - "decision_rationale": Explanation of the selection

        Raises:
            ValueError: If candidates list is empty or missing required fields
        """
        if not candidates:
            raise ValueError("Candidates list cannot be empty")

        # Validate candidate format
        required_fields = {"response", "quality", "privacy_risk", "copyright_loss"}
        for i, candidate in enumerate(candidates):
            missing = required_fields - set(candidate.keys())
            if missing:
                raise ValueError(
                    f"Candidate {i} missing required fields: {missing}"
                )

        # Step 1: Compute utility for each candidate
        utility_scores = []
        for candidate in candidates:
            utility = self._compute_utility(
                quality=candidate["quality"],
                privacy_risk=candidate["privacy_risk"],
                copyright_loss=candidate["copyright_loss"],
            )
            utility_scores.append({
                "agent_id": candidate.get("agent_id", f"agent_{len(utility_scores)}"),
                "utility": utility,
                "quality": candidate["quality"],
                "privacy_risk": candidate["privacy_risk"],
                "copyright_loss": candidate["copyright_loss"],
            })

        # Step 2: Find optimal candidate (max utility)
        best_idx = max(range(len(utility_scores)), key=lambda i: utility_scores[i]["utility"])
        selected_candidate = candidates[best_idx]

        # Step 3: Identify Pareto frontier
        pareto_frontier = self._compute_pareto_frontier(candidates)

        # Step 4: Generate decision rationale
        rationale = self._generate_rationale(
            selected=utility_scores[best_idx],
            all_scores=utility_scores,
        )

        return {
            "selected_response": selected_candidate,
            "selected_index": best_idx,
            "utility_scores": utility_scores,
            "pareto_frontier": pareto_frontier,
            "decision_rationale": rationale,
        }

    def _compute_utility(
        self, quality: float, privacy_risk: float, copyright_loss: float
    ) -> float:
        """
        Compute global utility using the game-theoretic objective.

        Formula:
            U_total = w_q · Q - λ₁ · R_priv - λ₂ · L_copy

        Args:
            quality: Response quality score [0, 1]
            privacy_risk: Privacy leakage risk [0, 1]
            copyright_loss: Copyright attribution loss [0, 1]

        Returns:
            Total utility score (can be negative if risks dominate)
        """
        quality_term = self.quality_weight * quality
        privacy_penalty = self.lambda_1 * privacy_risk
        copyright_penalty = self.lambda_2 * copyright_loss

        utility = quality_term - privacy_penalty - copyright_penalty
        return utility

    def _compute_pareto_frontier(
        self, candidates: List[Dict[str, any]]
    ) -> List[int]:
        """
        Identify candidates on the Pareto frontier.

        A candidate is Pareto-optimal if no other candidate is strictly better
        in all three objectives (quality, privacy, copyright).

        Args:
            candidates: List of candidate dictionaries

        Returns:
            List of indices of Pareto-optimal candidates
        """
        pareto_indices = []

        for i, candidate_i in enumerate(candidates):
            is_dominated = False

            for j, candidate_j in enumerate(candidates):
                if i == j:
                    continue

                # Check if j dominates i (strictly better in all objectives)
                # Note: For privacy_risk and copyright_loss, lower is better
                better_quality = candidate_j["quality"] >= candidate_i["quality"]
                better_privacy = candidate_j["privacy_risk"] <= candidate_i["privacy_risk"]
                better_copyright = candidate_j["copyright_loss"] <= candidate_i["copyright_loss"]

                # At least one must be strictly better
                strictly_better = (
                    candidate_j["quality"] > candidate_i["quality"]
                    or candidate_j["privacy_risk"] < candidate_i["privacy_risk"]
                    or candidate_j["copyright_loss"] < candidate_i["copyright_loss"]
                )

                if better_quality and better_privacy and better_copyright and strictly_better:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_indices.append(i)

        return pareto_indices

    def _generate_rationale(
        self, selected: Dict[str, any], all_scores: List[Dict[str, any]]
    ) -> str:
        """
        Generate human-readable explanation for the routing decision.

        Args:
            selected: The selected candidate's utility breakdown
            all_scores: Utility scores for all candidates

        Returns:
            Explanation string
        """
        rationale_parts = [
            f"Selected agent '{selected['agent_id']}' with utility {selected['utility']:.3f}",
            f"Quality: {selected['quality']:.3f}",
            f"Privacy risk: {selected['privacy_risk']:.3f} (penalty: {self.lambda_1 * selected['privacy_risk']:.3f})",
            f"Copyright loss: {selected['copyright_loss']:.3f} (penalty: {self.lambda_2 * selected['copyright_loss']:.3f})",
        ]

        # Compare with alternatives
        other_utilities = [s["utility"] for s in all_scores if s["agent_id"] != selected["agent_id"]]
        if other_utilities:
            max_other = max(other_utilities)
            advantage = selected["utility"] - max_other
            rationale_parts.append(f"Utility advantage over next best: {advantage:.3f}")

        return " | ".join(rationale_parts)

    def update_weights(
        self,
        lambda_1: Optional[float] = None,
        lambda_2: Optional[float] = None,
        quality_weight: Optional[float] = None,
    ) -> None:
        """
        Update routing weights dynamically (e.g., based on user feedback).

        This allows adaptive governance where the system learns optimal
        trade-offs over time.

        Args:
            lambda_1: New privacy risk weight (if provided)
            lambda_2: New copyright risk weight (if provided)
            quality_weight: New quality weight (if provided)
        """
        if lambda_1 is not None:
            if lambda_1 < 0:
                raise ValueError("lambda_1 must be non-negative")
            self.lambda_1 = lambda_1

        if lambda_2 is not None:
            if lambda_2 < 0:
                raise ValueError("lambda_2 must be non-negative")
            self.lambda_2 = lambda_2

        if quality_weight is not None:
            if quality_weight <= 0:
                raise ValueError("quality_weight must be positive")
            self.quality_weight = quality_weight

    def get_weights(self) -> Dict[str, float]:
        """
        Get current routing weights.

        Returns:
            Dictionary with current lambda_1, lambda_2, and quality_weight
        """
        return {
            "lambda_1": self.lambda_1,
            "lambda_2": self.lambda_2,
            "quality_weight": self.quality_weight,
        }
