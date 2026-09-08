# Roadmap

QCov remains a local, deterministic Quality Evidence Gap Engine. It reports
what remains unproven for an obligation; it is not a line-coverage detector or
test runner.

## Delivered through Iteration 4.5

Iteration 0 proves Obligation → Evidence → Gap. Iteration 1 adds config-driven
local discovery for pytest markers, JUnit XML, and coverage.py XML inventory.
Iteration 2 adds Playwright JSON and LCOV inventory readers through an explicit
built-in registry; external adapter plugins remain out of scope. Iteration 3
adds read-only committed-tree comparison through `qcov diff`. Iteration 4 adds
local `qcov policy check` with default status rules, auditable exact waivers,
explicit `--as-of`, and PASS/WARN/BLOCK decisions. Iteration 4.5 adds declarative
`EvidenceMapping` for junit/playwright inventory, `qcov map preview`, and
`--config` evaluation merge.

Remote Git operations, source-line impact inference, policy DSL, dimension
thresholds, wildcard waivers, coverage/LCOV promotion to passed evidence, and
automatic inventory-to-evidence inference remain deferred.

## Next after 4.5

Validate real-project integration time, explainability, and gap value beyond
ordinary reports before AI work. Design reference:
`docs/superpowers/specs/2026-09-08-iteration-4.5-obligation-mapping-design.md`.
See also [explicit evidence mapping](mapping.md).

Mapping must stay declarative and local. Adapters still must not infer that a
passing test or coverage rate proves a business obligation.
## Later iterations

Iterations 5–7 may introduce AI only as a proposal and planning layer under
deterministic policy checks. AI must never become evidence or gate authority.
Iteration 8 integrates production evidence.

## Validation gates before expansion

Validate these assumptions before accelerating into AI or production adapters:
Testing Obligations add value beyond requirement-to-test links; initial
integration is fast; gaps remain explainable; the tool finds omissions that
ordinary reports hide; and AI proposals never override deterministic decisions.
