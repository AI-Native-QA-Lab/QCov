# Iteration 4 策略与豁免实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 实现独立、批量可用且可复现的 `qcov policy check` 策略门禁与时限豁免。

**架构：** 以强类型 `QualityPolicy` 表达默认状态规则与精确义务豁免。纯策略引擎只消费 Gap Engine 结果和显式 `as_of` 时间；CLI 负责加载、批量求值、渲染和退出码。

**技术栈：** Python 3.11、Pydantic v2、Typer、PyYAML、pytest、Ruff、mypy、Hatchling。

**规格：** `docs/superpowers/specs/2026-09-07-iteration-4-policy-waivers-design.md`

## 全局约束

- 只支持本地文件和显式 `--as-of`；不得读取系统时钟或网络。
- 协议键、flags、枚举、错误码均为英文；Markdown 才会本地化。
- 不改变 `gaps`、`check` 或 `diff`；不引入 DSL、维度阈值、通配符、远程 Git、AI 或数据库。
- `--config` 批量评估全部义务；`--obligation` 和 `--evidence` 只能成对用于单项调试。
- 每项行为修改必须先取得实际 RED，再以最小改动变为 GREEN；文档和过程记录中文优先，README 英文优先且提供中文切换。

---

### Task 1: 收紧策略协议与 Schema

**Files:**

- Modify: `qcov/models/protocol.py:116-120`
- Modify: `schemas/policy.schema.json`
- Modify: `tests/models/test_protocol.py`
- Modify: `tests/models/test_io.py`

**Interfaces:**

- Produces: `DefaultPolicyRule(allowed_statuses: list[CoverageStatus])`、`PolicyRules(default: DefaultPolicyRule)`、`PolicyWaiver(obligation_ref, reason, expires_at, approved_by)`。
- Produces: `QualityPolicy.rules` 和 `QualityPolicy.waivers`；aliases 为 `allowedStatuses`、`obligationRef`、`expiresAt`、`approvedBy`。

- [ ] **Step 1: 写出模型的失败测试。**

```python
def test_policy_rejects_empty_allowed_statuses() -> None:
    with pytest.raises(ValidationError):
        QualityPolicy.model_validate({
            "apiVersion": "qcov.dev/v1alpha1", "kind": "QualityPolicy",
            "metadata": {"id": "release"},
            "rules": {"default": {"allowedStatuses": []}}, "waivers": [],
        })
```

另加测试：重复 `obligationRef`、缺失时区的 `expiresAt`、额外字段均必须拒绝；有效策略必须可以通过 `load_policy` 加载。

- [ ] **Step 2: 取得 RED。**

Run: `.venv/bin/pytest tests/models/test_protocol.py tests/models/test_io.py -q`

Expected: FAIL，因为现有模型仍要求宽松的 `policies` 字段。

- [ ] **Step 3: 写最小实现。**

```python
class DefaultPolicyRule(ProtocolModel):
    allowed_statuses: list[CoverageStatus] = Field(alias="allowedStatuses", min_length=1)

class PolicyWaiver(ProtocolModel):
    obligation_ref: str = Field(alias="obligationRef", min_length=1)
    reason: str = Field(min_length=1)
    expires_at: datetime = Field(alias="expiresAt")
    approved_by: str | None = Field(default=None, alias="approvedBy")
```

为 `QualityPolicy` 增加 after validator，拒绝重复的 `obligation_ref`、`tzinfo is None` 或 UTC offset 为 `None` 的期限。用 `QualityPolicy.model_json_schema(by_alias=True)` 重新生成 Schema。

- [ ] **Step 4: 取得 GREEN 并提交。**

Run: `.venv/bin/pytest tests/models/test_protocol.py tests/models/test_io.py -q`

Expected: PASS；无效策略经 loader 均报告 `QCOV-SCHEMA-001`。

Run: `git add qcov/models/protocol.py schemas/policy.schema.json tests/models/test_protocol.py tests/models/test_io.py && git commit -m "feat: define strict quality policy protocol"`

### Task 2: 实现纯策略判定

**Files:**

- Create: `qcov/engine/policy.py`
- Modify: `qcov/engine/__init__.py`
- Create: `tests/engine/test_policy.py`

**Interfaces:**

