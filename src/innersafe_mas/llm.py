"""Public LLM client interfaces for external integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Minimal interface for plugging an external LLM into the framework."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: object) -> str:
        """Return generated text for the given prompt."""


class MockLLMClient(BaseLLMClient):
    """Simple deterministic client used in tests and examples."""

    def __init__(self, response: str = "doctor recommend aspirin safely") -> None:
        self.response = response

    def generate(self, prompt: str, **kwargs: object) -> str:
        return self.response
