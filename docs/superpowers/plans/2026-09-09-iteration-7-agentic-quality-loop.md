# Iteration 7 实现计划：Agentic Quality Loop

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans。Steps 使用 checkbox（`- [ ]`）跟踪。

**Goal:** 交付 `qcov explain` 与 `qcov agent next`（稳定 `contractVersion: qcov.agent/v1` JSON），可选 `qcov agent validate-evidence`；不执行测试、不改 Gap/policy 语义。

**Architecture:** 新增纯引擎 `qcov.engine.explain`（派生 reason 码）与 `qcov.engine.agent_next`（复用 `build_quality_plan` / plan 文件 `rank`）；CLI 薄封装；agent JSON 外壳仅限新命令，不改既有 gaps/proposal schema。

**Tech Stack:** Python 3.11+、Pydantic v2、Typer、PyYAML、pytest、Ruff、mypy。

**Spec:** `docs/superpowers/specs/2026-09-09-iteration-7-agentic-quality-loop-design.md`

## 全局约束

- 严格 TDD：每行为先 RED 再 GREEN；在 `docs/process/2026-09-09-iteration-7-agentic-quality-loop.md` 记录真实命令输出。
- 排序唯一权威 = `build_quality_plan` / plan 内 `rank`；explain 不改 `evaluate_obligation`。
- `contractVersion` 仅出现在新命令 `--format json` 外壳。
- 默认测试无网络。
- 最终门禁：`pytest`、`ruff check .`、`mypy qcov`、`python3 -m build`、`git diff --check`。
- 开发过程文档仅中文；公开 `docs/en|zh-CN` 双语。
- Task 6（validate-evidence）为**可选**；未做不挡硬验收。

## 文件结构（预定）

| 路径 | 职责 |
| --- | --- |
| `qcov/models/agent_contract.py` | Agent JSON 外壳与 payload 的 Pydantic 模型（`extra=forbid`） |
| `qcov/models/errors.py` | `AgentInputError`（`QCOV-AGENT-001/002`） |
| `schemas/agent-contract.schema.json` | 与模型同步的 JSON Schema |
| `qcov/engine/explain.py` | 派生 reasons；三种解释入口 |
| `qcov/engine/agent_next.py` | 从 proposal 取 top-N |
| `qcov/cli/app.py` | `explain`；`agent` typer 组（`next`；可选 `validate-evidence`） |
| `tests/models/test_agent_contract.py` | 契约模型 |
| `tests/engine/test_explain.py` | reason 规则与稳定性 |
| `tests/engine/test_agent_next.py` | 与 planner 首项一致 |
| `tests/cli/test_explain.py`、`tests/cli/test_agent.py` | CLI |
| `docs/en|zh-CN/agent.md` | Agent playbook（新页） |
| `docs/en|zh-CN/roadmap.md`、`requirements.md`、`concepts.md` | 公开说明 |
| `AGENTS.md` | Iteration 7 范围 |
| `docs/process/2026-09-09-iteration-7-agentic-quality-loop.md` | 过程记录 |

---

### Task 1: Agent 契约模型与错误类型

**Files:**
- Create: `qcov/models/agent_contract.py`
- Modify: `qcov/models/errors.py`
- Create: `schemas/agent-contract.schema.json`
- Create: `tests/models/test_agent_contract.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/models/test_agent_contract.py
from __future__ import annotations

import pytest
from pydantic import ValidationError

from qcov.models.agent_contract import AgentEnvelope


def test_agent_envelope_accepts_explain_payload() -> None:
    envelope = AgentEnvelope.model_validate(
        {
            "contractVersion": "qcov.agent/v1",
            "command": "explain",
            "payload": {
                "mode": "gap",
                "obligationId": "QO-REFUND-001",
                "dimension": "behavior",
                "status": "MISSING",
                "requiredTypes": ["api_test"],
                "observedEvidenceIds": [],
                "reasons": [
                    {
                        "code": "NO_EVIDENCE_FOR_OBLIGATION",
                        "summary": {
                            "en": "No evidence references this obligation.",
                            "zh-CN": "没有指向该义务的证据。",
                        },
                    }
                ],
            },
        }
    )
    assert envelope.contract_version == "qcov.agent/v1"
    assert envelope.command == "explain"
    assert envelope.payload.mode == "gap"


def test_agent_envelope_rejects_unknown_contract_version() -> None:
    with pytest.raises(ValidationError):
        AgentEnvelope.model_validate(
            {
                "contractVersion": "qcov.agent/v0",
                "command": "explain",
                "payload": {
                    "mode": "gap",
                    "obligationId": "QO-1",
                    "dimension": "behavior",
                    "status": "MISSING",
                    "requiredTypes": [],
                    "observedEvidenceIds": [],
                    "reasons": [],
                },
            }
        )


def test_agent_input_error_codes() -> None:
    from qcov.models.errors import AgentInputError

    assert AgentInputError.CODE_NOT_QUALITY_PLAN == "QCOV-AGENT-001"
    assert AgentInputError.CODE_TARGET_NOT_FOUND == "QCOV-AGENT-002"
```