- Consumes: `Sequence[ObligationResult]`、`QualityPolicy`、时区感知的 `datetime as_of`。
- Produces: `PolicyDecision(PASS, WARN, BLOCK)`、`PolicyViolation(code)`、`PolicyResult`、`PolicyReport` 和 `evaluate_policy(results, policy, as_of)`。

- [ ] **Step 1: 写出失败的引擎测试。**

```python
def test_disallowed_status_blocks_without_waiver() -> None:
    report = evaluate_policy([partial_result("QO-002")], covered_only_policy(), AS_OF)
    assert report.results[0].decision is PolicyDecision.BLOCK
    assert report.results[0].violations == (PolicyViolation("QCOV-POLICY-001"),)

def test_active_waiver_warns_instead_of_blocking() -> None:
    report = evaluate_policy([partial_result("QO-002")], active_waiver_policy(), AS_OF)
    assert report.results[0].decision is PolicyDecision.WARN
```

再覆盖：`expires_at == as_of` 为过期；过期且违规为 `QCOV-POLICY-002/BLOCK`；过期但状态允许为 `WARN`；结果按义务 ID 升序；四个 CoverageStatus 都不被伪装为通过。

- [ ] **Step 2: 取得 RED。**

Run: `.venv/bin/pytest tests/engine/test_policy.py -q`

Expected: FAIL，因为 `qcov.engine.policy` 不存在。

- [ ] **Step 3: 写最小纯实现。**

策略引擎不得导入 Path、环境变量、时钟或 Typer。有效豁免条件为 `expires_at > as_of`；规则拒绝且无豁免产生 `QCOV-POLICY-001`；规则拒绝且豁免过期产生 `QCOV-POLICY-002`；规则允许但豁免过期保留 `WARN` 清理提示。

- [ ] **Step 4: 取得 GREEN 并提交。**

Run: `.venv/bin/pytest tests/engine/test_policy.py -q`

Expected: PASS，覆盖 PASS/WARN/BLOCK、到期边界和排序。

Run: `git add qcov/engine/__init__.py qcov/engine/policy.py tests/engine/test_policy.py && git commit -m "feat: evaluate deterministic policy gates"`

### Task 3: 生成稳定报告与本地化展示

**Files:**

- Create: `qcov/engine/policy_reports.py`
- Modify: `qcov/i18n/catalog.py`
- Create: `tests/engine/test_policy_reports.py`

**Interfaces:**

- Produces: `render_policy_json(report)` 和 `render_policy_markdown(report, locale)`。
- Produces JSON keys: `policyId`、`evaluatedAt`、`results`、`obligationId`、`coverageStatus`、`decision`、`violations`、`waiver`。

- [ ] **Step 1: 写出失败的报告测试。**

```python
def test_policy_json_uses_stable_machine_keys() -> None:
    payload = json.loads(render_policy_json(sample_policy_report()))
    assert payload["policyId"] == "release"
    assert payload["results"][0]["decision"] == "BLOCK"
    assert "/Users/" not in json.dumps(payload)

def test_policy_markdown_localizes_labels_not_codes() -> None:
    output = render_policy_markdown(sample_policy_report(), locale="zh-CN")
    assert "策略决定" in output
    assert "QCOV-POLICY-001" in output
```

- [ ] **Step 2: 取得 RED。**

Run: `.venv/bin/pytest tests/engine/test_policy_reports.py -q`

Expected: FAIL，因为 renderer 和 catalog 文案不存在。

- [ ] **Step 3: 写最小实现。**

JSON 用 `datetime.isoformat()`、`json.dumps(indent=2, sort_keys=True)` 和引擎原有排序。Markdown 每项输出原状态、决定、违规码和豁免详情。增加中英文策略 ID、评估时间、覆盖状态、策略决定、违规、豁免、期限、理由、批准人、PASS/WARN/BLOCK 标签。

- [ ] **Step 4: 取得 GREEN 并提交。**

Run: `.venv/bin/pytest tests/engine/test_policy_reports.py tests/i18n/test_catalog.py -q`

Expected: PASS；JSON 仅含稳定机器数据，Markdown 采用请求语言。

Run: `git add qcov/engine/policy_reports.py qcov/i18n/catalog.py tests/engine/test_policy_reports.py && git commit -m "feat: render policy gate reports"`

### Task 4: 接入独立 CLI 命令

**Files:**

- Modify: `qcov/cli/app.py:10-92,202-222`
- Create: `tests/cli/test_policy.py`

**Interfaces:**

