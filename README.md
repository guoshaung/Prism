# innersafe-mas

> **Endogenous Security Governance Framework for LLM Multi-Agent Systems**
>
> 客户端隐私保护 · 云端版权溯源 · 开放博弈式路由

`innersafe-mas` 是一个面向大模型多智能体系统（LLM-MAS）的**通用安全治理中间件**。它不绑定任何具体业务场景（教育 / 医疗 / 法律均可使用），核心解决 MAS 在处理敏感数据与生成知识内容时的**「隐私保护 ↔ 版权溯源」冲突问题**。

---

## ✨ 核心能力

| 模块 | 论文支撑 | 公式 |
|------|----------|------|
| `privacy.srpg_engine` | Variational Information Bottleneck | $\min I(X;Z_{sensitive}) - \beta \cdot I(Z_{logic};Y)$ |
| `copyright.kgw_watermark` | KGW Adaptive Watermark | $\delta_{dynamic} = \delta_{base} \times (1 - \mathcal{S}(i))$ |
| `governance.game_router` | Pareto Game Equilibrium | $\max U_{total} = Q(\pi_E) - \lambda_1 \mathcal{R}_{priv} - \lambda_2 \mathcal{L}_{copy}$ |

---

## 🚀 Quick Start

```python
from innersafe_mas import (
    InformationBottleneckPrivacyGate,
    AdaptiveKGWWatermark,
    GameTheoryRouter,
)

gate = InformationBottleneckPrivacyGate()
streams = gate.split_streams("患者张三服用阿司匹林后出现头痛")
# -> {"desensitized_stream": "...", "logic_stream": "..."}
```

完整示例见 `examples/medical_mas_demo.py`。

---

## 📦 Installation

```bash
pip install innersafe-mas
# or with optional graph backend
pip install "innersafe-mas[graph]"
```

## 📜 License

Apache-2.0
