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
from qcov.engine.agent_next import select_next_actions
from qcov.engine.delta import compare_snapshots
from qcov.engine.delta_reports import render_delta_json, render_delta_markdown
from qcov.engine.explain import explain_evidence, explain_gap, explain_plan_item
from qcov.engine.gaps import ObligationResult, evaluate_obligation
from qcov.engine.git_snapshots import DiffInputError, changed_files_between, load_snapshot
from qcov.engine.impact import ImpactInputError, affected_report, direct_impact, snapshot_impact
from qcov.engine.impact_reports import (
    render_affected_json,
    render_affected_markdown,
    render_impact_json,
    render_impact_markdown,
)
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
from qcov.models.agent_contract import (
    CONTRACT_VERSION,
    AgentEnvelope,
    ExplainPayload,
    NextPayload,
    ValidateFileResult,
    ValidatePayload,
)
from qcov.models.config import ProjectConfig, ResolvedPaths, resolve_paths
from qcov.models.errors import AgentInputError, ProposalInputError
from qcov.models.io import (
    ConfigLoadError,
    ProtocolLoadError,
    load_config,
    load_evidence,
    load_impact_config,
    load_mapping,
    load_obligation,
    load_policy,
    load_proposal,
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
agent_app = typer.Typer(no_args_is_help=True)
app.add_typer(policy_app, name="policy")
app.add_typer(map_app, name="map")
app.add_typer(obligation_app, name="obligation")
app.add_typer(risk_app, name="risk")
app.add_typer(agent_app, name="agent")

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
    selected_obligations = [obligation] if obligation is not None else list(resolved.obligations)
    selected_evidence_paths = (
        _evidence_files(evidence) if evidence is not None else list(resolved.evidence)
    )
    if not selected_obligations:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve at least one obligation"
        )
    markers = PytestAdapter().collect(config_dir_for(config_path))
    if not selected_evidence_paths and not config.mapping and not markers:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve obligations and at least one evidence file"
        )
    _require_mapping_files(config, resolved)
    authored = [load_evidence(path) for path in selected_evidence_paths]
    merged, diagnostics = _merge_evidence(
        config_path, config, resolved, authored, markers
    )
    results = tuple(
        evaluate_obligation(load_obligation(obligation_path), merged)
        for obligation_path in selected_obligations
    )
    return EvaluationBundle(results, diagnostics)


def _result_from_inputs(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> EvaluationBundle:
    if config is None:
        if obligation is not None and evidence is not None:
            return EvaluationBundle((_evaluate(obligation, evidence),), None)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    return _config_evaluation(config, obligation, evidence)


def _render(
    results: tuple[ObligationResult, ...],
    locale: str,
    output_format: str,
    mapping_diagnostics: tuple[MappingDiagnostic, ...] | None = None,
) -> str:
    if output_format == "json":
        return render_json(results, mapping_diagnostics=mapping_diagnostics)
    if output_format != "markdown":
        raise typer.BadParameter("format must be markdown or json")
    return render_markdown(results, locale=locale, mapping_diagnostics=mapping_diagnostics)


_INPUT_ERRORS = (
    ConfigLoadError,
    ProtocolLoadError,
    MappingConflictError,
    MappingDocumentError,
    ProposalInputError,
    AgentInputError,
    ImpactInputError,
    DiffInputError,
)
_InputError = (
    ConfigLoadError
    | ProtocolLoadError
    | MappingConflictError
    | MappingDocumentError
    | ProposalInputError
    | AgentInputError
    | ImpactInputError
    | DiffInputError
)


def _handle_input_error(error: _InputError) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code=4) from error


def _multi_obligation_evaluation(
    config_path: Path,
) -> tuple[EvaluationBundle, tuple[TestingObligation, ...]]:
    loaded = load_config(config_path)
    resolved = resolve_paths(loaded, config_path)
    if not resolved.obligations:
        raise ConfigLoadError(f"{ConfigLoadError.code}: config must resolve obligations")
    markers = PytestAdapter().collect(config_dir_for(config_path))
    if not resolved.evidence and not loaded.mapping and not markers:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: config must resolve obligations and evidence files"
        )
    _require_mapping_files(loaded, resolved)
    authored = [load_evidence(path) for path in resolved.evidence]
    merged, diagnostics = _merge_evidence(config_path, loaded, resolved, authored, markers)
    obligations = tuple(load_obligation(path) for path in resolved.obligations)
    results = tuple(evaluate_obligation(item, merged) for item in obligations)
    return EvaluationBundle(results, diagnostics), obligations


