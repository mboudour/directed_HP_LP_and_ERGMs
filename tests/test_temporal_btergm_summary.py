"""Tests for the bounded temporal btergm summary."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "35_summarize_temporal_btergm.py"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    """Write a compact test artifact."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_btergm_summary_keeps_conditional_score_boundary(tmp_path: Path) -> None:
    """The report labels estimation output without making forecast claims."""
    model_dir = tmp_path / "model"
    panel_dir = tmp_path / "panel"
    model_dir.mkdir()
    panel_dir.mkdir()
    (model_dir / "run_manifest.json").write_text(
        json.dumps({"status": "completed"}), encoding="utf-8"
    )
    (panel_dir / "temporal_input_manifest.json").write_text(
        json.dumps({"dataset": "eu_core", "selected_panel_labels": ["0", "1", "2"]}),
        encoding="utf-8",
    )
    write_csv(
        model_dir / "input_summary.csv",
        ["nodes", "transitions", "response_dyad_time_rows"],
        [{"nodes": "100", "transitions": "2", "response_dyad_time_rows": "19800"}],
    )
    write_csv(
        model_dir / "model_status.csv",
        ["model", "status", "message"],
        [{"model": "T2", "status": "fit_succeeded", "message": ""}],
    )
    write_csv(
        model_dir / "coefficients.csv",
        ["model", "term", "estimate", "ci_lower", "ci_upper", "ci_status"],
        [
            {
                "model": "T2",
                "term": "edges",
                "estimate": "-2.1",
                "ci_lower": "-2.4",
                "ci_upper": "-1.8",
                "ci_status": "extracted",
            }
        ],
    )
    completed = subprocess.run(
        [sys.executable, str(DRIVER), "--model-dir", str(model_dir), "--panel-dir", str(panel_dir)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    summary = (model_dir / "summary.md").read_text(encoding="utf-8")
    assert "btergm MPLE with temporal bootstrap" in summary
    assert "T1, T2, and T2_minus_H are MPLE conditional score estimators only" in summary
    assert "| T2 | edges | -2.1000 | [-2.4000, -1.8000] | extracted |" in summary
