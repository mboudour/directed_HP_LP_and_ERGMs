"""Low-cost regression checks for the repository-first Phase 2 layer."""

from __future__ import annotations

import py_compile
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE2_SCRIPTS = (
    "20_phase2_status.py",
    "21_prepare_eu_core.py",
    "22_prepare_covert_matrices.py",
    "23_prepare_jmail_v1.py",
    "24_prepare_mathoverflow.py",
    "25_build_enron_custodian_projection.py",
    "26_run_phase2.py",
)


def test_dataset_registry_has_all_planned_sources() -> None:
    """Keep the executable registry aligned with the agreed paper dataset scope."""
    registry = yaml.safe_load(
        (PROJECT_ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8")
    )
    assert set(registry["datasets"]) == {
        "enron_20150507",
        "email_eu_core_temporal",
        "caviar",
        "ciel",
        "jmail_v1_2026_02",
        "mathoverflow_stackexchange_2024",
    }


def test_phase2_scripts_compile() -> None:
    """Catch syntax regressions before local source data are needed."""
    for script in PHASE2_SCRIPTS:
        py_compile.compile(PROJECT_ROOT / "scripts" / script, doraise=True)
