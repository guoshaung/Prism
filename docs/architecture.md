# innersafe-mas Architecture

## Overview

`innersafe-mas` is a domain-agnostic security governance middleware for LLM Multi-Agent Systems (MAS). It addresses the fundamental tension between **privacy protection** (client-side) and **copyright enforcement** (cloud-side) through three core modules.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                            │
│                  (with potential PII)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Privacy Module (Client-Side)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  InformationBottleneckPrivacyGate                     │  │
│  │  • Detects PII (names, IDs, emails)                   │  │
│  │  • Splits into desensitized + logic streams           │  │
│  │  • Minimizes I(X; Z_sensitive)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ Desensitized Stream
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LLM Multi-Agent System                     │
│              (Medical / Legal / Financial Agents)            │
└────────────────────────┬────────────────────────────────────┘
                         │ Generated Responses
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Copyright Module (Cloud-Side)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AdaptiveKGWWatermark + KnowledgeGraphAdapter         │  │
│  │  • Injects watermark with adaptive bias               │  │
│  │  • δ_dynamic(i) = δ_base × (1 - S(i))                 │  │
│  │  • Preserves core domain concepts (S(i) → 1)          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ Watermarked Candidates
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Governance Module (Routing)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  GameTheoryRouter                                      │  │
│  │  • Evaluates U = Q - λ₁·R_priv - λ₂·L_copy            │  │
│  │  • Selects Pareto-optimal response                     │  │
│  │  • Balances quality, privacy, copyright                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  Final Response to User
```

---

## Module Details

### 1. Privacy Module (`innersafe_mas.privacy`)

**Core Class:** `InformationBottleneckPrivacyGate`

**Theoretical Foundation:**
- Variational Information Bottleneck (VIB)
- Objective: `L = I(X; Z_sensitive) - β·I(Z_logic; Y) + α·KL(q||p)`

**Key Methods:**
- `split_streams(text)`: Anonymize PII, extract logic tokens
- `calculate_loss(α, β, cost)`: Compute VIB loss
- `reconstruct(desensitized)`: Restore original (client-only)

**Use Cases:**
- Medical records with patient names
- Legal documents with case IDs
- Financial reports with account numbers

---

### 2. Copyright Module (`innersafe_mas.copyright`)

**Core Classes:**
- `KnowledgeGraphAdapter` (abstract base)
- `AdaptiveKGWWatermark`

**Theoretical Foundation:**
- Adaptive watermark bias: `δ_dynamic(i) = δ_base × (1 - S(i))`
- `S(i)`: Semantic centrality in domain knowledge graph

**Key Methods:**
- `inject_watermark(text, graph)`: Apply adaptive watermark
- `verify_watermark(text, graph)`: Detect watermark presence
- `get_semantic_centrality(word)`: Query graph centrality

**Integration Points:**
- NetworkX for in-memory graphs
- Neo4j for production-scale graphs
- Custom domain ontologies (UMLS, SNOMED, etc.)

---

### 3. Governance Module (`innersafe_mas.governance`)

**Core Class:** `GameTheoryRouter`

**Theoretical Foundation:**
- Pareto equilibrium: `π* = argmax_π [Q(π) - λ₁·R_priv(π) - λ₂·L_copy(π)]`

**Key Methods:**
- `evaluate_and_route(candidates)`: Select optimal response
- `update_weights(λ₁, λ₂)`: Adapt to user feedback
- `_compute_pareto_frontier(candidates)`: Find non-dominated solutions

**Tuning Guidelines:**
- High `λ₁` (e.g., 2.0): Prioritize privacy (medical, legal)
- High `λ₂` (e.g., 2.0): Enforce strong copyright (research, education)
- Balanced (e.g., 1.0, 1.0): General-purpose applications

---

## Extension Points

### Custom Knowledge Graphs

```python
from innersafe_mas import KnowledgeGraphAdapter

class MyDomainGraph(KnowledgeGraphAdapter):
    def get_semantic_centrality(self, word: str) -> float:
        # Connect to your domain ontology
        return my_ontology.query_centrality(word)
```

### Custom Privacy Patterns

```python
gate = InformationBottleneckPrivacyGate()
gate.sensitive_patterns["custom"] = r"YOUR_REGEX"
```

### Dynamic Weight Adjustment

```python
router = GameTheoryRouter(lambda_1=1.0, lambda_2=1.0)

# After user feedback
if user_prefers_privacy:
    router.update_weights(lambda_1=2.0)
```

---

## Performance Considerations

1. **Privacy Gate**: O(n) regex matching, negligible overhead
2. **Watermark Injection**: O(n·k) where k = graph query time
   - Use caching for repeated centrality lookups
3. **Game Router**: O(m²) for Pareto frontier (m = num candidates)
   - Typically m < 10, so very fast

---

## Security Best Practices

1. **Never transmit anonymization map to cloud**
   - Store `gate.get_anonymization_map()` locally only
2. **Protect watermark secret key**
   - Use environment variables or secure vaults
3. **Validate all inputs**
   - Sanitize user text before processing
4. **Audit watermark strength**
   - Monitor `watermark_metadata["watermark_strength"]`

---

## Future Roadmap

- [ ] Neural VIB encoder (replace regex-based privacy gate)
- [ ] Distributed watermark verification (blockchain anchoring)
- [ ] Federated learning for adaptive λ tuning
- [ ] Integration with LangChain / LlamaIndex
- [ ] Real-time monitoring dashboard

---

## References

1. Tishby et al. (2000). "The Information Bottleneck Method"
2. Kirchenbauer et al. (2023). "A Watermark for Large Language Models"
3. Nash (1950). "Equilibrium Points in N-Person Games"
