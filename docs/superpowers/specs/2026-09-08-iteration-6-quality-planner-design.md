# Iteration 6：AI Quality Planner（纯）设计

## 目标

在 Iteration 5（映射加固 + 仅提案 AI）之后，交付**纯 Quality Planner**：

- 输入：本地评估产出的 unproven gaps，以及配置/文件中的**已编写**
  `TestingObligation`（此处「已批准」指义务已进入仓库配置，**不是** Proposal 批准流）。
- 输出：下一步最值得采取的验证策略（`qcov plan`）。
- 框架：固定规则表下的**证据收益 vs 执行成本**；结果可复现、无网络。
- 形态：仍为 draft `QualityProposal`，**不得**成为证据或门禁权威。

原则不变：

> AI proposes. Policy approves. Deterministic engine verifies.

本迭代排序权威在**确定性引擎**，不在 LLM / `AIProvider`。名称仍叫 Quality Planner /
`provider.name: offline`，表示可复现、无网络的提案封装，**不**表示调用大模型。

路线图依据：`docs/superpowers/specs/2026-09-08-post-4.5-iteration-roadmap-design.md`。

## 非目标

- 经 `AIProvider` 排序，或远程模型改写优先级
- 可配置 planner 权重 / 策略 DSL
- 从历史 gap 报告文件或 draft Proposal 文件作为主输入
- 自动执行测试、写入 `QualityEvidence`、Agent 闭环（Iteration 7）
- 生产证据（Iteration 8）
- coverage/LCOV 提升为 passed 证据、inventory → 义务推断
- 远程 Git、Web UI、持久化、外部插件 SDK
- 策略 DSL、维度阈值、路径/通配符豁免

## 决策摘要

| 议题 | 选择 |
| --- | --- |
| 排序权威 | 确定性启发式（固定规则表） |
| 输出协议 | 扩展现有 `QualityProposal`（`type: quality_plan`） |
| 输入 | `--config` 走多义务评估（对齐 `policy check`）；或单义务+证据 |
| 收益/成本 | 固定规则表；本迭代不提供 YAML 权重配置 |
| 架构 | 纯引擎 `qcov.engine.planner`；不扩展 `AIProvider` |

## 架构

```text
qcov.yaml ──► 现有评估路径（scan / mapping / marker merge）
                    │
                    ▼
              Gap Engine（不变）
                    │
                    ▼
         unproven dimensions（非 COVERED）
                    │
                    ▼
         qcov.engine.planner（本迭代新增）
           · 固定 benefit / cost 规则表
           · 稳定 tie-break
                    │
                    ▼
         QualityProposal
           type: quality_plan
           status: draft
           source.kind: evaluation_gaps
           provider.name: offline
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     stdout 渲染          可选写出 YAML
          │
          ✕ 不进入 Gap 满足
          ✕ 不改写 policy
```

| 组件 | 职责 |
| --- | --- |
| `qcov.engine.planner` | 从评估结果 + 义务元数据生成有序计划行（纯函数） |
| `qcov.models.protocol` | 扩展 proposal `type` / source `kind` / item `kind` |
| `schemas/proposal.schema.json` | 同步枚举 |
| `qcov.cli.app` | `qcov plan`：`--config` 多义务评估（对齐 policy）；组装 / 渲染 / 写出 |
| Gap / policy / `AIProvider` | **不改**判定语义；本迭代不扩展 provider 协议 |

### 计划粒度

- 一条 unproven `(obligationId, dimension)` → 一条 proposal item。
- `detail.missingEvidenceTypes`：对该 unproven 维度，取义务上该维度的**完整**
  `requiredEvidence` 类型列表。Gap Engine 维度满足是「任一 required type 有
  `passed` 即 COVERED」，**没有**按类型的剩余集合；故此处列出的是「该维度声明需要的
  类型」，而非引擎算出的 per-type residual。
- `required_types` 为空时：该维度仍可进入计划（若 unproven）；`missingEvidenceTypes=[]`，
  `suggestedEvidenceType=null`，`costScore` 使用未识别档 **40**（避免除零/无类型时无成本）。
- 全部维度均为 `COVERED` 时：产出 `items: []` 的合法 draft proposal，退出码 0（成功，非错误）。

## 评分规则

排序键：`priorityScore = costScore - benefitScore`（**越小越优先**）。

同分稳定 tie-break：`obligationId` → `dimension` → 首个 `missingEvidenceType`（字典序）。

### benefitScore（可加）

| 因子 | 规则 |
| --- | --- |
| 维度状态 | `MISSING`=+50，`UNKNOWN`=+20（不排 `COVERED`）。说明：Gap Engine 在**维度**上仅产出 `COVERED`/`MISSING`/`UNKNOWN`；`PARTIAL` 只出现在义务级汇总，本迭代按维度规划故不使用 `PARTIAL` 档。 |
| `risk.severity`（大小写不敏感） | `critical`=+40，`high`=+30，`medium`=+20，`low`=+10；其他=+15 |
| 维度权重 | `security` / `fault` / `production`=+25；`concurrency` / `idempotency` / `data`=+20；`boundary` / `integration`=+15；`behavior`=+10 |

### costScore

取该维度 `required_types` 中、相对「补齐该类型」的**最低**成本（最便宜补齐路径）。
若 `required_types` 为空，见上文：`costScore=40`，`suggestedEvidenceType=null`。
本迭代**不**探测仓库是否已有对应 inventory；仅按类型族粗分，保证离线可复现。

