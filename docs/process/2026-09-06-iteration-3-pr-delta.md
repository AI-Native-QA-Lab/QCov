# Iteration 3 PR Delta

## TDD evidence

- RED: the snapshot suite failed while `load_snapshot` was absent, then on the
  recursive-glob case. GREEN: `.venv/bin/pytest tests/engine/test_git_snapshots.py -q`
  passed `20 passed`; module mypy passed.
- RED: the pure delta suite failed while `compare_snapshots` was absent. GREEN:
  `.venv/bin/pytest tests/engine/test_delta.py -q` passed `4 passed`; module
  mypy passed.
- RED: CLI test exposed a test-fixture Git configuration typo. GREEN:
  `.venv/bin/pytest tests/cli/test_diff.py -q` passed `2 passed`, covering real
  committed revisions, JSON, zh-CN Markdown, and stable error exit code.

## Scope

Implemented read-only local `qcov diff`: each revision loads its own config,
the existing evaluator computes results, and output reports added, removed,
modified, or unchanged obligations. Policies, remote fetching, checkout changes,
source-line mapping, and inferred evidence remain outside Iteration 3.

## Final verification

On 2026-09-06, `.venv/bin/ruff check .` passed, `.venv/bin/pytest` passed
`77 passed`, `.venv/bin/mypy qcov` passed with no issues, and
`.venv/bin/python -m build` produced the sdist and wheel after the approved
networked isolated-build retry installed `hatchling==1.32.0`. `git diff --check`
also passed.

## Review remediation

The Ponytail review found that `PurePosixPath.match('*.yaml')` can match a
nested path, unlike the existing configuration resolver. The Git snapshot
loader now uses segment-aware standard-library matching so `*` stays in one
directory while `**` recurses. Markdown now renders before/after dimension
requirements, statuses, and observed evidence. The two focused regression
tests passed before the final suite was rerun.

The executable `examples/pr-delta/demo.py` was added after plan completion
review. Its focused test passed and it uses only a temporary Git repository.
