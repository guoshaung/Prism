"""Integration adapters for model-side watermarking demos."""

from innersafe_mas.copyright.integrations.huggingface_wrapper import (
    HuggingFaceWrapper,
    MockGenerationModel,
)

__all__ = ["HuggingFaceWrapper", "MockGenerationModel"]
