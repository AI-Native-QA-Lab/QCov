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

三个固定提交均已在隔离临时目录重新克隆并核对。Python 实际运行 90 项测试通过；
脱敏 JUnit inventory 保留 90 个 identity，coverage.py XML 只保留 1 条聚合 inventory。
显式 JUnit mapping 物化 20 条 passed evidence，10 条经审阅 obligation 均为
`COVERED`。

Java 已在项目所有者提供的本地数据库及 JDK 19 下重跑：23 项测试通过并生成 JaCoCo XML，
源版本已固定为本地提交 `c7d19b48433e9794c58b2c498201bd1181d4c99a`。Playwright mapping
来自脱敏的成功 JSON 报告，但只能证明其中显式列出的导航 identity。

30 条 obligation 均完成 source.ref、标题、风险和 requiredEvidence 审阅，且已有所有者
接受与独立审阅记录。三个 Release Gate 仍保持 `NOT_MET`，因为 false-gap 发现仍需在修复后
重新裁决。

从干净 QCov 安装到首次成功输出 `qcov gaps` 的本地墙钟 TTFV 分别为：Python 12 秒、
Java 7 秒、TypeScript 7 秒；这些是本机测量值，不是性能承诺。

## 复现步骤

1. 从源项目所有者获取项目，并检出各自 `metadata.yaml` 记录的提交。
2. 确认该提交中的 `source.reference_files` 仍存在。
3. 只在源项目检出中运行记录的命令；QCov 仓库不会自动运行这些命令。
4. 脱敏报告内容，再创建显式 QCov evidence mapping。只有 JUnit 或 Playwright identity
   可物化 QualityEvidence；coverage.py 和 JaCoCo 始终只是 inventory，不能自动成为
   已通过 evidence。
5. 每个项目至少审阅 10 条 obligation，并收集 1.0 Release Gate 指标：可解释的
   缺口价值、false-gap rate、Gap → Added Verification conversion，以及开发/QA 接受度。

源记录是快照。再次验证某案例时，必须同步刷新提交和 metadata。
