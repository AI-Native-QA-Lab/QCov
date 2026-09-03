# Technical Design

For each required dimension, passing evidence with an exact obligation reference
and accepted type is `COVERED`; unknown observation is `UNKNOWN`; otherwise it
is `MISSING`. An obligation is covered only when all dimensions are covered,
missing when all are missing, unknown when all are unknown, and partial for any
mixture. No aggregate score is calculated.
