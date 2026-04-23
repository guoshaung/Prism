"""
innersafe-mas: Endogenous Security Governance Framework for LLM Multi-Agent Systems.

This package provides three core modules:
- privacy: SRPG Information Bottleneck Privacy Gate
- copyright: KGW Adaptive Knowledge Graph Watermark
- governance: Game-Theoretic Utility Router
"""

__version__ = "0.1.0"

from innersafe_mas.privacy.srpg_engine import InformationBottleneckPrivacyGate
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark
from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter
from innersafe_mas.governance.game_router import GameTheoryRouter

__all__ = [
    "InformationBottleneckPrivacyGate",
    "AdaptiveKGWWatermark",
    "KnowledgeGraphAdapter",
    "GameTheoryRouter",
]