- [ ] **Step 2: 运行确认 RED**

```bash
python3 -m pytest tests/models/test_agent_contract.py -v
```

Expected: FAIL（模块不存在）

- [ ] **Step 3: 最小实现**

在 `qcov/models/errors.py` 增加：

```python
class AgentInputError(ValueError):
    """Stable errors for agent CLI inputs and targets."""

    CODE_NOT_QUALITY_PLAN = "QCOV-AGENT-001"
    CODE_TARGET_NOT_FOUND = "QCOV-AGENT-002"

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")
```

在 `qcov/models/agent_contract.py` 实现（与现有 `ProtocolModel` 同风格，`extra=forbid`，别名 camelCase）：

- `CONTRACT_VERSION = "qcov.agent/v1"`
- `ReasonItem`：`code` Literal 冻结为规格表七码；`summary: LocalizedText`
- `ExplainPayload`：`mode`、`obligationId`、`dimension`、`status`、`requiredTypes`、`observedEvidenceIds`、`reasons`；plan_item 可选字段 `itemId`/`rank`/`priorityScore`/`suggestedEvidenceType` 用 `Optional` 默认 None
- `NextItem` / `NextPayload`：`source`、`limit`、`items`
- `ValidateFileResult` / `ValidatePayload`（供可选 Task 6；Task 1 可先定义以便 schema 完整）
- `AgentEnvelope`：`contractVersion`、`command` Literal[`explain`,`agent.next`,`agent.validate_evidence`]、`payload` 用 discriminated union 或按 command 校验

同步写 `schemas/agent-contract.schema.json`（至少覆盖 envelope + explain/next）。

- [ ] **Step 4: 运行确认 GREEN**

```bash
python3 -m pytest tests/models/test_agent_contract.py -v
```

- [ ] **Step 5: Commit**（仅当用户要求提交时执行；否则跳过）

```bash
git add qcov/models/agent_contract.py qcov/models/errors.py schemas/agent-contract.schema.json tests/models/test_agent_contract.py
git commit -m "$(cat <<'EOF'
feat: add agent contract models for iteration 7

EOF
)"
```

---

### Task 2: `qcov.engine.explain` 派生规则

**Files:**
- Create: `qcov/engine/explain.py`
- Create: `tests/engine/test_explain.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/engine/test_explain.py
from __future__ import annotations

from qcov.engine.explain import explain_gap, explain_evidence
from qcov.engine.gaps import evaluate_obligation
from qcov.models.protocol import CoverageStatus, QualityEvidence, TestingObligation


def _obl() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {"id": "QO-REFUND-001", "title": {"en": "Refund", "zh-CN": "退款"}},
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {"behavior": ["api_test"]},
        }
    )


def _ev(**overrides: object) -> QualityEvidence:
    raw: dict = {
        "apiVersion": "qcov.dev/v1alpha1",
        "kind": "QualityEvidence",
        "metadata": {"id": "QE-1"},
        "obligation": {"ref": "QO-REFUND-001"},
        "evidence": {"dimension": "behavior", "type": "api_test"},
        "producer": {"name": "pytest"},
        "execution": {"status": "failed", "timestamp": "2026-09-02T00:00:00+00:00"},
        "artifact": {"path": "t.py"},
        "confidence": {"deterministic": True, "reproducible": True},
    }
    for key, value in overrides.items():
        if key == "ref":
            raw["obligation"]["ref"] = value
        elif key == "dimension":
            raw["evidence"]["dimension"] = value
        elif key == "type":
            raw["evidence"]["type"] = value
        elif key == "status":
            raw["execution"]["status"] = value
        elif key == "id":
            raw["metadata"]["id"] = value
    return QualityEvidence.model_validate(raw)


def test_explain_gap_no_evidence_stable_reason_order() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [])
    payload = explain_gap(obl, result, "behavior")
    codes = [item.code for item in payload.reasons]
    assert codes == sorted(codes)
    assert "NO_EVIDENCE_FOR_OBLIGATION" in codes
    assert payload.status == CoverageStatus.UNKNOWN.value


def test_explain_evidence_emits_mismatch_codes() -> None:
    obl = _obl()
    payload = explain_evidence(
        obl,
        [_ev(ref="QO-OTHER", dimension="boundary", type="e2e_test", status="failed")],
        "behavior",
    )
    codes = {item.code for item in payload.reasons}
    assert "OBLIGATION_REF_MISMATCH" in codes
    assert "DIMENSION_MISMATCH" in codes
    assert "TYPE_NOT_REQUIRED" in codes


def test_explain_gap_already_covered() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [_ev(status="passed")])
    payload = explain_gap(obl, result, "behavior")
    assert [item.code for item in payload.reasons] == ["ALREADY_COVERED"]
```

