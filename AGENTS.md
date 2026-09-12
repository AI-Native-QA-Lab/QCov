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
become evidence/gate authority. Iteration 8 is delivered in v0.9.0 as an
offline production-observation foundation. Iteration 9 begins QCov 1.0:
real-project validation, deterministic Change → Obligation Impact, Adapter SDK
design, protocol stability, and documentation/onboarding readiness. QCov 1.5
and 2.0 require separately approved designs; see the roadmap.

For Iteration 9 validation, the target projects are read-only. Run their test
commands only from fixed-commit temporary copies or temporary output
directories, preserve any existing uncommitted changes, and keep all QCov case
configuration, mappings, artifacts, and reports under this repository's
`examples/case-studies/` or `docs/case-studies/` paths.

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
the RED and GREEN evidence in the commit or pull-request description.

## Documentation and Process

Protocol keys, CLI flags, enums, and error IDs are English.

**Project-facing docs (bilingual as today):** README, CONTRIBUTING, and public
product pages under paired `docs/en/` and `docs/zh-CN/` (matching stems and
heading structures).

**Development context (Chinese-only):** retain durable maintenance decisions in
`docs/zh-CN/development-context.md`. Detailed iteration plans and transient
process records are kept in Git history rather than the release worktree.

When closing a planned implementation task, record executed verification
commands and results in the commit or pull-request description, not as
expectations presented as results.
