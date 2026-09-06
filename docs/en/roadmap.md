# Roadmap

Iteration 0 proves Obligation → Evidence → Gap. Iteration 1 expands CLI imports;
Iteration 2 adds language/tool adapters; Iteration 3 introduces local PR delta;
Iteration 4 policies/waivers; Iterations 5–7 AI proposals and planning; and
Iteration 8 production evidence. Validate integration time, explainability, gap
value beyond ordinary reports, and AI proposal acceptance before expanding.

Iteration 1 is now the local first-value import milestone: config, pytest
marker detection, JUnit XML, and coverage.py XML inventory.

Iteration 2 adds local Playwright JSON and LCOV inventory readers through an
explicit built-in registry. External adapter plugins remain out of scope.

Iteration 3 adds read-only committed-tree comparison through `qcov diff`.
Policy gates, remote Git operations, and source-line impact inference remain deferred.