def _policy_bundle(
    obligation: Path | None, evidence: Path | None, config: Path | None
) -> EvaluationBundle:
    if config is None:
        if obligation is not None and evidence is not None:
            return EvaluationBundle((_evaluate(obligation, evidence),), None)
        raise ConfigLoadError(f"{ConfigLoadError.code}: provide --obligation/--evidence or --config")
    if obligation is not None or evidence is not None:
        raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
    bundle, _obligations = _multi_obligation_evaluation(config)
    return bundle


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
        typer.echo(_render(bundle.results, locale, output_format, bundle.mapping_diagnostics))
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
        typer.echo(_render((result,), locale, output_format, bundle.mapping_diagnostics))
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
    typer.echo(_render((result,), locale, output_format))


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
    output.write_text(_render(bundle.results, locale, output_format, bundle.mapping_diagnostics))
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
        changed_files = changed_files_between(repo, base, head)
    except DiffInputError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=4) from error
    if output_format == "json":
        typer.echo(render_delta_json(report, changed_files))
    elif output_format == "markdown":
        typer.echo(render_delta_markdown(report, locale))
    else:
        raise typer.BadParameter("format must be markdown or json")


@app.command()
def impact(
    config: Annotated[Path, typer.Option(exists=True, readable=True)],
    impact_config: Annotated[Path, typer.Option("--impact-config", exists=True, readable=True)],
    changed_file: Annotated[list[str] | None, typer.Option("--changed-file")] = None,
    base: Annotated[str | None, typer.Option()] = None,
    head: Annotated[str | None, typer.Option()] = None,
    repo: Annotated[Path | None, typer.Option()] = None,
    output_format: OutputFormat = "markdown",
) -> None:
    """Map explicit local changed files to Testing Obligations."""
    changed_files = tuple(changed_file or ())
    if changed_files and (base is not None or head is not None):
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: --changed-file cannot be combined with --base/--head"))
        return
    if (base is None) != (head is None):
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: provide both --base and --head"))
        return
    try:
        if base is not None and head is not None:
            target_repo = repo or config.parent
            try:
                config_ref = str(config.resolve().relative_to(target_repo.resolve()))
            except ValueError as error:
                raise ImpactInputError("QCOV-IMPACT-001: --config must be inside --repo") from error
            report = snapshot_impact(load_impact_config(impact_config), changed_files_between(target_repo, base, head), load_snapshot(target_repo, base, config_ref), load_snapshot(target_repo, head, config_ref))
        else:
            project = load_config(config)
            resolved = resolve_paths(project, config)
            known_obligations = {load_obligation(path).metadata.id for path in resolved.obligations}
            report = direct_impact(load_impact_config(impact_config), changed_files, known_obligation_ids=known_obligations)
    except DiffInputError as error:
        _handle_input_error(ImpactInputError(f"QCOV-IMPACT-001: {error}"))
        return
    except (ConfigLoadError, ProtocolLoadError, ImpactInputError) as error:
        _handle_input_error(error)
        return
    if output_format == "json":
        typer.echo(render_impact_json(report))
    elif output_format == "markdown":
        typer.echo(render_impact_markdown(report))
    else:
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: format must be markdown or json"))