| 证据类型族 | 成本 | 示例类型字符串 |
| --- | --- | --- |
| 声明式 / 易映射单元或 API | 10 | `api_test`, `junit_test`, `pytest_marker` |
| 属性 / 数据不变量 | 20 | `property_test`, `database_invariant` |
| E2E | 35 | `e2e_test`, `playwright_test` |
| 生产 / 人工观察 | 50 | `production_signal`, `manual_review` |
| 未识别 | 40 | 其他任意字符串 |

`detail.suggestedEvidenceType` = 上述最低成本对应的类型（并列时取字典序最小类型名）。

## 协议扩展

沿用 `qcov.dev/v1alpha1`，`kind: QualityProposal`：

```yaml
apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-...                 # 稳定哈希（与 Iteration 5 offline 风格一致）
  createdAt: "..."           # offline 可用固定纪元时间以利金样
proposal:
  type: quality_plan         # 新增；既有 obligation_suggest / change_risk 保留
  status: draft              # 本迭代仅 draft
source:
  kind: evaluation_gaps      # 新增
  refs: []                   # 如配置路径、义务路径等可审计引用
provider:
  name: offline
  model: null
items:
  - id: plan-<obligationId>-<dimension>
    kind: planned_verification   # 新增
    obligationRef: QO-...
    summary:
      en: "..."
      zh-CN: "..."
    detail:
      dimension: behavior
      gapStatus: MISSING          # 维度级：MISSING | UNKNOWN
      missingEvidenceTypes: [api_test]
      suggestedEvidenceType: api_test
      benefitScore: 100
      costScore: 10
      priorityScore: -90
      rank: 1
```

约束：

- `extra = forbid`；枚举字面量校验。
- `detail` 保持 `dict[str, object]`；上表键为本迭代**约定字段**（测试与文档固定）。
- 加载器不得把 `QualityProposal`（含 `quality_plan`）当作 `QualityEvidence` 读入评估。

## CLI：`qcov plan`

**评估路径（与「复用 `_result_from_inputs`」刻意区分）：**

| 调用方式 | 行为 |
| --- | --- |
| 仅 `--config` | 与 `_policy_bundle` 相同：**解析配置内全部义务**，合并 evidence/mapping/markers 后逐义务 `evaluate_obligation`。对全部结果的 unproven 维度统一排序。 |
| `--obligation` + `--evidence`（无 `--config`） | 单义务评估（与 `gaps` 直接路径一致）。 |
| `--config` 与直接义务/证据组合 | **禁止**（对齐 `policy check` 的 `QCOV-CLI-003`），避免「看起来像全量 plan、实际只评一个」的歧义。 |

说明：当前 `gaps`/`check` 的 `_config_evaluation` **强制恰好一个义务**；`plan` **不得**照搬该助手，否则与「全量下一步验证」目标冲突。实现时应抽取或复用 `_policy_bundle` 的多义务加载逻辑。

- `--output`：可选写出 proposal YAML。
- `--output-format`：`markdown` | `json`。
- `--locale`：影响 markdown 文案；JSON/YAML 协议键仍为英文。
- **不提供** `--provider`（排序不经 `AIProvider`）。
- mapping diagnostics：可选附在 markdown 末尾（与 `gaps` 类似）；**不得**写入 `QualityProposal.items` 冒充计划项。
- 退出码：加载/映射/协议错误走现有输入错误路径；规划成功（含空 `items`）为 **0**。不因存在 gap 而非零退出。

## 错误

| 码 | 用途 |
| --- | --- |
| 既有 `ConfigLoadError` / `ProtocolLoadError` / `Mapping*` | 评估输入失败 |
| `QCOV-PROPOSAL-001` | 写出或校验 plan proposal 非法（若出现） |

一般不新增 `QCOV-PLAN-*`，除非实现中出现无法归入上表的失败。

## 测试策略

1. planner 单元：固定义务 + 维度状态 → `benefitScore` / `costScore` / `priorityScore` / 顺序 / tie-break 稳定。
2. 成本：多 `required_types` 时选最低成本为 `suggestedEvidenceType`；并列字典序。
3. 协议：`quality_plan` / `planned_verification` / `evaluation_gaps` 合法；非法枚举拒绝；Proposal 不当证据加载。
4. CLI：fixture → `qcov plan` 产出含 `rank` 的 draft；全 COVERED → 空 `items`、exit 0。
5. 回归：`obligation suggest` / `risk analyze` / `gaps` / `policy check` 行为不变。
6. 默认测试套件**无网络**。

## 文档与过程

- 更新双语公开页：`docs/en|zh-CN/roadmap.md`（Iteration 6 交付说明）、`concepts.md`（或等价）说明 `qcov plan` 为启发式提案。
- 必要时轻触 `architecture.md`：planner 引擎边界。
- `AGENTS.md`：允许在已批准设计与计划下实现 Iteration 6；重申提案非门禁。
- 过程记录：`docs/process/` 仅中文。

## 验收标准

1. `qcov plan` 在 `--config`（或义务+证据）下产出合法 draft `QualityProposal(type=quality_plan)`。
2. 排序由固定规则表决定，同输入同输出（含稳定 id / rank）。
3. Proposal / plan 文件存在时，不改变既有 gap 满足与 `policy check` 结果。
4. 全 COVERED 时空计划、exit 0。
5. 公开文档明确：plan 建议 ≠ 证据 ≠ 门禁。
6. `pytest` / `ruff` / `mypy qcov` / `python -m build` / `git diff --check` 通过。

## 与后续迭代的接口

- Iteration 7：Agent 消费稳定的 gaps JSON + `quality_plan` Proposal；本迭代保证 plan 可被机器解析且含 `rank` / 分数约定字段。
- Iteration 8：生产证据；与 Planner 无关。
- Post-8：可配置权重等需单独设计，不在本迭代暗含。
