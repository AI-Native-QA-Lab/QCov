# Concepts

QCov models a **Testing Obligation**: why a requirement, risk, invariant, or
change must be verified. **Quality Evidence** is machine-readable proof mapped
to an obligation. The engine compares required and observed evidence and reports
an explainable gap, not a quality percentage.

A **QualityProposal** is a draft suggestion from `qcov obligation suggest`,
`qcov risk analyze`, or `qcov plan`. `qcov plan` applies a deterministic
heuristic to unproven gaps and emits a `quality_plan` draft. Proposals are never
evidence and never change `policy check` or Gap Engine decisions: AI proposes;
policy approves; the deterministic engine verifies.

`qcov explain` and `qcov agent next` help coding agents consume gaps and plans
under a stable `qcov.agent/v1` JSON envelope. They do not run tests, write
evidence, or act as gates. See [agent playbook](agent.md).
