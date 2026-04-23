"""
Medical Multi-Agent System Demo.

This example demonstrates how to use innersafe-mas in a medical diagnosis scenario:
1. Patient submits medical record with PII (name, ID)
2. Privacy gate desensitizes the input
3. Medical agent generates treatment plan
4. Watermark injector protects copyright (preserving drug names)
5. Game router selects optimal response balancing quality, privacy, and copyright
"""

from innersafe_mas import (
    InformationBottleneckPrivacyGate,
    AdaptiveKGWWatermark,
    KnowledgeGraphAdapter,
    GameTheoryRouter,
)


class MedicalKnowledgeGraph(KnowledgeGraphAdapter):
    """
    Medical domain knowledge graph with predefined drug/symptom centrality.

    In production, this would connect to a real medical ontology like:
    - UMLS (Unified Medical Language System)
    - SNOMED CT
    - RxNorm for medications
    """

    def __init__(self):
        # Core medical concepts with high centrality
        self.centrality_map = {
            # Medications (high centrality - should not be watermarked)
            "阿司匹林": 0.95,  # Aspirin
            "布洛芬": 0.92,    # Ibuprofen
            "青霉素": 0.90,    # Penicillin
            "胰岛素": 0.93,    # Insulin

            # Symptoms (medium centrality)
            "头痛": 0.70,      # Headache
            "发烧": 0.68,      # Fever
            "咳嗽": 0.65,      # Cough

            # Medical actions (medium centrality)
            "服用": 0.60,      # Take (medication)
            "诊断": 0.75,      # Diagnose
            "治疗": 0.72,      # Treat

            # General terms (low centrality - can be watermarked)
            "患者": 0.30,      # Patient
            "医生": 0.35,      # Doctor
            "建议": 0.20,      # Recommend
            "注意": 0.15,      # Attention
        }

    def get_semantic_centrality(self, word: str) -> float:
        """Return centrality score for medical terms."""
        return self.centrality_map.get(word, 0.0)


def simulate_medical_agent_response(desensitized_input: str) -> str:
    """
    Simulate a medical agent generating a treatment plan.

    In production, this would call an LLM API with medical fine-tuning.
    """
    # Mock response based on input keywords
    if "头痛" in desensitized_input:
        return (
            "根据症状分析，建议患者服用阿司匹林 100mg，每日一次。"
            "注意观察是否有过敏反应。如症状持续，建议进行头部CT检查。"
            "治疗期间避免饮酒，保持充足休息。"
        )
    else:
        return "请提供更详细的症状描述以便诊断。建议进行全面体检。"


