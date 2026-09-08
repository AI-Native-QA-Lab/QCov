# Iteration 5：映射加固 + AI 提案（Obligation / Change Risk）设计

## 目标

在 4.5 显式映射与路线图 Gate（真实项目验证）之后，Iteration 5 完成三件事：

1. **5a 映射加固**：让显式 `@pytest.mark.qcov` 进入 `--config` 评估路径；按需提供
   **有限、声明式**的 identity 通配。映射仍不得从测试名推断 `obligationRef`。
2. **5b Obligation Assistant**：基于需求等相关上下文产出 **Proposal**（建议义务 /
   风险 / 建议证据），不写入权威证据。
3. **5c Change Risk Analyzer**：基于**本地** diff 与既有义务产出 **Proposal**
   （受影响义务 / 风险 / 建议证据）。

原则不变：

> AI proposes. Policy approves. Deterministic engine verifies.

落地顺序：`5a → 5b（含 provider 抽象与 Proposal IR）→ 5c`。
5c 复用同一 Proposal IR 与 provider 抽象。

本迭代为更纯粹的 Iteration 6（Quality Planner）、7（Agent Loop）、8（生产证据）铺路。
路线图依据：`docs/superpowers/specs/2026-09-08-post-4.5-iteration-roadmap-design.md`。

## 非目标

- 将 Proposal 自动合并为 `QualityEvidence` 或自动满足 Gap
- AI 覆盖 / 改写 `policy check` 或 Gap Engine 判定
- 默认把建议义务写回磁盘并生效（可提供显式「写出 proposal 文件」；批准流可后置）
- coverage.py / LCOV 提升为可满足的 `passed` 证据
- inventory → 义务的自动推断
- 远程 Git、Web UI、数据库持久化、外部插件 SDK
- `qcov plan`（Iteration 6）、Agent 闭环协议（Iteration 7）、生产证据（Iteration 8）
- 策略 DSL、维度阈值、路径豁免、通配符 waiver

## 现状与缺口

4.5 之后：

```text
junit/playwright inventory + EvidenceMapping ──► QualityEvidence ──► Gap / policy
手写 QualityEvidence ─────────────────────────────────────────────► Gap / policy
pytest.mark.qcov ──► QualityEvidence(status=unknown) ──► 仅计入 scan 计数
```

缺口：

1. marker 证据未稳定进入 `gaps` / `check` / `report` / `policy check` 合并路径。
2. identity 仅精确匹配；真实项目映射成本可能偏高（有限通配仍声明式）。
3. 无 Proposal 协议、无 AI provider 抽象、无 `obligation suggest` / `risk analyze`。

## 架构

```text
                    ┌──────────────── 5a ────────────────┐
qcov.yaml ──► scan / marker collect ──► merge evidence ──► Gap / policy
mapping[] ──► mapping engine（精确 + 可选有限通配）──────┘

                    ┌──────────────── 5b / 5c ─────────────┐
context（需求 / 本地 diff / 既有义务）
        │
        ▼
 AIProvider（抽象；默认 offline）
        │
        ▼
 QualityProposal（draft）──► 写出文件 / stdout
        │
        ✕ 不进入 Gap 满足关系
        ✕ 不改写 policy 判定
```

| 组件 | 职责 |
| --- | --- |
| `qcov.models.protocol` | `QualityProposal` 及条目模型；Schema |
| `qcov.ai.provider` | `AIProvider` 协议；`OfflineProvider`；可选显式配置的远程 provider 壳 |
| `qcov.ai.propose` / `context` | 组装上下文 → 调用 provider → 校验 Proposal |
| `qcov.engine.mapping` | 5a：可选有限 identity 通配 |
| `qcov.cli.app` | `obligation suggest`、`risk analyze`；评估路径直接收集 pytest marker |
| Gap / policy | **不改**判定语义 |

## 协议：`QualityProposal`

沿用 `qcov.dev/v1alpha1`，新增 kind（名称固定为 `QualityProposal`）：

```yaml
apiVersion: qcov.dev/v1alpha1
kind: QualityProposal
metadata:
  id: QP-20260908-001
  createdAt: "2026-09-08T12:00:00+08:00"
proposal:
  type: obligation_suggest   # 或 change_risk
  status: draft              # 本迭代仅产出 draft
source:
  kind: requirements         # 或 local_diff
  refs: []                   # 路径、obligation id、git ref 等可审计引用
provider:
  name: offline
  model: null
items:
  - id: item-1
    kind: proposed_obligation  # 或 affected_obligation / suggested_evidence
    obligationRef: QO-REFUND-003   # 可选；新建义务时可为建议 id
    summary:
      en: "..."
      zh-CN: "..."
    detail: {}                 # 结构化草案；不得伪装成 QualityEvidence
```

约束：

- `extra = forbid`；`kind` 字面量校验。
- `proposal.status` 本迭代只允许 `draft`。
- Schema 放入 `schemas/proposal.schema.json`（或等价文件名）。
- 加载器不得把 `QualityProposal` 当作 `QualityEvidence` 读入评估。

## CLI

### `qcov obligation suggest`

