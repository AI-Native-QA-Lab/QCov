# 更新日志

## 0.7.0 - 2026-09-09

### 新功能

- 新增确定性的 `qcov plan`：使用固定收益/成本启发式对未被证明的义务维度排序，
  为下一步最优验证工作产出 draft `quality_plan` 提议。
- 新增稳定的 `quality_plan`、`evaluation_gaps` 与 `planned_verification`
  协议取值，并提供本地化 Markdown 计划输出。

### 边界

- 计划提议保持本地、确定性且仅提议：它们永远不是 QualityEvidence，也不能改变
  Gap Engine 或 policy 决策。

### 文档

- 在双语公开文档和中文过程记录中说明 Iteration 6 planner 的行为、边界与验证证据。

## 0.6.0 - 2026-09-08

### 新功能

- 将 pytest-marker observation 合并入确定性评估，并在声明式 mapping 中支持受限的 identity 后缀通配符。
- 新增离线、仅提议的 `qcov obligation suggest` 与 `qcov risk analyze`；提议不是证据，也不能成为门禁权威。

### 文档

- 记录 Iteration 5 的本地/离线边界和提议工作流。

## 0.5.0 - 2026-09-08

### 新功能

- 新增确定性的本地 `qcov policy check`：显式评估时间、默认覆盖状态规则、带时限的精确豁免，以及 PASS/WARN/BLOCK 决策。
- 新增稳定 JSON、本地化 Markdown 策略报告和可运行的 Refund 策略示例。

### 修复

- 将非法策略格式和语言参数统一映射为稳定的输入退出码 4，并显式标识需清理的过期豁免。

### 文档

- 新增中文主策略参考、英文 README 入口、过程证据和 Iteration 4 路线图完成状态。

## 0.3.0 - 2026-09-06

### 新功能

- 通过确定性的 built-in adapter registry 新增本地 Playwright JSON 与 LCOV inventory reader。

### 文档

- 新增 Iteration 2 的设计、实施、验证记录，以及新报告导入的可运行中英示例。

## 0.2.1 - 2026-09-06

### 修复

- 将缺少 obligation inventory 的结果从 `MISSING` 修正为 `UNKNOWN`。
- 让 `qcov init` 生成有效的 `QCovConfig`，并分别应用 `--config` 的局部显式覆盖。
- pytest-marker 发现过程排除隐藏依赖目录。

### 改进

- 在 Markdown 报告中展示 observed evidence ID，并在扫描输出中展示 pytest 文件与
  marker 记录事实。
- 恢复 `--obligations` 兼容别名，并统一配置与扫描诊断的路径解析。

### 文档

- 同步中英文技术文档，完成 Iteration 1 跟踪状态，并记录代码审查修复的 TDD 证据。
