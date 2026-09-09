# 架构

```mermaid
flowchart LR
  O[Obligation YAML/JSON] --> L[校验后的模型]
  E[Evidence YAML/JSON] --> L
  A[适配器] --> E
  L --> G[确定性 Gap Engine]
  G --> R[JSON / Markdown Reporter]
  R --> C[CLI]
```

Core 不理解具体框架；Adapter 只标准化生产者输出，只有 Core 评估协议数据。Quality Planner（`qcov.engine.planner`）仅将未满足缺口排序为 draft 提案，从不进入 Gap Engine 或 policy 判定。

`qcov.yaml` 相对自身解析报告路径。JUnit/coverage reader 仅解析本地文件并输出 scan diagnostics，不会直接进入 Gap Engine。
