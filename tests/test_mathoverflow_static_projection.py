"""Integration tests for the approved MathOverflow static projection."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "44_prepare_mathoverflow_static_projection.py"
EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("question_id", pa.string()),
        pa.field("question_created_at", pa.string()),
        pa.field("answer_window_days", pa.int16()),
        pa.field("tail_answerers", pa.list_(pa.string())),
        pa.field("head_asker", pa.string()),
        pa.field("construction", pa.string()),
    ]
)


def write_events(path: Path) -> None:
    """Write three valid reconstructed events with one non-core participant."""
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "event_id": "e1",
                    "question_id": "q1",
                    "question_created_at": "2024-01-01T00:00:00.000",
                    "answer_window_days": 30,
                    "tail_answerers": ["a", "b"],
                    "head_asker": "c",
                    "construction": "reconstructed_distinct_answerers_to_asker",
                },
                {
                    "event_id": "e2",
                    "question_id": "q2",
                    "question_created_at": "2024-01-02T00:00:00.000",
                    "answer_window_days": 30,
                    "tail_answerers": ["a"],
                    "head_asker": "c",
                    "construction": "reconstructed_distinct_answerers_to_asker",
                },
                {
                    "event_id": "e3",
                    "question_id": "q3",
                    "question_created_at": "2024-01-03T00:00:00.000",
                    "answer_window_days": 30,
                    "tail_answerers": ["d"],
                    "head_asker": "c",
                    "construction": "reconstructed_distinct_answerers_to_asker",
                },
            ],
            schema=EVENT_SCHEMA,
        ),
        path,
    )


def command(events: Path, output_dir: Path, summary: Path, report: Path, *extra: str) -> list[str]:
    """Build an explicit static-projection command for a fixture."""
    return [
        sys.executable,
        str(DRIVER),
        "--events",
        str(events),
        "--output-dir",
        str(output_dir),
        "--summary",
        str(summary),
        "--report",
        str(report),
        "--core-size",
        "3",
        *extra,
    ]


def test_static_projection_writes_consistent_core_views(tmp_path: Path) -> None:
    """The all-participant core uses the same reconstructed events as its static arcs."""
    events = tmp_path / "events.parquet"
    output_dir = tmp_path / "processed"
    summary_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"
    write_events(events)

    completed = subprocess.run(
        command(events, output_dir, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "MathOverflow static projection passed." in completed.stdout

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["source_native_events"] == 3
    assert summary["source_nodes"] == 4
    assert summary["source_static_arcs"] == 3
    assert summary["core_nodes"] == 3
    assert summary["core_all_participant_events"] == 2
    assert summary["core_static_arcs"] == 2
    assert summary["core_size_exception"] is False

    with (output_dir / "core100_nodes.csv").open(encoding="utf-8", newline="") as handle:
        nodes = list(csv.DictReader(handle))
    assert [row["node"] for row in nodes] == ["c", "a", "b"]

    arcs = pq.read_table(output_dir / "core100_static_arcs.parquet").to_pylist()
    assert arcs == [
        {"tail": "a", "head": "c", "interaction_count": 2},
        {"tail": "b", "head": "c", "interaction_count": 1},
    ]
    assert pq.read_table(output_dir / "core100_native_events.parquet").num_rows == 2


def test_static_projection_requires_explicit_overwrite(tmp_path: Path) -> None:
    """The source projection will not silently combine different core settings."""
    events = tmp_path / "events.parquet"
    output_dir = tmp_path / "processed"
    summary_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"
    write_events(events)
    first = subprocess.run(
        command(events, output_dir, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(events, output_dir, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "static projection output already exists" in blocked.stderr
    rerun = subprocess.run(
        command(events, output_dir, summary_path, report_path, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
