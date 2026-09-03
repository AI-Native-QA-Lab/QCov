# ADR 0001: Use a Python CLI with a deterministic core

## Status

Accepted — 2026-09-02.

## Decision

The MVP is an installable Python 3.11+ CLI. Its core computes evidence gaps
deterministically from explicit Testing Obligations and Quality Evidence.

## Consequences

The initial release has no database, web UI, AI provider, or remote service.
Adapters normalize data at the edge; they do not decide gap status. This makes
the core easy to test and leaves language-specific integrations to later
iterations.
