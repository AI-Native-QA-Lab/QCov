# Production evidence

`ProductionObservationReport` is a local JSON/YAML inventory format for runtime, incident, and observability observations. QCov never connects to a production service or executes code while reading it.

Every observation has an id, category, status, timezone-aware timestamp, and optional string attributes. Configure files with `scan.production`. An observation remains inventory until an explicit `EvidenceMapping` names its `production-observation` identity. Its observation timestamp becomes the mapped evidence execution timestamp; a mapping timestamp cannot replace it.

```bash
.venv/bin/python -m qcov scan --config examples/production-observations/qcov.yaml
.venv/bin/python -m qcov map preview --config examples/production-observations/qcov.yaml --format json
```

A passed observation is not `COVERED` without that mapping; QCov does not infer an obligation or dimension from an observation.
