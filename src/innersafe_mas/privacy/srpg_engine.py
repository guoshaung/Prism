"""
SRPG privacy gate built on top of a pluggable recognition layer.

In the revised architecture, entity recognition is delegated to a lower-level
adapter such as Microsoft Presidio, while SRPG remains responsible for
stream-splitting, utility preservation, and privacy-aware execution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SensitiveSpan:
    """Structured record for one detected sensitive entity."""

    entity_type: str
    start: int
    end: int
    text: str
    score: float = 1.0


class _RegexAnalyzer:
    """Fallback analyzer used when Presidio is unavailable."""

    def __init__(self) -> None:
        self.patterns: dict[str, str] = {
            "PERSON": (
                r"(?:(?<=患者)|(?<=病人)|(?<=医生建议)|(?<=建议)|(?<=姓名))"
                r"(?:[\u4e00-\u9fff]{2}|[\u4e00-\u9fff]{3}|[\u4e00-\u9fff]{4})"
                r"(?=(?:需要|继续|服用|复诊|观察|的|，|。|$))"
            ),
            "ID": r"\b\d{15,18}\b",
            "PHONE_NUMBER": r"(?<!\d)1[3-9]\d{9}(?!\d)",
            "EMAIL_ADDRESS": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        }

    def analyze(self, text: str) -> list[SensitiveSpan]:
        spans: list[SensitiveSpan] = []
        for entity_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                spans.append(
                    SensitiveSpan(
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        text=match.group(0),
                        score=1.0,
                    )
                )
        return sorted(spans, key=lambda span: (span.start, span.end))


class PresidioPrivacyAdapter:
    """
    Adapter layer for privacy perception.

    When Presidio is installed, this adapter uses it as the lower-level
    recognizer/anonymizer. Otherwise, it falls back to a regex-based recognizer
    so the research prototype remains runnable in lightweight environments.
    """

    def __init__(self) -> None:
        self._engine_mode = "regex-fallback"
        self._analyzer = _RegexAnalyzer()
        self._presidio_analyzer: Any | None = None
        self._presidio_anonymizer: Any | None = None

        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine

            self._presidio_analyzer = AnalyzerEngine()
            self._presidio_anonymizer = AnonymizerEngine()
            self._engine_mode = "presidio"
        except ImportError:
            pass

    @property
    def engine_mode(self) -> str:
        return self._engine_mode

    def analyze(self, text: str) -> list[SensitiveSpan]:
        if self._presidio_analyzer is None:
            return self._analyzer.analyze(text)

        results = self._presidio_analyzer.analyze(text=text, language="en")
        spans = [
            SensitiveSpan(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                text=text[result.start : result.end],
                score=result.score,
            )
            for result in results
        ]
        return sorted(spans, key=lambda span: (span.start, span.end))


class InformationBottleneckPrivacyGate:
    """
    SRPG execution layer above a pluggable privacy recognizer.

    The recognizer detects sensitive spans; SRPG then decides how to protect
    them while preserving as much downstream utility as possible.
    """

    def __init__(
        self,
        placeholder_prefix: str = "[ANON_",
        recognizer: PresidioPrivacyAdapter | None = None,
    ) -> None:
        self.placeholder_prefix = placeholder_prefix
        self.recognizer = recognizer or PresidioPrivacyAdapter()
        self._anonymization_map: dict[str, str] = {}
        self._counter = 0

    def split_streams(self, text: str) -> dict[str, Any]:
        """
        Split text into a privacy-safe stream and a utility-preserving stream.
        """
        detected_spans = self.recognizer.analyze(text)
        desensitized = text
        detected_entities: list[tuple[str, str, str]] = []

        for span in detected_spans:
            placeholder = self._placeholder_for(span.text, span.entity_type)
            desensitized = desensitized.replace(span.text, placeholder)
            detected_entities.append((span.entity_type, span.text, placeholder))

        logic_stream = self._extract_logic_tokens(desensitized)
        return {
            "desensitized_stream": desensitized,
            "logic_stream": logic_stream,
            "detected_entities": detected_entities,
            "recognizer_backend": self.recognizer.engine_mode,
        }

    def calculate_loss(
        self,
        alpha: float,
        beta: float,
        cost: float,
    ) -> tuple[float, dict[str, float]]:
        """
        Compute a simple SRPG-style objective decomposition.
        """
        i_x_z_sensitive = 2.5
        i_z_logic_y = 4.0
        kl_divergence = 0.8

        privacy_term = i_x_z_sensitive
        utility_term = -beta * i_z_logic_y
        regularization_term = alpha * kl_divergence
        total_loss = privacy_term + utility_term + regularization_term + cost

        return total_loss, {
            "privacy_leakage": privacy_term,
            "utility_gain": -utility_term,
            "regularization": regularization_term,
            "computational_cost": cost,
            "total_loss": total_loss,
        }

    def get_anonymization_map(self) -> dict[str, str]:
        return self._anonymization_map.copy()

    def reconstruct(self, desensitized_text: str) -> str:
        reconstructed = desensitized_text
        for original, placeholder in self._anonymization_map.items():
            reconstructed = reconstructed.replace(placeholder, original)
        return reconstructed

    def _placeholder_for(self, original: str, entity_type: str) -> str:
        if original not in self._anonymization_map:
            self._counter += 1
            label = entity_type.upper().replace(" ", "_")
            self._anonymization_map[original] = (
                f"{self.placeholder_prefix}{label}_{self._counter}]"
            )
        return self._anonymization_map[original]

    def _extract_logic_tokens(self, text: str) -> str:
        """
        Preserve domain keywords and anonymized placeholders.
        """
        keywords = [
            "aspirin",
            "treatment",
            "diagnosis",
            "symptom",
            "report",
            "patient",
            "doctor",
            "medication",
            "dose",
            "allergy",
            "检查",
            "诊断",
            "治疗",
            "症状",
            "患者",
            "药物",
        ]

        lowered = text.lower()
        tokens = [keyword for keyword in keywords if keyword.lower() in lowered]
        placeholders = re.findall(r"\[ANON_[A-Z_0-9]+\]", text)
        tokens.extend(placeholders)
        return " ".join(tokens)
