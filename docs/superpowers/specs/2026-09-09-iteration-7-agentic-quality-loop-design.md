# Iteration 7：Agentic Quality Loop（纯）设计

## 目标

在 Iteration 6（确定性 `qcov plan`）之后，交付**纯 Agentic Quality Loop 助手面**：

- 为 coding agent 提供稳定、可复现的机器可读契约与本地 CLI 助手。
- **必做** `qcov explain`：确定性解释 gap、plan item、以及证据为何未使维度 `COVERED`。
- **必做** `qcov agent next`：给出当前最高优先级的下一步验证（读 plan 或现场评估）。
- **可选** `qcov agent validate-evidence`：协议/loader 自检；不进入硬验收。
- 形态上支持闭环：**消费 gaps/plan → 选择验证 →（外部）执行 → 产出证据 → `qcov` gaps / policy check**。
- QCov **不**执行测试、**不**写入权威证据、**不**绕过 hard gate。

原则不变：

> AI proposes. Policy approves. Deterministic engine verifies.

路线图依据：`docs/superpowers/specs/2026-09-08-post-4.5-iteration-roadmap-design.md`。
公开路线图原文将 `explain` 标为 optional；**本迭代将其升为必交付**，并同步更新公开 `roadmap` / `requirements`。

## 非目标

- 执行测试、生成/写入权威 `QualityEvidence`、自动改配置或义务
- `qcov agent loop` 编排器、远程 LLM / Agent 运行时、Web UI、持久化
- 改 Gap Engine / `policy check` 判定语义
- 第二套优先级排序（不得平行于 `build_quality_plan`）
- coverage/LCOV 提升为 passed 证据、inventory → 义务推断
- 生产证据生产者（Iteration 8）
- 策略 DSL、维度阈值、路径/通配符豁免、远程 Git、外部插件 SDK

## 决策摘要

| 议题 | 选择 |
| --- | --- |
| 交付形态 | 方案 1：纯引擎助手 + CLI（契约 + playbook） |
| 必做命令 | `explain`、`agent next` |
| 可选命令 | `agent validate-evidence`（软验收） |
| `next` 输入 | `--plan` 或 `--config` / 义务+证据（对齐 `plan` 互斥规则） |
| 输出习惯 | `--format markdown\|json`（默认 markdown；JSON 为稳定契约） |
| `explain` 深度 | gap + plan item + 证据未满足原因（派生规则表） |
| `contractVersion` | 仅新命令 JSON 外壳；不改既有 gaps / proposal schema |
| 排序权威 | 唯一 = 既有 planner / plan 文件中的 `rank` |

## 架构

```text
现有 Gap 评估 / build_quality_plan（排序唯一权威）
              │
    ┌─────────┴─────────┐
    ▼                   ▼
qcov.engine.explain   qcov.engine.agent_next
 · 规则表派生 reasons   · 复用 plan rank / planner
 · 不改 evaluate_*      · 不重算另一套分数
              │
              ▼
CLI：explain / agent next  [可选 validate-evidence]
              │
     --format markdown | json
     json 外壳：contractVersion + command + payload
              │
     ✕ 不进入 Gap 满足
     ✕ 不改写 policy
     ✕ 不执行测试
```

| 组件 | 职责 |
| --- | --- |
| `qcov.engine.explain` | 纯函数：从评估结果 / plan item / 证据列表派生结构化 Explanation |
| `qcov.engine.agent_next` | 纯函数：从 `QualityProposal(type=quality_plan)` 或现场 `build_quality_plan` 取 top-N |
| `qcov.cli.app` | `explain`、`agent` 子命令组（`next`；可选 `validate-evidence`） |
| Agent 契约 | Pydantic `qcov.models.agent_contract`（`extra=forbid`）；不另维护运行时 JSON Schema 文件 |
| Gap / policy / planner 评分 | **不改**判定与排序语义 |

## CLI

共用：`--format markdown|json`（默认 markdown）、`--locale en|zh-CN`（影响 markdown；JSON 键仍为英文）。

### `qcov explain`

| 模式 | 触发 | 行为 |
| --- | --- | --- |
| gap | `--config` + ids，或 `--obligation`+`--evidence` + ids（默认 `--mode gap`） | 评估后解释该维度状态与派生 `reasons` |
| plan-item | `--plan` + `--item-id` | 解释该 `planned_verification` 项（含 rank/分数摘要）；**不**重新排序 |
| evidence | `--obligation` + `--evidence` + ids + `--mode evidence` | 对给定证据列出为何不能使该维度 `COVERED` 的派生码 |

