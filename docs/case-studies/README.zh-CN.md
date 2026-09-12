# QCov 1.0 案例输入包

QCov 1.0 需要在 Python/pytest/coverage、Java/JUnit/JaCoCo 与
TypeScript/Playwright 三类真实项目上验证。
[`examples/case-studies/`](../../examples/case-studies/) 保存三个可复现、
已脱敏的输入包；本目录说明它们的边界与使用方式。

每个包固定了本次审阅的源项目提交、技术栈和源项目所有者应执行的命令，并
包含少量显式 obligation；其中 `source.ref` 对应固定提交中的真实文件路径。
包内绝不复制源码、测试输出、凭据、绝对路径或环境配置。它们是验证输入，
不是源项目夹具的替代品。

## 当前状态

三个包均为 `NOT_RUN`，Release Gate 状态均为 `NOT_MET`。它们只是诚实的
起步骨架，并不表示 QCov 已完成真实项目验证。尤其是 Java 项目固定版本的
`pom.xml` 尚未配置 JaCoCo；当前也没有导入或映射任何报告，且每个项目都不足
10 条经审阅 obligation。

## 复现步骤

1. 从源项目所有者获取项目，并检出各自 `metadata.yaml` 记录的提交。
2. 确认该提交中的 `source.reference_files` 仍存在。
3. 只在源项目检出中运行记录的命令；QCov 仓库不会自动运行这些命令。
4. 脱敏报告内容，再创建显式 QCov evidence mapping。JUnit、pytest、coverage、
   JaCoCo 或 Playwright 结果都只是 inventory 输入，不会自动成为已通过 evidence。
5. 每个项目至少审阅 10 条 obligation，并收集 1.0 Release Gate 指标：可解释的
   缺口价值、false-gap rate、Gap → Added Verification conversion，以及开发/QA 接受度。

源记录是快照。再次验证某案例时，必须同步刷新提交和 metadata。
