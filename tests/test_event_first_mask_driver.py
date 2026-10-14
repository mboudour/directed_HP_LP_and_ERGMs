"""Integration tests for primary event-first native-event-type masking."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "36_prepare_event_first_masks.py"


def write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Write core events with a duplicated type and an arity-excluded record."""
    events = tmp_path / "events.parquet"
    nodes = tmp_path / "nodes.csv"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"sender": "a", "recipients": ["b"]},
                {"sender": "a", "recipients": ["b"]},
                {"sender": "a", "recipients": ["c"]},
                {"sender": "b", "recipients": ["c"]},
                {"sender": "b", "recipients": ["d"]},
                {"sender": "c", "recipients": ["d"]},
                {"sender": "d", "recipients": ["a"]},
                {"sender": "d", "recipients": ["b", "c", "e"]},
                {"sender": "outside", "recipients": ["a"]},
                {"sender": "a", "recipients": ["a"]},
            ]
        ),
        events,
    )
    with nodes.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"node": node} for node in ("a", "b", "c", "d", "e"))
    return events, nodes


def command(events: Path, nodes: Path, output: Path, *extra: str) -> list[str]:
    """Build a fixed two-mechanism masking run on the temporary fixture."""
    return [
        sys.executable,
        str(DRIVER),
        "--dataset-id",
        "fixture",
        "--events",
        str(events),
        "--nodes",
        str(nodes),
        "--event-tail-column",
        "sender",
        "--event-head-column",
        "recipients",
        "--node-column",
        "node",
        "--tail-cap",
        "1",
        "--head-cap",
        "2",
        "--mask-rate",
        "0.5",
        "--mechanisms",
        "mcar,mnar_out",
        "--replicates",
        "2",
        "--seed",
        "81",
        "--output-dir",
        str(output),
        *extra,
    ]


def rows(path: Path) -> list[dict[str, str]]:
    """Read a generated non-empty CSV output table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_event_first_masks_hold_out_complete_event_types_and_reconcile_arcs(tmp_path: Path) -> None:
    """Every duplicate of a selected tail/head type is absent from observed types."""
    events, nodes = write_fixture(tmp_path)
    output = tmp_path / "masks"
    completed = subprocess.run(
        command(events, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Event-first native-event-type masking passed." in completed.stdout

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "native_event_type"
    assert manifest["input_accounting"]["event_records_read"] == 10
    assert manifest["input_accounting"]["cap_eligible_event_records"] == 7
    assert manifest["input_accounting"]["cap_eligible_event_types"] == 6
    assert len(manifest["split_summaries"]) == 4

    for split in output.iterdir():
        if not split.is_dir():
            continue
        observed = rows(split / "observed_event_types.csv")
        heldout = rows(split / "heldout_event_types.csv")
        assert {row["event_type_id"] for row in observed}.isdisjoint(
            row["event_type_id"] for row in heldout
        )
        assert len(observed) + len(heldout) == 6
        assert not {row["event_type_id"] for row in observed}.intersection(
            row["event_type_id"] for row in heldout
        )
        assert all("event_id" not in row for row in observed + heldout)
        full = {(row["tail"], row["head"]) for row in rows(split / "observed_arcs.csv")}
        removed = {(row["tail"], row["head"]) for row in rows(split / "removed_arcs.csv")}
        assert full.isdisjoint(removed)
        assert len(full | removed) == 6
        assert (split / "removal_strata.csv").is_file()


def test_event_first_masks_require_explicit_overwrite_and_recreate_result(tmp_path: Path) -> None:
    """A rerun cannot blend result sets from different frozen masking requests."""
    events, nodes = write_fixture(tmp_path)
    output = tmp_path / "masks"
    first = subprocess.run(
        command(events, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(events, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "event-first mask output directory is nonempty" in blocked.stderr
    rerun = subprocess.run(
        command(events, nodes, output, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
