"""QCov command-line application."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from qcov.engine.delta import compare_snapshots
from qcov.engine.delta_reports import render_delta_json, render_delta_markdown
from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.git_snapshots import DiffInputError, load_snapshot
from qcov.engine.policy import PolicyDecision, evaluate_policy
from qcov.engine.policy_reports import render_policy_json, render_policy_markdown
from qcov.engine.reports import render_json, render_markdown, render_scan_json, render_scan_markdown
from qcov.engine.scan import scan_project
from qcov.models.config import resolve_paths
from qcov.models.io import (
    ConfigLoadError,
    ProtocolLoadError,
    load_config,
    load_evidence,
    load_obligation,
    load_policy,
)
from qcov.models.protocol import CoverageStatus, QualityEvidence

app = typer.Typer(no_args_is_help=True)
policy_app = typer.Typer(no_args_is_help=True)
app.add_typer(policy_app, name="policy")

ObligationPath = Annotated[Path, typer.Option("--obligation", "--obligations", exists=True, readable=True)]
EvidencePath = Annotated[Path, typer.Option(exists=True, readable=True)]
Locale = Annotated[str, typer.Option("--locale", case_sensitive=False)]
OutputFormat = Annotated[str, typer.Option("--format", case_sensitive=False)]
OptionalObligationPath = Annotated[
    Path | None, typer.Option("--obligation", "--obligations", exists=True, readable=True)
]
OptionalEvidencePath = Annotated[Path | None, typer.Option(exists=True, readable=True)]


def _evidence_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted([*path.glob("*.yaml"), *path.glob("*.yml"), *path.glob("*.json")])


def _evaluate(obligation_path: Path, evidence_path: Path) -> ObligationResult:
    obligation = load_obligation(obligation_path)
    evidence: list[QualityEvidence] = [load_evidence(path) for path in _evidence_files(evidence_path)]
    return evaluate_obligation(obligation, evidence)


def _evaluate_files(obligation_path: Path, evidence_paths: list[Path]) -> ObligationResult:
    obligation = load_obligation(obligation_path)
    evidence = [load_evidence(path) for path in evidence_paths]
    return evaluate_obligation(obligation, evidence)


def _config_inputs(
    config_path: Path, obligation: Path | None, evidence: Path | None
) -> tuple[Path, list[Path]]:
    resolved = resolve_paths(load_config(config_path), config_path)
    selected_obligation = obligation
    selected_evidence = _evidence_files(evidence) if evidence is not None else list(resolved.evidence)
    if selected_obligation is None and len(resolved.obligations) == 1:
        selected_obligation = resolved.obligations[0]
    if selected_obligation is None or not selected_evidence:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve exactly one obligation and at least one evidence file"
        )
    return selected_obligation, selected_evidence


def _result_from_inputs(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> ObligationResult:
    if config is None:
        if obligation is not None and evidence is not None:
            return _evaluate(obligation, evidence)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    config_obligation, config_evidence = _config_inputs(config, obligation, evidence)
    return _evaluate_files(config_obligation, config_evidence)


def _render(result: ObligationResult, locale: str, output_format: str) -> str:
    if output_format == "json":
        return render_json([result])
    if output_format != "markdown":
        raise typer.BadParameter("format must be markdown or json")
    return render_markdown([result], locale=locale)


def _handle_input_error(error: ConfigLoadError | ProtocolLoadError) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code=4) from error


def _policy_results(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> tuple[ObligationResult, ...]:
    if config is None:
        if obligation is not None and evidence is not None:
            return (_evaluate(obligation, evidence),)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    if obligation is not None or evidence is not None:
        raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
    resolved = resolve_paths(load_config(config), config)
    if not resolved.obligations or not resolved.evidence:
        raise ConfigLoadError(f"{ConfigLoadError.code}: config must resolve obligations and evidence files")
    observed = [load_evidence(path) for path in resolved.evidence]
    return tuple(evaluate_obligation(load_obligation(path), observed) for path in resolved.obligations)


@app.command()
def gaps(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Show explainable gaps for one Testing Obligation."""
    try:
        typer.echo(_render(_result_from_inputs(obligation, evidence, config), locale, output_format))
    except (ConfigLoadError, ProtocolLoadError) as error:
        _handle_input_error(error)


