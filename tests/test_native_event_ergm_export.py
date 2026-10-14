"""Integration tests for frozen native-event ERGM input export."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "39_export_native_event_ergm_inputs.py"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write a minimal stable fixture CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def candidate_rows(prefix: str) -> list[dict[str, object]]:
    """Return one positive and one unseen negative event type for a panel fixture."""
    return [
        {
            "candidate_id": f"{prefix}_positive",
            "tail_nodes_json": '["a"]',
            "head_nodes_json": '["b", "c"]',
            "label": 1,
        },
        {
            "candidate_id": f"{prefix}_negative",
            "tail_nodes_json": '["b"]',
            "head_nodes_json": '["a", "c"]',
            "label": 0,
        },
    ]


def write_fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """Create a complete frozen mask plus random and hard panel source bundles."""
    masks = tmp_path / "masks"
    heuristics = tmp_path / "heuristics"
    hard = tmp_path / "hard"
    nodes = tmp_path / "nodes.csv"
    split = "mcar_replicate_001"
    write_csv(nodes, ["node"], [{"node": node} for node in ("a", "b", "c", "d")])
    write_csv(
        masks / split / "observed_arcs.csv",
        ["tail", "head"],
        [{"tail": "a", "head": "b"}, {"tail": "b", "head": "c"}],
    )
    write_csv(
        masks / split / "observed_event_types.csv",
        ["event_type_id"],
        [{"event_type_id": "event_type_00001"}],
    )
    write_csv(
        masks / split / "heldout_event_types.csv",
        ["event_type_id"],
        [{"event_type_id": "event_type_00002"}],
    )
    fields = ["candidate_id", "tail_nodes_json", "head_nodes_json", "label"]
    write_csv(heuristics / split / "candidate_predictions.csv", fields, candidate_rows("random"))
    write_csv(
        hard / split / "reversal_orientation_candidate_predictions.csv",
        fields,
        candidate_rows("reversal"),
    )
    write_csv(
        hard / split / "role_exchange_candidate_predictions.csv",
        fields,
        candidate_rows("exchange"),
    )
    return masks, heuristics, hard, nodes


def command(
    masks: Path, heuristics: Path, hard: Path, nodes: Path, output: Path, *extra: str
) -> list[str]:
    """Build an explicit fixture export invocation."""
    return [
        sys.executable,
        str(DRIVER),
        "--dataset-id",
        "fixture",
        "--mask-dir",
        str(masks),
        "--heuristic-dir",
        str(heuristics),
        "--hard-panel-dir",
        str(hard),
        "--nodes",
        str(nodes),
        "--node-column",
        "node",
        "--output-dir",
        str(output),
        *extra,
    ]


def rows(path: Path) -> list[dict[str, str]]:
    """Read an output CSV table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_export_native_event_ergm_inputs_preserves_split_specific_contract(tmp_path: Path) -> None:
    """The export namespaces panels while retaining each split's observed graph only."""
    masks, heuristics, hard, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    completed = subprocess.run(
        command(masks, heuristics, hard, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Native-event ERGM input export passed." in completed.stdout
    split = output / "splits" / "mcar_replicate_001"
    assert rows(split / "train_edges.csv") == [
        {"from": "a", "to": "b"},
        {"from": "b", "to": "c"},
    ]
    footprint_rows = rows(split / "candidate_footprints.csv")
    assert len(footprint_rows) == 12
    assert {row["panel"] for row in footprint_rows} == {
        "random",
        "reversal_orientation",
        "role_exchange",
    }
    assert all("::" in row["candidate_id"] for row in footprint_rows)
    dyads = rows(split / "candidate_dyads.csv")
    assert {(row["candidate_tail"], row["candidate_head"]) for row in dyads} == {
        ("a", "b"),
        ("a", "c"),
        ("b", "a"),
        ("b", "c"),
    }
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "native_event_type"
    assert manifest["panels"] == ["random", "reversal_orientation", "role_exchange"]


def test_export_native_event_ergm_inputs_requires_explicit_overwrite(tmp_path: Path) -> None:
    """A rerun cannot accidentally combine footprints from incompatible split outputs."""
    masks, heuristics, hard, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    first = subprocess.run(
        command(masks, heuristics, hard, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(masks, heuristics, hard, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "native-event ERGM input directory is nonempty" in blocked.stderr
    rerun = subprocess.run(
        command(masks, heuristics, hard, nodes, output, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
