# Roadmap

QCov remains a local, deterministic Quality Evidence Gap Engine. It reports
what remains unproven for an obligation; it is not a line-coverage detector or
test runner.

## Delivered through Iteration 4

Iteration 0 proves Obligation → Evidence → Gap. Iteration 1 adds config-driven
local discovery for pytest markers, JUnit XML, and coverage.py XML inventory.
Iteration 2 adds Playwright JSON and LCOV inventory readers through an explicit
built-in registry; external adapter plugins remain out of scope. Iteration 3
adds read-only committed-tree comparison through `qcov diff`. Iteration 4 adds
local `qcov policy check` with default status rules, auditable exact waivers,
explicit `--as-of`, and PASS/WARN/BLOCK decisions.

Remote Git operations, source-line impact inference, policy DSL, dimension
thresholds, wildcard waivers, and inventory-to-evidence inference remain
deferred.

## Next: Iteration 4.5 mapping and validation

Before AI work, close the first-value loop that ADR 0003 deferred: an **explicit
obligation mapping** from inventory observations (and related adapter output) to
`QualityEvidence`, plus real-project checks of integration time, explainability,
and gap value beyond ordinary reports.

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
