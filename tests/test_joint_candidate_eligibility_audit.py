"""Tests for aggregate joint-footprint candidate eligibility auditing."""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "42_audit_joint_candidate_eligibility.py"


def load_driver(path: Path):
    """Load a standalone driver for a temporary local-data fixture."""
    spec = importlib.util.spec_from_file_location("joint_candidate_eligibility", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    """Write a small CSV fixture."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def test_joint_eligibility_audit_counts_strict_and_relaxed_two_dyad_candidates(
    tmp_path: Path, monkeypatch
) -> None:
    """Exact-two candidates must be counted separately from reciprocal-qualified candidates."""
    module = load_driver(DRIVER)
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    input_dir = tmp_path / "inputs"
    split_dir = input_dir / "splits" / "mcar_replicate_001"
    write_csv(
        split_dir / "train_edges.csv",
        ["from", "to"],
        [["a", "b"], ["b", "a"], ["d", "a"], ["e", "a"]],
    )
    headers = [
        "panel",
        "candidate_id",
        "label",
        "footprint_size",
        "candidate_tail",
        "candidate_head",
    ]
    write_csv(
        split_dir / "candidate_footprints.csv",
        headers,
        [
            ["random", "one_unknown", "1", "2", "a", "b"],
            ["random", "one_unknown", "1", "2", "a", "c"],
            ["role_exchange", "strict_two", "0", "2", "a", "d"],
            ["role_exchange", "strict_two", "0", "2", "a", "e"],
            ["role_exchange", "relaxed_two", "0", "2", "a", "f"],
            ["role_exchange", "relaxed_two", "0", "2", "a", "g"],
        ],
    )
    output_dir = tmp_path / "output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(DRIVER),
            "--dataset-id=test_dataset",
            f"--input-dir={input_dir}",
            f"--output-dir={output_dir}",
            "--overwrite",
        ],
    )

    module.main()

    with (output_dir / "split_selection_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [
        {
            "split": "mcar_replicate_001",
            "mechanism": "mcar",
            "replicate": "1",
            "candidates_total": "3",
            "candidates_exactly_two_unknown_dyads": "2",
            "candidates_exactly_two_unknown_dyads_all_reverse_observed": "1",
        }
    ]
    report = (output_dir / "summary.md").read_text(encoding="utf-8")
    assert "Candidates with exactly two unknown footprint dyads: `2`" in report
    assert "reverse arc observed: `1`" in report
