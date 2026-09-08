"""QCov command-line application."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
import yaml

from qcov.adapters.base import ScanDiagnostic
from qcov.adapters.pytest import PytestAdapter
from qcov.ai import (
    ChangeRiskContext,
    ObligationSuggestContext,
    analyze_change,
    propose_obligations,
    resolve_provider,
)
from qcov.engine.delta import compare_snapshots
from qcov.engine.delta_reports import render_delta_json, render_delta_markdown
from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.git_snapshots import DiffInputError, load_snapshot
from qcov.engine.inventory import collect_mappable_inventory, config_dir_for
from qcov.engine.mapping import (
    MappingConflictError,
    MappingDiagnostic,
    MappingDocumentError,
    MappingMaterialization,
    apply_mappings,
)
from qcov.engine.mapping_reports import render_map_preview_json, render_map_preview_markdown
from qcov.engine.planner import build_quality_plan
from qcov.engine.policy import PolicyDecision, evaluate_policy
from qcov.engine.policy_reports import render_policy_json, render_policy_markdown
from qcov.engine.reports import render_json, render_markdown, render_scan_json, render_scan_markdown
from qcov.engine.scan import scan_project
from qcov.models.config import ProjectConfig, ResolvedPaths, resolve_paths
from qcov.models.errors import ProposalInputError
from qcov.models.io import (
    ConfigLoadError,
    ProtocolLoadError,
    load_config,
    load_evidence,
    load_mapping,
    load_obligation,
    load_policy,
)
from qcov.models.protocol import (
    CoverageStatus,
    EvidenceMapping,
    QualityEvidence,
    QualityProposal,
    TestingObligation,
)

app = typer.Typer(no_args_is_help=True)
policy_app = typer.Typer(no_args_is_help=True)
map_app = typer.Typer(no_args_is_help=True)
obligation_app = typer.Typer(no_args_is_help=True)
risk_app = typer.Typer(no_args_is_help=True)
app.add_typer(policy_app, name="policy")
app.add_typer(map_app, name="map")
app.add_typer(obligation_app, name="obligation")
app.add_typer(risk_app, name="risk")

ObligationPath = Annotated[Path, typer.Option("--obligation", "--obligations", exists=True, readable=True)]
EvidencePath = Annotated[Path, typer.Option(exists=True, readable=True)]
Locale = Annotated[str, typer.Option("--locale", case_sensitive=False)]
OutputFormat = Annotated[str, typer.Option("--format", case_sensitive=False)]
OptionalObligationPath = Annotated[
    Path | None, typer.Option("--obligation", "--obligations", exists=True, readable=True)
]
OptionalEvidencePath = Annotated[Path | None, typer.Option(exists=True, readable=True)]


@dataclass(frozen=True)
class EvaluationBundle:
    results: tuple[ObligationResult, ...]
    mapping_diagnostics: tuple[MappingDiagnostic, ...] | None


def _evidence_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted([*path.glob("*.yaml"), *path.glob("*.yml"), *path.glob("*.json")])


def _evaluate(obligation_path: Path, evidence_path: Path) -> ObligationResult:
    obligation = load_obligation(obligation_path)
    evidence: list[QualityEvidence] = [load_evidence(path) for path in _evidence_files(evidence_path)]
    return evaluate_obligation(obligation, evidence)


def _require_mapping_files(config: ProjectConfig, resolved: ResolvedPaths) -> None:
    if config.mapping and not resolved.mapping:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: configured mapping patterns resolved to no files"
        )


def _scan_diagnostics_as_mapping(
    diagnostics: tuple[ScanDiagnostic, ...],
) -> tuple[MappingDiagnostic, ...]:
    return tuple(
        MappingDiagnostic(item.code, item.message, artifact_path=item.artifact_path)
        for item in diagnostics
    )


def _combine_mapping_diagnostics(
    materialization: MappingMaterialization,
    scan_diagnostics: tuple[ScanDiagnostic, ...],
) -> tuple[MappingDiagnostic, ...]:
    return tuple(
        sorted(
            (*materialization.diagnostics, *_scan_diagnostics_as_mapping(scan_diagnostics)),
            key=lambda item: (
                item.code,
                item.message,
                item.mapping_id or "",
                item.identity or "",
                item.artifact_path or "",
            ),
        )
    )


def _load_mappings(resolved: ResolvedPaths, config: ProjectConfig) -> list[EvidenceMapping]:
    _require_mapping_files(config, resolved)
    return [load_mapping(path) for path in resolved.mapping]


def _merge_evidence(
    config_path: Path,
    config: ProjectConfig,
    resolved: ResolvedPaths,
    authored: list[QualityEvidence],
    markers: list[QualityEvidence],
) -> tuple[list[QualityEvidence], tuple[MappingDiagnostic, ...] | None]:
    seen_ids = {item.metadata.id for item in authored}
    for item in markers:
        if item.metadata.id in seen_ids:
            raise MappingConflictError(
                f"{MappingConflictError.code}: evidence id conflict: {item.metadata.id}"
            )
        seen_ids.add(item.metadata.id)
    combined = [*authored, *markers]
    if not config.mapping:
        return combined, None
    mappings = _load_mappings(resolved, config)
    inventory = collect_mappable_inventory(resolved)
    materialization = apply_mappings(
        inventory.records,
        mappings,
        config_dir_for(config_path),
        authored_ids=seen_ids,
    )
    return (
        [*combined, *materialization.evidence],
        _combine_mapping_diagnostics(materialization, inventory.diagnostics),
    )


def _config_evaluation(
    config_path: Path, obligation: Path | None, evidence: Path | None
) -> EvaluationBundle:
    config = load_config(config_path)
    resolved = resolve_paths(config, config_path)
    selected_obligation = obligation
    if selected_obligation is None and len(resolved.obligations) == 1:
        selected_obligation = resolved.obligations[0]
    selected_evidence_paths = (
        _evidence_files(evidence) if evidence is not None else list(resolved.evidence)
    )
    if selected_obligation is None:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve exactly one obligation"
        )
    markers = PytestAdapter().collect(config_dir_for(config_path))
    if not selected_evidence_paths and not config.mapping and not markers:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve exactly one obligation and at least one evidence file"
        )
    _require_mapping_files(config, resolved)
    authored = [load_evidence(path) for path in selected_evidence_paths]
    merged, diagnostics = _merge_evidence(
        config_path, config, resolved, authored, markers
    )
    result = evaluate_obligation(load_obligation(selected_obligation), merged)
    return EvaluationBundle((result,), diagnostics)


def _result_from_inputs(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> EvaluationBundle:
    if config is None:
        if obligation is not None and evidence is not None:
            return EvaluationBundle((_evaluate(obligation, evidence),), None)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    return _config_evaluation(config, obligation, evidence)


def _render(
    result: ObligationResult,
    locale: str,
    output_format: str,
    mapping_diagnostics: tuple[MappingDiagnostic, ...] | None = None,
) -> str:
    if output_format == "json":
        return render_json([result], mapping_diagnostics=mapping_diagnostics)
    if output_format != "markdown":
        raise typer.BadParameter("format must be markdown or json")
    return render_markdown([result], locale=locale, mapping_diagnostics=mapping_diagnostics)


_InputError = (
    ConfigLoadError
    | ProtocolLoadError
    | MappingConflictError
    | MappingDocumentError
    | ProposalInputError
)


def _handle_input_error(error: _InputError) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code=4) from error


def _policy_bundle(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> EvaluationBundle:
    if config is None:
        if obligation is not None and evidence is not None:
            return EvaluationBundle((_evaluate(obligation, evidence),), None)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    if obligation is not None or evidence is not None:
        raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
    loaded = load_config(config)
    resolved = resolve_paths(loaded, config)
    if not resolved.obligations:
        raise ConfigLoadError(f"{ConfigLoadError.code}: config must resolve obligations")
    markers = PytestAdapter().collect(config_dir_for(config))
    if not resolved.evidence and not loaded.mapping and not markers:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve obligations and evidence files"
        )
    _require_mapping_files(loaded, resolved)
    authored = [load_evidence(path) for path in resolved.evidence]
    merged, diagnostics = _merge_evidence(config, loaded, resolved, authored, markers)
    results = tuple(evaluate_obligation(load_obligation(path), merged) for path in resolved.obligations)
    return EvaluationBundle(results, diagnostics)


def _map_preview(config_path: Path) -> MappingMaterialization:
    config = load_config(config_path)
    if not config.mapping:
        raise ConfigLoadError(f"{ConfigLoadError.code}: map preview requires mapping entries")
    resolved = resolve_paths(config, config_path)
    mappings = _load_mappings(resolved, config)
    inventory = collect_mappable_inventory(resolved)
    materialization = apply_mappings(inventory.records, mappings, config_dir_for(config_path))
    return MappingMaterialization(
        materialization.evidence,
        _combine_mapping_diagnostics(materialization, inventory.diagnostics),
        materialization.mapping_ids,
    )


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
        bundle = _result_from_inputs(obligation, evidence, config)
        typer.echo(_render(bundle.results[0], locale, output_format, bundle.mapping_diagnostics))
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError) as error:
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
        bundle = _result_from_inputs(obligation, evidence, config)
        result = bundle.results[0]
        typer.echo(_render(result, locale, output_format, bundle.mapping_diagnostics))
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError) as error:
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
        bundle = _result_from_inputs(obligation, evidence, config)
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError) as error:
        _handle_input_error(error)
        return
    output.write_text(_render(bundle.results[0], locale, output_format, bundle.mapping_diagnostics))
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
        bundle = _policy_bundle(obligation, evidence, config)
        report = evaluate_policy(bundle.results, load_policy(policy), evaluated_at)
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError, ValueError) as error:
        _handle_input_error(
            error
            if isinstance(
                error,
                (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError),
            )
            else ConfigLoadError(str(error))
        )
        return
    if output_format == "json":
        typer.echo(render_policy_json(report, mapping_diagnostics=bundle.mapping_diagnostics))
    elif output_format == "markdown":
        typer.echo(
            render_policy_markdown(report, locale, mapping_diagnostics=bundle.mapping_diagnostics)
        )
    else:
        raise typer.BadParameter("format must be markdown or json")
    if any(item.decision is PolicyDecision.BLOCK for item in report.results):
        raise typer.Exit(code=2)


@map_app.command("preview")
def map_preview(
    config: Annotated[Path, typer.Option(exists=True, readable=True)],
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Preview QualityEvidence that would be produced by configured mappings."""
    if output_format not in {"json", "markdown"}:
        _handle_input_error(ConfigLoadError("QCOV-CLI-004: format must be markdown or json"))
    if locale not in {"en", "zh-CN"}:
        _handle_input_error(ConfigLoadError("QCOV-CLI-005: locale must be en or zh-CN"))
    try:
        materialization = _map_preview(config)
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError) as error:
        _handle_input_error(error)
        return
    if output_format == "json":
        typer.echo(render_map_preview_json(materialization))
    else:
        typer.echo(render_map_preview_markdown(materialization, locale))


