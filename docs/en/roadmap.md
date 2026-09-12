# Roadmap

QCov is a local, deterministic Quality Evidence Gap Engine. It answers what
remains unproven about an explicit requirement, risk, or change; it is neither a
line-coverage detector nor a test runner.

## Delivered through Iteration 7

Iterations 0–4 establish explicit Obligation → Evidence → Gap evaluation,
local inventory discovery, committed-tree `qcov diff`, and deterministic local
`qcov policy check`. Iteration 4.5 adds declarative `EvidenceMapping` and map
preview. Iterations 5–7 add proposal-only assistance, deterministic planning,
and `qcov.agent/v1` helpers. These helpers do not run tests, write authoritative
evidence, or decide gates. See the [agent playbook](agent.md).

## Planned Iteration 8: production-observation foundation

Iteration 8 delivered an offline production-observation inventory producer under the
existing protocol rules. Runtime, incident, and observability observations stay
inventory until an explicit `EvidenceMapping` materializes them as evidence.
It is a foundation for validation, not a claim that production feedback or the
product roadmap is complete.

## QCov 1.0 — Find the Gap

**Question:** What is still unproven?

**Goal:** Prove QCov creates value in real projects without an AI dependency for
core correctness.

Iteration 9 is the 1.0 delivery track:

| Workstream | Outcome |
| --- | --- |
| Real-project validation | Validate Python/pytest/coverage, Java/JUnit/JaCoCo, and TypeScript/Playwright projects; target at least 3 projects, 30 real obligations, and time to first value of 10 minutes or less. |
| Change → obligation impact | Deterministic path/package/module/service/API/component mappings produce affected obligations and the resulting gap delta through `qcov impact`, `qcov affected`, and local `qcov diff`. |
| Adapter extensibility | Define `qcov.adapter/v1` and an Adapter SDK v1 without making adapters evidence authorities. A passing JUnit result or coverage rate still does not prove a business obligation. |
| Protocol stability | Stabilize `qcov.dev/v1`, `qcov.agent/v1`, `qcov.impact/v1`, and `qcov.adapter/v1` as compatibility promises. |

The release gate requires evidence that ordinary test, coverage, and static
reports do not directly expose: critical or previously unknown, explainable
quality gaps; plus measured false-gap rate, gap-to-verification conversion, and
developer/QA acceptance.

## QCov 1.5 — Understand & Plan

**Question:** What should we verify next?

**Goal:** AI-assisted Quality Evidence Intelligence.

After 1.0 validation, add AI obligation discovery, AI-suggested change impact,
`qcov explain --ai`, an AI-suggested plan alongside the deterministic `qcov
plan`, and Quality Evidence ROI. AI proposals must remain separate from
authoritative obligations and deterministic impact. AI can understand, suggest,
explain, and plan; it cannot prove evidence or decide a gate.

## QCov 2.0 — Close the Loop

**Question:** How can agents continuously close quality gaps?

**Goal:** AI Native Quality Planning.

Evolve the Agent contract from `qcov.agent/v1` to a separately designed
`qcov.agent/v2` that accepts candidate evidence. The deterministic system must
validate, normalize, map, and evaluate that candidate. Agents cannot mark their
own work `COVERED`. This release track also designs QA-for-AI evidence
dimensions, a production quality feedback loop, and a Quality BOM.

## Future: Continuous Quality Control Plane

Only after 2.0: cross-project quality graphs, organization policy, historical
evidence, release intelligence, cross-repository impact, multi-agent
coordination, and compliance evidence. Web UI, persistence, remote Git,
automatic inventory-to-obligation inference, policy DSL, dimension thresholds,
wildcard/path waivers, and coverage/LCOV promotion remain out of scope until a
separate approved design.
