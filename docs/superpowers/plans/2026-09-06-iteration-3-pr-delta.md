# Iteration 3 PR Delta Implementation Plan

> Execute inline with executing-plans and test-driven-development. User approved
> the design on 2026-09-06. No commit, push, or release is requested.

**Goal:** Explain obligation/evidence changes between two local committed trees.
**Architecture:** Git snapshot loader → pure comparison → localized reports/CLI.
**Tech Stack:** Python 3.11+, Git subprocess argument lists, existing Pydantic/YAML/Typer.

## 1. Committed snapshot loader

- [x] Add `tests/engine/test_git_snapshots.py`: real temporary Git repositories,
  separate revisions/configs, empty snapshots, duplicate IDs, unsafe paths,
  malformed inputs and unknown refs. Run `.venv/bin/pytest tests/engine/test_git_snapshots.py` for RED.
- [x] Create `qcov/engine/git_snapshots.py`: `DiffInputError`, `Snapshot`,
  `load_snapshot(repo, ref, config)`. Resolve commit OIDs with rev-parse,
  list NUL-delimited tree entries, read regular blobs by object ID, validate
  config-relative patterns and parse existing protocol models. Reject missing
  patterns, symlinks, submodules, absolute paths and traversal. Run scoped GREEN.

## 2. Pure comparison

- [x] Add `tests/engine/test_delta.py` and run RED for `compare_snapshots`:
  added/removed/modified/unchanged, definition-only changes, evidence changes,
  no promotion of unrelated evidence, unknown transitions and stable ordering.
- [x] Create `qcov/engine/delta.py`: sorted IDs, canonical model comparison,
  evaluator reuse, typed before/after obligation results and explicit changed
  evidence IDs. Preserve four-state semantics. Run scoped GREEN.

## 3. Reports and command

- [x] Add `tests/cli/test_diff.py` for real revisions, JSON, both locales,
  dirty checkout isolation, format/locale validation and input error exit 4.
  Run scoped RED (diff command absent).
- [x] Create `qcov/engine/delta_reports.py`, register `diff` in
  `qcov/cli/app.py`, and extend `qcov/i18n/catalog.py`. JSON contains commit
  OIDs and ordered per-obligation results; Markdown shows each side's dimension
  types/status/evidence. Run all three new suites for GREEN.

## 4. Documentation and verification

- [x] Add bilingual `docs/{en,zh-CN}/pr-delta.md`, update README, roadmap,
  development, requirements/technical scope as needed and process index.
- [x] Add executable `examples/pr-delta/demo.py` creating a temporary Git
  repository and running the installed CLI without changing this checkout.
- [x] Record actual RED/GREEN and final evidence under `docs/process/`.
- [x] Run `.venv/bin/pytest`, `.venv/bin/ruff check .`, `.venv/bin/mypy qcov`,
  `.venv/bin/python -m build`, and `git diff --check`. Check final Git status.
