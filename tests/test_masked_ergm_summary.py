"""Tests for the local masked-ERGM result summarizer."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "33_summarize_masked_ergm.py"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    """Write a compact fixture CSV."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_masked_ergm_summary_aggregates_completed_metrics(tmp_path: Path) -> None:
    """The report distinguishes successful scores from visible model failures."""
    write_csv(
        tmp_path / "model_status.csv",
        ["replicate", "model", "status"],
        [
            {"replicate": "replicate_001", "model": "M0", "status": "scored"},
            {"replicate": "replicate_002", "model": "M0", "status": "scored"},
            {"replicate": "replicate_001", "model": "M4c", "status": "fit_failed"},
        ],
    )
    write_csv(
        tmp_path / "replicate_status.csv",
        ["replicate", "status"],
        [
            {"replicate": "replicate_001", "status": "completed_with_model_failures"},
            {"replicate": "replicate_002", "status": "completed"},
        ],
    )
    write_csv(
        tmp_path / "metrics.csv",
        ["replicate", "model", "metric", "value", "status"],
        [
            {
                "replicate": "replicate_001",
                "model": "M0",
                "metric": "roc_auc",
                "value": "0.70",
                "status": "calculated",
            },
            {
                "replicate": "replicate_002",
                "model": "M0",
                "metric": "roc_auc",
                "value": "0.80",
                "status": "calculated",
            },
            {
                "replicate": "replicate_001",
                "model": "M4c",
                "metric": "roc_auc",
                "value": "",
                "status": "not_scored_fit_failed",
            },
        ],
    )
    completed = subprocess.run(
        [sys.executable, str(DRIVER), "--input-dir", str(tmp_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "| M0 | roc_auc | 2 | 0.7500 | 0.0707 |" in summary
    assert "`M4c` / `roc_auc`: `not_scored_fit_failed`" in summary
