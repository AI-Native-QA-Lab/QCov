# Iteration 6 实现计划：Quality Planner（`qcov plan`）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans。Steps 使用 checkbox（`- [ ]`）跟踪。

**Goal:** 交付确定性 `qcov plan`：对评估出的 unproven 维度按固定收益/成本规则排序，产出 draft `QualityProposal(type=quality_plan)`，且永不进入 Gap/policy。

**Architecture:** 扩展 `QualityProposal` 枚举；新增纯函数 `qcov.engine.planner`；CLI `--config` 复用 `_policy_bundle` 多义务评估（禁止与直接义务/证据组合）；组装 proposal 不经 `AIProvider`。

**Tech Stack:** Python 3.11+、Pydantic v2、Typer、PyYAML、pytest、Ruff、mypy。

**Spec:** `docs/superpowers/specs/2026-09-08-iteration-6-quality-planner-design.md`

## 全局约束

- 严格 TDD：每行为先 RED 再 GREEN；在对应 `docs/process/` 记录真实命令输出。
- Plan 仅为 draft Proposal；不改 Gap Engine / policy 判定语义。
- 不扩展 `AIProvider`；不提供 `qcov plan --provider`。
- 默认测试无网络。
- 最终门禁：`pytest`、`ruff check .`、`mypy qcov`、`python3 -m build`、`git diff --check`。
- 开发过程文档仅中文；公开 `docs/en|zh-CN` 仍双语。

## 文件结构（预定）

| 路径 | 职责 |
| --- | --- |
| `qcov/models/protocol.py` | 扩展 proposal `type` / source `kind` / item `kind` Literals |
| `schemas/proposal.schema.json` | 同步枚举 |
| `qcov/engine/planner.py` | 打分、排序、组装 `QualityProposal` |
| `qcov/cli/app.py` | `qcov plan` 命令 |
| `tests/models/test_protocol.py`、`test_io.py` | 协议 / 加载 |
| `tests/engine/test_planner.py` | 启发式与稳定性 |
| `tests/cli/test_plan.py` | CLI |
| `docs/en|zh-CN/concepts.md`、`roadmap.md` | 公开说明 |
| `AGENTS.md` | Iteration 6 已在批准设计/计划范围内 |
| `docs/process/2026-09-08-iteration-6-quality-planner.md` | 实现过程记录 |

---

### Task 1: 扩展 QualityProposal 协议枚举

**Files:**
- Modify: `qcov/models/protocol.py`（`ProposalDescriptor` / `ProposalSource` / `ProposalItem`）
- Modify: `schemas/proposal.schema.json`
- Modify: `qcov/ai/provider.py`（`_draft_proposal` / `_item` 的 Literal 需包含新值，或保持旧 Literal 并确认 mypy 仍通过——若 `_draft_proposal` 仍只接受旧 type，可不动 provider，仅扩展 protocol）
- Test: `tests/models/test_protocol.py`、`tests/models/test_io.py`

- [ ] **Step 1: 写失败测试（quality_plan 合法）**

在 `tests/models/test_protocol.py` 增加：

```python
VALID_QUALITY_PLAN = {
    "apiVersion": "qcov.dev/v1alpha1",
    "kind": "QualityProposal",
    "metadata": {
        "id": "QP-plan-001",
        "createdAt": "2026-09-08T12:00:00+08:00",
    },
    "proposal": {"type": "quality_plan", "status": "draft"},
    "source": {"kind": "evaluation_gaps", "refs": ["qcov.yaml"]},
    "provider": {"name": "offline", "model": None},
    "items": [
        {
            "id": "plan-QO-REFUND-001-behavior",
            "kind": "planned_verification",
            "obligationRef": "QO-REFUND-001",
            "summary": {
                "en": "Prefer api_test for behavior gap",
                "zh-CN": "优先用 api_test 补齐 behavior 缺口",
            },
            "detail": {
                "dimension": "behavior",
                "gapStatus": "MISSING",
                "missingEvidenceTypes": ["api_test"],
                "suggestedEvidenceType": "api_test",
                "benefitScore": 100,
                "costScore": 10,
                "priorityScore": -90,
                "rank": 1,
            },
        }
    ],
}


def test_quality_proposal_accepts_quality_plan() -> None:
    from qcov.models.protocol import QualityProposal

    proposal = QualityProposal.model_validate(VALID_QUALITY_PLAN)
    assert proposal.proposal.type == "quality_plan"
    assert proposal.source.kind == "evaluation_gaps"
    assert proposal.items[0].kind == "planned_verification"
```

- [ ] **Step 2: 运行确认 RED**

