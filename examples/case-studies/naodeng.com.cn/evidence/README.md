# Evidence import boundary

`playwright.json` records the path-free runner-level block: the execution
sandbox denied the local preview listener before any browser identity ran.
`../mapping.yaml` is intentionally explicit but cannot materialize evidence
until a completed JSON report exists. A passed browser test would still require
that explicit mapping.
