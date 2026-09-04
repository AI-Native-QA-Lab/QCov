# Protocol

`qcov.dev/v1alpha1` defines `TestingObligation`, `QualityEvidence`, and
`QualityPolicy`. Machine keys are English; localized prose uses `en` and
`zh-CN`. Published schemas are in `schemas/`. Stable errors such as
`QCOV-SCHEMA-001` are never translated.

`QCovConfig` is also versioned as `qcov.dev/v1alpha1`; invalid configuration is
reported as `QCOV-CONFIG-001`. `QCOV-SCAN-001` represents a non-fatal artifact
inspection diagnostic.
