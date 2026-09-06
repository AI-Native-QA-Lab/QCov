# Iteration 2 Adapter Verification

Iteration 2 adds Playwright JSON and LCOV inventory readers and a deterministic
built-in adapter registry. Imports remain observations, never obligation
evidence.

The focused tests were first run before implementation and failed during
collection because the new modules were absent. After the minimal readers,
registry, and config fields were added, the focused and regression suites passed.

Follow-up review added coverage for the registry, nested Playwright suites,
all four Playwright outcomes, unterminated LCOV sections, and documentation
claims. Those follow-up tests were added after the original implementation, so
they are regression evidence rather than retrospective RED/GREEN evidence.

Final validation runs pytest, Ruff, mypy, package build, example scans, and
`git diff --check`; malformed or missing reports remain `QCOV-SCAN-001` diagnostics.

Observed results: `49 passed`, Ruff passed, mypy reported no issues, the example
scan detected five adapters with no diagnostics, and `git diff --check` passed.
After retrying with network access, `python -m build` passed in its isolated
environment with `hatchling==1.32.0` and built `qcov-0.2.1.tar.gz` and
`qcov-0.2.1-py3-none-any.whl`. The local `--no-isolation` build also passed.
