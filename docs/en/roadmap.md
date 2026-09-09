# Roadmap

QCov remains a local, deterministic Quality Evidence Gap Engine. It reports
what remains unproven for an obligation; it is not a line-coverage detector or
test runner.

## Delivered through Iteration 6

Iteration 0 proves Obligation → Evidence → Gap. Iteration 1 adds config-driven
local discovery for pytest markers, JUnit XML, and coverage.py XML inventory.
Iteration 2 adds Playwright JSON and LCOV inventory readers through an explicit
built-in registry; external adapter plugins remain out of scope. Iteration 3
adds read-only committed-tree comparison through `qcov diff`. Iteration 4 adds
local `qcov policy check` with default status rules, auditable exact waivers,
explicit `--as-of`, and PASS/WARN/BLOCK decisions. Iteration 4.5 adds declarative
`EvidenceMapping` for junit/playwright inventory, `qcov map preview`, and
`--config` evaluation merge. Iteration 5 adds pytest-marker evaluation merge,
limited identity suffix wildcards, and proposal-only AI (`obligation suggest` /
`risk analyze`) with a default offline provider. Iteration 6 adds deterministic
`qcov plan`: fixed benefit/cost heuristics over unproven gaps emit a draft
`QualityProposal` (`type: quality_plan`) for next-best verification—never
evidence or gate authority.

Remote Git operations, source-line impact inference, policy DSL, dimension
thresholds, wildcard waivers, coverage/LCOV promotion to passed evidence, and
automatic inventory-to-evidence inference remain deferred unless a later design
approves them.

## Gate after 4.5

Validate real-project integration time, explainability, and gap value beyond
ordinary reports before accelerating AI. Mapping must stay declarative and local.
Adapters still must not infer that a passing test or coverage rate proves a
business obligation. Design reference:
`docs/superpowers/specs/2026-09-08-post-4.5-iteration-roadmap-design.md`.
See also [explicit evidence mapping](mapping.md).

## Planned Iterations 7–8

Principle: AI proposes; policy approves; the deterministic engine verifies. AI
must never become evidence or gate authority.

| Iteration | Focus |
| --- | --- |
| **7** | Agentic Quality Loop only (stable agent contracts; optional `explain`) |
| **8** | Production evidence only (runtime / incident / observability-style producers under protocol rules) |

**Roadmap Complete through Iteration 8** closes this core arc (gap → change →
policy → mapping → AI propose/plan/agent feedback → production feedback). It is
a milestone, not the end of the product.

## Post-8 backlog

Separate approved designs are required for QA-for-AI dimensions, Quality BOM,
Adapter SDK / broader ecosystems, remote Git and deeper CI automation, policy
DSL and dimension thresholds, coverage/LCOV promotion to covering evidence,
automatic inventory-to-obligation inference, web UI, persistence, and a packaged
Continuous Quality Control Plane.

## Validation gates before expansion

Validate these assumptions before accelerating into AI or production adapters:
Testing Obligations add value beyond requirement-to-test links; initial
integration is fast; gaps remain explainable; the tool finds omissions that
ordinary reports hide; and AI proposals never override deterministic decisions.
