"""Regression checks for the aggregate-only Paper 2 temporal RHEM materials."""

from __future__ import annotations

import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = PROJECT_ROOT / "results" / "published" / "paper2_temporal_20261030"
PAPER = PROJECT_ROOT / "manuscript" / "paper2"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a small tracked aggregate artifact."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_paper2_published_rhem_bundle_has_all_required_sensitivities() -> None:
    """The working draft must distinguish seed, tie-order, and record-policy checks."""
    rows = read_csv(PUBLISHED / "rhem_group_contrasts_pooled.csv")
    variants = {row["variant"] for row in rows}
    assert variants == {
        "primary_ascending_seed_20261030",
        "sampling_seed_20261031",
        "descending_order_seed_20261030",
        "collapsed_timestamp_footprints_seed_20261030",
    }
    multi = {row["variant"]: row for row in rows if row["scope"] == "head_size_ge_2"}
    assert float(multi["primary_ascending_seed_20261030"]["delta_mean_log_score"]) > 0
    assert float(multi["collapsed_timestamp_footprints_seed_20261030"]["delta_mean_log_score"]) < 0


def test_paper2_published_rhem_bundle_excludes_row_level_identifiers() -> None:
    """Published Paper 2 output must preserve the repository aggregate-only policy."""
    prohibited = {"source", "target", "sender", "recipient", "actor", "event_id", "event_interval"}
    for path in sorted(PUBLISHED.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        normalized = {column.lower() for column in header}
        assert prohibited.isdisjoint(normalized), path
    manifest = json.loads((PUBLISHED / "manifest.json").read_text(encoding="utf-8"))
    serialized = json.dumps(manifest).lower()
    assert "actor_ids_private" not in serialized
    assert "event_index_private.csv" not in serialized


def test_paper2_working_manuscript_materials_exist_and_label_the_boundary() -> None:
    """Tables and source must expose the representation sensitivity, not hide it."""
    source = (PAPER / "Paper2_TemporalRHEM.tex").read_text(encoding="utf-8")
    assert "Working manuscript" in source
    assert "batch-history" in source
    assert "not yet a stable scientific conclusion" in source
    assert (PAPER / "figures" / "figure_01_group_contrast_sensitivity.pdf").is_file()
    sensitivity = (PAPER / "tables" / "table_03_rhem_sensitivity.tex").read_text(encoding="utf-8")
    assert "Collapse identical time--role footprints" in sensitivity


def test_eventnet_exporter_pins_its_case_control_sampling_seed() -> None:
    """The RHEM input contract must use Eventnet's explicit XML seed setting."""
    exporter = (PROJECT_ROOT / "scripts" / "78_prepare_enron_rhem_inputs.py").read_text(
        encoding="utf-8"
    )
    assert "eventnet-random-seed" in exporter
    assert 'random.seed="{eventnet_random_seed}"' in exporter
