# Iteration 3: PR Quality Coverage Delta

Status: Approved by the user on 2026-09-06; implementation in progress.

## Purpose / 目标

Compare explicit Testing Obligations and Quality Evidence at two local Git
commits, producing an explainable PR delta without checking out either revision.
比较两个本地 Git 提交中的显式测试义务与质量证据，生成可解释的 PR 增量报告。

## Options / 方案

1. Recommended: read protocol inputs from Git revisions and reuse the existing
   deterministic evaluator. This directly supports PR comparisons with no new
   snapshot publishing workflow.
2. Compare exported JSON reports. Simpler input handling, but requires separately
   generated baseline reports and cannot explain obligation definition changes.
3. Infer affected obligations from changed source lines. Broader impact analysis
   requires a new source mapping contract and is deferred.

推荐读取 Git 提交中的协议文件并复用现有引擎。比较导出报告需要额外维护基线；
从源码变更推断受影响义务需要新的映射契约，留待后续设计。

## Command and revision semantics / 命令与提交语义

`qcov diff --base <ref> --head HEAD --config qcov.yaml --format markdown --locale en`

- Resolve refs to immutable commit IDs before reading inputs. Read only locally
  available commits; never fetch, execute project code, or change the checkout.
- Compare base to head directly. For PR merge-base semantics, the caller passes
  the desired merge-base commit as base; the command does not silently substitute it.
- Config is repository-relative and loaded separately at each revision. Resolve
  obligation/evidence patterns against each committed tree, relative to its config.
  Reject absolute paths, parent traversal, symlinks, and non-blob inputs.
- Missing revisions/configs, malformed protocol data, unresolved explicit paths,
  and duplicate IDs within a snapshot are input errors, never empty baselines.
- Valid empty lists permit an explicitly empty snapshot. Unmatched nonempty
  patterns are errors, avoiding accidental deletion reports.

提交引用先解析为固定 SHA；只读本地 Git 对象，不切换工作区。直接比较 base 与 head，
PR 的共同祖先由调用者明确传入。每侧读取自己的配置，路径限于仓库内普通文件；
缺失输入、重复 ID、错误协议与未匹配模式均报错，显式空列表允许空快照。

## Comparison model / 比较模型

- Match obligations by stable ID; support multiple obligations per snapshot.
- Report added, removed, modified, and unchanged obligations with before/after
  statuses and per-dimension required types, statuses, and observed evidence IDs.
- Treat changes to obligation definitions and referenced evidence contents as
  modifications even when aggregate status is unchanged.
- Describe dimension transitions explicitly. Do not assign an arbitrary numeric
  ordering to UNKNOWN, MISSING, PARTIAL, and COVERED, or interpret removal as improvement.
- Preserve the existing evaluator semantics. Imported test/coverage inventory is
  not promoted to QualityEvidence. Unreferenced evidence does not confer coverage.
- Deterministic JSON uses English machine keys and stable ID/dimension ordering;
  Markdown supports en and zh-CN. Include resolved base/head SHAs for traceability.
- Successful comparisons exit 0 even when gaps increase; invalid inputs exit 4
  with a stable QCOV-DIFF error identifier. Policy gates remain Iteration 4.

按稳定 ID 比较多个义务，展示新增、删除、修改与未变项以及逐维度前后状态。
义务定义或关联证据内容变化也计为修改。不对四种状态强行排序，不把删除视作改善。
JSON 保持确定性，Markdown 支持中英文，报告包含两侧 SHA。差异本身不触发策略门禁。

## Architecture / 架构

A read-only Git snapshot loader validates paths and protocol inputs; a pure delta
engine compares loaded snapshots using evaluate_obligation; report renderers
produce JSON and localized Markdown; the CLI handles arguments and stable errors.
No new runtime dependency or protocol-schema change is planned.

只读 Git 快照加载器负责路径及协议校验；纯比较引擎复用现有评估逻辑；
渲染器输出 JSON 与双语 Markdown；CLI 统一参数和错误。预计不增加运行时依赖或协议字段。

## Acceptance and execution / 验收与实施

1. Record focused RED/GREEN evidence for snapshot loading, comparison, and CLI.
2. Use temporary real Git repositories to verify two committed revisions, added
   and removed obligations, definition-only changes, evidence changes, unknown
   states, empty snapshots, invalid refs/configs, duplicate IDs, and unsafe paths.
3. Verify dirty/untracked worktree contents do not affect committed comparisons
   and the command leaves Git status unchanged.
4. Verify deterministic JSON and both Markdown locales through CLI integration.
5. Update paired user/developer documentation, README navigation, an executable
   example, roadmap, and dated process records.
6. Run full pytest, ruff check ., mypy qcov, python -m build, and git diff --check;
   record actual results and inspect final Git status.

遵循逐项 TDD，使用真实临时 Git 仓库覆盖正常路径与边界，验证脏工作区不影响结果且
不会被修改。同步双语文档、示例及过程记录，执行完整测试、静态检查和构建。
提交、推送、PR 与版本发布不包含在本设计的默认交付范围内。