- gap 模式下 `--config` 与直接义务/证据组合：**禁止**（`QCOV-CLI-003`）。
- 直接义务+证据默认 `--mode gap`；`--mode evidence` 走证据缺陷派生。
- 缺少模式所需参数：输入错误（现有 `QCOV-CLI-*` / `ConfigLoadError` 风格）。
- 退出码：加载/协议错误走现有输入错误路径；解释成功为 **0**。

### `qcov agent next`

| 调用方式 | 行为 |
| --- | --- |
| `--plan PATH` | 加载 proposal；要求 `type=quality_plan`；按 `rank` 取前 `--limit`（默认 **1**） |
| `--config`（无 `--plan`） | 与 `qcov plan` 相同多义务评估 → `build_quality_plan` → 取前 N |
| `--obligation` + `--evidence`（无 `--plan`/`--config`） | 单义务路径，同 `plan` |
| `--config` 与直接义务/证据 | **禁止**（`QCOV-CLI-003`） |
| `--plan` 与 `--config` / 直接输入 | **禁止**（`QCOV-CLI-006`） |

- 默认**不**写出 proposal；本迭代**不要求**实现 `--output`（需要落盘时用 `qcov plan --output`）。
- 空计划：`payload.items: []`，exit **0**。
- 排序不得另起规则：现场路径必须调用 `build_quality_plan`。

### `qcov agent validate-evidence`（可选）

- 输入：`--evidence` 文件或目录（glob 行为对齐现有证据加载）。
- 行为：逐文件 `load_evidence`；成功列出 id；失败报告 protocol 错误。
- Markdown / JSON 均须标明：`validForLoad=true` **不**表示维度 `COVERED`，也 **不**表示 `policy check` PASS。
- 不修改文件；不做推断匹配。

## Agent JSON 契约

仅适用于本迭代新命令的 `--format json` 输出。既有 `gaps` / `plan` / proposal YAML **不**强制包此外壳。

```json
{
  "contractVersion": "qcov.agent/v1",
  "command": "explain",
  "payload": {}
}
```

| 字段 | 约定 |
| --- | --- |
| `contractVersion` | 字面量 `qcov.agent/v1`（本迭代冻结） |
| `command` | `explain` \| `agent.next` \| `agent.validate_evidence` |
| `payload` | 见下；键为英文；JSON Schema / 模型校验均 **`extra = forbid`** |

### `explain` payload（约定字段）

- `mode`: `gap` \| `plan_item` \| `evidence`
- `obligationId`, `dimension`（适用时）
- `status`: 维度级 `COVERED` \| `MISSING` \| `UNKNOWN`（若可知）
- `requiredTypes`: string[]（gap/evidence：义务维度所需类型；plan_item 为空）
- `missingEvidenceTypes`: string[]（仅 plan_item：对齐 plan detail 的 missingEvidenceTypes）
- `observedEvidenceIds`: string[]
- `reasons`: 对象数组，每项含稳定 `code` + `summary.en` / `summary.zh-CN`
- plan-item 模式另含：`itemId`, `rank`, `priorityScore`, `suggestedEvidenceType` 等与 plan detail 对齐的只读摘要

### `agent.next` payload（约定字段）

- `source`: `plan_file` \| `evaluation`
- `limit`: number
- `items`: 数组；元素字段对齐 `planned_verification` 的约定 detail（至少含 obligation 引用、dimension、suggestedEvidenceType、rank、priorityScore、item id）
- 空计划时 `items` 为 `[]`

### `agent.validate_evidence` payload（可选命令）

- `files`: 每项含 `path`, `validForLoad`, `evidenceId`（成功时）, `error`（失败时）
- 顶层可含 `allValidForLoad: boolean`
- `disclaimer`: `{en, zh-CN}`，明确 `validForLoad` ≠ COVERED ≠ policy PASS
- 文案/字段不得把加载成功写成 `COVERED` / `PASS`

## 派生 reason 码（本迭代冻结）

由 explain **规则表**从义务引用、维度、类型、`execution.status`、观测集合派生；**不**修改 `evaluate_obligation`，**不**在 Gap Engine 新增 reason 字段。

