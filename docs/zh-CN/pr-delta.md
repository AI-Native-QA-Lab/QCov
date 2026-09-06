# PR 质量覆盖增量

使用 `qcov diff` 比较本地 Git 仓库中两个已存在提交里的显式 Testing Obligation
和 Quality Evidence。

```bash
qcov diff --repo . --base origin/main --head HEAD --config qcov.yaml
qcov diff --repo . --base origin/main --head HEAD --config qcov.yaml --format json
```

报告按稳定义务 ID 展示 `ADDED`、`REMOVED`、`MODIFIED` 或 `UNCHANGED`，并列出
变更前后覆盖状态和已变更的关联证据 ID。它只读取 Git 对象：不会 fetch、切换提交、
执行测试，也不会读取脏文件或未跟踪文件。需要比较共同祖先时，请显式传给 `--base`。

缺失提交或配置、错误协议数据、仓库外路径、符号链接、重复 ID 和未匹配配置路径会产生
`QCOV-DIFF-001` 并以退出码 4 结束。有效空配置表示空快照。该命令不设策略门禁。
