"""Integration tests for the local cap-first formal-concept audit driver."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "28_audit_formal_concepts.py"


def write_fixture(root: Path) -> tuple[Path, Path]:
    """Write a small directed rectangle plus a non-rectangle edge."""
    nodes = root / "nodes.csv"
    edges = root / "edges.parquet"
    nodes.write_text("node\na\nb\nx\ny\nz\n", encoding="utf-8")
    table = pa.Table.from_pylist(
        [
            {"tail": "a", "head": "x"},
            {"tail": "a", "head": "y"},
            {"tail": "b", "head": "x"},
            {"tail": "b", "head": "y"},
            {"tail": "b", "head": "z"},
        ]
    )
    pq.write_table(table, edges)
    return nodes, edges


def test_formal_concept_audit_outputs_capped_representation_diagnostics(tmp_path: Path) -> None:
    """The driver emits deterministic concepts, coverage, and role-overlap evidence."""
    nodes, edges = write_fixture(tmp_path)
    output = tmp_path / "audit"
    command = [
        sys.executable,
        str(DRIVER),
        "--dataset=fixture",
        f"--edges={edges}",
        f"--nodes={nodes}",
        f"--output-dir={output}",
        "--tail-cap=2",
        "--head-cap=2",
    ]
    completed = subprocess.run(
        command, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    )
    assert completed.returncode == 0, completed.stderr
    assert "Capped formal-concept audit passed." in completed.stdout

    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["graph"] == {"directed_arcs": 5, "nodes": 5, "self_loops": 0}
    assert summary["enumeration"]["caps_applied_during_enumeration"] is True
    assert summary["concepts"]["count"] >= 1
    assert 0 <= summary["concepts"]["capped_footprint_arc_coverage"] <= 1

    with (output / "concepts.csv").open(encoding="utf-8", newline="") as handle:
        concepts = list(csv.DictReader(handle))
    assert any(row["tail_nodes_json"] == '["a","b"]' for row in concepts)
    assert all(int(row["tail_arity"]) <= 2 for row in concepts)
    assert all(int(row["head_arity"]) <= 2 for row in concepts)

    with (output / "arc_multiplicity.csv").open(encoding="utf-8", newline="") as handle:
        multiplicity = list(csv.DictReader(handle))
    assert len(multiplicity) == 5
    assert {tuple(row[key] for key in ("tail", "head")) for row in multiplicity} == {
        ("a", "x"),
        ("a", "y"),
        ("b", "x"),
        ("b", "y"),
        ("b", "z"),
    }


def test_formal_concept_audit_requires_explicit_overwrite(tmp_path: Path) -> None:
    """A rerun cannot silently alter a prior representation audit."""
    nodes, edges = write_fixture(tmp_path)
    output = tmp_path / "audit"
    base = [
        sys.executable,
        str(DRIVER),
        "--dataset=fixture",
        f"--edges={edges}",
        f"--nodes={nodes}",
        f"--output-dir={output}",
        "--tail-cap=2",
        "--head-cap=2",
    ]
    first = subprocess.run(base, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(base, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    assert blocked.returncode != 0
    assert "formal-concept audit output already exists" in blocked.stderr
    retried = subprocess.run(
        [*base, "--overwrite"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    )
    assert retried.returncode == 0, retried.stderr
