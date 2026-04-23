# innersafe-mas

> Endogenous Security Governance Framework for LLM Multi-Agent Systems
>
> 面向多智能体系统的通用开源框架，聚焦隐私保护、版权保护与效用平衡。

`innersafe-mas` 是一个面向 LLM Multi-Agent Systems (MAS) 的通用安全治理框架，目标不是单独优化某一个安全指标，而是在以下三者之间建立统一的工程接口与理论表达：

- 隐私保护：尽量减少敏感信息暴露
- 版权保护：为生成内容提供可追踪、可验证的水印能力
- 效用保持：尽量不破坏原始内容的可读性、可用性与任务性能

它适用于教育、医疗、法律、科研等高价值知识场景，尤其适合“既要保护输入隐私，又要保护输出版权，还不能明显损伤内容质量”的系统。

---

## Core Modules

| Module | Theory | Current Objective |
| --- | --- | --- |
| `privacy.srpg_engine` | Variational Information Bottleneck | `min I(X; Z_sensitive) - beta * I(Z_logic; Y)` |
| `copyright.kgw_watermark` | Knowledge-Graph-Guided Watermarking | `delta_dynamic(i) = delta_base * (1 - S(i))` |
| `governance.game_router` | Pareto / Utility Routing | `max U_total = Q(pi) - lambda_1 R_priv - lambda_2 L_copy` |

---

## Innovation Focus

这个项目的核心创新不在于“把三个模块简单拼起来”，而在于把它们组织成一个统一的治理框架：

1. 输入侧用隐私门控机制做敏感信息分流
2. 输出侧用知识图谱引导的自适应水印做版权保护
3. 决策侧用效用函数或博弈路由在隐私、版权、质量之间做平衡

其中，创新点 2 的关键不是“给所有内容均匀打水印”，而是“让水印跟着语义价值走”。

---

## Innovation 2: KGW-Guided Adaptive Watermark

### Design Goal

在生成水印信号 `W(x, y)` 时，不再对整个数据区域均匀施加强保护，而是根据知识图谱引导的语义重要性，在“核心知识区域”和“非核心区域”之间寻找最优平衡。

这意味着：

- 对核心知识点，优先保护内容完整性与可用性
- 对语义边缘区域，可以承载更强的水印信号
- 水印系统不再只追求“能检出”，而是同时追求“鲁棒”和“低失真”

### Unified Formula

```math
W(x,y) = \alpha \cdot S_{kgw}(x,y) + \beta \cdot R_{robust}(x,y) - \gamma \cdot D_{distort}(x,y)
```

### Interpretation

`W(x,y)`：最终生成的水印信号或保护策略

- 表示在坐标 `(x, y)` 处应施加多强的保护力度
- 在图像中，它可以对应像素或区域
- 在文本中，它可以对应 token 位置、局部表示或语义片段

`alpha * S_kgw(x,y)`：KGW 语义权重

- `S_kgw(x,y)` 表示知识图谱引导的语义重要性得分
- 如果某处包含核心知识，例如公式关键步骤、医学病灶描述、法律责任条款，其得分应更高
- `alpha` 是调节系数，用来控制语义重要性对水印分布的影响强度
- 这一项体现了本项目的核心思想：保护策略应优先响应“知识价值”，而不是对所有区域一视同仁

`beta * R_robust(x,y)`：鲁棒性约束

- `R_robust(x,y)` 描述水印抵抗压缩、裁剪、改写或扰动的能力
- `beta` 是鲁棒性权重
- 这一项保证水印不只是“被加上去”，而且在实际攻击或二次处理后仍尽量可检测、可验证

`- gamma * D_distort(x,y)`：视觉或效用失真惩罚

- `D_distort(x,y)` 描述引入水印后对内容质量的损伤
- 对图像来说，可能体现为清晰度下降、伪影增加
- 对文本来说，可能体现为可读性下降、语义不自然、任务性能变差
- `gamma` 是惩罚系数
- 负号说明这是一个约束项：水印不能以明显破坏内容效用为代价

### Why This Matters

这个公式明确表达了本项目对版权保护模块的理解：

- 目标不是把水印“铺满”
- 目标也不是单纯把水印“做强”
- 目标是在语义重要性、鲁棒性和失真之间做结构化权衡

从这个角度看，项目当前的 `AdaptiveKGWWatermark` 实现方向是正确的，但它目前还是一个简化版本：

- 当前实现已经体现了“语义越重要，水印偏置越小”的思想
- 当前代码中的核心表达是 `delta_dynamic(i) = delta_base * (1 - S(i))`
- 它抓住了 KGW 引导的关键直觉，但还没有完全展开成上面的统一三目标公式

因此，更准确的表述应该是：

- 当前仓库已经实现了创新点 2 的核心机制雏形
- 上述 `W(x,y)` 公式是该机制更完整、更一般化的理论表达

---

## Quick Start

```python
from innersafe_mas import (
    AdaptiveKGWWatermark,
    GameTheoryRouter,
    InformationBottleneckPrivacyGate,
)

gate = InformationBottleneckPrivacyGate()
streams = gate.split_streams("患者张三服用阿司匹林后出现头痛")

watermarker = AdaptiveKGWWatermark(base_delta=2.0)
router = GameTheoryRouter()
```

完整示例见 [examples/medical_mas_demo.py](/D:/pycharm/interface-mas/examples/medical_mas_demo.py)。

---

## Installation

```bash
pip install innersafe-mas
pip install "innersafe-mas[graph]"
```

---

## Architecture

系统级设计见 [docs/architecture.md](/D:/pycharm/interface-mas/docs/architecture.md)。

---

## Roadmap

- [x] 隐私门控、版权水印、治理路由三模块解耦
- [x] KGW 语义中心性驱动的自适应水印原型
- [ ] 将 `W(x,y)` 三目标公式落地为统一优化接口
- [ ] 支持更细粒度的文本片段 / 图像区域保护策略
- [ ] 引入鲁棒性评估与失真评估的标准化指标
- [ ] 与真实生成模型的 logit processor / decoder 深度集成

---

## License

Apache-2.0
