"""QCov command-line application."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from qcov.adapters.pytest import PytestAdapter
from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.reports import render_json, render_markdown
from qcov.models.io import ProtocolLoadError, load_evidence, load_obligation
from qcov.models.protocol import CoverageStatus, QualityEvidence

app = typer.Typer(no_args_is_help=True)

ObligationPath = Annotated[Path, typer.Option(exists=True, readable=True)]
EvidencePath = Annotated[Path, typer.Option(exists=True, readable=True)]
Locale = Annotated[str, typer.Option("--locale", case_sensitive=False)]
OutputFormat = Annotated[str, typer.Option("--format", case_sensitive=False)]


def _evidence_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted([*path.glob("*.yaml"), *path.glob("*.yml"), *path.glob("*.json")])


def _evaluate(obligation_path: Path, evidence_path: Path) -> ObligationResult:
    obligation = load_obligation(obligation_path)
    evidence: list[QualityEvidence] = [load_evidence(path) for path in _evidence_files(evidence_path)]
    return evaluate_obligation(obligation, evidence)


def _render(result: ObligationResult, locale: str, output_format: str) -> str:
    if output_format == "json":
        return render_json([result])
    if output_format != "markdown":
        raise typer.BadParameter("format must be markdown or json")
    return render_markdown([result], locale=locale)


def _handle_protocol_error(error: ProtocolLoadError) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code=4) from error


@app.command()
def gaps(
    obligation: ObligationPath,
    evidence: EvidencePath,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Show explainable gaps for one Testing Obligation."""
    try:
        typer.echo(_render(_evaluate(obligation, evidence), locale, output_format))
    except ProtocolLoadError as error:
        _handle_protocol_error(error)


@app.command()
def check(
    obligation: ObligationPath,
    evidence: EvidencePath,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Evaluate an obligation and return a gate-compatible status code."""
    try:
        result = _evaluate(obligation, evidence)
        typer.echo(_render(result, locale, output_format))
    except ProtocolLoadError as error:
        _handle_protocol_error(error)
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
    obligation: ObligationPath,
    evidence: EvidencePath,
    output: Annotated[Path, typer.Option()],
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Write a report file without overwriting protocol data."""
    output.write_text(_render(_evaluate(obligation, evidence), locale, output_format))
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
def scan(path: Annotated[Path, typer.Option(exists=True, readable=True)] = Path(".")) -> None:
    """List MVP-local evidence producers detected in a project."""
    result = PytestAdapter().detect(path)
    typer.echo(f"{result.name}  {'detected' if result.detected else 'not detected'}")