def main():
    print("=" * 70)
    print("Medical Multi-Agent System Demo - innersafe-mas")
    print("=" * 70)
    print()

    # ========== Step 1: Patient Input with PII ==========
    print("【Step 1】Patient Input (with PII)")
    patient_input = "患者张三，身份证号110101199001011234，服用阿司匹林后出现头痛症状"
    print(f"Original: {patient_input}")
    print()

    # ========== Step 2: Privacy Protection ==========
    print("【Step 2】Privacy Protection (SRPG Information Bottleneck)")
    privacy_gate = InformationBottleneckPrivacyGate()
    privacy_result = privacy_gate.split_streams(patient_input)

    print(f"Desensitized: {privacy_result['desensitized_stream']}")
    print(f"Logic Stream: {privacy_result['logic_stream']}")
    print(f"Detected PII: {privacy_result['detected_entities']}")

    # Calculate privacy loss
    loss, components = privacy_gate.calculate_loss(alpha=0.05, beta=1.0, cost=0.1)
    print(f"Privacy Loss: {loss:.3f}")
    print(f"  - Privacy Leakage: {components['privacy_leakage']:.3f}")
    print(f"  - Utility Gain: {components['utility_gain']:.3f}")
    print()

    # ========== Step 3: Medical Agent Generation ==========
    print("【Step 3】Medical Agent Response Generation")
    agent_response = simulate_medical_agent_response(
        privacy_result['desensitized_stream']
    )
    print(f"Generated: {agent_response}")
    print()

    # ========== Step 4: Copyright Watermarking ==========
    print("【Step 4】Copyright Protection (Adaptive KGW Watermark)")
    medical_graph = MedicalKnowledgeGraph()
    watermark = AdaptiveKGWWatermark(base_delta=2.5, secret_key="medical-demo-key")

    watermark_result = watermark.inject_watermark(
        text=agent_response,
        graph=medical_graph,
    )

    print(f"Watermarked: {watermark_result['watermarked_text']}")
    print(f"Watermark Strength: {watermark_result['watermark_metadata']['watermark_strength']:.3f}")
    print(f"Watermarked Tokens: {watermark_result['watermark_metadata']['num_watermarked_tokens']}/{watermark_result['watermark_metadata']['total_tokens']}")

    # Show adaptive bias for key terms
    print("\nAdaptive Bias Examples:")
    for decision in watermark_result['token_decisions'][:5]:
        print(f"  '{decision['token']}': centrality={decision['centrality']:.2f}, "
              f"δ_dynamic={decision['adaptive_delta']:.2f}, "
              f"watermarked={decision['watermarked']}")
    print()

    # ========== Step 5: Game-Theoretic Routing ==========
    print("【Step 5】Game-Theoretic Routing (Pareto Equilibrium)")

    # Simulate multiple agent candidates with different trade-offs
    candidates = [
        {
            "agent_id": "conservative_agent",
            "response": watermark_result['watermarked_text'],
            "quality": 0.85,
            "privacy_risk": 0.10,  # Low privacy risk (well desensitized)
            "copyright_loss": 0.15,  # Low copyright loss (strong watermark)
        },
        {
            "agent_id": "quality_focused_agent",
            "response": "高质量但可能泄露隐私的回答...",
            "quality": 0.95,
            "privacy_risk": 0.40,  # Higher privacy risk
            "copyright_loss": 0.10,
        },
        {
            "agent_id": "balanced_agent",
            "response": "平衡型回答...",
            "quality": 0.80,
            "privacy_risk": 0.20,
            "copyright_loss": 0.20,
        },
    ]

    router = GameTheoryRouter(lambda_1=1.5, lambda_2=1.0)  # Prioritize privacy
    routing_result = router.evaluate_and_route(candidates)

    print(f"Selected Agent: {routing_result['selected_response']['agent_id']}")
    print(f"Decision Rationale: {routing_result['decision_rationale']}")
    print("\nAll Utility Scores:")
    for score in routing_result['utility_scores']:
        print(f"  {score['agent_id']}: U={score['utility']:.3f} "
              f"(Q={score['quality']:.2f}, R_priv={score['privacy_risk']:.2f}, "
              f"L_copy={score['copyright_loss']:.2f})")

    print(f"\nPareto Frontier: {routing_result['pareto_frontier']}")
    print()

    # ========== Step 6: Watermark Verification ==========
    print("【Step 6】Watermark Verification")
    verification = watermark.verify_watermark(
        text=watermark_result['watermarked_text'],
        graph=medical_graph,
    )
    print(f"Is Watermarked: {verification['is_watermarked']}")
    print(f"Confidence: {verification['confidence']:.3f}")
    print(f"Z-Score: {verification['statistics']['z_score']:.3f}")
    print()

    # ========== Summary ==========
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("✓ Privacy: PII (张三, ID) successfully anonymized")
    print("✓ Copyright: Watermark injected with adaptive bias")
    print("✓ Quality: Core medical terms (阿司匹林) preserved without distortion")
    print("✓ Governance: Optimal agent selected via game-theoretic routing")
    print("\nThis framework can be adapted to any domain (legal, financial, education)")
    print("by implementing custom KnowledgeGraphAdapter subclasses.")


if __name__ == "__main__":
    main()
