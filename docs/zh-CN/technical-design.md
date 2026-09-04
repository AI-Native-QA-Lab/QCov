# 技术设计

每个所需维度中，精确匹配义务引用和允许类型的 passed 证据为 `COVERED`；unknown 观测为 `UNKNOWN`；其他情况为 `MISSING`。所有维度覆盖才是 covered；全 missing 为 missing；全 unknown 为 unknown；任何混合为 partial。不计算聚合分数。

JUnit XML 与 coverage.py XML 只产生测试/结构 inventory；QCov 不会从测试名、类名或 line rate 推断需求关联。