另加：`explain_plan_item` 从 `ProposalItem` 组装只读摘要（含 rank）；未知 dimension → 由调用方抛 `AgentInputError`（引擎可抛或返回由 CLI 处理——**本计划约定引擎抛 `AgentInputError`**）。

- [ ] **Step 2: RED**

```bash
python3 -m pytest tests/engine/test_explain.py -v
```

- [ ] **Step 3: 实现 `qcov/engine/explain.py`**

公开函数：

```python
def explain_gap(
    obligation: TestingObligation,
    result: ObligationResult,
    dimension: str,
) -> ExplainPayload: ...

def explain_evidence(
    obligation: TestingObligation,
    evidence: Sequence[QualityEvidence],
    dimension: str,
) -> ExplainPayload: ...

def explain_plan_item(item: ProposalItem) -> ExplainPayload: ...
```

规则（与规格一致）：

| 条件 | code |
| --- | --- |
| 无 `obligation.ref == id` 的证据 | `NO_EVIDENCE_FOR_OBLIGATION` |
| 证据 ref 不匹配（evidence 模式逐条） | `OBLIGATION_REF_MISMATCH` |
| 维度不匹配 | `DIMENSION_MISMATCH` |
| type ∉ required_types | `TYPE_NOT_REQUIRED` |
| 维度 `UNKNOWN`（含 unknown status） | `STATUS_UNKNOWN` |
| 维度 `MISSING`（有义务相关证据但未 COVERED） | `STATUS_NOT_PASSED` |
| 维度 `COVERED` | `ALREADY_COVERED` |

`reasons` 按 `code` 字典序排序；summary 中英固定字符串表（模块内常量）。

- [ ] **Step 4: GREEN**

```bash
python3 -m pytest tests/engine/test_explain.py -v
```

- [ ] **Step 5: Commit**（用户要求时）

```bash
git commit -m "$(cat <<'EOF'
feat: add deterministic explain engine with frozen reason codes

EOF
)"
```

---

### Task 3: `qcov.engine.agent_next`

**Files:**
- Create: `qcov/engine/agent_next.py`
- Create: `tests/engine/test_agent_next.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/engine/test_agent_next.py
from __future__ import annotations

from qcov.engine.agent_next import select_next_actions
from qcov.engine.gaps import evaluate_obligation
from qcov.engine.planner import build_quality_plan
from qcov.models.errors import AgentInputError
from qcov.models.protocol import QualityProposal, TestingObligation
import pytest


def _obl() -> TestingObligation:
    return TestingObligation.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "TestingObligation",
            "metadata": {"id": "QO-REFUND-001", "title": {"en": "Refund", "zh-CN": "退款"}},
            "source": {"type": "requirement", "ref": "REFUND-001"},
            "risk": {"domain": "financial", "severity": "critical"},
            "requiredEvidence": {
                "behavior": ["api_test"],
                "boundary": ["property_test"],
            },
        }
    )


def test_select_next_matches_planner_first_item() -> None:
    obl = _obl()
    result = evaluate_obligation(obl, [])
    plan = build_quality_plan([result], [obl], refs=["fixture"])
    payload = select_next_actions(plan, limit=1, source="evaluation")
    assert payload.limit == 1
    assert len(payload.items) == 1
    assert payload.items[0].id == plan.items[0].id
    assert payload.items[0].rank == 1


def test_select_next_empty_plan() -> None:
    plan = QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {"id": "QP-empty", "createdAt": "2026-09-08T00:00:00+00:00"},
            "proposal": {"type": "quality_plan", "status": "draft"},
            "source": {"kind": "evaluation_gaps", "refs": []},
            "provider": {"name": "offline", "model": None},
            "items": [],
        }
    )
    payload = select_next_actions(plan, limit=1, source="plan_file")
    assert payload.items == []


def test_select_next_rejects_non_quality_plan() -> None:
    plan = QualityProposal.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityProposal",
            "metadata": {"id": "QP-x", "createdAt": "2026-09-08T00:00:00+00:00"},
            "proposal": {"type": "obligation_suggest", "status": "draft"},
            "source": {"kind": "requirements", "refs": []},
            "provider": {"name": "offline", "model": None},
            "items": [],
        }
    )
    with pytest.raises(AgentInputError) as exc:
        select_next_actions(plan, limit=1, source="plan_file")
    assert exc.value.code == AgentInputError.CODE_NOT_QUALITY_PLAN
```