| code | 含义（简述） |
| --- | --- |
| `NO_EVIDENCE_FOR_OBLIGATION` | 无指向该义务的证据 |
| `OBLIGATION_REF_MISMATCH` | 证据 `obligation.ref` 不匹配目标义务 |
| `DIMENSION_MISMATCH` | 证据维度与目标维度不一致 |
| `TYPE_NOT_REQUIRED` | 证据 type 不在该维度 `required_types` 中 |
| `STATUS_NOT_PASSED` | 匹配路径上存在证据但无一 `passed`（且非 unknown 主导） |
| `STATUS_UNKNOWN` | 匹配证据含 `unknown`，维度为 `UNKNOWN` |
| `ALREADY_COVERED` | 维度已是 `COVERED`（解释仍成功，reasons 可仅含此码） |

约束：

- 一条解释可含多个 code；输出顺序为 **code 字典序**（稳定）。
- 本迭代不扩展上表以外的码；新增码需改设计。

## 错误

| 码 | 用途 |
| --- | --- |
| 既有 `ConfigLoadError` / `ProtocolLoadError` / `Mapping*` / `QCOV-CLI-003` | 评估与互斥输入 |
| `QCOV-CLI-006` | `--plan` 与 `--config` / 直接义务证据同时出现（`005` 已用于 locale） |
| `QCOV-AGENT-001` | `--plan` 不是 `type=quality_plan` 的合法 proposal |
| `QCOV-AGENT-002` | explain / next 目标找不到（未知 obligationId、dimension、item-id） |
| `QCOV-AGENT-003` | `--limit` 非法（必须 ≥ 1） |

成功路径的 JSON 始终含完整外壳；失败不输出半截契约 JSON（对齐现有 CLI）。

## 测试策略

1. explain 单元：固定义务+证据夹具 → 稳定 `reasons` 码与顺序；不改变 `evaluate_obligation` 金样。
2. agent_next 单元：同一夹具下 top-1 与 `build_quality_plan` 首项一致；空计划 `items=[]`。
3. CLI：三种 explain 模式；`agent next` 的 `--plan` 与 `--config` 路径；JSON 含 `contractVersion`。
4. 回归：`gaps` / `plan` / `policy check` / proposal 不当证据 行为不变。
5. 可选：validate-evidence 合法/非法文件；断言文案或字段含 `validForLoad` 且不宣称 COVERED。
6. 默认测试套件**无网络**。

## 文档与过程

- 设计：本文档（`docs/superpowers/specs/`，中文）。
- 计划：批准后另写 `docs/superpowers/plans/2026-09-09-iteration-7-agentic-quality-loop.md`。
- 过程记录：`docs/process/` 仅中文。
- 公开双语：`docs/en|zh-CN/roadmap.md`（Iteration 7 交付；explain 为必做）、`requirements.md`；新增或并入 Agent playbook（建议命令序：`gaps`/`plan` → `agent next` → 外部执行 → 写证据 → `gaps`/`policy check`）。
- 必要时轻触 `architecture.md` / `concepts.md`：agent 助手边界与 `contractVersion`。
- `AGENTS.md`：允许在已批准设计与计划下实现 Iteration 7；重申提案/解释非门禁。

## 验收标准

**硬验收**

1. `qcov explain` 三种模式可运行；JSON 含 `contractVersion: qcov.agent/v1` 与稳定 `reasons`。
2. `qcov agent next` 支持 `--plan` 与评估输入；同输入首项与 planner 一致；空计划 exit 0。
3. 不改变 Gap / policy / 既有 gaps·plan JSON 语义；proposal 仍不能当 evidence。
4. 公开文档与 `AGENTS.md` 已更新；Agent playbook 说明闭环中外部执行与门禁边界。
5. `pytest` / `ruff` / `mypy qcov` / `python -m build` / `git diff --check` 通过。

**软验收**

- `qcov agent validate-evidence` 已实现且明确 `validForLoad` ≠ COVERED ≠ policy PASS；未实现不挡 Iteration 7 关闭。

## 与后续迭代的接口

- ← Iteration 6：消费 `quality_plan` 的 `rank` / 分数字段与 gaps 评估；不平行再造排序。
- → Iteration 8：生产证据仍走 inventory / 显式证据协议；本迭代契约不预留生产专用命令。
- Post-8：可配置 explain 文案、更多 reason、agent loop 运行时等需单独设计，不在本迭代暗含。

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| explain 范围膨胀 | 冻结初版 reason 枚举；只派生、不改引擎 |
| 破坏现有 JSON 消费者 | `contractVersion` 外壳仅限新命令 |
| validate 被误当门禁 | `validForLoad` 字段 + 文档；硬验收可不含该命令 |
| 与公开 roadmap「optional explain」不一致 | 交付时改写公开 roadmap / requirements |