@app.command()
def check(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Evaluate an obligation and return a gate-compatible status code."""
    try:
        result = _result_from_inputs(obligation, evidence, config)
        typer.echo(_render(result, locale, output_format))
    except (ConfigLoadError, ProtocolLoadError) as error:
        _handle_input_error(error)
        return
    if result.status is CoverageStatus.COVERED:
        return
    if result.status is CoverageStatus.UNKNOWN:
        raise typer.Exit(code=3)
    raise typer.Exit(code=2)


@app.command()
def inspect(
    obligation_id: str,
    obligation: ObligationPath,
    evidence: EvidencePath,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Inspect one obligation by its stable identifier."""
    result = _evaluate(obligation, evidence)
    if result.obligation_id != obligation_id:
        typer.echo(f"QCOV-CLI-001: obligation not found: {obligation_id}", err=True)
        raise typer.Exit(code=4)
    typer.echo(_render(result, locale, output_format))


@app.command()
def report(
    output: Annotated[Path, typer.Option()],
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Write a report file without overwriting protocol data."""
    try:
        result = _result_from_inputs(obligation, evidence, config)
    except (ConfigLoadError, ProtocolLoadError) as error:
        _handle_input_error(error)
        return
    output.write_text(_render(result, locale, output_format))
    typer.echo(str(output))


@app.command()
def init(path: Annotated[Path, typer.Option()] = Path(".")) -> None:
    """Create a non-destructive starter configuration."""
    path.mkdir(parents=True, exist_ok=True)
    config = path / "qcov.yaml"
    if config.exists():
        typer.echo(f"QCOV-CLI-002: configuration already exists: {config}", err=True)
        raise typer.Exit(code=4)
    config.write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nobligations: []\nevidence: []\n"
    )
    typer.echo(str(config))


@app.command()
def scan(
    path: Annotated[Path, typer.Option(exists=True, readable=True)] = Path("."),
    config: Annotated[Path | None, typer.Option(exists=True, readable=True)] = None,
    output_format: OutputFormat = "markdown",
) -> None:
    """Discover supported local evidence artifacts without executing tests."""
    config_path = config or path / "qcov.yaml"
    try:
        report = scan_project(path, config_path)
    except ConfigLoadError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4) from error
    if output_format == "json":
        typer.echo(render_scan_json(report))
    elif output_format == "markdown":
        typer.echo(render_scan_markdown(report))
    else:
        raise typer.BadParameter("format must be markdown or json")


@app.command()
def diff(
    base: Annotated[str, typer.Option()],
    head: Annotated[str, typer.Option()] = "HEAD",
    config: Annotated[str, typer.Option()] = "qcov.yaml",
    repo: Annotated[Path, typer.Option(exists=True, file_okay=False, readable=True)] = Path("."),
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Compare explicit quality coverage in two local committed Git trees."""
    try:
        report = compare_snapshots(load_snapshot(repo, base, config), load_snapshot(repo, head, config))
    except DiffInputError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4) from error
    if output_format == "json":
        typer.echo(render_delta_json(report))
    elif output_format == "markdown":
        typer.echo(render_delta_markdown(report, locale))
    else:
        raise typer.BadParameter("format must be markdown or json")


@policy_app.command("check")
def policy_check(
    policy: Annotated[Path, typer.Option(exists=True, readable=True)],
    as_of: Annotated[str, typer.Option("--as-of")],
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Evaluate a local quality policy without changing coverage facts."""
    if output_format not in {"json", "markdown"}:
        _handle_input_error(ConfigLoadError("QCOV-CLI-004: format must be markdown or json"))
    if locale not in {"en", "zh-CN"}:
        _handle_input_error(ConfigLoadError("QCOV-CLI-005: locale must be en or zh-CN"))
    try:
        evaluated_at = datetime.fromisoformat(as_of)
        if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
            raise ValueError("--as-of must be timezone-aware")
        report = evaluate_policy(_policy_results(obligation, evidence, config), load_policy(policy), evaluated_at)
    except (ConfigLoadError, ProtocolLoadError, ValueError) as error:
        _handle_input_error(error if isinstance(error, (ConfigLoadError, ProtocolLoadError)) else ConfigLoadError(str(error)))
        return
    if output_format == "json":
        typer.echo(render_policy_json(report))
    elif output_format == "markdown":
        typer.echo(render_policy_markdown(report, locale))
    else:
        raise typer.BadParameter("format must be markdown or json")
    if any(item.decision is PolicyDecision.BLOCK for item in report.results):
        raise typer.Exit(code=2)
