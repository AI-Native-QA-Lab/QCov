"""QCov command-line application."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.reports import render_json, render_markdown, render_scan_json, render_scan_markdown
from qcov.engine.scan import scan_project
from qcov.models.config import resolve_paths
from qcov.models.io import (
    ConfigLoadError,
    ProtocolLoadError,
    load_config,
    load_evidence,
    load_obligation,
)
from qcov.models.protocol import CoverageStatus, QualityEvidence

app = typer.Typer(no_args_is_help=True)

ObligationPath = Annotated[Path, typer.Option(exists=True, readable=True)]
EvidencePath = Annotated[Path, typer.Option(exists=True, readable=True)]
Locale = Annotated[str, typer.Option("--locale", case_sensitive=False)]
OutputFormat = Annotated[str, typer.Option("--format", case_sensitive=False)]
OptionalPath = Annotated[Path | None, typer.Option(exists=True, readable=True)]


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


def _config_inputs(config_path: Path) -> tuple[Path, list[Path]]:
    resolved = resolve_paths(load_config(config_path), config_path)
    if len(resolved.obligations) != 1 or not resolved.evidence:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve exactly one obligation and at least one evidence file"
        )
    return resolved.obligations[0], list(resolved.evidence)


def _result_from_inputs(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> ObligationResult:
    if obligation is not None and evidence is not None:
        return _evaluate(obligation, evidence)
    if config is None:
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    config_obligation, config_evidence = _config_inputs(config)
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


@app.command()
def gaps(
    obligation: OptionalPath = None,
    evidence: OptionalPath = None,
    config: OptionalPath = None,
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
    obligation: OptionalPath = None,
    evidence: OptionalPath = None,
    config: OptionalPath = None,
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
    obligation: OptionalPath = None,
    evidence: OptionalPath = None,
    config: OptionalPath = None,
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
    config.write_text("obligations: []\nevidence: []\n")
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