```bash
python3 -m pytest tests/models/test_protocol.py::test_quality_proposal_accepts_quality_plan -v
```

Expected: FAIL（`quality_plan` / `evaluation_gaps` / `planned_verification` 不在 Literal/enum 内）

- [ ] **Step 3: 最小实现**

`qcov/models/protocol.py`：

```python
class ProposalDescriptor(ProtocolModel):
    type: Literal["obligation_suggest", "change_risk", "quality_plan"]
    status: Literal["draft"]


class ProposalSource(ProtocolModel):
    kind: Literal["requirements", "local_diff", "evaluation_gaps"]
    refs: list[str] = Field(default_factory=list)


class ProposalItem(ProtocolModel):
    id: str = Field(min_length=1)
    kind: Literal[
        "proposed_obligation",
        "affected_obligation",
        "suggested_evidence",
        "planned_verification",
    ]
    obligation_ref: str | None = Field(default=None, alias="obligationRef", min_length=1)
    summary: LocalizedText
    detail: dict[str, object] = Field(default_factory=dict)
```

同步 `schemas/proposal.schema.json` 三处 `enum`。

若 `qcov/ai/provider.py` 中 `_draft_proposal` / `_item` 的 Literal 与 protocol 收窄不一致导致 mypy 告警，将 provider 侧 Literal 扩到与 protocol 一致（仍只实现旧两条路径即可）。

- [ ] **Step 4: 补充 io 回归（可选同测）**

确认 `tests/models/test_io.py::test_load_evidence_rejects_quality_proposal_kind` 仍对 `kind: QualityProposal`（含可改为 `quality_plan` 样例）拒绝为 evidence。可新增 `test_load_proposal_accepts_quality_plan` 写出 YAML 再 `load_proposal`。

- [ ] **Step 5: GREEN**

```bash
python3 -m pytest tests/models/test_protocol.py tests/models/test_io.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add qcov/models/protocol.py schemas/proposal.schema.json qcov/ai/provider.py \
  tests/models/test_protocol.py tests/models/test_io.py
git commit -m "$(cat <<'EOF'
feat: extend QualityProposal enums for quality_plan

EOF
)"
```

---

### Task 2: `qcov.engine.planner` 打分与排序

**Files:**
- Create: `qcov/engine/planner.py`
- Test: `tests/engine/test_planner.py`

评分规则（与 spec 一致，实现时做成模块级常量 dict）：

- `benefit`：状态 `MISSING=50` / `UNKNOWN=20`；severity `critical=40` `high=30` `medium=20` `low=10` 其他 `15`；维度权重见 spec。
- `cost`：类型族 `api_test|junit_test|pytest_marker=10`；`property_test|database_invariant=20`；`e2e_test|playwright_test=35`；`production_signal|manual_review=50`；其他 `40`；空类型列表 → cost `40`、`suggestedEvidenceType=None`。
- `priorityScore = costScore - benefitScore`（越小越优先）。
- tie-break：`obligation_id`、`dimension.value`、首个 missing type。

公开 API 建议：

```python
def build_quality_plan(
    results: Sequence[ObligationResult],
    obligations: Sequence[TestingObligation],
    *,
    refs: Sequence[str],
) -> QualityProposal: ...
```

内部可用 dataclass `PlanRow` 再组装 items。

- [ ] **Step 1: 写失败测试**

`tests/engine/test_planner.py`：

