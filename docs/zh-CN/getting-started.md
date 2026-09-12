# 5 分钟快速上手

QCov 是本地、确定性的证据缺口引擎。它评估显式的 `TestingObligation` 与
`QualityEvidence` 记录；不会执行测试、不会从测试名推断 obligation，也不会让 AI 成为门禁权威。

本流程使用仓库中已提交的 fixture，因此所有命令都可从仓库根目录执行。流程为
`gaps → scan → map preview → gaps → 本地 Git 变更影响 → policy check`。

## 1. 安装 QCov

QCov 要求 Python 3.11+。即使被观察的项目是 Java 或 TypeScript，工具本身仍是 Python CLI。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

下文使用 `.venv/bin/python -m qcov`，避免依赖 shell entry point 的 PATH。

## 2. 查看证据缺口

```bash
.venv/bin/python -m qcov gaps \
  --obligation examples/refund/obligation.yaml \
  --evidence examples/refund/evidence
```

结果刻意为 `PARTIAL`：Refund fixture 有行为、边界和数据证据，但没有并发、幂等性和生产证据。
`gaps` 只报告事实，不阻塞构建。

## 3. 扫描本地工件，不执行测试

```bash
.venv/bin/python -m qcov scan --config examples/imported-reports/qcov.yaml
```

`scan` 只读取已声明的本地路径。该 fixture 扫描 JUnit XML、coverage.py XML、Playwright JSON
和 LCOV；它从不执行 pytest、Maven、Gradle、npm 或 Playwright。

## 4. 预览显式映射，再评估

```bash
.venv/bin/python -m qcov map preview \
  --config examples/imported-reports/qcov.yaml --format json

.venv/bin/python -m qcov gaps --config examples/imported-reports/qcov.yaml
```

预览是只读的。`mappings/refund.yaml` 显式将选定的 JUnit 与 Playwright identity 映射为
`QualityEvidence`；随后 `gaps --config` 合并手写证据、显式 pytest marker 证据与映射结果。

## 5. 查看已提交 Git 快照中的变更影响

当前 QCov 已实现的变更影响命令是 `qcov diff`，不是 `qcov impact` 或 `qcov affected`。它比较
两个已存在的本地提交中的显式 obligation 与 evidence。运行自包含演示：

```bash
.venv/bin/python examples/pr-delta/demo.py
```

在你的仓库中，先提交相关的 `qcov.yaml`、obligation 与 evidence 文件，再执行：

```bash
.venv/bin/python -m qcov diff \
  --repo . --base origin/main --head HEAD --config qcov.yaml
```

它只读取 Git object：不会 fetch、切换提交、执行测试，也不会读取脏文件或未跟踪文件。

## 6. 应用可复现的本地策略

```bash
.venv/bin/python -m qcov policy check \
  --config examples/imported-reports/qcov.yaml \
  --policy examples/refund/policy.yaml \
  --as-of 2026-09-07T00:00:00+08:00
```

该 fixture 以退出码 `0` 结束：它刻意保留的 `PARTIAL` 有一个尚未到期的豁免。Policy 评估
既有 status，绝不改变 evidence 或 coverage 事实。退出码 `2` 表示 `BLOCK`，`4` 表示输入无效。

## 各语言入口

| 项目 | 在 QCov 外生成 | 在 QCov 中声明 | 权威边界 |
| --- | --- | --- | --- |
| Python | 在 QCov 外运行 pytest，并可生成 coverage.py XML。 | 使用显式 `@pytest.mark.qcov` evidence 或手写 YAML；将 coverage.py 列在 `scan.coverage`。 | marker 或手写 `QualityEvidence` 才可能成为证据；coverage.py 仅是 inventory。 |
| Java | 在 QCov 外运行 JUnit/JaCoCo，并保留 JUnit XML。 | 将 JUnit XML 写入 `scan.junit`；用 `EvidenceMapping` 映射选定 identity。 | 只有显式 JUnit mapping 才生成 `QualityEvidence`；JaCoCo/LCOV 类比率不是覆盖证据。 |
| TypeScript | 在 QCov 外运行 Playwright，并保留 JSON report。 | 将报告写入 `scan.playwright`；用 `EvidenceMapping` 映射选定 identity。 | 只有显式 Playwright mapping 才生成 `QualityEvidence`；测试名本身不推断 obligation。 |

可先无覆盖地创建初始配置：

```bash
.venv/bin/python -m qcov init --path .
```

然后只加入现有 Python、Java 或 TypeScript 工具链已经产出的工件路径。schema 与诊断见
[显式映射](mapping.md)和[策略门禁](policy.md)。

## 故障排查与权威边界

- **`QCOV-CONFIG-*` 或退出码 `4`：** config 路径、协议文档、mapping 或 policy 输入无效。
  检查路径是否相对 `qcov.yaml` 存在，以及 `--as-of` 是否带时区。
- **`PARTIAL`、`MISSING` 或 `UNKNOWN`：** 它们是评估结果，不是 scan 失败。用 `qcov explain`
  检查某个 gap；应补充或修正真实 evidence，而不是手工更改 status。
- **scan 找到了报告，但 gaps 未变化：** inventory 不是权威。为 JUnit/Playwright 添加显式 mapping，
  或手写 `QualityEvidence`。coverage.py 与 LCOV 不能通过 mapping 提升。
- **policy 阻塞：** 检查结果和豁免到期时间。`policy check` 基于权威评估结果决定本地门禁；不会把
  scanner 记录、AI proposal、`qcov plan` 或 `qcov agent` 输出变成权威。
- **Git 比较遗漏未提交内容：** 这是预期行为。提交 QCov 输入后重跑 `qcov diff`；它刻意忽略脏文件。

AI proposal 命令与 agent helper 可以解释或建议工作，但永远不会成为 evidence 或 policy/gate 权威。
