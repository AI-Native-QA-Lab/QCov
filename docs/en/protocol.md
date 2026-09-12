# Protocol

`qcov.dev/v1alpha1` defines `TestingObligation`, `QualityEvidence`, and
`QualityPolicy`. Machine keys are English; localized prose uses `en` and
`zh-CN`. Published schemas are in `schemas/`. Stable errors such as
`QCOV-SCHEMA-001` are never translated.

`QCovConfig` is also versioned as `qcov.dev/v1alpha1`; invalid configuration is
reported as `QCOV-CONFIG-001`. `QCOV-SCAN-001` represents a non-fatal artifact
inspection diagnostic.

QCov 1.0 adds the additive `qcov.impact/v1` and `qcov.adapter/v1` contracts.
The impact output schema is [qcov.impact-v1.schema.json](../../schemas/qcov.impact-v1.schema.json);
its `changedFiles`, obligation IDs, gap arrays, diagnostics, and ordering rules
are stable for the 1.0 release. `qcov.agent/v1` remains proposal/helper output
and keeps its existing compatibility contract. None of these contracts rename
or weaken `qcov.dev/v1alpha1`, and no `qcov.agent/v2` is introduced in 1.0.
