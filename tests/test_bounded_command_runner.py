from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "scripts" / "40_run_bounded_command.py"


def test_bounded_runner_completes_and_writes_log(tmp_path: Path) -> None:
    log_path = tmp_path / "completed.txt"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--timeout-seconds=5",
            f"--log={log_path}",
            "--",
            sys.executable,
            "-c",
            "print('bounded runner pass')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Completed with exit code 0" in result.stdout
    log_text = log_path.read_text(encoding="utf-8")
    assert "bounded runner pass" in log_text
    assert "Status: completed" in log_text


def test_bounded_runner_times_out_and_writes_log(tmp_path: Path) -> None:
    log_path = tmp_path / "timed_out.txt"
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--timeout-seconds=0.1",
            f"--log={log_path}",
            "--",
            sys.executable,
            "-c",
            "import time; print('started', flush=True); time.sleep(5)",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 124
    assert "Timed out after 0.1 seconds" in result.stdout
    log_text = log_path.read_text(encoding="utf-8")
    assert "started" in log_text
    assert "Status: timed_out_after_0.1_seconds" in log_text