- Produces: `qcov policy check` 和退出码 `0`（PASS/WARN）、`2`（BLOCK）、`4`（输入错误）。

- [ ] **Step 1: 写出失败的 CLI 测试。**

```python
def test_policy_check_config_evaluates_all_obligations(tmp_path: Path) -> None:
    config, policy = write_two_obligation_fixture(tmp_path)
    result = runner.invoke(app, ["policy", "check", "--config", str(config), "--policy", str(policy),
                                 "--as-of", "2026-09-07T00:00:00+08:00", "--format", "json"])
    assert result.exit_code == 2
    assert result.stdout.index("QO-001") < result.stdout.index("QO-002")
```

覆盖单项中文 WARN、缺失 `--as-of`、naive 时间、`--config` 和直接输入混用，以及无效策略为退出码 4。

- [ ] **Step 2: 取得 RED。**

Run: `.venv/bin/pytest tests/cli/test_policy.py -q`

Expected: FAIL，因为 `policy` Typer group 不存在。

- [ ] **Step 3: 写最小 CLI glue。**

创建 `policy = typer.Typer()` 并以 `app.add_typer(policy)` 注册。配置模式要求至少一个解析后的义务和 evidence 文件，evidence 只加载一次、每项义务调用现有 evaluator。直接模式必须成对输入且不可与 config 混用；混用返回 `QCOV-CLI-003` 和 4。解析后的 `as_of` 必须带 offset。BLOCK 映射为 2；loader/config 输入错误沿用 4。

- [ ] **Step 4: 取得 GREEN 并提交。**

Run: `.venv/bin/pytest tests/cli/test_policy.py tests/cli/test_commands.py -q`

Expected: PASS，覆盖批量、单项、JSON、中文 Markdown 和全部退出码。

Run: `git add qcov/cli/app.py tests/cli/test_policy.py && git commit -m "feat: add policy check command"`

### Task 5: 交付示例、中文主文档与验证记录

**Files:**

- Create: `examples/refund/policy.yaml`
- Create: `docs/zh-CN/policy.md`
- Create: `docs/en/policy.md`
- Create: `docs/process/2026-09-07-iteration-4-policy-waivers.md`
- Modify: `README.md`, `README.zh-CN.md`, `examples/refund/README.md`, `examples/refund/README.zh-CN.md`
- Modify: `docs/zh-CN/roadmap.md`, `docs/en/roadmap.md`, `tests/examples/test_refund_data.py`, `tests/docs/test_documentation_links.py`

**Interfaces:**

- Produces: 一个可复现的 Refund 策略示例，在所记录的 `--as-of` 下以有效豁免返回 WARN。

- [ ] **Step 1: 写出失败的示例和链接测试。**

```python
def test_refund_policy_fixture_is_valid() -> None:
    policy = load_policy(ROOT / "examples/refund/policy.yaml")
    assert policy.waivers[0].obligation_ref == "QO-REFUND-001"

def test_policy_docs_exist() -> None:
    assert (ROOT / "docs/zh-CN/policy.md").exists()
    assert (ROOT / "docs/en/policy.md").exists()
```

- [ ] **Step 2: 取得 RED。**

Run: `.venv/bin/pytest tests/examples/test_refund_data.py tests/docs/test_documentation_links.py -q`

Expected: FAIL，因为示例策略和策略页面尚不存在。

- [ ] **Step 3: 写示例和文档。**

新增带明确 offset 的 Refund 豁免和在其过期前的 `--as-of` 命令。`docs/zh-CN/policy.md` 写完整契约、决定表、退出码和 CI 用法；英文页保留对应命令和稳定标识。两个 README 替换“策略门禁未实现”的过期表述并保持语言切换。全量验证完成后才在路线图标记 Iteration 4。

- [ ] **Step 4: 取得 GREEN、记录实际证据并提交。**

Run: `.venv/bin/pytest tests/examples/test_refund_data.py tests/docs/test_documentation_links.py -q`

Run: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy qcov && .venv/bin/python -m build && git diff --check`

Expected: 全部退出 0；过程文档只记录真实 RED/GREEN 和最终命令结果。

Run: `git add README.md README.zh-CN.md examples/refund docs/zh-CN docs/en docs/process tests/examples/test_refund_data.py tests/docs/test_documentation_links.py && git commit -m "docs: document iteration 4 policy gates"`