- [ ] **Step 2: RED** → **Step 3: 实现**

```python
# qcov/engine/agent_next.py
def select_next_actions(
    proposal: QualityProposal,
    *,
    limit: int,
    source: Literal["plan_file", "evaluation"],
) -> NextPayload:
    if proposal.proposal.type != "quality_plan":
        raise AgentInputError(
            AgentInputError.CODE_NOT_QUALITY_PLAN,
            "proposal type must be quality_plan",
        )
    if limit < 1:
        raise AgentInputError(AgentInputError.CODE_TARGET_NOT_FOUND, "limit must be >= 1")
    # items already ordered by rank from planner; take first `limit`
    ...
```

将每个 `ProposalItem` 映射为 `NextItem`（从 `detail` 读取 rank / dimension / scores / suggestedEvidenceType；`obligationRef` 来自 item）。

- [ ] **Step 4: GREEN**

```bash
python3 -m pytest tests/engine/test_agent_next.py -v
```

- [ ] **Step 5: Commit**（用户要求时）

---

### Task 4: CLI `qcov explain`

**Files:**
- Modify: `qcov/cli/app.py`
- Create: `tests/cli/test_explain.py`

- [ ] **Step 1: 写失败测试**

复用 `tests/cli/test_plan.py` 的 `_write_project` 模式（可抽到 conftest，但本计划允许在 `test_explain.py` 内复制最小 fixture）。

```python
def test_explain_gap_json_has_contract_version(tmp_path: Path) -> None:
    config = _write_project(tmp_path)  # behavior covered only
    result = runner.invoke(
        app,
        [
            "explain",
            "--config",
            str(config),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "boundary",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["contractVersion"] == "qcov.agent/v1"
    assert payload["command"] == "explain"
    assert payload["payload"]["mode"] == "gap"
    assert payload["payload"]["reasons"]


def test_explain_plan_item(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    runner.invoke(app, ["plan", "--config", str(config), "--output", str(plan_path)])
    plan = yaml.safe_load(plan_path.read_text())
    item_id = plan["items"][0]["id"]
    result = runner.invoke(
        app,
        ["explain", "--plan", str(plan_path), "--item-id", item_id, "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["payload"]["mode"] == "plan_item"
    assert body["payload"]["itemId"] == item_id


def test_explain_evidence_mode(tmp_path: Path) -> None:
    obl = tmp_path / "obligation.yaml"
    obl.write_text(Path("examples/refund/obligation.yaml").read_text())
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        Path("examples/refund/evidence/behavior.yaml")
        .read_text()
        .replace("QO-REFUND-001", "QO-OTHER")
    )
    result = runner.invoke(
        app,
        [
            "explain",
            "--obligation",
            str(obl),
            "--evidence",
            str(bad),
            "--obligation-id",
            "QO-REFUND-001",
            "--dimension",
            "behavior",
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    codes = {r["code"] for r in json.loads(result.output)["payload"]["reasons"]}
    assert "OBLIGATION_REF_MISMATCH" in codes
```

再测：未知 dimension → exit 非 0 且含 `QCOV-AGENT-002`；`--config`+直接输入 → `QCOV-CLI-003`。

- [ ] **Step 2: RED** → **Step 3: 实现 CLI**

