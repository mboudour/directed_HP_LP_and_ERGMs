"""Tests for the bounded temporal-check result summary."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "34_summarize_temporal_check.py"


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    """Write a compact fixture CSV."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_temporal_summary_reports_bounded_lagged_contract(tmp_path: Path) -> None:
    """The summary must preserve the distinction from full temporal ERGM fitting."""
    model_dir = tmp_path / "model"
    panel_dir = tmp_path / "panel"
    model_dir.mkdir()
    panel_dir.mkdir()
    write_csv(
        model_dir / "feature_summary.csv",
        [
            "nodes",
            "transitions",
            "factorized_dyad_rows",
            "positive_outcomes",
            "outcome_rate",
        ],
        [
            {
                "nodes": "4",
                "transitions": "2",
                "factorized_dyad_rows": "24",
                "positive_outcomes": "6",
                "outcome_rate": "0.25",
            }
        ],
    )
    write_csv(
        model_dir / "factorized_model_status.csv",
        ["model", "status", "message"],
        [
            {"model": model, "status": "fit_succeeded", "message": ""}
            for model in ("T0", "T1", "T2")
        ],
    )
    write_csv(
        model_dir / "factorized_coefficients.csv",
        ["model", "term", "estimate"],
        [{"model": "T2", "term": "lag_cn_out", "estimate": "0.7"}],
    )
    write_csv(
        model_dir / "proposition6_identity.csv",
        ["proposition6_pass"],
        [{"proposition6_pass": "TRUE"}],
    )
    write_csv(
        model_dir / "package_placeholder_status.csv",
        ["engine", "requested_mode", "status"],
        [
            {"engine": "btergm", "requested_mode": "check", "status": "available_not_fit"},
            {
                "engine": "tergm",
                "requested_mode": "check",
                "status": "available_placeholder_not_fit",
            },
        ],
    )
    (panel_dir / "temporal_input_manifest.json").write_text(
        json.dumps({"dataset": "eu_core", "selected_panel_labels": ["0", "1", "2"]}),
        encoding="utf-8",
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
    assert "Selected panel labels: `0, 1, 2`" in summary
    assert "| T2 | lag_cn_out | 0.700000 | 2.013753 |" in summary
    assert "Status: `passed`" in summary
    assert "not a full TERGM" in summary
