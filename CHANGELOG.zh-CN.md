# 更新日志

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