- `@app.command("explain")`
- 分支：`plan`+`item-id` → plan_item；否则若提供评估输入 + obligation-id + dimension → 若仅义务+证据且意图解释证据集合用 evidence 模式：**判定规则**——当 `--plan` 缺省且提供 `--obligation`+`--evidence`+ids 时走 **evidence**；当 `--config`（或义务+证据用于评估）+ids 且需要 gap 状态时走 **gap**。  
  **钉死（避免歧义）：**
  - `--plan` + `--item-id` → plan_item（禁止评估输入，`QCOV-CLI-006`）
  - `--config` + `--obligation-id` + `--dimension` → gap（禁止直接义务/证据）
  - `--obligation` + `--evidence` + `--obligation-id` + `--dimension` → **evidence**（规格：evidence 模式）
  - 若需对「配置评估后的 gap」解释，只用 `--config` 路径（gap），不用 evidence 路径
- 渲染：`AgentEnvelope` → markdown（简短：mode、status、reason codes+locale summary）或 `model_dump(by_alias=True)` JSON
- 错误：`AgentInputError` / `ConfigLoadError` / `ProtocolLoadError` 走 `_handle_input_error`（扩展该助手以接受 `AgentInputError`，exit 码与现有输入错误一致，通常 4）

- [ ] **Step 4: GREEN**

```bash
python3 -m pytest tests/cli/test_explain.py -v
```

- [ ] **Step 5: Commit**（用户要求时）

---

### Task 5: CLI `qcov agent next`

**Files:**
- Modify: `qcov/cli/app.py`（`agent_app = typer.Typer(...)`；`app.add_typer(agent_app, name="agent")`）
- Create: `tests/cli/test_agent.py`

- [ ] **Step 1: 写失败测试**

```python
def test_agent_next_from_config_matches_plan(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan = runner.invoke(app, ["plan", "--config", str(config), "--format", "json"])
    nxt = runner.invoke(
        app, ["agent", "next", "--config", str(config), "--format", "json"]
    )
    assert nxt.exit_code == 0, nxt.output
    plan_id = json.loads(plan.output)["items"][0]["id"]
    body = json.loads(nxt.output)
    assert body["contractVersion"] == "qcov.agent/v1"
    assert body["command"] == "agent.next"
    assert body["payload"]["source"] == "evaluation"
    assert body["payload"]["items"][0]["id"] == plan_id


def test_agent_next_from_plan_file(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    runner.invoke(app, ["plan", "--config", str(config), "--output", str(plan_path)])
    nxt = runner.invoke(
        app, ["agent", "next", "--plan", str(plan_path), "--format", "json"]
    )
    assert nxt.exit_code == 0, nxt.output
    assert json.loads(nxt.output)["payload"]["source"] == "plan_file"


def test_agent_next_rejects_plan_with_config(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text("kind: QualityProposal\n")  # path exists; may fail load later
    result = runner.invoke(
        app,
        ["agent", "next", "--plan", str(plan_path), "--config", str(config)],
    )
    assert result.exit_code == 4
    assert "QCOV-CLI-006" in result.output
```

空计划：全 COVERED 夹具 → `items: []`、exit 0（可复制 `test_plan.py` 全覆盖写法或构造仅 behavior 义务且已覆盖）。

- [ ] **Step 2: RED** → **Step 3: 实现**

- `load_proposal` 需已存在（Iter 5/6）；`--plan` 路径调用 `select_next_actions(..., source="plan_file")`
- 评估路径：复用 `plan` 命令的 `_multi_obligation_evaluation` / 单义务逻辑 → `build_quality_plan` → `select_next_actions(..., source="evaluation")`
- `--limit` 默认 1
- **不**实现 `--output`

- [ ] **Step 4: GREEN** + 回归

```bash
python3 -m pytest tests/cli/test_agent.py tests/cli/test_plan.py tests/cli/test_commands.py -v
```

- [ ] **Step 5: Commit**（用户要求时）

---

### Task 6（可选）: `qcov agent validate-evidence`

**Files:**
- Modify: `qcov/cli/app.py`
- Modify: `tests/cli/test_agent.py`

- [ ] **Step 1: 测试**

