"""
Knowledge Graph Adapter for Semantic Centrality Computation.

This module provides an abstract interface for integrating domain-specific
knowledge graphs into the KGW (Knowledge Graph Watermark) framework.

Theoretical Foundation:
    The semantic centrality S(i) of a word/concept i in a knowledge graph
    measures its importance to the domain. Common metrics include:
    - Degree centrality: S(i) = degree(i) / max_degree
    - PageRank centrality: S(i) = PR(i) / max_PR
    - Betweenness centrality: S(i) = betweenness(i) / max_betweenness

    Words with high centrality (S(i) → 1) are core domain concepts that
    should NOT be distorted by watermarking. The adaptive watermark formula:
        δ_dynamic(i) = δ_base × (1 - S(i))
    ensures zero watermark bias when S(i) = 1.
"""

from abc import ABC, abstractmethod
from typing import Optional


class KnowledgeGraphAdapter(ABC):
    """
    Abstract base class for knowledge graph adapters.

    Subclasses must implement `get_semantic_centrality` to provide
    domain-specific centrality scores for words/concepts.

    This design allows innersafe-mas to integrate with various graph backends:
    - NetworkX (for small in-memory graphs)
    - Neo4j (for large-scale production graphs)
    - Custom domain ontologies (medical, legal, financial, etc.)
    """

    @abstractmethod
    def get_semantic_centrality(self, word: str) -> float:
        """
        Compute the semantic centrality of a word in the knowledge graph.

        Args:
            word: The word/concept to query (case-insensitive recommended).

        Returns:
            Centrality score in range [0.0, 1.0]:
            - 0.0: Word not in graph or peripheral concept
            - 1.0: Core domain concept (e.g., "aspirin" in medical graph)

        Implementation Notes:
            - Should handle unknown words gracefully (return 0.0)
            - May cache results for performance
            - Consider normalizing by domain-specific max centrality
        """
        pass

    def batch_get_centrality(self, words: list[str]) -> dict[str, float]:
        """
        Batch query for centrality scores (optional optimization).

        Default implementation calls get_semantic_centrality sequentially.
        Subclasses can override for efficient batch processing.

        Args:
            words: List of words to query.

        Returns:
            Dictionary mapping words to centrality scores.
        """
        return {word: self.get_semantic_centrality(word) for word in words}


class MockKnowledgeGraph(KnowledgeGraphAdapter):
    """
    Mock knowledge graph for testing and demonstration.

    This implementation uses a simple dictionary to store predefined
    centrality scores. Useful for unit tests and examples.
    """

    def __init__(self, centrality_map: Optional[dict[str, float]] = None):
        """
        Initialize mock graph with predefined centrality scores.

        Args:
            centrality_map: Dictionary mapping words to centrality scores.
                           If None, uses an empty graph.
        """
        self.centrality_map = centrality_map or {}

    def get_semantic_centrality(self, word: str) -> float:
        """Return predefined centrality or 0.0 for unknown words."""
        return self.centrality_map.get(word.lower(), 0.0)

    def add_concept(self, word: str, centrality: float) -> None:
        """
        Add or update a concept in the mock graph.

        Args:
            word: The word/concept.
            centrality: Centrality score in [0.0, 1.0].
        """
        if not 0.0 <= centrality <= 1.0:
            raise ValueError(f"Centrality must be in [0.0, 1.0], got {centrality}")
        self.centrality_map[word.lower()] = centrality
