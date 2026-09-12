# Iteration 8 Production Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement task-by-task.

**Goal:** Add offline production observation inventory that can become evidence only through explicit mapping.

**Spec:** `docs/superpowers/specs/2026-09-11-iteration-8-production-evidence-design.md`

## Tasks

- [ ] Add strict `ProductionObservationReport` Pydantic models and a `ProductionObservationAdapter`; first test a valid report, invalid timezone, duplicate observation id, and malformed artifact diagnostic.
- [ ] Add `scan.production`, `ResolvedPaths.production`, registry and scan wiring; first test config resolution and deterministic scan summary.
- [ ] Extend mapping producer/status handling; first test passed/failed production mapping and observation timestamp authority; test unmatched observation produces no evidence.
- [ ] Add static production example and test existing `scan` / `map preview` CLI paths; no new command or network integration.
- [ ] Update paired public docs, roadmap/requirements, link tests and Chinese process evidence.
- [ ] Run `.venv/bin/pytest -q`, `.venv/bin/ruff check .`, `.venv/bin/mypy qcov`, `.venv/bin/python -m build`, and `git diff --check`.