```python
def test_agent_validate_evidence_valid_for_load(tmp_path: Path) -> None:
    ev = tmp_path / "behavior.yaml"
    ev.write_text(Path("examples/refund/evidence/behavior.yaml").read_text())
    result = runner.invoke(
        app, ["agent", "validate-evidence", "--evidence", str(ev), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    body = json.loads(result.output)
    assert body["command"] == "agent.validate_evidence"
    assert body["payload"]["allValidForLoad"] is True
    assert "COVERED" not in result.output
    assert "PASS" not in result.output
```

非法文件：`validForLoad=false` 且含 error；退出码：规格允许报告失败——**约定**只要命令跑完列出结果则 exit 0，或任一失败 exit 4。**钉死：任一文件 loader 失败 → exit 4**（与协议错误一致），JSON 仍尽量不半截（失败走 `_handle_input_error` 则无 stderr）。为满足「列出每文件结果」，改为：**始终 exit 0 并在 payload 中标记**；与「失败走输入错误」冲突时以 **payload 枚举 + exit 0** 为准（自检助手，非门禁）。

- [ ] **Step 2–4: 实现并 GREEN**（可跳过整个 Task 6）

---

### Task 7: 公开文档与 AGENTS

**Files:**
- Create: `docs/en/agent.md`、`docs/zh-CN/agent.md`
- Modify: `docs/en/roadmap.md`、`docs/zh-CN/roadmap.md`（Iter 7 交付；explain 必做）
- Modify: `docs/en/requirements.md`、`docs/zh-CN/requirements.md`
- Modify: `docs/en/concepts.md`、`docs/zh-CN/concepts.md`
- Modify: `docs/en/architecture.md`、`docs/zh-CN/architecture.md`（轻触）
- Modify: 文档索引/链接页（若 `docs/en/process.md` 或 README 有目录链，补上 `agent.md`）
- Modify: `AGENTS.md`
- Create: `docs/process/2026-09-09-iteration-7-agentic-quality-loop.md`
- Modify: `tests/docs/test_documentation_links.py`（若有死链检测）

Playbook 必含命令序：

```text
qcov gaps / qcov plan
→ qcov agent next --format json
→ （外部）执行测试并编写 QualityEvidence YAML
→ qcov explain …（可选排障）
→ qcov gaps / qcov policy check
```

明确：解释与 next ≠ 证据 ≠ 门禁；可选 validate 仅 `validForLoad`。

- [ ] **Step 1: 更新文档**
- [ ] **Step 2: 跑链接测试**（若有）

```bash
python3 -m pytest tests/docs/test_documentation_links.py -v
```

- [ ] **Step 3: 过程记录写入真实 RED/GREEN 命令摘要**
- [ ] **Step 4: Commit**（用户要求时）

---

### Task 8: 最终门禁

- [ ] **Step 1: 全量检查**

```bash
pytest
ruff check .
mypy qcov
python3 -m build
git diff --check
```

Expected: 全部通过。

- [ ] **Step 2: 对照规格硬验收清单勾选**（explain 三模式、next 双路径、contractVersion、不改 gaps/policy、文档已更新）

---

## Spec 覆盖对照（计划自检）

| 规格要求 | Task |
| --- | --- |
| `contractVersion` / agent JSON 外壳 / extra=forbid | 1, 4, 5 |
| explain 三模式 + 冻结 reason 码 | 2, 4 |
| `agent next` + `--plan`/`--config` + 与 planner 一致 | 3, 5 |
| `QCOV-CLI-006` / `QCOV-AGENT-001/002` | 1, 4, 5 |
| 不改 Gap/policy；proposal 不当证据 | 回归 Task 5/8 |
| 可选 validate-evidence | 6 |
| 公开文档 + playbook + AGENTS | 7 |
| 最终工具链门禁 | 8 |

## 计划审查结论（给实现前）

**可通过，建议按 Task 1→5→7→8 为硬路径；Task 6 可选。**

| 严重度 | 发现 | 处理 |
| --- | --- | --- |
| 中 | gap vs evidence CLI 分支易混 | Task 4 已钉死：`--config`→gap；义务+证据→evidence |
| 中 | validate exit 码与「列出结果」冲突 | Task 6 钉死：枚举结果 + exit 0 |
| 低 | `ExplainPayload.status` 用 str vs enum | 模型用 Literal 字符串，与 JSON 一致 |
| 低 | Commit 步骤依赖用户授权 | 各 Task Step 5 标注「用户要求时」 |

无 TBD/TODO 占位；函数名统一 `explain_gap` / `explain_evidence` / `explain_plan_item` / `select_next_actions`。