@app.command()
def affected(
    config: Annotated[Path, typer.Option(exists=True, readable=True)],
    impact_config: Annotated[Path, typer.Option("--impact-config", exists=True, readable=True)],
    changed_file: Annotated[list[str] | None, typer.Option("--changed-file")] = None,
    base: Annotated[str | None, typer.Option()] = None,
    head: Annotated[str | None, typer.Option()] = None,
    repo: Annotated[Path | None, typer.Option()] = None,
    output_format: OutputFormat = "markdown",
) -> None:
    """Show current non-covered gaps for explicitly affected obligations."""
    changed_files = tuple(changed_file or ())
    if changed_files and (base is not None or head is not None):
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: --changed-file cannot be combined with --base/--head"))
        return
    if (base is None) != (head is None):
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: provide both --base and --head"))
        return
    try:
        mappings = load_impact_config(impact_config)
        if base is not None and head is not None:
            target_repo = repo or config.parent
            try:
                config_ref = str(config.resolve().relative_to(target_repo.resolve()))
            except ValueError as error:
                raise ImpactInputError("QCOV-IMPACT-001: --config must be inside --repo") from error
            snapshot = load_snapshot(target_repo, head, config_ref)
            impact = direct_impact(
                mappings,
                changed_files_between(target_repo, base, head),
                known_obligation_ids=set(snapshot.obligations),
            )
            results = tuple(
                evaluate_obligation(item, tuple(snapshot.evidence.values()))
                for item in snapshot.obligations.values()
            )
        else:
            bundle, _obligations = _multi_obligation_evaluation(config)
            impact = direct_impact(
                mappings,
                changed_files,
                known_obligation_ids={item.obligation_id for item in bundle.results},
            )
            results = bundle.results
        report = affected_report(impact, results)
    except DiffInputError as error:
        _handle_input_error(ImpactInputError(f"QCOV-IMPACT-001: {error}"))
        return
    except (ConfigLoadError, ProtocolLoadError, MappingConflictError, MappingDocumentError, ImpactInputError) as error:
        _handle_input_error(error)
        return
    if output_format == "json":
        typer.echo(render_affected_json(report))
    elif output_format == "markdown":
        typer.echo(render_affected_markdown(report))
    else:
        _handle_input_error(ImpactInputError("QCOV-IMPACT-001: format must be markdown or json"))


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


_VALIDATE_DISCLAIMER = {
    "en": (
        "validForLoad=true means the file loaded as QualityEvidence only; "
        "it does not mean COVERED and is not a policy PASS."
    ),
    "zh-CN": (
        "validForLoad=true 仅表示文件可作为 QualityEvidence 加载；"
        "不表示 COVERED，也不是 policy PASS。"
    ),
}


