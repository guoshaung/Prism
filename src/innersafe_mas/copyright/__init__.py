"""Copyright module for innersafe-mas."""

from innersafe_mas.copyright.attacks import (
    ParaphraseAttack,
    TruncationAttack,
    WordDeletionAttack,
)
from innersafe_mas.copyright.evaluation import (
    run_generation_attack_loop,
    run_robustness_suite,
)
from innersafe_mas.copyright.graph_adapter import KnowledgeGraphAdapter, MockKnowledgeGraph
from innersafe_mas.copyright.integrations import HuggingFaceWrapper, MockGenerationModel
from innersafe_mas.copyright.kgw_watermark import AdaptiveKGWWatermark
from innersafe_mas.copyright.mock_components import (
    MockCopyrightPolicy,
    MockForensicRecorder,
    MockKeyManager,
)

__all__ = [
    "AdaptiveKGWWatermark",
    "HuggingFaceWrapper",
    "KnowledgeGraphAdapter",
    "MockCopyrightPolicy",
    "MockForensicRecorder",
    "MockGenerationModel",
    "MockKeyManager",
    "MockKnowledgeGraph",
    "ParaphraseAttack",
    "TruncationAttack",
    "WordDeletionAttack",
    "run_generation_attack_loop",
    "run_robustness_suite",
]
