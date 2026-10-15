"""Regression checks for aggregate-only manuscript table generation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT_ROOT / "scripts" / "53_build_manuscript_tables.py"


def test_manuscript_table_generator_writes_primary_evidence_tables(tmp_path: Path) -> None:
    output_dir = tmp_path / "tables"
    subprocess.run(
        [sys.executable, str(GENERATOR), "--output-dir", str(output_dir)],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = {
        "table_01_dataset_target_eligibility.csv",
        "table_02_concept_event_fidelity.csv",
        "table_03a_primary_native_random_panel_pr_auc.csv",
        "table_03b_primary_native_hard_panel_pr_auc.csv",
        "table_03c_primary_native_role_assignment.csv",
        "table_04_paired_ergm_random_panel_pr_auc.csv",
        "table_05_bounded_temporal_diagnostic.csv",
        "table_06_pilot_gates_and_exclusions.csv",
        "MANIFEST.json",
    }
    assert expected.issubset({path.name for path in output_dir.iterdir()})

    paired = pd.read_csv(output_dir / "table_04_paired_ergm_random_panel_pr_auc.csv")
    assert len(paired) == 4
    assert set(paired["contrast"]) == {"M4c::L1g − M0::L1"}
    assert set(paired["paired_masks"]) == {30}
    assert paired.loc[
        (paired["dataset"] == "Enron strict custodian core") & (paired["mechanism"] == "MCAR"),
        "mean_difference",
    ].iloc[0] == pytest.approx(0.3583603199811184)

    fidelity = pd.read_csv(output_dir / "table_02_concept_event_fidelity.csv")
    assert set(fidelity["exact_tail_head_matches"]) == {0}

    manifest = json.loads((output_dir / "MANIFEST.json").read_text())
    assert manifest["privacy"].startswith("Aggregate-only")
    assert all("candidate" not in source["path"] for source in manifest["sources"])
