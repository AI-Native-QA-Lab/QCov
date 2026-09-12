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

The three fixed commits were cloned into isolated temporary directories and
rechecked. Python completed with 90 passing tests; its redacted JUnit inventory
has 90 identities and its coverage.py XML has one aggregate inventory record.
Explicit JUnit mapping materialized 20 passed evidence entries and the ten
reviewed obligations evaluate as `COVERED`.

The Java case was re-run against the owner-provided local database with JDK 19:
23 tests passed and JaCoCo XML was generated at local fixed commit
`c7d19b48433e9794c58b2c498201bd1181d4c99a`. Playwright mapping is derived from
a redacted successful JSON report, but remains scoped to the explicit
navigation identities it contains.

All thirty obligations received source/ref/title/risk/required-evidence review;
owner acceptance and independent reviews are recorded. All release-gate statuses
remain `NOT_MET` because false-gap findings still require a post-fix adjudication.

Clean-install Time to First Value, measured through first successful `qcov gaps`
output, was 12 seconds (Python), 7 seconds (Java), and 7 seconds (TypeScript).
These are local wall-clock measurements, not a performance guarantee.

## Reproducing a case

1. Obtain the source project from its owner and check out the commit recorded in
   its `metadata.yaml`.
2. Confirm the recorded `source.reference_files` still exist at that revision.
3. Run only the declared project command in that checkout; this repository never
   runs it automatically.
4. Redact report content and create an explicit QCov evidence mapping. Only
   JUnit or Playwright identities can materialize evidence; coverage.py and
   JaCoCo remain inventory, never automatically passed evidence.
5. Review at least ten obligations per project and collect the 1.0 release-gate
   measures: explainable gap value, false-gap rate, gap-to-verification
   conversion, and developer/QA acceptance.

The source records are snapshots, so refresh the commit and metadata together
when a case is revalidated.