```python
from __future__ import annotations

from qcov.engine.gaps import DimensionResult, ObligationResult, evaluate_obligation
from qcov.engine.planner import build_quality_plan
from qcov.models.protocol import CoverageStatus, QualityDimension, TestingObligation


def _obligation(**overrides: object) -> TestingObligation:
    base = {
        "apiVersion": "qcov.dev/v1alpha1",
        "kind": "TestingObligation",
        "metadata": {
            "id": "QO-A",
            "title": {"en": "A", "zh-CN": "甲"},
        },
        "source": {"type": "requirement", "ref": "A"},
        "risk": {"domain": "x", "severity": "critical"},
        "requiredEvidence": {"behavior": ["api_test"], "security": ["e2e_test"]},
    }
    base.update(overrides)
    return TestingObligation.model_validate(base)


def test_planner_orders_by_priority_score() -> None:
    obl = _obligation()
    # no evidence → Gap Engine marks dimensions UNKNOWN (not MISSING)
    result = evaluate_obligation(obl, [])
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.proposal.type == "quality_plan"
    assert proposal.source.kind == "evaluation_gaps"
    assert proposal.provider.name == "offline"
    ranks = [item.detail["rank"] for item in proposal.items]
    assert ranks == [1, 2]
    # security: benefit 20+40+25=85, cost 35 → priority -50
    # behavior: benefit 20+40+10=70, cost 10 → priority -60  → behavior first
    assert proposal.items[0].obligation_ref == "QO-A"
    assert proposal.items[0].detail["dimension"] == "behavior"
    assert proposal.items[0].detail["gapStatus"] == "UNKNOWN"
    assert proposal.items[0].detail["suggestedEvidenceType"] == "api_test"
    assert proposal.items[0].detail["priorityScore"] == -60
    assert proposal.items[1].detail["dimension"] == "security"
    assert proposal.items[1].detail["priorityScore"] == -50


def test_planner_missing_status_scores_higher_than_unknown() -> None:
    """Hand-build results: MISSING outranks UNKNOWN when other factors equal."""
    from qcov.engine.gaps import DimensionResult, ObligationResult

    obl = _obligation(
        requiredEvidence={"behavior": ["api_test"]},
        risk={"domain": "x", "severity": "low"},
    )
    missing = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                ("api_test",),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([missing], [obl], refs=["fixture"])
    assert proposal.items[0].detail["gapStatus"] == "MISSING"
    assert proposal.items[0].detail["benefitScore"] == 50 + 10 + 10  # missing+low+behavior
    assert proposal.items[0].detail["priorityScore"] == 10 - 70


def test_planner_empty_required_types_uses_default_cost() -> None:
    from qcov.engine.gaps import DimensionResult, ObligationResult

    obl = _obligation(requiredEvidence={"behavior": []})
    result = ObligationResult(
        "QO-A",
        CoverageStatus.MISSING,
        (
            DimensionResult(
                QualityDimension.BEHAVIOR,
                (),
                CoverageStatus.MISSING,
                (),
            ),
        ),
    )
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items[0].detail["costScore"] == 40
    assert proposal.items[0].detail["suggestedEvidenceType"] is None
    assert proposal.items[0].detail["missingEvidenceTypes"] == []


def test_planner_empty_when_all_covered() -> None:
    from qcov.models.protocol import QualityEvidence

    obl = _obligation(
        requiredEvidence={"behavior": ["api_test"]},
    )
    evidence = QualityEvidence.model_validate(
        {
            "apiVersion": "qcov.dev/v1alpha1",
            "kind": "QualityEvidence",
            "metadata": {"id": "QE-1"},
            "obligation": {"ref": "QO-A"},
            "evidence": {"dimension": "behavior", "type": "api_test"},
            "execution": {
                "status": "passed",
                "timestamp": "2026-09-08T12:00:00+08:00",
                "artifact": {"path": "t", "identity": "t"},
            },
        }
    )
    result = evaluate_obligation(obl, [evidence])
    assert result.status is CoverageStatus.COVERED
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items == []


def test_planner_picks_cheapest_suggested_type() -> None:
    obl = _obligation(
        requiredEvidence={"behavior": ["e2e_test", "api_test"]},
    )
    result = evaluate_obligation(obl, [])
    proposal = build_quality_plan([result], [obl], refs=["fixture"])
    assert proposal.items[0].detail["suggestedEvidenceType"] == "api_test"
    assert proposal.items[0].detail["costScore"] == 10
    assert proposal.items[0].detail["missingEvidenceTypes"] == ["api_test", "e2e_test"]
```

（`missingEvidenceTypes` 实现为**字典序**排序。）

- [ ] **Step 2: RED**

```bash
python3 -m pytest tests/engine/test_planner.py -v
```

Expected: FAIL（`ModuleNotFoundError: qcov.engine.planner`）

- [ ] **Step 3: 实现 `qcov/engine/planner.py`**

要点：

- 用 `obligation_id → TestingObligation` 映射取 `risk.severity`。
- 只处理 `result.unproven_dimensions`。
- `missingEvidenceTypes = sorted(dimension.required_types)`。
- 空 `required_types`：`suggestedEvidenceType=None`，`costScore=40`。
- `createdAt` 使用与 offline 相同的 `"1970-01-01T00:00:00+00:00"` 以利稳定金样。
- `metadata.id`：`sha256` 拼接 `quality_plan` + refs + item ids（同 Iteration 5 风格）。
- `summary` 双语模板即可，例如  
  en: `Rank {n}: verify {dimension} for {id} via {suggested}`  
  zh-CN: `第 {n} 步：为 {id} 的 {dimension} 优先补齐 {suggested}`。
- item `id`: `plan-{obligationId}-{dimension}`。

- [ ] **Step 4: 再加稳定性格测**

