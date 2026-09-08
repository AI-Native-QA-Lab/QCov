# Iteration 5 实现计划：映射加固 + AI 提案

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans 或按任务 TDD 执行。Steps 使用 checkbox（`- [ ]`）跟踪。

**Goal:** 落地 5a（pytest marker 进评估 + 有限 identity 后缀通配）与 5b/5c（`QualityProposal` + offline AIProvider + `obligation suggest` / `risk analyze`），且 Proposal 永不进入 Gap 满足。

**Architecture:** 评估路径合并 marker 证据；mapping 引擎支持 `identity` 后缀 `*`；新增 Proposal 协议与 `qcov.ai`；CLI 子命令只产出 draft Proposal。

**Tech Stack:** Python 3.11+、Pydantic v2、Typer、PyYAML、pytest、Ruff、mypy。

**Spec:** `docs/superpowers/specs/2026-09-08-iteration-5-ai-proposal-mapping-design.md`

## 全局约束

- 先 RED 再 GREEN；AI 非证据/门禁；无网络默认测试。
- coverage/LCOV 仍不可 covering；禁止推断 `obligationRef`。
- 最终门禁：`pytest`、`ruff check .`、`mypy qcov`、`python3 -m build`、`git diff --check`。
- 开发过程文档仅中文；公开 `docs/en|zh-CN` 仍双语。

## 文件结构（预定）

| 路径 | 职责 |
| --- | --- |
| `qcov/engine/markers.py` | 从项目根收集 pytest marker → `QualityEvidence` |
| `qcov/engine/mapping.py` | 后缀 `*` identity 匹配 |
| `qcov/cli/app.py` | 评估合并 marker；`obligation`/`risk` 子命令 |
| `qcov/models/protocol.py` | `QualityProposal` |
| `schemas/proposal.schema.json` | Proposal schema |
| `qcov/ai/provider.py` | `AIProvider` + `OfflineProvider` |
| `qcov/engine/propose.py` | 组装上下文并校验 Proposal |
| `tests/...` | 对应 RED/GREEN |

---

### Task 1: pytest marker 进入 `--config` 评估

**Files:** Create `qcov/engine/markers.py`；Modify `qcov/cli/app.py`；Test `tests/engine/test_markers.py`、`tests/cli/test_markers_eval.py`

- [x] RED：`--config` 下仅有 marker（无手写 evidence / 可无 mapping）时，`gaps` JSON 能看到对应 `unknown` 证据且不满足 COVERED
- [x] 实现 `collect_marker_evidence(project_root)`；`_config_evaluation` 合并 marker；放宽「至少一份 evidence」门槛（有 mapping **或** marker **或** authored evidence）
- [x] GREEN + 回归既有 map/gaps 测试

### Task 2: 有限 identity 后缀通配

**Files:** `qcov/engine/mapping.py`；`tests/engine/test_mapping.py`；双语 `docs/en|zh-CN/mapping.md`

- [x] RED：`identity: "refund.*"` 匹配唯一 → 物化；匹配 0 → MAP-001；匹配多 → MAP-005；精确匹配回归
- [x] 实现：仅当 identity 以 `*` 结尾且仅含一个 `*`（后缀通配）；否则仍精确相等
- [x] GREEN + 文档说明

### Task 3: QualityProposal 协议与加载

**Files:** `qcov/models/protocol.py`、`io.py`、`__init__.py`；`schemas/proposal.schema.json`；`tests/models/test_protocol.py`、`test_io.py`

- [x] RED：合法 draft proposal；非法 status/kind；`load_proposal`；证据加载器拒绝 Proposal kind
- [x] GREEN

### Task 4: Offline AIProvider + propose 引擎

**Files:** Create `qcov/ai/__init__.py`、`qcov/ai/provider.py`、`qcov/engine/propose.py`；`tests/ai/test_offline_provider.py`、`tests/engine/test_propose.py`

- [x] RED：`propose_obligations` / `analyze_change` 返回可校验的 draft；缺输入 → `QCOV-PROPOSAL-002`；未知 provider → `QCOV-AI-001`
- [x] Offline：确定性条目（例如从需求文本提取已有义务 id 提及，或固定「至少一条 suggested_evidence」启发式——以测试金样锁定）
- [x] GREEN

### Task 5: CLI `obligation suggest` / `risk analyze`

**Files:** `qcov/cli/app.py`；`tests/cli/test_propose.py`；必要时 `qcov/models/config.py` 增加 `ai.provider`（缺省 offline）

- [x] RED：suggest 需 requirements；risk 用本地 git fixture；`--output` 写 YAML；gaps 不读取 proposal 文件
- [x] GREEN

### Task 6: 文档、AGENTS、过程记录与门禁

**Files:** 双语 mapping/concepts 或简短 AI 页；`AGENTS.md`；`docs/process/2026-09-08-iteration-5-*.md`；示例可选

- [x] 公开文档写明 AI ≠ 证据 ≠ 门禁
- [x] 全量门禁通过；过程记录写入真实命令与结果

---

## 执行说明

按 Task 1→6 顺序。每任务内严格 TDD。用户未要求时可不自动 `git commit`；逻辑完成后由用户决定提交。
