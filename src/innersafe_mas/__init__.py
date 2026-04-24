"""
innersafe-mas: Endogenous Security Governance Framework for LLM Multi-Agent Systems.

This package provides three core modules:
- privacy: SRPG Information Bottleneck Privacy Gate
- copyright: KGW Adaptive Knowledge Graph Watermark
- governance: Game-Theoretic Utility Router
"""

__version__ = "0.1.0"

from innersafe_mas.privacy.srpg_engine import InformationBottleneckPrivacyGate
from innersafe_mas.privacy import PresidioPrivacyAdapter
from innersafe_mas.copyright import (
    AdaptiveKGWWatermark,
    HuggingFaceWrapper,
    KnowledgeGraphAdapter,
    MockGenerationModel,
    MockKnowledgeGraph,
    ParaphraseAttack,
    TruncationAttack,
    run_generation_attack_loop,
    run_robustness_suite,
)
from innersafe_mas.governance.game_router import GameTheoryRouter
from innersafe_mas.api import SecureService
from innersafe_mas.llm import BaseLLMClient, MockLLMClient
from innersafe_mas.pipeline import (
    CopyrightAgent,
    PrivacyAgent,
    SecureInferencePipeline,
    SecurityContext,
)

__all__ = [
    "InformationBottleneckPrivacyGate",
    "PresidioPrivacyAdapter",
    "AdaptiveKGWWatermark",
    "SecureService",
    "BaseLLMClient",
    "MockLLMClient",
    "HuggingFaceWrapper",
    "KnowledgeGraphAdapter",
    "MockGenerationModel",
    "MockKnowledgeGraph",
    "ParaphraseAttack",
    "TruncationAttack",
    "GameTheoryRouter",
    "SecurityContext",
    "PrivacyAgent",
    "CopyrightAgent",
    "SecureInferencePipeline",
    "run_generation_attack_loop",
    "run_robustness_suite",
]