```python
def test_planner_is_deterministic() -> None:
    obl = _obligation()
    result = evaluate_obligation(obl, [])
    a = build_quality_plan([result], [obl], refs=["r"])
    b = build_quality_plan([result], [obl], refs=["r"])
    assert a.model_dump(by_alias=True, mode="json") == b.model_dump(by_alias=True, mode="json")
```

- [ ] **Step 5: GREEN**

```bash
python3 -m pytest tests/engine/test_planner.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add qcov/engine/planner.py tests/engine/test_planner.py
git commit -m "$(cat <<'EOF'
feat: add deterministic quality planner engine

EOF
)"
```

---

### Task 3: CLI `qcov plan`

**Files:**
- Modify: `qcov/cli/app.py`
- Test: `tests/cli/test_plan.py`

行为（spec）：

| 输入 | 行为 |
| --- | --- |
| 仅 `--config` | 调用现有 `_policy_bundle(None, None, config)`，收集全部义务对象，`build_quality_plan` |
| `--obligation` + `--evidence` | 单义务 `_evaluate`；refs 为两路径 |
| `--config` + 直接输入 | `QCOV-CLI-003`，exit 4 |
| `--output` | 复用 `_write_proposal_yaml` |
| format | 复用 `_render_proposal`（可按需在 markdown 中带上 rank；最小改动：现有 items 列表已够用，或在 summary 已含 rank） |

加载义务列表：从 `_policy_bundle` 的结果 ids 对 `resolved.obligations` `load_obligation`，或在 plan 命令内复制 policy 加载后同时保留 `list[TestingObligation]`。推荐小重构：抽出

```python
def _multi_obligation_evaluation(config_path: Path) -> tuple[EvaluationBundle, tuple[TestingObligation, ...]]:
    ...
```

供 `_policy_bundle` 与 `plan` 共用（若改动面大，plan 可先复制 `_policy_bundle` 主体并额外返回 obligations，避免破坏 policy 测试；优先少重复）。

- [ ] **Step 1: 写失败 CLI 测试**

`tests/cli/test_plan.py`：

```python
from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

runner = CliRunner()


def _write_project(tmp_path: Path) -> Path:
    (tmp_path / "obligation.yaml").write_text(Path("examples/refund/obligation.yaml").read_text())
    (tmp_path / "evidence").mkdir()
    # only behavior covered → other dimensions remain gaps
    (tmp_path / "evidence" / "behavior.yaml").write_text(
        Path("examples/refund/evidence/behavior.yaml").read_text()
    )
    config = tmp_path / "qcov.yaml"
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\n"
        "kind: QCovConfig\n"
        "obligations: [obligation.yaml]\n"
        "evidence: [evidence/*.yaml]\n"
    )
    return config


def test_plan_writes_quality_plan_from_config(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    output = tmp_path / "plan.yaml"
    result = runner.invoke(
        app,
        ["plan", "--config", str(config), "--output", str(output), "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["proposal"]["type"] == "quality_plan"
    assert payload["source"]["kind"] == "evaluation_gaps"
    assert payload["items"], "expected unproven dimensions"
    assert payload["items"][0]["detail"]["rank"] == 1


def test_plan_rejects_config_with_direct_inputs(tmp_path: Path) -> None:
    config = _write_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "plan",
            "--config",
            str(config),
            "--obligation",
            str(tmp_path / "obligation.yaml"),
            "--evidence",
            str(tmp_path / "evidence" / "behavior.yaml"),
        ],
    )
    assert result.exit_code == 4
    assert "QCOV-CLI-003" in result.output


def test_plan_empty_when_fully_covered(tmp_path: Path) -> None:
    obl = tmp_path / "obligation.yaml"
    obl.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: TestingObligation
metadata:
  id: QO-ONE
  title: {en: One, zh-CN: 一}
source: {type: requirement, ref: R1}
risk: {domain: x, severity: low}
requiredEvidence:
  behavior: [api_test]
"""
    )
    ev = tmp_path / "evidence.yaml"
    ev.write_text(
        """apiVersion: qcov.dev/v1alpha1
kind: QualityEvidence
metadata: {id: QE-1}
obligation: {ref: QO-ONE}
evidence: {dimension: behavior, type: api_test}
execution:
  status: passed
  timestamp: "2026-09-08T12:00:00+08:00"
  artifact: {path: t, identity: t}
"""
    )
    result = runner.invoke(
        app,
        [
            "plan",
            "--obligation",
            str(obl),
            "--evidence",
            str(ev),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["items"] == []
```

- [ ] **Step 2: RED**