@app.command("plan")
def plan(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    output: Annotated[Path | None, typer.Option()] = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Rank next-best verification steps from gaps (proposal only)."""
    try:
        if config is not None and (obligation is not None or evidence is not None):
            raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
        if config is not None:
            bundle = _policy_bundle(None, None, config)
            loaded = load_config(config)
            resolved = resolve_paths(loaded, config)
            obligations = tuple(load_obligation(path) for path in resolved.obligations)
            refs = [str(config)]
        elif obligation is not None and evidence is not None:
            bundle = EvaluationBundle((_evaluate(obligation, evidence),), None)
            obligations = (load_obligation(obligation),)
            refs = [str(obligation), str(evidence)]
        else:
            raise ConfigLoadError(
                f"{ConfigLoadError.code}: provide --obligation/--evidence or --config"
            )
        proposal = build_quality_plan(bundle.results, obligations, refs=refs)
    except (
        ConfigLoadError,
        ProtocolLoadError,
        MappingConflictError,
        MappingDocumentError,
        ProposalInputError,
    ) as error:
        _handle_input_error(error)
        return
    if output is not None:
        _write_proposal_yaml(output, proposal)
    _ = locale
    typer.echo(_render_proposal(proposal, output_format))


def _render_proposal(proposal: QualityProposal, output_format: str) -> str:
    payload = proposal.model_dump(by_alias=True, mode="json")
    if output_format == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    if output_format == "markdown":
        lines = [
            f"# QualityProposal `{proposal.metadata.id}`",
            "",
            f"- type: `{proposal.proposal.type}`",
            f"- status: `{proposal.proposal.status}`",
            f"- provider: `{proposal.provider.name}`",
            "",
            "## Items",
        ]
        for item in proposal.items:
            lines.append(f"- `{item.id}` ({item.kind}) {item.summary.en}")
        return "\n".join(lines) + "\n"
    raise typer.BadParameter("format must be markdown or json")


def _write_proposal_yaml(path: Path, proposal: QualityProposal) -> None:
    payload = proposal.model_dump(by_alias=True, mode="json")
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))


def _load_config_obligations(
    config_path: Path,
) -> tuple[ProjectConfig, list[TestingObligation]]:
    config = load_config(config_path)
    resolved = resolve_paths(config, config_path)
    if not resolved.obligations:
        raise ConfigLoadError(f"{ConfigLoadError.code}: config must resolve obligations")
    return config, [load_obligation(path) for path in resolved.obligations]


def _resolve_obligations(
    config: Path | None, obligation: Path | None
) -> tuple[str, tuple[TestingObligation, ...]]:
    """Return provider default name and obligations from --config or --obligation."""
    if config is not None and obligation is not None:
        raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with --obligation")
    if config is not None:
        loaded, obligations = _load_config_obligations(config)
        return loaded.ai.provider, tuple(obligations)
    if obligation is not None:
        return "offline", (load_obligation(obligation),)
    raise ConfigLoadError(f"{ConfigLoadError.code}: provide --config or --obligation")


def _requirements_text(
    requirements: Path | None, *, allow_stdin: bool
) -> tuple[str, tuple[str, ...]]:
    if requirements is not None:
        return requirements.read_text(), (str(requirements),)
    if allow_stdin and not sys.stdin.isatty():
        text = sys.stdin.read()
        if text.strip():
            return text, ("stdin",)
    raise ProposalInputError("QCOV-PROPOSAL-002: requirements input is required")


def _local_diff_text(repo: Path, base: str, head: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), "diff", f"{base}...{head}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ProposalInputError(f"QCOV-PROPOSAL-002: unable to read local diff: {error}") from error
    return completed.stdout


@obligation_app.command("suggest")
def obligation_suggest(
    config: Annotated[Path | None, typer.Option(exists=True, readable=True)] = None,
    obligation: OptionalObligationPath = None,
    requirements: Annotated[Path | None, typer.Option(exists=True, readable=True)] = None,
    output: Annotated[Path | None, typer.Option()] = None,
    provider: Annotated[str | None, typer.Option()] = None,
    output_format: OutputFormat = "markdown",
) -> None:
    """Propose draft obligations/evidence from requirements (proposal only)."""
    try:
        default_provider, obligations = _resolve_obligations(config, obligation)
        text, refs = _requirements_text(requirements, allow_stdin=True)
        proposal = propose_obligations(
            ObligationSuggestContext(
                requirements_text=text,
                requirements_refs=refs,
                obligations=obligations,
            ),
            resolve_provider(provider or default_provider),
        )
    except (ConfigLoadError, ProtocolLoadError, ProposalInputError) as error:
        _handle_input_error(error)
        return
    if output is not None:
        _write_proposal_yaml(output, proposal)
    typer.echo(_render_proposal(proposal, output_format))


@risk_app.command("analyze")
def risk_analyze(
    config: Annotated[Path | None, typer.Option(exists=True, readable=True)] = None,
    obligation: OptionalObligationPath = None,
    base: Annotated[str, typer.Option()] = "HEAD~1",
    head: Annotated[str, typer.Option()] = "HEAD",
    output: Annotated[Path | None, typer.Option()] = None,
    provider: Annotated[str | None, typer.Option()] = None,
    output_format: OutputFormat = "markdown",
) -> None:
    """Propose change-risk draft from a local git diff (proposal only)."""
    try:
        default_provider, obligations = _resolve_obligations(config, obligation)
        repo = config_dir_for(config) if config is not None else Path.cwd()
        if obligation is not None:
            repo = obligation.resolve().parent
        diff_text = _local_diff_text(repo, base, head)
        proposal = analyze_change(
            ChangeRiskContext(
                diff_text=diff_text,
                base_ref=base,
                head_ref=head,
                obligations=obligations,
            ),
            resolve_provider(provider or default_provider),
        )
    except (ConfigLoadError, ProtocolLoadError, ProposalInputError) as error:
        _handle_input_error(error)
        return
    if output is not None:
        _write_proposal_yaml(output, proposal)
    typer.echo(_render_proposal(proposal, output_format))
