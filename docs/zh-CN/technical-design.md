# 技术设计

每个所需维度中，精确匹配义务引用和允许类型的 passed 证据为 `COVERED`；缺少该 obligation 的 inventory 或出现 unknown 观测为 `UNKNOWN`；其他情况为 `MISSING`。所有维度覆盖才是 covered；全 missing 为 missing；全 unknown 为 unknown；任何混合为 partial。Markdown 和 JSON 报告会列出每个维度的 observed evidence ID；不计算聚合分数。

JUnit XML 与 coverage.py XML 只产生测试/结构 inventory；QCov 不会从测试名、类名或 line rate 推断需求关联。

Playwright JSON 与 LCOV 导入遵循相同的 inventory-only 规则，保留测试结果或源代码行计数，不会创建 Quality Evidence。

`gaps`、`check` 和 `report` 接受 `--obligation`（兼容旧的 `--obligations` 别名）与 `--evidence`。使用 `--config` 时，显式参数只覆盖其对应的配置默认值。
