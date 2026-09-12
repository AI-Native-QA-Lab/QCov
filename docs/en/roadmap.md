# Roadmap

QCov is a local, deterministic Quality Evidence Gap Engine. It reports what
remains unproven for an explicit requirement, risk, or change; it is not a
line-coverage detector or test runner.

## Delivered through Iteration 8

Iterations 0–4 establish Obligation → Evidence → Gap evaluation, local
inventory discovery, committed-tree `qcov diff`, and deterministic local
`qcov policy check`. Iteration 4.5 adds declarative `EvidenceMapping` and map
preview. Iterations 5–7 add proposal-only assistance, deterministic planning,
and `qcov.agent/v1` helpers; none runs tests, writes authoritative evidence, or
decides gates. Iteration 8 adds a local `production-observation` inventory
producer: runtime, incident, and observability observations become evidence only
through explicit mappings. See the [agent playbook](agent.md) and
[production-evidence guide](production-evidence.md).

## QCov 1.0 — Find the Gap

**Question:** What is still unproven?

**Goal:** Prove QCov creates measurable value in real projects, without an AI
dependency for core correctness.

Iteration 9 is the 1.0 delivery track:

| Workstream | Outcome |
| --- | --- |
| Real-project validation | Validate `ai-native-qa-agents` (Python/pytest/coverage), `ai4se-demo-project` (Java/JUnit/JaCoCo), and `naodeng.com.cn` (TypeScript/Playwright); use `ai-test-auditor` as an extra TypeScript/Node ecosystem case. Target at least 3 projects, 30 real obligations, and time to first value of 10 minutes or less. |
| Change → obligation impact | Deterministic repository-relative path glob mappings produce affected obligations and, when two local snapshots are supplied, the resulting gap delta through `qcov impact`, `qcov affected`, and `qcov diff`. Higher-level package/module/service/API mappings must be pre-expanded to paths. |
| Adapter extensibility | Define the in-process `qcov.adapter/v1` contract and add a JaCoCo XML inventory reader without making adapters evidence authorities. Passing JUnit or coverage rates still do not prove a business obligation; external plugin loading remains deferred. |
| Protocol stability | Preserve released `qcov.dev/v1alpha1` and stabilize `qcov.agent/v1`, `qcov.impact/v1`, and `qcov.adapter/v1` as compatibility promises; no implicit core-protocol rename. |
| Documentation and onboarding | Clean paired READMEs; provide tested installation paths, a first runnable example, command/configuration guidance, and troubleshooting so a new Python, Java, or TypeScript user can reach first value without source inspection. |

The 1.0 release gate requires three real projects, three technology stacks, at
least 30 real Testing Obligations, and measured time to first value of 10 minutes
or less. It must also show critical or previously unknown, explainable gaps that
ordinary test, coverage, and static reports do not directly expose; record
false-gap rate, gap-to-verification conversion, and developer/QA acceptance.

The documentation gate requires paired README navigation, verified install and
quick-start commands, links to configuration and examples, clear local-only and
evidence-authority boundaries, and a troubleshooting path. Documentation is a
1.0 product deliverable, not post-release cleanup.

## QCov 1.5 — Understand & Plan

**Question:** What should we verify next?

**Goal:** AI-assisted Quality Evidence Intelligence.

After 1.0 validation, these are candidate 1.5 themes that each require a
separate approved design: AI obligation discovery, AI-suggested change impact,
`qcov explain --ai`, an AI-suggested plan alongside deterministic `qcov plan`,
and Quality Evidence ROI. Any AI suggestion must remain separate from
authoritative obligations and deterministic impact. AI may understand, suggest,
explain, and plan; it cannot prove evidence or decide a gate.

## QCov 2.0 — Close the Loop

**Question:** How can agents continuously close quality gaps?

**Goal:** AI Native Quality Planning.

These are candidate 2.0 themes that require a separate approved design:
evolving the Agent contract from `qcov.agent/v1` to `qcov.agent/v2` for
candidate evidence, QA-for-AI evidence dimensions, a production quality
feedback loop, and a Quality BOM. If accepted, the deterministic system must
validate, normalize, map, and evaluate candidates; agents cannot mark their own
work `COVERED`.

## Future: Continuous Quality Control Plane

Only after 2.0: cross-project quality graphs, organization policy, historical
evidence, release intelligence, cross-repository impact, multi-agent
coordination, and compliance evidence. Web UI, persistence, remote Git,
automatic inventory-to-obligation inference, policy DSL, dimension thresholds,
wildcard/path waivers, and coverage/LCOV promotion remain out of scope until a
separate approved design.
