# QCov Contributor Rules

## Scope

QCov's MVP is a local, deterministic Quality Evidence Gap Engine. Do not add
AI, a web UI, persistence, Git delta analysis, external plugins, or policy
enforcement without an approved design and plan update.

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

## Documentation and Process

Protocol keys, CLI flags, enums, and error IDs are English. Public prose is
maintained in paired `docs/en/` and `docs/zh-CN/` pages with matching stems and
heading structures. Update the relevant process record in `docs/process/` when
closing a planned implementation task; record executed verification commands
and results, not expectations presented as results.
