"""Regression checks for survival-stratified matched-mask diagnostics."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "61_summarize_survival_and_reversal_diagnostics.py"


def load_module():
    """Import the standalone diagnostic script as a testable module."""
    specification = importlib.util.spec_from_file_location("survival_diagnostics", SCRIPT)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_bootstrap_interval_is_deterministic_and_brackets_mean() -> None:
    module = load_module()
    values = [-0.1, 0.0, 0.2, 0.4]
    first = module.bootstrap_interval(values, "synthetic-key")
    second = module.bootstrap_interval(values, "synthetic-key")
    assert first == second
    assert first[0] <= sum(values) / len(values) <= first[1]


def test_contrast_rows_include_whole_mask_percentile_interval() -> None:
    module = load_module()
    split_metrics = []
    for replicate, (m4c, reference) in enumerate(((0.8, 0.6), (0.7, 0.5)), start=1):
        for score, value in (("M4c::L1g", m4c), ("directed_aa_total", reference)):
            split_metrics.append(
                {
                    "mechanism": "mcar",
                    "replicate": replicate,
                    "survival_stratum": "B=0 at least one arc absent",
                    "score": score,
                    "metric": "pr_auc",
                    "value": value,
                }
            )
    rows = module.contrast_rows(split_metrics, "synthetic")
    aa_row = next(row for row in rows if row["contrast"].endswith("directed_aa_total"))
    assert aa_row["completed_masks"] == 2
    assert aa_row["mean_pr_auc_difference"] == 0.2
    assert aa_row["bootstrap_reps"] == 10_000
    assert aa_row["bootstrap_ci_lower"] <= 0.2 <= aa_row["bootstrap_ci_upper"]
