"""Regression checks for the Network Science aggregate-only manuscript tables."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT_ROOT / "scripts" / "71_build_network_science_tables.py"


def test_network_science_table_generator_writes_full_appendix_bundle(tmp_path: Path) -> None:
    """The table builder must retain primary and plan-bounded appendix exhibits."""
    output_dir = tmp_path / "network_science_tables"
    subprocess.run(
        [sys.executable, str(GENERATOR), "--output-dir", str(output_dir)],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    expected = {
        "MANIFEST.json",
        "table_01_senate_data.tex",
        "table_02_primary_performance.tex",
        "table_03_competitive_contrasts.tex",
        "table_04_sponsor_identification.tex",
        "table_05_cap_sensitivity.tex",
        "table_06_concept_fidelity.tex",
        "table_a1_actor_universe.tex",
        "table_a2_cap_audit.tex",
        "table_a3_mask_realisation.tex",
        "table_a4_ergm_ladder.tex",
        "table_a5_mtt_check.tex",
        "table_a6_static_diagnostic.tex",
        "table_a7_scope_checks.tex",
        "table_a8_scope_fidelity.tex",
        "table_a9_scope_panels.tex",
        "table_a10_scope_ladder.tex",
        "table_a11_scope_mtt.tex",
        "table_a12_bounded_temporal.tex",
    }
    assert {path.name for path in output_dir.iterdir()} == expected

    assert (
        "Full conditional-score ladder" in (output_dir / "table_a10_scope_ladder.tex").read_text()
    )
    assert "Cross-source empirical check" in (output_dir / "table_a11_scope_mtt.tex").read_text()
    assert (
        "Bounded chronological diagnostic"
        in (output_dir / "table_a12_bounded_temporal.tex").read_text()
    )

    manifest = json.loads((output_dir / "MANIFEST.json").read_text())
    assert manifest["privacy"].startswith("Generated tables contain aggregate")
    assert "table_a12_bounded_temporal.tex" in manifest["tables"]
