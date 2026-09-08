# Concepts

QCov models a **Testing Obligation**: why a requirement, risk, invariant, or
change must be verified. **Quality Evidence** is machine-readable proof mapped
to an obligation. The engine compares required and observed evidence and reports
an explainable gap, not a quality percentage.

A **QualityProposal** is a draft suggestion from `qcov obligation suggest` or
`qcov risk analyze`. Proposals are never evidence and never change `policy check`
or Gap Engine decisions: AI proposes; policy approves; the deterministic engine
verifies.
