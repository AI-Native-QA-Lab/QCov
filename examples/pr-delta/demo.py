"""Run a self-contained local PR quality coverage delta demonstration."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[2]


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def commit(repo: Path) -> str:
    git(repo, "add", ".")
    git(
        repo,
        "-c",
        "user.name=QCov Demo",
        "-c",
        "user.email=demo@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-qm",
        "snapshot",
    )
    return git(repo, "rev-parse", "HEAD")


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        repo = Path(temporary)
        git(repo, "init", "-q")
        shutil.copytree(ROOT / "examples/refund", repo / "quality")
        (repo / "quality/qcov.yaml").write_text(
            "apiVersion: qcov.dev/v1alpha1\nkind: QCovConfig\n"
            "obligations: [obligation.yaml]\nevidence: [evidence/*.yaml]\n"
        )
        base = commit(repo)
        (repo / "quality/evidence/behavior.yaml").unlink()
        head = commit(repo)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "qcov",
                "diff",
                "--repo",
                str(repo),
                "--base",
                base,
                "--head",
                head,
                "--config",
                "quality/qcov.yaml",
            ],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    main()
