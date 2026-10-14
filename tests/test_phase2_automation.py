"""Low-cost regression checks for the repository-first Phase 2 layer."""

from __future__ import annotations

import importlib.util
import py_compile
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE2_SCRIPTS = (
    "14_profile_enron_event_timestamps.py",
    "15_materialize_enron_strict_mapping.py",
    "20_phase2_status.py",
    "21_prepare_eu_core.py",
    "22_prepare_covert_matrices.py",
    "23_prepare_jmail_v1.py",
    "24_prepare_mathoverflow.py",
    "25_build_enron_custodian_projection.py",
    "26_run_phase2.py",
    "27_phase2_readiness_report.py",
    "28_audit_formal_concepts.py",
    "29_audit_native_event_fidelity.py",
    "30_run_static_benchmark.py",
    "31_export_temporal_panel.py",
    "32_export_static_pilot_masks.py",
    "33_summarize_masked_ergm.py",
    "34_summarize_temporal_check.py",
    "35_summarize_temporal_btergm.py",
    "36_prepare_event_first_masks.py",
    "37_run_native_event_heuristics.py",
    "38_run_native_event_hard_panels.py",
    "39_export_native_event_ergm_inputs.py",
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


def test_readiness_report_recognizes_prepared_temporal_source() -> None:
    """EU-core preparation metadata should not be reported as an unknown audit state."""
    report_path = PROJECT_ROOT / "scripts" / "27_phase2_readiness_report.py"
    spec = importlib.util.spec_from_file_location("phase2_readiness_report", report_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (
        module.compact_status(
            {"core_static_directed_arcs": 2_682, "window_width_days": [14, 28, 30]}
        )
        == "prepared_static_and_temporal"
    )
