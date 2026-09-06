import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_pr_delta_demo_runs_without_changing_the_workspace() -> None:
    result = subprocess.run(
        [sys.executable, "examples/pr-delta/demo.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "PR Quality Coverage Delta" in result.stdout
    assert "MODIFIED" in result.stdout
