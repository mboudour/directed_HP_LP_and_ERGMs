"""Integration tests for directed native-event hard-negative panels."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "38_run_native_event_hard_panels.py"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write a stable fixture table."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Create a frozen split where reversal and role exchange are unseen event types."""
    nodes = tmp_path / "nodes.csv"
    mask_dir = tmp_path / "masks"
    split = mask_dir / "mcar_replicate_001"
    split.mkdir(parents=True)
    write_csv(nodes, ["node"], [{"node": node} for node in ("a", "b", "c", "d")])
    fields = ["event_type_id", "tail_nodes_json", "head_nodes_json"]
    write_csv(
        split / "observed_event_types.csv",
        fields,
        [
            {
                "event_type_id": "event_type_00001",
                "tail_nodes_json": '["a"]',
                "head_nodes_json": '["b"]',
            },
            {
                "event_type_id": "event_type_00002",
                "tail_nodes_json": '["b"]',
                "head_nodes_json": '["c"]',
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
                "head_nodes_json": '["a", "d"]',
            }
        ],
    )
    write_csv(
        split / "observed_arcs.csv",
        ["tail", "head"],
        [
            {"tail": "a", "head": "b"},
            {"tail": "b", "head": "c"},
            {"tail": "c", "head": "d"},
            {"tail": "d", "head": "a"},
        ],
    )
    return mask_dir, nodes


def command(mask_dir: Path, nodes: Path, output: Path, *extra: str) -> list[str]:
    """Build an explicit hard-panel driver invocation."""
    return [
        sys.executable,
        str(DRIVER),
        "--dataset-id",
        "fixture",
        "--mask-dir",
        str(mask_dir),
        "--nodes",
        str(nodes),
        "--node-column",
        "node",
        "--max-weak-distance",
        "2",
        "--seed",
        "41",
        "--output-dir",
        str(output),
        *extra,
    ]


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a generated CSV table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_hard_panels_use_only_unseen_transformed_event_types(tmp_path: Path) -> None:
    """Reversal and role-exchange negatives are true non-event transformations."""
    mask_dir, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    completed = subprocess.run(
        command(mask_dir, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Native-event directed hard-negative benchmark passed." in completed.stdout

    split = output / "mcar_replicate_001"
    known = {
        ('["a"]', '["b"]'),
        ('["b"]', '["c"]'),
        ('["c"]', '["a", "d"]'),
    }
    for panel in ("reversal_orientation", "role_exchange"):
        predictions = read_rows(split / f"{panel}_candidate_predictions.csv")
        assert len(predictions) == 2
        assert {row["label"] for row in predictions} == {"0", "1"}
        negative = next(row for row in predictions if row["label"] == "0")
        assert (negative["tail_nodes_json"], negative["head_nodes_json"]) not in known
        metrics = read_rows(split / f"{panel}_metrics.csv")
        assert {row["metric"] for row in metrics} == {
            "roc_auc",
            "pr_auc",
            "precision_at_k",
            "recall_at_k",
        }
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["hard_panels"] == ["reversal_orientation", "role_exchange"]


def test_hard_panels_require_explicit_overwrite(tmp_path: Path) -> None:
    """A rerun cannot accidentally mix transformed negative panels."""
    mask_dir, nodes = write_fixture(tmp_path)
    output = tmp_path / "output"
    first = subprocess.run(
        command(mask_dir, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(mask_dir, nodes, output),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "native-event hard-panel output directory is nonempty" in blocked.stderr
    rerun = subprocess.run(
        command(mask_dir, nodes, output, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
