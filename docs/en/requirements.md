# Requirements

The MVP accepts versioned obligation/evidence files, validates them, computes
four states per obligation, and renders JSON or Markdown. Exact passed evidence
must match obligation ID, dimension, and required type. It excludes AI, UI,
storage, Git diff, external plugin loading, and policy enforcement.

Iteration 1 adds config-driven local discovery for pytest markers, JUnit XML,
and coverage.py XML. Generic imports remain inventory observations until an
explicit obligation mapping exists.
