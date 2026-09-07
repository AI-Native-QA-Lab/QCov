# Iteration 4 策略与豁免设计

## 目标

Iteration 4 为 QCov 增加本地、离线、确定性的策略门禁。它复用既有义务
覆盖计算，针对一组义务输出 `PASS`、`WARN` 或 `BLOCK`，并允许带理由和
时限的精确豁免。策略不改变 `gaps`、`check` 或 `diff` 的现有语义。

本迭代不增加远程 Git 操作、数据库、网络时钟、策略 DSL、维度级阈值、路径或
通配符豁免，以及 AI 决策。

## CLI 契约

新增独立命令：

```text
qcov policy check --policy POLICY --as-of TIMESTAMP \
  [--config CONFIG | --obligation OBLIGATION --evidence EVIDENCE] \
  [--format markdown|json] [--locale en|zh-CN]
```

`--as-of` 是必填、带时区的 ISO 8601 时间戳。策略引擎只能使用该显式输入
判断豁免是否过期；报告写出同一个 `evaluatedAt`，因此同一组文件和命令参数会
得到相同结果。

`--config` 是门禁的标准批量路径：命令解析配置中全部 obligation 与 evidence
文件，并按义务 ID 排序评估。`--obligation` 与 `--evidence` 是单义务调试路径；
二者必须同时给出，且不得与 `--config` 混用。

退出码如下：

| 退出码 | 含义 |
| --- | --- |
| 0 | 所有义务均为 `PASS` 或 `WARN` |
| 2 | 至少一个义务为 `BLOCK` |
| 4 | CLI、配置或策略输入无效 |

## 策略协议

`QualityPolicy` 仍使用 `qcov.dev/v1alpha1`，但替换宽松的 `policies` 映射，
以强类型 `rules` 和 `waivers` 表达本迭代支持的规则：

```yaml
apiVersion: qcov.dev/v1alpha1
kind: QualityPolicy
metadata:
  id: refund-release-gate
rules:
  default:
    allowedStatuses: [COVERED]
waivers:
  - obligationRef: QO-REFUND-001
    reason: Production evidence is unavailable in the local fixture.
    expiresAt: 2026-10-01T00:00:00+08:00
    approvedBy: qa-owner
```

`allowedStatuses` 至少包含一个现有 `CoverageStatus`。策略、规则与豁免模型
均禁止额外字段。每个豁免必须有非空 `obligationRef`、非空 `reason` 和带时区的
`expiresAt`；`approvedBy` 可选。一个策略内不得有重复 `obligationRef`。机器
字段、枚举值和错误码保持英文。

## 判定语义

策略引擎先调用现有 Gap Engine 获得每个 obligation 的 `CoverageStatus`，随后：

1. 状态在 `rules.default.allowedStatuses` 中时，判定为 `PASS`。
2. 状态不被允许且存在未到期的精确豁免时，判定为 `WARN`，保留原始状态和
   豁免理由。
3. 状态不被允许且不存在有效豁免时，判定为 `BLOCK`，附带
   `QCOV-POLICY-001`。
4. 若豁免在 `evaluatedAt` 当刻或之前到期，它不生效。若该义务因此违反默认
   规则，判定为 `BLOCK`，附带 `QCOV-POLICY-002`；若状态本已允许，判定为
   `WARN`，提示应清理失效豁免。

策略判断只读取计算结果、策略和明确给出的时间；不推断风险，也不把 `UNKNOWN`
伪装为通过。

## 报告

JSON 输出使用固定英文键与稳定枚举，根对象包含 `policyId`、`evaluatedAt` 和
按 obligation ID 升序排列的 `results`。每项含 `obligationId`、原始
`coverageStatus`、`decision`、`violations` 与（如适用）`waiver`。报告不得包含
本机绝对路径。

Markdown 输出沿用 `--locale` 的展示语言；稳定 ID、协议字段与枚举不翻译。
它至少显示策略 ID、评估时间、每项的原始覆盖状态、策略决定、违规码和豁免详情。

## 组件边界

- `qcov.models.protocol`：强类型策略与豁免协议模型。
- `qcov.models.io`：复用 `load_policy` 的安全 YAML/JSON 加载与 `QCOV-SCHEMA-001`。
- `qcov.engine.policy`：纯策略判定和稳定策略错误对象；不读取文件、不访问时钟。
- `qcov.engine.policy_reports`：策略结果的 JSON 和本地化 Markdown 渲染。
- `qcov.cli.app`：解析 `policy check` 输入，加载文件、调用既有 evaluator 与策略
  引擎，并映射退出码。

## 测试与文档

按 TDD 执行。先为模型/Schema、纯策略引擎、报告和 CLI 各写一个聚焦的失败测试，
记录实际 RED 结果；以最小实现转为 GREEN 后运行相关回归。重点覆盖非法策略、
重复豁免、时区缺失、有效与到期豁免、到期边界、稳定排序、批量配置、单项调试、
中英文 Markdown、JSON 和退出码。

实现完成后执行 `pytest`、`ruff check .`、`mypy qcov`、`python -m build` 与
`git diff --check`，并在 `docs/process/` 中记录实际命令和结果。

本迭代的设计、计划、开发和过程文档以中文为主；README 保持英文主文并通过
`README.zh-CN.md` 提供中文切换。面向 README 的英文产品页保留对应入口、命令与
机器标识的一致性，但不再要求内部过程文档逐篇双语镜像。
