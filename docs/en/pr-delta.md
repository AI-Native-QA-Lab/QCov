# PR Quality Coverage Delta

Use `qcov diff` to compare explicit Testing Obligations and Quality Evidence in
two commits that already exist in the local Git repository.

```bash
qcov diff --repo . --base origin/main --head HEAD --config qcov.yaml
qcov diff --repo . --base origin/main --head HEAD --config qcov.yaml --format json
```

The report lists each stable obligation ID as `ADDED`, `REMOVED`, `MODIFIED`, or
`UNCHANGED`, with before/after coverage and changed referenced evidence IDs. It
reads Git objects only: it does not fetch, check out commits, run tests, or read
dirty/untracked files. Pass the merge base explicitly when needed.

Missing refs/configuration, invalid data, unsafe paths, symlinks, duplicate IDs,
and unmatched paths produce `QCOV-DIFF-001` and exit code 4. A valid empty
configuration is an empty snapshot. The command has no policy gate.
