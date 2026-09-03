# Documentation Delivery Record

## Scope

Task 8 publishes English-first README navigation, Chinese counterparts,
requirements, architecture, protocol, technical design, development guide,
roadmap, process documentation, Mermaid sources, and ADR 0002.

## Test-first and verification record

The first documentation test failed because `README.md` was absent. On
2026-09-03 (Asia/Shanghai), these checks passed:

```text
.venv/bin/python -m pytest tests/docs/test_documentation_links.py -q  # 2 passed
.venv/bin/ruff check tests/docs                                        # passed
.venv/bin/mypy tests/docs                                              # passed
rg TODO/TBD across public docs                                         # no matches
.venv/bin/python -m build                                              # sdist and wheel built
```

The first isolated `build` attempt was blocked by sandbox DNS resolution for
PyPI. A permitted retry installed `hatchling==1.32.0` and produced
`qcov-0.1.0a0.tar.gz` and `qcov-0.1.0a0-py3-none-any.whl`.
