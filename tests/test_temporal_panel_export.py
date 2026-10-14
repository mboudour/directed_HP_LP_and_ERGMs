"""Integration test for the bounded temporal-panel export driver."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "31_export_temporal_panel.py"


def test_temporal_panel_export_writes_bounded_r_contract(tmp_path: Path) -> None:
    """The export must retain the declared node universe and selected panel range."""
    panel_path = tmp_path / "windows.parquet"
    nodes_path = tmp_path / "nodes.csv"
    output_dir = tmp_path / "temporal_result"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"window_index": 0, "tail": "a", "head": "b"},
                {"window_index": 0, "tail": "b", "head": "c"},
                {"window_index": 1, "tail": "a", "head": "c"},
                {"window_index": 2, "tail": "c", "head": "a"},
                {"window_index": 3, "tail": "c", "head": "b"},
            ]
        ),
        panel_path,
    )
    with nodes_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"])
        writer.writeheader()
        writer.writerows({"node": node} for node in ("a", "b", "c", "isolated"))

    completed = subprocess.run(
        [
            sys.executable,
            str(DRIVER),
            "--dataset",
            "eu_core",
            "--input",
            str(panel_path),
            "--nodes",
            str(nodes_path),
            "--output-dir",
            str(output_dir),
            "--start",
            "1",
            "--panel-count",
            "3",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr

    manifest = json.loads((output_dir / "temporal_input_manifest.json").read_text(encoding="utf-8"))
    assert manifest["selected_panel_labels"] == ["1", "2", "3"]
    assert manifest["nodes"] == 4
    assert manifest["transitions"] == 2
    with (output_dir / "panel_edges.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [(row["time"], row["from"], row["to"]) for row in rows] == [
        ("1", "a", "c"),
        ("2", "c", "a"),
        ("3", "c", "b"),
    ]
