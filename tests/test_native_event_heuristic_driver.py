"""Integration tests for leakage-safe native-event heuristic scoring."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "37_run_native_event_heuristics.py"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Create a stable temporary split table."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Create a complete event-first split with a two-hop positive event type."""
    nodes = tmp_path / "nodes.csv"
    masks = tmp_path / "masks"
    split = masks / "mcar_replicate_001"
    split.mkdir(parents=True)
    write_csv(nodes, ["node"], [{"node": node} for node in ("a", "b", "c")])
    fields = [
        "event_type_id",
        "tail_nodes_json",
        "head_nodes_json",
        "tail_arity",
        "head_arity",
        "occurrence_count",
    ]
    write_csv(
        split / "observed_event_types.csv",
        fields,
        [
            {
                "event_type_id": "event_type_00001",
                "tail_nodes_json": '["a"]',
                "head_nodes_json": '["b"]',
                "tail_arity": 1,
                "head_arity": 1,
                "occurrence_count": 2,
            },
            {
                "event_type_id": "event_type_00002",
                "tail_nodes_json": '["b"]',
                "head_nodes_json": '["c"]',
                "tail_arity": 1,
                "head_arity": 1,
                "occurrence_count": 1,
            },
        ],
    )
    write_csv(
        split / "heldout_event_types.csv",
        fields,
        [
            {
                "event_type_id": "event_type_00003",
                "tail_nodes_json": '["c"]',
                "head_nodes_json": '["a"]',
                "tail_arity": 1,
                "head_arity": 1,
                "occurrence_count": 1,
            }
        ],
    )
    write_csv(
        split / "observed_arcs.csv",
        ["tail", "head"],
        [{"tail": "a", "head": "b"}, {"tail": "b", "head": "c"}],
    )
    return masks, nodes


def command(masks: Path, nodes: Path, output: Path, *extra: str) -> list[str]:
    """Build a fully explicit temporary benchmark command."""
    return [
        sys.executable,
        str(DRIVER),
        "--dataset-id",
        "fixture",
        "--mask-dir",
        str(masks),
        "--nodes",
        str(nodes),
        "--node-column",
        "node",
        "--max-weak-distance",
        "2",
        "--seed",
        "31",
        "--output-dir",
        str(output),
        *extra,
    ]


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a generated CSV result table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_native_event_heuristics_exclude_all_known_event_types_from_negatives(
    tmp_path: Path,
) -> None:
    """Random negatives cannot overlap observed or held-out event types."""
    masks, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    completed = subprocess.run(
        command(masks, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Event-first native-event heuristic benchmark passed." in completed.stdout

    split_output = output / "mcar_replicate_001"
    predictions = read_rows(split_output / "candidate_predictions.csv")
    assert len(predictions) == 2
    positive = next(row for row in predictions if int(row["label"]) == 1)
    negative = next(row for row in predictions if int(row["label"]) == 0)
    assert positive["source_event_type_id"] == "event_type_00003"
    known_keys = {
        ('["a"]', '["b"]'),
        ('["b"]', '["c"]'),
        ('["c"]', '["a"]'),
    }
    assert (negative["tail_nodes_json"], negative["head_nodes_json"]) not in known_keys
    metrics = read_rows(split_output / "metrics.csv")
    assert {row["metric"] for row in metrics} == {
        "roc_auc",
        "pr_auc",
        "precision_at_k",
        "recall_at_k",
    }
    assert "log_loss" not in {row["metric"] for row in metrics}
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "native_event_type"
    assert manifest["splits_completed"] == 1


def test_native_event_heuristics_require_explicit_overwrite(tmp_path: Path) -> None:
    """A rerun cannot blend candidate panels generated under different settings."""
    masks, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    first = subprocess.run(
        command(masks, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(masks, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "native-event heuristic output directory is nonempty" in blocked.stderr
    rerun = subprocess.run(
        command(masks, nodes, output, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