```bash
python3 -m pytest tests/cli/test_plan.py -v
```

Expected: FAIL（无 `plan` 命令）

- [ ] **Step 3: 实现 CLI**

在 `qcov/cli/app.py`：

```python
from qcov.engine.planner import build_quality_plan


@app.command("plan")
def plan(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    output: Annotated[Path | None, typer.Option()] = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Rank next-best verification steps from gaps (proposal only)."""
    try:
        if config is not None and (obligation is not None or evidence is not None):
            raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
        if config is not None:
            bundle = _policy_bundle(None, None, config)
            loaded = load_config(config)
            resolved = resolve_paths(loaded, config)
            obligations = tuple(load_obligation(path) for path in resolved.obligations)
            refs = [str(config)]
        elif obligation is not None and evidence is not None:
            bundle = EvaluationBundle((_evaluate(obligation, evidence),), None)
            obligations = (load_obligation(obligation),)
            refs = [str(obligation), str(evidence)]
        else:
            raise ConfigLoadError(
                f"{ConfigLoadError.code}: provide --obligation/--evidence or --config"
            )
        proposal = build_quality_plan(bundle.results, obligations, refs=refs)
    except _InputError as error:
        _handle_input_error(error)
        return
    if output is not None:
        _write_proposal_yaml(output, proposal)
    # locale reserved for future markdown i18n; json path ignores it
    _ = locale
    typer.echo(_render_proposal(proposal, output_format))
```

（若 markdown 需按 `locale` 切换 summary 语言，最小增强：渲染时选 `item.summary.zh_cn` vs `.en`；非必须，有则加测。）

另加：`test_gaps_unaffected_by_plan_yaml`（把 plan 文件放进 evidence glob 时 gaps 仍拒绝 / 不满足）——可复制 `test_gaps_does_not_load_proposal_as_evidence` 并改 `type: quality_plan`。

- [ ] **Step 4: GREEN + policy 回归**

```bash
python3 -m pytest tests/cli/test_plan.py tests/cli/test_policy_command.py tests/cli/test_propose.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add qcov/cli/app.py tests/cli/test_plan.py
git commit -m "$(cat <<'EOF'
feat: add qcov plan CLI for next-best verification

EOF
)"
```

---

### Task 4: 文档、AGENTS、过程记录与全量门禁

**Files:**
- Modify: `docs/en/concepts.md`、`docs/zh-CN/concepts.md`
- Modify: `docs/en/roadmap.md`、`docs/zh-CN/roadmap.md`（Iteration 6 改为已交付或「本版本包含 plan」——与仓库当前「Planned」表述对齐：将 6 标为 delivered / 简述 `qcov plan`）
- Modify: `AGENTS.md`（Iteration 6 Quality Planner 已实现；7–8 仍 planned）
- Create: `docs/process/2026-09-08-iteration-6-quality-planner.md`
- 可选：`docs/en/architecture.md` / `docs/zh-CN/architecture.md` 一句 planner 边界

- [x] **Step 1: 更新 concepts（双语）**

英文补充一句：`qcov plan` 基于确定性启发式产出 `quality_plan` draft；仍不是证据/门禁。  
中文对称更新。

- [x] **Step 2: 更新 roadmap / AGENTS**

- [x] **Step 3: 写过程记录**（真实 RED/GREEN 命令与输出摘录；全量门禁结果）

- [x] **Step 4: 全量门禁**

```bash
python3 -m pytest
ruff check .
mypy qcov
python3 -m build
git diff --check
```

Expected: 全部通过。

- [x] **Step 5: Commit**

```bash
git add docs AGENTS.md
git commit -m "$(cat <<'EOF'
docs: document iteration 6 quality planner

EOF
)"
```

---

## Spec 覆盖自检

| Spec 要求 | Task |
| --- | --- |
| 扩展 `quality_plan` / `evaluation_gaps` / `planned_verification` | Task 1 |
| 固定规则表 benefit/cost、priority、tie-break | Task 2 |
| 空 required_types → cost 40 / suggested null | Task 2（实现时加单测一行） |
| `--config` 多义务（`_policy_bundle`） | Task 3 |
| 禁止 config+直接输入 | Task 3 |
| 全 COVERED → 空 items、exit 0 | Task 2 + 3 |
| 不经 AIProvider / 无 `--provider` | Task 3 |
| Proposal 不当证据 | Task 1 + 3 |
| 双语文档 + AGENTS + 过程记录 | Task 4 |
| 全量门禁 | Task 4 |

## 占位符扫描

无 TBD/TODO；函数名统一 `build_quality_plan`；CLI 名 `plan`。
