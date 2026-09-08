# QCov Contributor Rules

## Scope

QCov is a local, deterministic Quality Evidence Gap Engine. Iterations 0–4.5
deliver gap evaluation, inventory scan adapters (with retained records), local
`qcov diff`, local `qcov policy check`, and declarative junit/playwright evidence
mapping.

Do not add AI providers, a web UI, persistence, remote Git operations, external
plugins, automatic inventory-to-evidence inference, coverage/LCOV promotion to
passed evidence, or policy DSL / wildcard waivers without an approved design and
plan update.

Prefer real-project validation of mapping before AI proposal work. Do not
describe QCov as a line-coverage detector.

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

Protocol keys, CLI flags, enums, and error IDs are English. Public prose is
maintained in paired `docs/en/` and `docs/zh-CN/` pages with matching stems and
heading structures. Update the relevant process record in `docs/process/` when
closing a planned implementation task; record executed verification commands
and results, not expectations presented as results.