@app.command("explain")
def explain(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    plan_path: Annotated[Path | None, typer.Option("--plan", exists=True, readable=True)] = None,
    item_id: Annotated[str | None, typer.Option("--item-id")] = None,
    obligation_id: Annotated[str | None, typer.Option("--obligation-id")] = None,
    dimension: Annotated[str | None, typer.Option("--dimension")] = None,
    mode: Annotated[str | None, typer.Option("--mode", case_sensitive=False)] = None,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Explain a gap, plan item, or why evidence does not COVER a dimension."""
    try:
        payload = _build_explain_payload(
            obligation=obligation,
            evidence=evidence,
            config=config,
            plan_path=plan_path,
            item_id=item_id,
            obligation_id=obligation_id,
            dimension=dimension,
            mode=mode,
        )
        envelope = AgentEnvelope.model_validate(
            {
                "contractVersion": CONTRACT_VERSION,
                "command": "explain",
                "payload": payload,
            }
        )
    except _INPUT_ERRORS as error:
        _handle_input_error(error)
        return
    typer.echo(_render_agent_envelope(envelope, output_format, locale=locale))


@agent_app.command("next")
def agent_next(
    obligation: OptionalObligationPath = None,
    evidence: OptionalEvidencePath = None,
    config: OptionalEvidencePath = None,
    plan_path: Annotated[Path | None, typer.Option("--plan", exists=True, readable=True)] = None,
    limit: Annotated[int, typer.Option("--limit")] = 1,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Return the next-best planned verification steps for agents."""
    try:
        if limit < 1:
            raise AgentInputError(
                AgentInputError.CODE_INVALID_LIMIT,
                "--limit must be >= 1",
            )
        payload = _build_next_payload(
            obligation=obligation,
            evidence=evidence,
            config=config,
            plan_path=plan_path,
            limit=limit,
        )
        envelope = AgentEnvelope.model_validate(
            {
                "contractVersion": CONTRACT_VERSION,
                "command": "agent.next",
                "payload": payload,
            }
        )
    except _INPUT_ERRORS as error:
        _handle_input_error(error)
        return
    typer.echo(_render_agent_envelope(envelope, output_format, locale=locale))


@agent_app.command("validate-evidence")
def agent_validate_evidence(
    evidence: EvidencePath,
    locale: Locale = "en",
    output_format: OutputFormat = "markdown",
) -> None:
    """Check whether evidence files are valid for protocol load (not gate/COVERED)."""
    try:
        payload = _validate_evidence_payload(evidence)
        envelope = AgentEnvelope.model_validate(
            {
                "contractVersion": CONTRACT_VERSION,
                "command": "agent.validate_evidence",
                "payload": payload,
            }
        )
    except _INPUT_ERRORS as error:
        _handle_input_error(error)
        return
    typer.echo(_render_agent_envelope(envelope, output_format, locale=locale))


def _build_explain_payload(
    *,
    obligation: Path | None,
    evidence: Path | None,
    config: Path | None,
    plan_path: Path | None,
    item_id: str | None,
    obligation_id: str | None,
    dimension: str | None,
    mode: str | None,
) -> ExplainPayload:
    if plan_path is not None:
        if config is not None or obligation is not None or evidence is not None:
            raise ConfigLoadError(
                "QCOV-CLI-006: --plan cannot be combined with --config or direct inputs"
            )
        if item_id is None:
            raise ConfigLoadError(f"{ConfigLoadError.code}: --plan requires --item-id")
        proposal = load_proposal(plan_path)
        for item in proposal.items:
            if item.id == item_id:
                return explain_plan_item(item)
        raise AgentInputError(
            AgentInputError.CODE_TARGET_NOT_FOUND,
            f"plan item not found: {item_id}",
        )

    if obligation_id is None or dimension is None:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: provide --obligation-id and --dimension "
            "(or --plan with --item-id)"
        )

    explain_mode = (mode or "gap").lower()
    if explain_mode not in {"gap", "evidence"}:
        raise ConfigLoadError(f"{ConfigLoadError.code}: --mode must be gap or evidence")

    if config is not None:
        if obligation is not None or evidence is not None:
            raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
        if explain_mode != "gap":
            raise ConfigLoadError(f"{ConfigLoadError.code}: --config explain supports --mode gap only")
        bundle, obligations = _multi_obligation_evaluation(config)
        matched = next((item for item in obligations if item.metadata.id == obligation_id), None)
        result = next((item for item in bundle.results if item.obligation_id == obligation_id), None)
        if matched is None or result is None:
            raise AgentInputError(
                AgentInputError.CODE_TARGET_NOT_FOUND,
                f"obligation not found: {obligation_id}",
            )
        return explain_gap(matched, result, dimension)

    if obligation is not None and evidence is not None:
        loaded_obligation = load_obligation(obligation)
        if loaded_obligation.metadata.id != obligation_id:
            raise AgentInputError(
                AgentInputError.CODE_TARGET_NOT_FOUND,
                f"obligation not found: {obligation_id}",
            )
        evidence_items = [load_evidence(path) for path in _evidence_files(evidence)]
        if explain_mode == "evidence":
            return explain_evidence(loaded_obligation, evidence_items, dimension)
        result = evaluate_obligation(loaded_obligation, evidence_items)
        return explain_gap(loaded_obligation, result, dimension)

    raise ConfigLoadError(
        f"{ConfigLoadError.code}: provide --config, --obligation/--evidence, or --plan"
    )


def _quality_plan_from_inputs(
    *,
    obligation: Path | None,
    evidence: Path | None,
    config: Path | None,
) -> QualityProposal:
    if config is not None and (obligation is not None or evidence is not None):
        raise ConfigLoadError("QCOV-CLI-003: --config cannot be combined with direct inputs")
    if config is not None:
        bundle, obligations = _multi_obligation_evaluation(config)
        refs = [str(config)]
    elif obligation is not None and evidence is not None:
        loaded_obligation = load_obligation(obligation)
        evidence_items = [load_evidence(path) for path in _evidence_files(evidence)]
        bundle = EvaluationBundle(
            (evaluate_obligation(loaded_obligation, evidence_items),),
            None,
        )
        obligations = (loaded_obligation,)
        refs = [str(obligation), str(evidence)]
    else:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: provide --obligation/--evidence or --config"
        )
    return build_quality_plan(bundle.results, obligations, refs=refs)


