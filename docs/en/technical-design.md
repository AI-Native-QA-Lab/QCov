# Technical Design

For each required dimension, passing evidence with an exact obligation reference
and accepted type is `COVERED`; unknown observation is `UNKNOWN`; otherwise it
is `MISSING`. An obligation is covered only when all dimensions are covered,
missing when all are missing, unknown when all are unknown, and partial for any
mixture. No aggregate score is calculated.

JUnit XML and coverage.py XML report only test/structural inventory. QCov does
not infer a requirement relationship from a test name, class name, or line rate.
