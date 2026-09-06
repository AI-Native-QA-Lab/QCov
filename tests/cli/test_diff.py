import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from qcov.cli.app import app

ROOT = Path(__file__).parents[2]
runner = CliRunner()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def _commit(repo: Path) -> str:
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "test")
    return _git(repo, "rev-parse", "HEAD")


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    _git(tmp_path, "init", "-q")
    shutil.copytree(ROOT / "examples/refund", tmp_path / "quality")
    (tmp_path / "quality/qcov.yaml").write_text(
        "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\nobligations: [obligation.yaml]\nevidence: [evidence/*.yaml]\n"
    )
    base = _commit(tmp_path)
    (tmp_path / "quality/evidence/behavior.yaml").unlink()
    head = _commit(tmp_path)
    return tmp_path, base, head


def test_diff_emits_deterministic_json_and_localized_markdown(tmp_path: Path) -> None:
    repo, base, head = _repo(tmp_path)
    json_result = runner.invoke(app, ["diff", "--repo", str(repo), "--base", base, "--head", head, "--config", "quality/qcov.yaml", "--format", "json"])
    chinese_result = runner.invoke(app, ["diff", "--repo", str(repo), "--base", base, "--head", head, "--config", "quality/qcov.yaml", "--locale", "zh-CN"])
    assert json_result.exit_code == 0
    assert '"baseCommit"' in json_result.stdout
    assert '"change": "MODIFIED"' in json_result.stdout
    assert chinese_result.exit_code == 0
    assert "质量覆盖增量" in chinese_result.stdout
    assert "行为" in chinese_result.stdout
    assert "所需证据" in chinese_result.stdout


def test_diff_rejects_invalid_ref_with_exit_four(tmp_path: Path) -> None:
    repo, _, head = _repo(tmp_path)
    result = runner.invoke(app, ["diff", "--repo", str(repo), "--base", "missing", "--head", head, "--config", "quality/qcov.yaml"])
    assert result.exit_code == 4
    assert "QCOV-DIFF-001" in result.stderr
