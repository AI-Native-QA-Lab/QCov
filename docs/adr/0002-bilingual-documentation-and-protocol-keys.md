# ADR 0002: Keep protocol keys English and localize presentation

## Status

Accepted — 2026-09-03.

## Decision

Schemas, YAML keys, CLI flags, enums, and error codes are English and stable.
English is the default README; Chinese has an equivalent entry point and
paired documentation. Localized title/message fields use `en` and `zh-CN`.

## Consequences

Automation receives a language-neutral contract, while people can use CLI
reports and documentation in either supported language without changing data.
