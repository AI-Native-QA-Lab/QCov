# QCov Contributor Rules

## Scope

QCov is a local, deterministic Quality Evidence Gap Engine. Iterations 0–4.5
deliver gap evaluation, inventory scan adapters (with retained records), local
`qcov diff`, local `qcov policy check`, and declarative junit/playwright evidence
mapping. Iteration 5 adds pytest-marker evaluation merge, limited identity suffix
wildcards, and proposal-only AI (`obligation suggest` / `risk analyze`) with a
default offline provider. Iteration 6 adds the deterministic Quality Planner
(`qcov plan` → draft `quality_plan` proposal). Iteration 7 adds Agentic Quality
Loop helpers (`qcov explain`, `qcov agent next`, optional
`qcov agent validate-evidence`) under `qcov.agent/v1`; they never run tests or
become evidence/gate authority. Planned Iteration 8 is an offline production-
observation foundation. Iteration 9 begins QCov 1.0: real-project validation,
deterministic Change → Obligation Impact, Adapter SDK design, and protocol
stability. QCov 1.5 and 2.0 require separately approved designs; see the
roadmap.

Do not add remote LLM providers beyond the approved Iteration 5 provider
abstraction, a web UI, persistence, remote Git host APIs, external plugins,
automatic inventory-to-obligation inference, coverage/LCOV promotion to passed
evidence, or policy DSL / path-based waivers without an approved design and plan
update. AI must never become evidence or gate authority.


Prefer real-project validation of mapping before expanding AI proposal work. Do
not describe QCov as a line-coverage detector.

## Commands

Run the relevant checks before reporting completion:

```bash
pytest
ruff check .
mypy qcov
python -m build
git diff --check
```

Use the environment's available `python3` command when `python` is absent.

## Test-Driven Development

For every behavior change, write one focused automated test first and run it to
observe the expected RED failure. Only then write the smallest implementation
needed for GREEN; re-run the scoped test and relevant regression suite. Record
the RED and GREEN evidence in the corresponding `docs/process/` entry.

## Documentation and Process

Protocol keys, CLI flags, enums, and error IDs are English.

**Project-facing docs (bilingual as today):** README, CONTRIBUTING, and public
product pages under paired `docs/en/` and `docs/zh-CN/` (matching stems and
heading structures).

**Development process docs (Chinese-only going forward):** design specs and
implementation plans under `docs/superpowers/`, process records under
`docs/process/`, and similar engineering working notes (including ADRs written
after this rule). Do not maintain paired English copies of these process docs.

Update the relevant `docs/process/` entry when closing a planned implementation
task; record executed verification commands and results, not expectations
presented as results.
