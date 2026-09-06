"""Read protocol snapshots from immutable local Git objects."""

import json
import subprocess
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath
from typing import Any, TypeVar

import yaml
from pydantic import ValidationError

from qcov.models.config import ProjectConfig
from qcov.models.protocol import QualityEvidence, TestingObligation

ProtocolItem = TypeVar("ProtocolItem", TestingObligation, QualityEvidence)


class DiffInputError(ValueError):
    """Invalid or inaccessible delta input."""

    code = 'QCOV-DIFF-001'


@dataclass(frozen=True)
class Snapshot:
    commit: str
    obligations: dict[str, TestingObligation]
    evidence: dict[str, QualityEvidence]


def _error(message: str) -> DiffInputError:
    return DiffInputError(f"{DiffInputError.code}: {message}")


def _git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise _error("local Git object could not be read") from error


def _safe_path(path: str) -> PurePosixPath:
    candidate = PurePosixPath(path)
    if not path or candidate.is_absolute() or ".." in candidate.parts or path == ".":
        raise _error(f"unsafe repository path: {path!r}")
    return candidate


def _tree(repo: Path, commit: str) -> dict[PurePosixPath, tuple[str, str]]:
    output = _git(repo, "ls-tree", "-rz", commit)
    entries: dict[PurePosixPath, tuple[str, str]] = {}
    for item in output.split(b"\0"):
        if not item:
            continue
        header, raw_path = item.split(b"\t", 1)
        mode, _kind, oid = header.decode().split()
        entries[_safe_path(raw_path.decode())] = (mode, oid)
    return entries


def _blob(repo: Path, entry: tuple[str, str], path: PurePosixPath) -> str:
    mode, oid = entry
    if mode != "100644" and mode != "100755":
        raise _error(f"repository input must be a regular file: {path}")
    try:
        return _git(repo, "cat-file", "blob", oid).decode()
    except UnicodeDecodeError as error:
        raise _error(f"repository input must be UTF-8 text: {path}") from error


def _parse_config(text: str, path: PurePosixPath) -> ProjectConfig:
    try:
        raw: Any = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        return ProjectConfig.model_validate(raw)
    except (json.JSONDecodeError, yaml.YAMLError, ValidationError) as error:
        raise _error(f"invalid config: {path}") from error


def _matches(pattern: PurePosixPath, relative: PurePosixPath) -> bool:
    pattern_parts = pattern.parts
    path_parts = relative.parts

    def matches_at(pattern_index: int, path_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        part = pattern_parts[pattern_index]
        if part == "**":
            return any(matches_at(pattern_index + 1, index) for index in range(path_index, len(path_parts) + 1))
        return (
            path_index < len(path_parts)
            and fnmatchcase(path_parts[path_index], part)
            and matches_at(pattern_index + 1, path_index + 1)
        )

    return matches_at(0, 0)


def _select(
    entries: dict[PurePosixPath, tuple[str, str]], base: PurePosixPath, patterns: list[str]
) -> list[PurePosixPath]:
    paths: set[PurePosixPath] = set()
    for raw_pattern in patterns:
        pattern = _safe_path(raw_pattern)
        matches = [
            path for path in entries if path.is_relative_to(base) and _matches(pattern, path.relative_to(base))
        ]
        if not matches:
            raise _error(f"configuration pattern matched no committed files: {raw_pattern}")
        paths.update(matches)
    return sorted(paths)


def _load_models(
    repo: Path,
    entries: dict[PurePosixPath, tuple[str, str]],
    paths: list[PurePosixPath],
    model: type[ProtocolItem],
) -> dict[str, ProtocolItem]:
    loaded: dict[str, ProtocolItem] = {}
    for path in paths:
        try:
            raw: Any = json.loads(_blob(repo, entries[path], path)) if path.suffix == ".json" else yaml.safe_load(_blob(repo, entries[path], path))
            item = model.model_validate(raw)
        except (json.JSONDecodeError, yaml.YAMLError, ValidationError) as error:
            raise _error(f"invalid protocol input: {path}") from error
        identifier = item.metadata.id
        if identifier in loaded:
            raise _error(f"duplicate protocol identifier: {identifier}")
        loaded[identifier] = item
    return loaded


def load_snapshot(repo: Path, ref: str, config: str) -> Snapshot:
    config_path = _safe_path(config)
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    entries = _tree(repo, commit)
    if config_path not in entries:
        raise _error(f"configuration is absent from commit: {config_path}")
    configuration = _parse_config(_blob(repo, entries[config_path], config_path), config_path)
    base = config_path.parent
    obligations = _load_models(
        repo, entries, _select(entries, base, configuration.obligations), TestingObligation
    )
    evidence = _load_models(repo, entries, _select(entries, base, configuration.evidence), QualityEvidence)
    return Snapshot(commit, obligations, evidence)
