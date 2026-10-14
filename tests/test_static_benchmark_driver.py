"""Integration test for the local static Phase 2 pilot driver."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "30_run_static_benchmark.py"


def test_static_benchmark_writes_reproducible_local_bundle(tmp_path: Path) -> None:
    """A small prepared arc table should generate LP, concept, and ERGM inputs."""
    arcs_path = tmp_path / "arcs.parquet"
    nodes_path = tmp_path / "nodes.csv"
    output_dir = tmp_path / "results"
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
        writer.writerows({"node": node} for node in ("a", "b", "c", "d", "isolated"))

    completed = subprocess.run(
        [
            sys.executable,
            str(DRIVER),
            "--dataset",
            "eu_core",
            "--arcs",
            str(arcs_path),
            "--nodes",
            str(nodes_path),
            "--output-dir",
            str(output_dir),
            "--replicates",
            "2",
            "--mask-rate",
            "0.5",
            "--tail-cap",
            "2",
            "--head-cap",
            "2",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Static Phase 2 pilot complete." in completed.stdout

    manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["nodes"] == 5
    assert manifest["static_arcs"] == 6
    assert manifest["masking"]["replicates"] == 2
    assert manifest["concept_fidelity"]["formal_concepts"] > 0
    assert (output_dir / "arc_lp_metrics.csv").is_file()
    assert (output_dir / "concept_section.csv").is_file()
    assert (output_dir / "r_inputs" / "static_edges.csv").is_file()
    assert (output_dir / "r_inputs" / "nodes.csv").is_file()

    predictions = pq.read_table(output_dir / "arc_lp_predictions.parquet")
    assert predictions.num_rows > 0
    assert set(predictions.column("label").to_pylist()) == {0, 1}

    rerun = subprocess.run(
        [
            *completed.args,
            "--overwrite",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
    rerun_manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert rerun_manifest == manifest
