"""Integration tests for the approved strict Enron custodian projection workflow."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAPPING_DRIVER = PROJECT_ROOT / "scripts" / "15_materialize_enron_strict_mapping.py"
PROJECTION_DRIVER = PROJECT_ROOT / "scripts" / "25_build_enron_custodian_projection.py"


def load_driver(path: Path, name: str):
    """Load a standalone driver for a temporary local-data fixture."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_policy(path: Path) -> None:
    """Write the timestamp-only policy consumed by the strict mapping driver."""
    path.write_text(
        "status: approved_for_timestamp_filter_only\n"
        "inclusion:\n"
        "  timestamp_start_utc: '1998-01-01T00:00:00+00:00'\n"
        "  timestamp_end_utc: '2002-12-31T23:59:59.999999+00:00'\n",
        encoding="utf-8",
    )


def test_strict_mapping_approves_only_unique_high_support_noncolliding_rows(
    tmp_path: Path, monkeypatch
) -> None:
    """The approved rule must exclude low-support, shared, and absent candidates."""
    module = load_driver(MAPPING_DRIVER, "enron_strict_mapping")
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    headers = tmp_path / "headers.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"custodian_mailbox": "alpha"},
                {"custodian_mailbox": "beta"},
                {"custodian_mailbox": "gamma"},
                {"custodian_mailbox": "delta"},
            ]
        ),
        headers,
    )
    evidence = tmp_path / "evidence.csv"
    evidence.write_text(
        "custodian_mailbox,rank,candidate_sender_address,supporting_sent_like_messages,"
        "eligible_sent_like_messages,support_share,unique_top_candidate\n"
        "alpha,1,shared@example.org,99,100,0.99,True\n"
        "beta,1,shared@example.org,98,100,0.98,True\n"
        "gamma,1,low@example.org,89,100,0.89,True\n",
        encoding="utf-8",
    )
    policy = tmp_path / "temporal_policy.yaml"
    write_policy(policy)
    mapping = tmp_path / "processed" / "mapping.csv"
    gate = tmp_path / "metadata" / "gate.json"
    summary = tmp_path / "metadata" / "summary.json"
    report = tmp_path / "audit.md"
    monkeypatch.setattr(module, "HEADERS", headers)
    monkeypatch.setattr(module, "EVIDENCE", evidence)
    monkeypatch.setattr(module, "TEMPORAL_POLICY", policy)
    monkeypatch.setattr(module, "MAPPING", mapping)
    monkeypatch.setattr(module, "GATE", gate)
    monkeypatch.setattr(module, "SUMMARY", summary)
    monkeypatch.setattr(module, "REPORT", report)
    monkeypatch.setattr(module, "OUTPUTS", (mapping, gate, summary, report))
    monkeypatch.setattr(module, "EXPECTED_CUSTODIANS", 4)
    monkeypatch.setattr(sys, "argv", [str(MAPPING_DRIVER), "--overwrite"])

    with pytest.raises(SystemExit, match="approved no mappings"):
        module.main()

    evidence.write_text(
        evidence.read_text(encoding="utf-8") + "delta,1,delta@example.org,95,100,0.95,True\n",
        encoding="utf-8",
    )
    module.main()

    with mapping.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    approved = [row for row in rows if row["approved"] == "True"]
    assert approved == [
        {
            "address": "delta@example.org",
            "custodian_mailbox": "delta",
            "approved": "True",
            "selection_status": "approved_strict_automatic",
            "support_share": "0.95",
            "supporting_sent_like_messages": "95",
            "eligible_sent_like_messages": "100",
        }
    ]
    gate_payload = json.loads(gate.read_text(encoding="utf-8"))
    assert gate_payload["approved"] is True
    assert gate_payload["mapping_policy"]["approved_mappings"] == 1
    assert gate_payload["projection_policy"]["unmapped_participant"] == "exclude_entire_event"


def test_strict_projection_filters_full_events_and_can_be_rerun(
    tmp_path: Path, monkeypatch
) -> None:
    """The projection applies the approved interval and full-event mapping rule."""
    module = load_driver(PROJECTION_DRIVER, "enron_strict_projection")
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    event_table = tmp_path / "events.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "event_id": "e1",
                    "sent_at_utc": datetime(2000, 1, 1, tzinfo=UTC),
                    "sender_address": "alpha@example.org",
                    "head_addresses": ["beta@example.org"],
                },
                {
                    "event_id": "e2",
                    "sent_at_utc": datetime(2003, 1, 1, tzinfo=UTC),
                    "sender_address": "alpha@example.org",
                    "head_addresses": ["beta@example.org"],
                },
                {
                    "event_id": "e3",
                    "sent_at_utc": datetime(2000, 1, 2, tzinfo=UTC),
                    "sender_address": "alpha@example.org",
                    "head_addresses": ["outside@example.org"],
                },
                {
                    "event_id": "e4",
                    "sent_at_utc": datetime(2000, 1, 3, tzinfo=UTC),
                    "sender_address": "alpha@example.org",
                    "head_addresses": ["alpha@example.org"],
                },
                {
                    "event_id": "e5",
                    "sent_at_utc": datetime(2000, 1, 4, tzinfo=UTC),
                    "sender_address": "beta@example.org",
                    "head_addresses": ["alpha@example.org"],
                },
            ]
        ),
        event_table,
    )
    mapping = tmp_path / "mapping.csv"
    mapping.write_text(
        "address,custodian_mailbox,approved\n"
        "alpha@example.org,alpha,True\n"
        "beta@example.org,beta,True\n",
        encoding="utf-8",
    )
    gate = tmp_path / "gate.json"
    gate.write_text(
        json.dumps(
            {
                "approved": True,
                "projection_policy": {
                    "unmapped_participant": "exclude_entire_event",
                    "self_custodian_in_head": "remove",
                    "message_copy_policy": "retain_distinct_maildir_records_after_duplicate_audit",
                    "timestamp_start_utc": "1998-01-01T00:00:00+00:00",
                    "timestamp_end_utc": "2002-12-31T23:59:59.999999+00:00",
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "processed"
    projected = output_dir / "events.parquet"
    core_nodes = output_dir / "core_nodes.csv"
    core_arcs = output_dir / "core_arcs.parquet"
    monthly = output_dir / "monthly.parquet"
    summary = tmp_path / "metadata" / "summary.json"
    report = tmp_path / "audit.md"
    monkeypatch.setattr(module, "INPUT", event_table)
    monkeypatch.setattr(module, "MAPPING", mapping)
    monkeypatch.setattr(module, "GATE", gate)
    monkeypatch.setattr(module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(module, "PROJECTED_EVENTS", projected)
    monkeypatch.setattr(module, "CORE_NODES", core_nodes)
    monkeypatch.setattr(module, "CORE_ARCS", core_arcs)
    monkeypatch.setattr(module, "MONTHLY_ARCS", monthly)
    monkeypatch.setattr(module, "SUMMARY", summary)
    monkeypatch.setattr(module, "REPORT", report)
    monkeypatch.setattr(module, "CORE_SIZE", 2)
    monkeypatch.setattr(sys, "argv", [str(PROJECTION_DRIVER), "--overwrite"])

    module.main()
    first = json.loads(summary.read_text(encoding="utf-8"))
    assert first["custodian_events_retained"] == 2
    assert first["projection_exclusions"] == {
        "empty_head_after_self_custodian_removal": 1,
        "outside_approved_timestamp_range": 1,
        "unmapped_participant": 1,
    }
    assert first["core_all_participant_events"] == 2
    assert first["core_static_arcs"] == 2
    module.main()
    assert json.loads(summary.read_text(encoding="utf-8")) == first
