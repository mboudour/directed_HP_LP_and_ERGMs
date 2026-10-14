"""Integration tests for the bounded native-event/formal-concept fidelity audit."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "29_audit_native_event_fidelity.py"


def write_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a recorded-event fixture with matching, merged, and excluded cases."""
    events = tmp_path / "events.parquet"
    arcs = tmp_path / "arcs.parquet"
    nodes = tmp_path / "nodes.csv"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"sender": "a", "recipients": ["c", "d"]},
                {"sender": "a", "recipients": ["c", "d"]},
                {"sender": "b", "recipients": ["c", "d"]},
                {"sender": "a", "recipients": ["a"]},
                {"sender": "outside", "recipients": ["c"]},
                {"sender": "a", "recipients": ["b", "c", "d"]},
            ]
        ),
        events,
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"tail": "a", "head": "c"},
                {"tail": "a", "head": "d"},
                {"tail": "b", "head": "c"},
                {"tail": "b", "head": "d"},
            ]
        ),
        arcs,
    )
    with nodes.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"node": node} for node in ("a", "b", "c", "d"))
    return events, arcs, nodes


def command(events: Path, arcs: Path, nodes: Path, output: Path, *extra: str) -> list[str]:
    """Build the fully explicit audit command for a temporary prepared fixture."""
    return [
        sys.executable,
        str(DRIVER),
        "--dataset-id",
        "fixture",
        "--events",
        str(events),
        "--arcs",
        str(arcs),
        "--nodes",
        str(nodes),
        "--event-tail-column",
        "sender",
        "--event-head-column",
        "recipients",
        "--arc-tail-column",
        "tail",
        "--arc-head-column",
        "head",
        "--node-column",
        "node",
        "--tail-cap",
        "2",
        "--head-cap",
        "2",
        "--output-dir",
        str(output),
        *extra,
    ]


def test_native_event_fidelity_audit_writes_bounded_representation_evidence(tmp_path: Path) -> None:
    """The audit separates event records/types from derived capped concepts."""
    events, arcs, nodes = write_fixture(tmp_path)
    output = tmp_path / "fidelity"
    completed = subprocess.run(
        command(events, arcs, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Native-event/formal-concept fidelity audit passed." in completed.stdout
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["native_events"]["event_records_read"] == 6
    assert summary["native_events"]["fixed_universe_event_records"] == 4
    assert summary["native_events"]["cap_eligible_event_records"] == 3
    assert summary["native_events"]["cap_eligible_event_types"] == 2
    assert summary["formal_concepts"]["count"] == 1
    assert summary["exact_tail_head_equality"]["matching_pairs"] == 0
    assert summary["footprint_agreement"]["jaccard"] == 1.0
    assert (
        summary["cover_structure"][
            "formal_concepts_with_two_or_more_contributing_native_event_types"
        ]
        == 1
    )
    assert (output / "event_to_concept_matches.csv").is_file()
    assert (output / "concept_to_event_aggregation.csv").is_file()

    with (output / "event_to_concept_matches.csv").open(encoding="utf-8", newline="") as handle:
        event_rows = list(csv.DictReader(handle))
    assert [int(row["occurrence_count"]) for row in event_rows] == [2, 1]
    assert all(float(row["best_role_similarity"]) == 0.75 for row in event_rows)


def test_native_event_fidelity_audit_requires_explicit_overwrite_and_is_rerunnable(
    tmp_path: Path,
) -> None:
    """A complete result bundle cannot be mixed with a later run by accident."""
    events, arcs, nodes = write_fixture(tmp_path)
    output = tmp_path / "fidelity"
    first = subprocess.run(
        command(events, arcs, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(events, arcs, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "fidelity-audit output directory is nonempty" in blocked.stderr
    rerun = subprocess.run(
        command(events, arcs, nodes, output, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
