# 需求

MVP 接收版本化的 Obligation/Evidence 文件，进行校验、计算四种义务状态，并输出 JSON 或 Markdown。通过的证据必须精确匹配义务 ID、维度和所需类型。AI、UI、存储、Git diff、外部插件加载和策略执行不在范围内。

Iteration 1 增加配置驱动的 pytest marker、JUnit XML 和 coverage.py XML 本地发现。通用导入仅是 inventory observation，只有显式映射后才能关联 Obligation。
