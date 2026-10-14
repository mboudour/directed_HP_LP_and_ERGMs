"""Tests for the deterministic nested Enron MCMLE feasibility core."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "41_materialize_enron_mcmle_core50.py"


def load_driver(path: Path):
    """Load a standalone driver for a temporary local-data fixture."""
    spec = importlib.util.spec_from_file_location("enron_mcmle_core50", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nested_core_is_rank_prefix_and_filters_full_events(tmp_path: Path, monkeypatch) -> None:
    """The feasibility core must retain only all-participant events in the rank prefix."""
    module = load_driver(DRIVER)
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "CORE_SIZE", 2)

    source_nodes = tmp_path / "core100.csv"
    source_nodes.write_text(
        "rank,custodian_mailbox,sent_activity,received_activity,total_activity\n"
        "1,alpha,10,2,12\n"
        "2,beta,8,3,11\n"
        "3,gamma,7,2,9\n",
        encoding="utf-8",
    )
    source_events = tmp_path / "source_events.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "event_id": "e1",
                    "sent_at_utc": datetime(2000, 1, 1, tzinfo=UTC),
                    "tail_custodian": "alpha",
                    "head_custodians": ["beta"],
                },
                {
                    "event_id": "e2",
                    "sent_at_utc": datetime(2000, 1, 2, tzinfo=UTC),
                    "tail_custodian": "alpha",
                    "head_custodians": ["gamma"],
                },
                {
                    "event_id": "e3",
                    "sent_at_utc": datetime(2000, 2, 1, tzinfo=UTC),
                    "tail_custodian": "beta",
                    "head_custodians": ["alpha"],
                },
            ],
            schema=module.EVENT_SCHEMA,
        ),
        source_events,
    )
    output_dir = tmp_path / "processed"
    monkeypatch.setattr(module, "SOURCE_NODES", source_nodes)
    monkeypatch.setattr(module, "SOURCE_EVENTS", source_events)
    monkeypatch.setattr(module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(module, "OUTPUT_NODES", output_dir / "nodes.csv")
    monkeypatch.setattr(module, "OUTPUT_EVENTS", output_dir / "events.parquet")
    monkeypatch.setattr(module, "OUTPUT_ARCS", output_dir / "arcs.parquet")
    monkeypatch.setattr(module, "OUTPUT_MONTHLY_ARCS", output_dir / "monthly.parquet")
    monkeypatch.setattr(module, "SUMMARY", tmp_path / "metadata" / "summary.json")
    monkeypatch.setattr(module, "REPORT", tmp_path / "audit.md")
    monkeypatch.setattr(sys, "argv", [str(DRIVER), "--overwrite"])

    module.main()

    with module.OUTPUT_NODES.open(newline="", encoding="utf-8") as handle:
        node_rows = list(csv.DictReader(handle))
    assert [row["custodian_mailbox"] for row in node_rows] == ["alpha", "beta"]
    events = pq.read_table(module.OUTPUT_EVENTS).to_pylist()
    assert [event["event_id"] for event in events] == ["e1", "e3"]
    summary = json.loads(module.SUMMARY.read_text(encoding="utf-8"))
    assert summary["retained_all_participant_events"] == 2
    assert summary["excluded_events_with_participant_outside_core"] == 1
    assert summary["static_directed_arcs"] == 2
    module.main()
    assert json.loads(module.SUMMARY.read_text(encoding="utf-8")) == summary
