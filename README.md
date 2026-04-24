# innersafe-mas

Research-oriented security framework for LLM applications with three coordinated layers:

- Privacy perception and execution
- KGW-based copyright watermarking
- Governance-driven strategy optimization

The package is designed to be imported directly from another project, so you can use it as a Python security middleware instead of only as a standalone demo.

## Install

```bash
pip install innersafe-mas
pip install "innersafe-mas[graph]"
pip install "innersafe-mas[privacy]"
pip install "innersafe-mas[graph,privacy]"
```

## Public Interfaces

The main SDK-style entrypoint is:

```python
from innersafe_mas import SecureService
```

`SecureService` exposes four core integration methods:

- `protect_text(text)`: run privacy analysis, governance, and watermarking
- `preview_watermark(text, context="")`: show text before and after watermarking
- `protect_generated_text(prompt, client)`: call any external LLM client and then protect its output
- `generate_with_huggingface(prompt, model=None)`: run the HuggingFace-style KGW interception demo

## Quick Start

```python
from innersafe_mas import SecureService

service = SecureService()
service.build_mock_graph(
    {
        "aspirin": 0.95,
        "treatment": 0.80,
        "doctor": 0.20,
    }
)

context = service.protect_text(
    "Patient ZhangSan needs aspirin treatment and ID 110101199001011234."
)

print(context.desensitized_text)
print(context.watermarked_text)
print(context.final_config)
```

## Watermark Preview Interface

If you want to display text before and after watermarking in another project:

```python
from innersafe_mas import SecureService

service = SecureService()
service.build_mock_graph({"aspirin": 0.95, "doctor": 0.10})

preview = service.preview_watermark(
    "doctor recommend aspirin",
    context="medical answer",
)

print(preview["before_text"])
print(preview["after_text"])
print(preview["watermark_metadata"])
```

This interface is suitable for:

- admin dashboards
- model output comparison views
- demo pages showing watermark insertion effects

## Knowledge Graph Interface

The framework exposes an abstract knowledge graph adapter:

```python
from innersafe_mas import KnowledgeGraphAdapter
```

To connect your own graph backend:

```python
from innersafe_mas import KnowledgeGraphAdapter, SecureService


class MyKnowledgeGraph(KnowledgeGraphAdapter):
    def get_semantic_centrality(self, word: str) -> float:
        values = {
            "aspirin": 0.95,
            "treatment": 0.80,
            "doctor": 0.20,
        }
        return values.get(word.lower(), 0.0)


service = SecureService()
service.set_graph(MyKnowledgeGraph())
```

For quick experiments you can also use:

```python
from innersafe_mas import MockKnowledgeGraph
```

## LLM Calling Interfaces

### Generic LLM Client Interface

If your project already has an LLM client, implement the minimal interface:

```python
from innersafe_mas import BaseLLMClient, SecureService


class MyLLMClient(BaseLLMClient):
    def generate(self, prompt: str, **kwargs: object) -> str:
        return "doctor recommend aspirin safely"


service = SecureService()
context = service.protect_generated_text("medical prompt", MyLLMClient())

print(context.original_text)
print(context.text)
print(context.final_config)
```

### HuggingFace-Style Interface

The framework also includes a lightweight wrapper that demonstrates where KGW should intercept logits during generation:

```python
from innersafe_mas import MockGenerationModel, SecureService

service = SecureService()
service.build_mock_graph({"recommend": 0.10, "safe": 0.10})

result = service.generate_with_huggingface(
    "medical prompt",
    model=MockGenerationModel(),
)

print(result["generated_text"])
print(result["watermarked_text"])
print(result["generation_trace"])
```

## Secure Inference Pipeline

The unified internal pipeline is:

1. build `SecurityContext`
2. analyze privacy entities
3. analyze KG semantic weights
4. optimize strategy with `GameTheoryRouter`
5. execute privacy protection
6. execute watermarking
7. return the final context

Important public classes:

- `SecurityContext`
- `PrivacyAgent`
- `CopyrightAgent`
- `SecureInferencePipeline`
- `GameTheoryRouter`

## Privacy Layer

The privacy stack is intentionally layered:

- `PresidioPrivacyAdapter`: perception layer
- `InformationBottleneckPrivacyGate`: SRPG execution layer

If `presidio-analyzer` and `presidio-anonymizer` are installed, the framework can use Presidio as the recognizer backend. Otherwise it falls back to a lightweight regex recognizer for demos and tests.

## Copyright Layer

The copyright stack includes:

- `AdaptiveKGWWatermark`
- `KnowledgeGraphAdapter`
- attack simulators in `innersafe_mas.copyright.attacks`
- robustness evaluation in `innersafe_mas.copyright.evaluation`

## Testing

```bash
pytest tests -q
python -m ruff check src tests
```

## License

Apache-2.0
