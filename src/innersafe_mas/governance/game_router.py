"""Governance router for strategy optimization in the secure pipeline."""

from __future__ import annotations

from typing import Any, Optional


class GameTheoryRouter:
    """
    Lightweight governance router.

    It still supports candidate scoring, but now also exposes
    `optimize_strategy(context)` for the unified secure inference pipeline.
    """

    def __init__(
        self,
        lambda_1: float = 1.0,
        lambda_2: float = 1.0,
        quality_weight: float = 1.0,
        privacy_threshold: float = 0.3,
        semantic_threshold: float = 0.7,
    ) -> None:
        if lambda_1 < 0 or lambda_2 < 0 or quality_weight <= 0:
            raise ValueError("All weights must be non-negative (quality_weight > 0)")

        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.quality_weight = quality_weight
        self.privacy_threshold = privacy_threshold
        self.semantic_threshold = semantic_threshold

    def optimize_strategy(self, context: Any) -> Any:
        """
        Update context.final_config using simple weighted governance rules.

        Rules:
        - If privacy risk is high, force strong anonymization.
        - If semantic importance is high, force weak watermarking to preserve utility.
        - Otherwise, choose the stronger-scoring option from weighted signals.
        """
        privacy_risk = self._estimate_privacy_risk(context)
        semantic_importance = self._estimate_semantic_importance(context)

        final_config = dict(context.final_config)
        final_config["privacy_risk"] = privacy_risk
        final_config["semantic_importance"] = semantic_importance

        if privacy_risk >= self.privacy_threshold:
            anonymization_level = "strong"
        elif privacy_risk > 0:
            anonymization_level = "standard"
        else:
            anonymization_level = "none"

        if semantic_importance >= self.semantic_threshold:
            watermark_strength = "weak"
        else:
            privacy_score = self.lambda_1 * privacy_risk
            copyright_score = self.lambda_2 * (1.0 - semantic_importance)
            watermark_strength = "strong" if copyright_score >= privacy_score else "medium"

        final_config["anonymization_level"] = anonymization_level
        final_config["watermark_strength"] = watermark_strength
        context.final_config = final_config
        return context

    def evaluate_and_route(
        self, candidates: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not candidates:
            raise ValueError("Candidates list cannot be empty")

        required_fields = {"response", "quality", "privacy_risk", "copyright_loss"}
        for index, candidate in enumerate(candidates):
            missing = required_fields - set(candidate.keys())
            if missing:
                raise ValueError(f"Candidate {index} missing required fields: {missing}")

        utility_scores = []
        for candidate in candidates:
            utility = self._compute_utility(
                quality=candidate["quality"],
                privacy_risk=candidate["privacy_risk"],
                copyright_loss=candidate["copyright_loss"],
            )
            utility_scores.append(
                {
                    "agent_id": candidate.get("agent_id", f"agent_{len(utility_scores)}"),
                    "utility": utility,
                    "quality": candidate["quality"],
                    "privacy_risk": candidate["privacy_risk"],
                    "copyright_loss": candidate["copyright_loss"],
                }
            )

        best_idx = max(range(len(utility_scores)), key=lambda i: utility_scores[i]["utility"])
        selected_candidate = candidates[best_idx]
        pareto_frontier = self._compute_pareto_frontier(candidates)
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
        self,
        quality: float,
        privacy_risk: float,
        copyright_loss: float,
    ) -> float:
        quality_term = self.quality_weight * quality
        privacy_penalty = self.lambda_1 * privacy_risk
        copyright_penalty = self.lambda_2 * copyright_loss
        return quality_term - privacy_penalty - copyright_penalty

    def _compute_pareto_frontier(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[int]:
        pareto_indices = []
        for i, candidate_i in enumerate(candidates):
            is_dominated = False
            for j, candidate_j in enumerate(candidates):
                if i == j:
                    continue

                better_quality = candidate_j["quality"] >= candidate_i["quality"]
                better_privacy = candidate_j["privacy_risk"] <= candidate_i["privacy_risk"]
                better_copyright = (
                    candidate_j["copyright_loss"] <= candidate_i["copyright_loss"]
                )
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
        self,
        selected: dict[str, Any],
        all_scores: list[dict[str, Any]],
    ) -> str:
        rationale_parts = [
            f"Selected agent '{selected['agent_id']}' with utility {selected['utility']:.3f}",
            f"Quality: {selected['quality']:.3f}",
            (
                f"Privacy risk: {selected['privacy_risk']:.3f} "
                f"(penalty: {self.lambda_1 * selected['privacy_risk']:.3f})"
            ),
            (
                f"Copyright loss: {selected['copyright_loss']:.3f} "
                f"(penalty: {self.lambda_2 * selected['copyright_loss']:.3f})"
            ),
        ]
        other_utilities = [
            score["utility"]
            for score in all_scores
            if score["agent_id"] != selected["agent_id"]
        ]
        if other_utilities:
            rationale_parts.append(
                f"Utility advantage over next best: {selected['utility'] - max(other_utilities):.3f}"
            )
        return " | ".join(rationale_parts)

    def _estimate_privacy_risk(self, context: Any) -> float:
        entity_count = len(getattr(context, "privacy_entities", []))
        if entity_count == 0:
            return 0.0
        return min(entity_count / 3.0, 1.0)

    def _estimate_semantic_importance(self, context: Any) -> float:
        weights = getattr(context, "kg_weights", {})
        if not weights:
            return 0.0
        return max(weights.values())

    def update_weights(
        self,
        lambda_1: Optional[float] = None,
        lambda_2: Optional[float] = None,
        quality_weight: Optional[float] = None,
    ) -> None:
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

    def get_weights(self) -> dict[str, float]:
        return {
            "lambda_1": self.lambda_1,
            "lambda_2": self.lambda_2,
            "quality_weight": self.quality_weight,
        }