def _build_next_payload(
    *,
    obligation: Path | None,
    evidence: Path | None,
    config: Path | None,
    plan_path: Path | None,
    limit: int,
) -> NextPayload:
    if plan_path is not None:
        if config is not None or obligation is not None or evidence is not None:
            raise ConfigLoadError(
                "QCOV-CLI-006: --plan cannot be combined with --config or direct inputs"
            )
        return select_next_actions(load_proposal(plan_path), limit=limit, source="plan_file")
    if obligation is None and evidence is None and config is None:
        raise ConfigLoadError(
            f"{ConfigLoadError.code}: provide --plan, --config, or --obligation/--evidence"
        )
    return select_next_actions(
        _quality_plan_from_inputs(obligation=obligation, evidence=evidence, config=config),
        limit=limit,
        source="evaluation",
    )


def _validate_evidence_payload(evidence: Path) -> ValidatePayload:
    files: list[ValidateFileResult] = []
    for path in _evidence_files(evidence):
        try:
            loaded = load_evidence(path)
            files.append(
                ValidateFileResult.model_validate(
                    {
                        "path": str(path),
                        "validForLoad": True,
                        "evidenceId": loaded.metadata.id,
                        "error": None,
                    }
                )
            )
        except ProtocolLoadError as error:
            files.append(
                ValidateFileResult.model_validate(
                    {
                        "path": str(path),
                        "validForLoad": False,
                        "evidenceId": None,
                        "error": str(error),
                    }
                )
            )
    return ValidatePayload.model_validate(
        {
            "files": [item.model_dump(by_alias=True, mode="json") for item in files],
            "allValidForLoad": all(item.valid_for_load for item in files),
            "disclaimer": _VALIDATE_DISCLAIMER,
        }
    )


def _render_agent_envelope(
    envelope: AgentEnvelope, output_format: str, *, locale: str = "en"
) -> str:
    if output_format == "json":
        return json.dumps(envelope.model_dump(by_alias=True, mode="json"), indent=2, ensure_ascii=False)
    if output_format != "markdown":
        raise typer.BadParameter("format must be markdown or json")
    lines = [
        f"# Agent `{envelope.command}`",
        "",
        f"- contractVersion: `{envelope.contract_version}`",
        "",
    ]
    payload = envelope.payload
    if isinstance(payload, ExplainPayload):
        lines.extend(
            [
                f"- mode: `{payload.mode}`",
                f"- obligationId: `{payload.obligation_id or '—'}`",
                f"- dimension: `{payload.dimension or '—'}`",
                f"- status: `{payload.status or '—'}`",
                "",
                "## Reasons",
            ]
        )
        for reason in payload.reasons:
            summary = reason.summary.zh_cn if locale == "zh-CN" else reason.summary.en
            lines.append(f"- `{reason.code}`: {summary}")
        if not payload.reasons:
            lines.append("- —")
    elif isinstance(payload, NextPayload):
        lines.extend(
            [
                f"- source: `{payload.source}`",
                f"- limit: `{payload.limit}`",
                "",
                "## Items",
            ]
        )
        for next_item in payload.items:
            lines.append(
                f"- `{next_item.id}` rank={next_item.rank} "
                f"{next_item.obligation_ref}/{next_item.dimension} "
                f"suggested={next_item.suggested_evidence_type or '—'}"
            )
        if not payload.items:
            lines.append("- —")
    elif isinstance(payload, ValidatePayload):
        disclaimer = payload.disclaimer.zh_cn if locale == "zh-CN" else payload.disclaimer.en
        lines.extend(
            [
                f"- allValidForLoad: `{payload.all_valid_for_load}`",
                f"- disclaimer: {disclaimer}",
                "",
                "## Files",
            ]
        )
        for file_item in payload.files:
            lines.append(
                f"- `{file_item.path}` validForLoad=`{file_item.valid_for_load}` "
                f"id=`{file_item.evidence_id or '—'}`"
            )
            if file_item.error:
                lines.append(f"  - error: {file_item.error}")
    else:
        raise typer.BadParameter(f"unsupported agent payload: {type(payload)!r}")
    return "\n".join(lines) + "\n"


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
        proposal = _quality_plan_from_inputs(
            obligation=obligation, evidence=evidence, config=config
        )
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
    typer.echo(_render_proposal(proposal, output_format, locale=locale))


def _render_proposal(
    proposal: QualityProposal, output_format: str, *, locale: str = "en"
) -> str:
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
            summary = item.summary.zh_cn if locale == "zh-CN" else item.summary.en
            lines.append(f"- `{item.id}` ({item.kind}) {summary}")
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
