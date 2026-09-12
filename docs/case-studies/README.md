# QCov 1.0 case-study inputs

QCov 1.0 needs real-project validation across Python/pytest/coverage,
Java/JUnit/JaCoCo, and TypeScript/Playwright. This directory documents the
three source-redacted, reproducible input packages in
[`examples/case-studies/`](../../examples/case-studies/).

Each package pins the source revision inspected, declares its stack and source
owner command, and includes a small set of explicit obligations whose
`source.ref` is a real path in that pinned project. The packages deliberately do
not copy source code, test output, credentials, absolute paths, or environment
settings. They are validation inputs, not substitute project fixtures.

## Current status

All three packages are `NOT_RUN` and their release-gate status is `NOT_MET`.
They are an honest starting skeleton, not evidence that QCov has validated the
projects. In particular, the Java project's pinned `pom.xml` does not configure
JaCoCo. No report has been imported or mapped, and each project has fewer than
the required ten reviewed obligations.

## Reproducing a case

1. Obtain the source project from its owner and check out the commit recorded in
   its `metadata.yaml`.
2. Confirm the recorded `source.reference_files` still exist at that revision.
3. Run only the declared project command in that checkout; this repository never
   runs it automatically.
4. Redact report content and create an explicit QCov evidence mapping. A JUnit,
   pytest, coverage, JaCoCo, or Playwright result is inventory input, not
   automatically passed evidence.
5. Review at least ten obligations per project and collect the 1.0 release-gate
   measures: explainable gap value, false-gap rate, gap-to-verification
   conversion, and developer/QA acceptance.

The source records are snapshots, so refresh the commit and metadata together
when a case is revalidated.