- 需要 `--config`（或显式义务集）以提供已有义务上下文。
- 需求输入：文件路径选项（如 `--requirements`）和/或 stdin；至少一种。
- 默认输出：Markdown 或 JSON 的 Proposal 视图；可选 `--output` 写 YAML。
- **不**修改 obligations/evidence 文件，除非未来显式子命令（本迭代不做批准写回）。

### `qcov risk analyze`

- `--config` 必需。
- `--base` / `--head`：本地 git 可解析 ref（默认与 `qcov diff` 习惯对齐，只读本地对象）。
- 输出同为 `QualityProposal`（`type: change_risk`）。
- 不调用远程 Git host API。

### 现有命令

- `gaps` / `check` / `report` / `policy check`：**禁止**自动吞并 Proposal。
- JSON 报告若提及提案，仅可在独立字段（本迭代可不实现「提案附着报告」）。

退出码：输入/协议错误沿用 exit 4；provider 失败使用明确错误码字符串（见下），exit 4；
不因「有建议」而失败 gate。

## Provider 抽象

```python
class AIProvider(Protocol):
    def propose_obligations(self, context: ObligationSuggestContext) -> QualityProposal: ...
    def analyze_change(self, context: ChangeRiskContext) -> QualityProposal: ...
```

- 默认 **`offline`**：确定性、可测（基于启发式或测试 fixture）；无网络。
- 可选远程 provider：必须显式配置；密钥只来自环境变量；失败不得静默当作「无缺口」。
- 配置键（示意）：`qcov.yaml` 下 `ai.provider: offline | ...`；缺省 `offline`。

## 5a 映射加固

### pytest marker 进入评估

- `PytestAdapter.collect` 已产出带 `obligation.ref` 的 `QualityEvidence`（当前多为
  `unknown`）。
- `--config` 评估合并路径显式纳入这些记录（与手写 evidence、mapping 产物合并，
  冲突规则对齐 4.5：同 id 冲突致命）。
- **`unknown` 永不满足** required evidence（既有规则）。
- **本迭代第一刀不强制**「marker ↔ junit 同 identity 自动升格为 passed」。
  若真实项目验证需要该升格，作为 5a 第二刀单列任务，须仍保持声明式关联，
  禁止名称猜测。

### 有限 identity 通配

- 仅在 `EvidenceMapping` 的 `from.identity` 支持有限通配（推荐：仅后缀 `*`，
  或文档固定的一种模式；不做任意正则，除非实现计划证明测试矩阵可控）。
- 匹配 0 条 → 现有「未找到」类诊断；匹配多条且策略为「必须唯一」→ 对齐
  `QCOV-MAP-005` 精神的诊断；禁止静默取第一条充 passed。
- **禁止**通配或启发式填写 `to.obligationRef`。

### 仍保持 inventory-only

- coverage.py / LCOV：不可映射为 covering `passed` 证据。

## 错误码

| 码 | 含义 |
| --- | --- |
| `QCOV-PROPOSAL-001` | Proposal 协议校验失败 |
| `QCOV-PROPOSAL-002` | 缺少需求或 diff 等必要输入 |
| `QCOV-AI-001` | provider 未配置或名称未知 |
| `QCOV-AI-002` | provider 调用失败（含网络/鉴权）；不得当作 PASS |
| 既有 `QCOV-MAP-*` | 映射诊断；语义保持 |

## 测试策略

- 协议：合法/非法 `QualityProposal` 金样；拒绝把 Proposal 当 Evidence 加载。
- 5a：marker 合并进 `gaps` 的回归；`unknown` 不满足；有限通配的 0/1/多匹配。
- 5b/5c：`offline` provider 固定输出；CLI 写出 draft；评估命令不受 Proposal 文件影响。
- 默认测试套件**无网络**；远程 provider 仅可选测或 mock。

## 文档与过程

- 更新双语公开页：`docs/en|zh-CN/roadmap.md`（已在路线图修订中规划）、
  `mapping.md`（5a）、新增简短 proposal/AI 说明页或并入 concepts（实现计划定路径）。
- `AGENTS.md`：允许在已批准设计与计划下实现 Iteration 5 范围；重申 AI 非门禁权威。
- 过程记录：`docs/process/` 仅中文。

## 验收标准

1. 带 `@pytest.mark.qcov` 的项目在 `--config` 下可在 gaps/check 中看到对应证据行
   （即便 status 为 `unknown`）。
2. 可选有限通配行为与诊断可测且文档化。
3. `obligation suggest` / `risk analyze` 产出合法 `QualityProposal`（draft）。
4. Proposal 文件存在时，不改变既有 gate / gap 满足结果。
5. 默认 `offline` provider 下全量测试无网络依赖。
6. 公开文档明确：AI 建议 ≠ 证据 ≠ 门禁。

## 与后续迭代的接口

- Iteration 6：消费 gaps（及可选已批准义务）做 `qcov plan`；可读取 Proposal 但不依赖本迭代批准流。
- Iteration 7：稳定 JSON 契约给 Agent；本迭代只保证 Proposal / gaps JSON 可被机器解析。
- Iteration 8：生产证据；与 AI 提案无关。
