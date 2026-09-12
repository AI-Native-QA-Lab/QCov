# QCov 开发上下文

本文是 1.0 发布分支的中文维护上下文。它取代已从工作树清理的逐迭代过程记录、计划和设计草案；完整细节仍可通过 Git 历史追溯。

## 产品定位与边界

QCov 是本地、确定性的质量证据缺口引擎：它评估某条显式 Testing Obligation 是否拥有满足所需维度的有效证据，并解释 `COVERED`、`PARTIAL`、`MISSING` 与 `UNKNOWN`。

- 通过的测试、coverage.py、JaCoCo、LCOV 与静态分析都只是 inventory，不能自动成为业务通过证据。
- 只有显式 `EvidenceMapping` 才能将可识别的测试或观察 identity 物化为 QualityEvidence。
- AI 只能提出建议、解释或规划；永远不是 evidence 或 gate authority。
- QCov 不运行目标项目测试、不连接生产服务、不提供远程 Git API、Web UI、持久化或自动 inventory→obligation 推断。

## 已交付演进

| 阶段 | 主要能力 |
| --- | --- |
| 0～4 | Obligation→Evidence→Gap、库存扫描、`qcov diff`、本地 policy 与豁免 |
| 4.5 | 声明式 EvidenceMapping、`qcov map preview`、配置合并 |
| 5～7 | pytest marker、离线 AI 提案、确定性 quality plan、`qcov.agent/v1` 助手 |
| 8 / v0.9.0 | `production-observation` 本地 inventory，观察必须显式 mapping |
| 9 / 1.0 | 三真实项目案例、`qcov impact`、`qcov affected`、`qcov.impact/v1`、`qcov.adapter/v1`、Adapter SDK 与 JaCoCo inventory adapter |

## 当前稳定接口

- 配置：`qcov.dev/v1alpha1`
- Agent：`qcov.agent/v1`
- 影响分析：`qcov.impact/v1`
- 适配器：`qcov.adapter/v1`
- 常用命令：`qcov gaps`、`qcov scan`、`qcov map preview`、`qcov policy check`、`qcov diff`、`qcov impact`、`qcov affected`

协议 key、CLI flag、枚举和错误 ID 保持英文。公开产品文档维护中英文镜像；此维护上下文以中文为准。

## 证据与适配器规则

- JUnit、pytest、Playwright 与 production observation 可通过显式 mapping 产生 evidence。
- 映射 identity、producer、type 与 requiredEvidence 必须匹配；类型不匹配应如实形成 gap，不能通过别名猜测提升。
- JUnit XML、JaCoCo、coverage.py、LCOV 是扫描输入，不要放入 `evidence` 配置字段；`evidence` 仅接收 QualityEvidence 协议文档。
- 一个测试只能映射到它的断言实际证明的维度；不能为了消除 `PARTIAL` 把 identity 复制到无关 behavior、boundary、integration、security 或 data 维度。

## 1.0 真实案例

案例输入位于 `examples/case-studies/`，说明位于 `docs/case-studies/`：

- `ai-native-qa-agents`：Python/pytest/coverage
- `ai4se-demo-project`：Java/JUnit/JaCoCo；固定本地提交 `c7d19b48433e9794c58b2c498201bd1181d4c99a`，使用 JDK 19 与环境变量 `TEST_DB_PASSWORD`
- `naodeng.com.cn`：TypeScript/Playwright

案例只保存脱敏、显式映射的输入。源项目提交、运行环境、案例 metadata、测试 identity 和映射必须同步更新；不要把源代码、凭据、绝对路径或完整原始报告写入 QCov。

## 质量门与维护方式

提交前运行：

```bash
PYTHONPATH=. .venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/mypy qcov
.venv/bin/python -m build
git diff --check
```

在工作树环境中，`.venv` 路径按工作树位置调整。构建隔离环境无法联网时，记录为环境阻塞，不得标记为产品构建失败或通过。

新功能或修复应先添加聚焦测试并观察 RED，再做最小实现并验证 GREEN。发布、Tag、GitHub Release、CI 和包仓库状态是不同证据，必须分别验证。

## 后续方向

1.5 和 2.0 只是候选方向，需另行批准设计。可能主题包括 AI 辅助理解/规划、QA-for-AI 证据维度、质量反馈闭环与 Quality BOM。不得在未批准设计前扩大为远程 Git、自动推断、覆盖率提升为业务证据、Web UI、持久化或策略 DSL。

## 历史追溯

1.0 前的过程文档、计划、规格和临时报告已从发布工作树移除。需要历史决策或验证细节时，使用 Git：

```bash
git log --all -- docs/process docs/superpowers
git log --all -- path/to/file
git show <commit>:path/to/file
```
