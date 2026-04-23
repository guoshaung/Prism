"""
SRPG Information Bottleneck Privacy Gate.

This module implements the Variational Information Bottleneck (VIB) approach
for privacy-preserving data stream splitting in LLM Multi-Agent Systems.

Theoretical Foundation:
    Based on the Information Bottleneck principle, we aim to:
    - Minimize mutual information between input X and sensitive latent Z_sensitive:
      I(X; Z_sensitive) → min
    - Maximize mutual information between logic latent Z_logic and output Y:
      I(Z_logic; Y) → max

    The optimization objective is:
        L = I(X; Z_sensitive) - β * I(Z_logic; Y) + α * KL(q(Z|X) || p(Z))

    Where:
    - α: Regularization weight for KL divergence (prevents overfitting)
    - β: Trade-off parameter (higher β = prioritize utility over privacy)
    - cost: Computational cost penalty for complex transformations
"""

import re
from typing import Dict, Tuple


class InformationBottleneckPrivacyGate:
    """
    Privacy gate that splits input text into desensitized and logic streams.

    This class implements a simplified version of the SRPG (Stream Reconstruction
    Privacy Gate) mechanism. In production, this would involve neural encoders
    and variational inference. Here we use rule-based heuristics for demonstration.

    Attributes:
        sensitive_patterns: Regex patterns for detecting PII (names, IDs, etc.)
        placeholder_prefix: Prefix for anonymized tokens
    """

    def __init__(self, placeholder_prefix: str = "[ANON_"):
        """
        Initialize the privacy gate.

        Args:
            placeholder_prefix: Prefix for anonymized sensitive tokens.
        """
        self.placeholder_prefix = placeholder_prefix
        self.sensitive_patterns = {
            # Chinese names (2-4 chars) in common clinical phrasing.
            # Keep this heuristic broad enough to catch names at sentence end,
            # e.g. "医生建议张三".
            "name": r"(?:(?<=患者)|(?<=医生建议)|(?<=建议))[\u4e00-\u9fa5]{2,4}(?=服用|的|$)",
            "id": r"\d{15,18}",  # ID numbers
            "phone": r"1[3-9]\d{9}",  # Phone numbers
            "email": r"[\w\.-]+@[\w\.-]+\.\w+",  # Email addresses
        }
        self._anonymization_map: Dict[str, str] = {}
        self._counter = 0

    def split_streams(self, text: str) -> Dict[str, str]:
        """
        Split input text into desensitized and logic streams.

        This method implements the core I(X; Z_sensitive) minimization by:
        1. Detecting sensitive entities using pattern matching
        2. Replacing them with anonymized placeholders in desensitized_stream
        3. Preserving logical structure (medical terms, actions) in logic_stream

        Mathematical Intuition:
            desensitized_stream ≈ Z_logic (low mutual info with sensitive data)
            logic_stream ≈ projection that maximizes I(Z_logic; Y)

        Args:
            text: Raw input text containing potential PII.

        Returns:
            Dictionary with two keys:
            - "desensitized_stream": Text with PII replaced by placeholders
            - "logic_stream": Extracted logical/semantic content
        """
        desensitized = text
        detected_entities = []

        # Step 1: Detect and anonymize sensitive patterns
        for entity_type, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(0)
                if original not in self._anonymization_map:
                    self._counter += 1
                    placeholder = f"{self.placeholder_prefix}{entity_type.upper()}_{self._counter}]"
                    self._anonymization_map[original] = placeholder
                else:
                    placeholder = self._anonymization_map[original]

                desensitized = desensitized.replace(original, placeholder)
                detected_entities.append((entity_type, original, placeholder))

        # Step 2: Extract logic stream (preserve domain-specific terms)
        # In a real implementation, this would use NER or domain ontology
        logic_stream = self._extract_logic_tokens(desensitized)

        return {
            "desensitized_stream": desensitized,
            "logic_stream": logic_stream,
            "detected_entities": detected_entities,
        }

    def _extract_logic_tokens(self, text: str) -> str:
        """
        Extract logical/semantic tokens while filtering out noise.

        This simulates the I(Z_logic; Y) maximization by keeping only
        tokens that contribute to downstream task performance.

        Args:
            text: Desensitized text.

        Returns:
            Space-separated logical tokens.
        """
        # Mock implementation: keep medical terms, actions, symptoms
        # In production, use domain-specific NER or knowledge graph
        medical_keywords = [
            "服用", "阿司匹林", "头痛", "症状", "诊断", "治疗",
            "药物", "剂量", "副作用", "过敏", "检查", "报告"
        ]

        tokens = []
        for keyword in medical_keywords:
            if keyword in text:
                tokens.append(keyword)

        # Also preserve anonymized placeholders (they carry structural info)
        placeholders = re.findall(r"\[ANON_[A-Z_0-9]+\]", text)
        tokens.extend(placeholders)

        return " ".join(tokens)

    def calculate_loss(
        self, alpha: float, beta: float, cost: float
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate the Information Bottleneck loss function.

        This method computes the theoretical loss for the VIB objective:
            L = I(X; Z_sensitive) - β * I(Z_logic; Y) + α * KL(q||p) + cost

        In a real neural implementation, these terms would be estimated via:
        - I(X; Z_sensitive): Estimated using variational bounds
        - I(Z_logic; Y): Approximated via task-specific loss (e.g., cross-entropy)
        - KL divergence: Computed between learned posterior q(Z|X) and prior p(Z)

        Here we provide a mock calculation for demonstration.

        Args:
            alpha: Weight for KL regularization term (typical range: 0.01 - 0.1)
            beta: Trade-off between privacy and utility (typical range: 0.1 - 10)
                  Higher β → prioritize utility over privacy
            cost: Computational cost penalty (e.g., inference latency)

        Returns:
            Tuple of (total_loss, loss_components_dict)
        """
        # Mock values (in production, these would be computed from data)
        i_x_z_sensitive = 2.5  # Mutual info with sensitive data (lower is better)
        i_z_logic_y = 4.0  # Mutual info with task output (higher is better)
        kl_divergence = 0.8  # KL(q(Z|X) || p(Z))

        # Compute total loss
        privacy_term = i_x_z_sensitive
        utility_term = -beta * i_z_logic_y  # Negative because we maximize this
        regularization_term = alpha * kl_divergence
        total_loss = privacy_term + utility_term + regularization_term + cost

        components = {
            "privacy_leakage": privacy_term,
            "utility_gain": -utility_term,  # Report as positive for clarity
            "regularization": regularization_term,
            "computational_cost": cost,
            "total_loss": total_loss,
        }

        return total_loss, components

    def get_anonymization_map(self) -> Dict[str, str]:
        """
        Retrieve the mapping from original sensitive data to placeholders.

        This map should be stored securely on the client side and never
        transmitted to the cloud. It enables local reconstruction if needed.

        Returns:
            Dictionary mapping original PII to anonymized placeholders.
        """
        return self._anonymization_map.copy()

    def reconstruct(self, desensitized_text: str) -> str:
        """
        Reconstruct original text from desensitized version (client-side only).

        Args:
            desensitized_text: Text with anonymized placeholders.

        Returns:
            Original text with PII restored.
        """
        reconstructed = desensitized_text
        for original, placeholder in self._anonymization_map.items():
            reconstructed = reconstructed.replace(placeholder, original)
        return reconstructed
