import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath

import pytest

from qcov.engine import git_snapshots

ROOT = Path(__file__).parents[2]


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def commit(repo: Path) -> str:
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'snapshot')
    return git(repo, 'rev-parse', 'HEAD')


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    git(tmp_path, 'init', '-q')
    shutil.copytree(ROOT / 'examples/refund', tmp_path / 'quality')
    (tmp_path / 'quality/qcov.yaml').write_text(json.dumps({
        'apiVersion': 'qcov.dev/v1alpha1', 'kind': 'QCovConfig',
        'obligations': ['obligation.yaml'], 'evidence': ['evidence/*.yaml'],
    }))
    commit(tmp_path)
    return tmp_path


def test_reads_committed_inputs_ignoring_dirty_worktree(repo: Path) -> None:
    oid = git(repo, 'rev-parse', 'HEAD')
    (repo / 'quality/obligation.yaml').write_text('broken')
    snapshot = git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml')
    assert snapshot.commit == oid
    assert list(snapshot.obligations) == ['QO-REFUND-001']
    assert len(snapshot.evidence) == 3


def test_each_revision_uses_its_own_config(repo: Path) -> None:
    base = git(repo, 'rev-parse', 'HEAD')
    (repo / 'quality/qcov.yaml').write_text(
        'apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nobligations: []\nevidence: []\n')
    head = commit(repo)
    assert git_snapshots.load_snapshot(repo, base, 'quality/qcov.yaml').obligations
    assert not git_snapshots.load_snapshot(repo, head, 'quality/qcov.yaml').obligations


@pytest.mark.parametrize('ref', ['missing-ref', '--help', 'HEAD:quality/qcov.yaml'])
def test_invalid_commit_is_stable_error(repo: Path, ref: str) -> None:
    with pytest.raises(git_snapshots.DiffInputError, match='QCOV-DIFF-001'):
        git_snapshots.load_snapshot(repo, ref, 'quality/qcov.yaml')


@pytest.mark.parametrize('path', ['/tmp/config.yaml', '../config.yaml', 'missing.yaml', ''])
def test_invalid_config_path(repo: Path, path: str) -> None:
    with pytest.raises(git_snapshots.DiffInputError, match='QCOV-DIFF-001'):
        git_snapshots.load_snapshot(repo, 'HEAD', path)


@pytest.mark.parametrize('pattern', ['../obligation.yaml', '/tmp/o.yaml', 'missing*.yaml', 'evidence'])
def test_invalid_patterns(repo: Path, pattern: str) -> None:
    config = repo / 'quality/qcov.yaml'
    raw = json.loads(config.read_text())
    raw['obligations'] = [pattern]
    config.write_text(json.dumps(raw))
    commit(repo)
    with pytest.raises(git_snapshots.DiffInputError, match='QCOV-DIFF-001'):
        git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml')


@pytest.mark.parametrize('kind', ['obligations', 'evidence'])
def test_duplicate_ids_are_rejected(repo: Path, kind: str) -> None:
    config = repo / 'quality/qcov.yaml'
    raw = json.loads(config.read_text())
    original = 'obligation.yaml' if kind == 'obligations' else 'evidence/behavior.yaml'
    shutil.copy(repo / 'quality' / original, repo / 'quality/copy.yaml')
    raw[kind].append('copy.yaml')
    config.write_text(json.dumps(raw))
    commit(repo)
    with pytest.raises(git_snapshots.DiffInputError, match='duplicate'):
        git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml')


@pytest.mark.parametrize('path', ['qcov.yaml', 'obligation.yaml', 'evidence/behavior.yaml'])
def test_malformed_inputs_are_rejected(repo: Path, path: str) -> None:
    (repo / 'quality' / path).write_text('invalid: [')
    commit(repo)
    with pytest.raises(git_snapshots.DiffInputError, match='QCOV-DIFF-001'):
        git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml')


def test_symlink_is_rejected(repo: Path) -> None:
    path = repo / 'quality/obligation.yaml'
    path.unlink()
    path.symlink_to('evidence/behavior.yaml')
    commit(repo)
    with pytest.raises(git_snapshots.DiffInputError, match='regular'):
        git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml')


def test_recursive_glob_and_overlapping_patterns(repo: Path) -> None:
    config = repo / 'quality/qcov.yaml'
    raw = json.loads(config.read_text())
    raw['evidence'] = ['evidence/**/*.yaml', 'evidence/behavior.yaml']
    config.write_text(json.dumps(raw))
    commit(repo)
    assert len(git_snapshots.load_snapshot(repo, 'HEAD', 'quality/qcov.yaml').evidence) == 3


def test_non_recursive_glob_does_not_match_nested_paths() -> None:
    assert not git_snapshots._matches(PurePosixPath('*.yaml'), PurePosixPath('nested/evidence.yaml'))
    assert git_snapshots._matches(PurePosixPath('**/*.yaml'), PurePosixPath('nested/evidence.yaml'))
