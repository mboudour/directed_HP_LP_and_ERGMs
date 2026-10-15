"""Integration test for the arc-first formal-concept recovery driver."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "46_run_arcfirst_concept_recovery.py"


def write_fixture(root: Path) -> tuple[Path, Path]:
    """Build a connected, non-sensitive relation with capped concept targets."""
    nodes = [f"n{index:02d}" for index in range(30)]
    tail_a, tail_b = "n00", "n01"
    head_x, head_y = "n03", "n04"
    arcs = {
        (tail_a, head_x),
        (tail_a, head_y),
        (tail_b, head_x),
        (tail_b, head_y),
    }
    blocked_targets = {head_x, head_y}
    for index, tail in enumerate(nodes):
        targets: list[str] = []
        offset = 1
        while len(targets) < 3:
            head = nodes[(index + offset) % len(nodes)]
            offset += 1
            if head == tail or head in blocked_targets:
                continue
            targets.append(head)
        arcs.update((tail, head) for head in targets)

    node_path = root / "nodes.csv"
    with node_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"node": node} for node in nodes)

    arc_path = root / "arcs.parquet"
    pq.write_table(
        pa.Table.from_pylist([{"tail": tail, "head": head} for tail, head in sorted(arcs)]),
        arc_path,
    )
    return arc_path, node_path


def test_arcfirst_concept_recovery_writes_balanced_panels(tmp_path: Path) -> None:
    """Concept recovery preserves target identity and reports panel availability."""
    arcs, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    command = [
        sys.executable,
        str(DRIVER),
        "--dataset",
        "eu_core",
        "--arcs",
        str(arcs),
        "--nodes",
        str(nodes),
        "--tail-column",
        "tail",
        "--head-column",
        "head",
        "--node-column",
        "node",
        "--tail-cap",
        "2",
        "--head-cap",
        "2",
        "--max-weak-distance",
        "10",
        "--mechanisms",
        "mcar",
        "--replicates",
        "1",
        "--output-dir",
        str(output),
    ]
    completed = subprocess.run(
        command, cwd=PROJECT_ROOT, check=True, text=True, capture_output=True
    )
    assert "Arc-first formal-concept recovery benchmark passed." in completed.stdout

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "full_graph_formal_concepts_lost_after_arc_first_masking"
    assert manifest["completed_splits"] == 1

    with (output / "split_summary.csv").open(encoding="utf-8", newline="") as handle:
        summary = next(csv.DictReader(handle))
    assert int(summary["eligible_positive_concepts"]) > 0
    assert int(summary["random_positive_concepts"]) == int(summary["random_negative_concepts"])
    assert int(summary["degree_matched_positive_concepts"]) == int(
        summary["degree_matched_negative_concepts"]
    )

    with (output / "mcar_replicate_001" / "random_predictions.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert {row["label"] for row in rows} == {"0", "1"}
    assert "Positive target: a full-graph formal concept" in (output / "summary.md").read_text(
        encoding="utf-8"
    )
