"""Regression checks for static-arc and formal-concept manuscript tables."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT_ROOT / "scripts" / "58_build_plan_aligned_tables.py"


def test_plan_aligned_table_generator_uses_aggregate_inputs(tmp_path: Path) -> None:
    output_dir = tmp_path / "tables"
    subprocess.run(
        [sys.executable, str(GENERATOR), "--output-dir", str(output_dir)],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = {
        "static_arc_score_pilot.csv",
        "formal_concept_scope.csv",
        "formal_concept_recovery.csv",
        "plan_aligned_tables_manifest.json",
    }
    assert expected == {path.name for path in output_dir.iterdir()}

    static = pd.read_csv(output_dir / "static_arc_score_pilot.csv")
    assert len(static) == 24
    assert set(static["completed_masks"]) == {3}
    assert static.loc[
        (static["dataset"] == "Enron strict core") & (static["method"] == "M3"),
        "pr_auc_mean",
    ].iloc[0] == pytest.approx(0.9242258773330064)

    scope = pd.read_csv(output_dir / "formal_concept_scope.csv")
    assert set(scope["formal_concepts"]) == {45, 80, 207, 232}

    manifest = json.loads((output_dir / "plan_aligned_tables_manifest.json").read_text())
    assert manifest["privacy"].startswith("Aggregate-only")
    assert all("candidate" not in source["path"] for source in manifest["sources"])
