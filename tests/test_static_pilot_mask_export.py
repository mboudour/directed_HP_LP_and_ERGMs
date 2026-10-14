"""Integration test for deterministic export of completed static-pilot masks."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PILOT_DRIVER = PROJECT_ROOT / "scripts" / "30_run_static_benchmark.py"
MASK_DRIVER = PROJECT_ROOT / "scripts" / "32_export_static_pilot_masks.py"


def test_mask_export_reconstructs_pilot_heldout_positives(tmp_path: Path) -> None:
    """The conditional-scoring inputs must exactly match pilot labels and masks."""
    arcs_path = tmp_path / "arcs.parquet"
    nodes_path = tmp_path / "nodes.csv"
    pilot_dir = tmp_path / "pilot"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"tail": "a", "head": "b"},
                {"tail": "a", "head": "c"},
                {"tail": "b", "head": "c"},
                {"tail": "b", "head": "d"},
                {"tail": "c", "head": "d"},
                {"tail": "d", "head": "a"},
            ]
        ),
        arcs_path,
    )
    with nodes_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"])
        writer.writeheader()
        writer.writerows({"node": node} for node in ("a", "b", "c", "d"))

    pilot = subprocess.run(
        [
            sys.executable,
            str(PILOT_DRIVER),
            "--dataset",
            "eu_core",
            "--arcs",
            str(arcs_path),
            "--nodes",
            str(nodes_path),
            "--output-dir",
            str(pilot_dir),
            "--replicates",
            "2",
            "--mask-rate",
            "0.5",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert pilot.returncode == 0, pilot.stderr
    export = subprocess.run(
        [sys.executable, str(MASK_DRIVER), "--pilot-dir", str(pilot_dir)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert export.returncode == 0, export.stderr

    export_manifest = json.loads(
        (pilot_dir / "masks" / "mask_export_manifest.json").read_text(encoding="utf-8")
    )
    assert len(export_manifest["replicates"]) == 2
    predictions = pq.read_table(pilot_dir / "arc_lp_predictions.parquet").to_pylist()
    for replicate in (1, 2):
        expected = {
            (str(row["candidate_tail"]), str(row["candidate_head"]))
            for row in predictions
            if int(row["replicate"]) == replicate and int(row["label"]) == 1
        }
        with (pilot_dir / "masks" / f"replicate_{replicate:03d}_heldout_edges.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            actual = {(row["from"], row["to"]) for row in csv.DictReader(handle)}
        assert actual == expected
