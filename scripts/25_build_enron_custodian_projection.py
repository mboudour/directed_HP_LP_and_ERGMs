#!/usr/bin/env python3
"""Project audited Enron address events onto reviewed custodian nodes and core-100 panels."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

CORE_SIZE = 100
BATCH_SIZE = 25_000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "native_events_address_level.parquet"
MAPPING = PROJECT_ROOT / "data" / "processed" / "enron_20150507" / "custodian_address_map.csv"
GATE = PROJECT_ROOT / "data" / "metadata" / "gates" / "enron_custodian_projection.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "enron_20150507"
PROJECTED_EVENTS = OUTPUT_DIR / "custodian_native_events.parquet"
CORE_NODES = OUTPUT_DIR / "custodian_core100_nodes.csv"
CORE_ARCS = OUTPUT_DIR / "custodian_core100_static_arcs.parquet"
MONTHLY_ARCS = OUTPUT_DIR / "custodian_core100_monthly_arcs.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_custodian_projection.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_custodian_projection.md"

EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("sent_at_utc", pa.timestamp("us", tz="UTC")),
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodians", pa.list_(pa.string())),
    ]
)
ARC_SCHEMA = pa.schema(
    [
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodian", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)
MONTH_SCHEMA = pa.schema(
    [
        pa.field("month", pa.string()),
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodian", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)


def read_policy() -> tuple[datetime, datetime, str]:
    """Validate the explicit gate and its timestamp inclusion window."""
    if not GATE.is_file():
        raise SystemExit(
            "STOP: custodian projection requires a reviewed gate record:\n"
            f"  {GATE.relative_to(PROJECT_ROOT)}"
        )
    record = json.loads(GATE.read_text(encoding="utf-8"))
    policy = record.get("projection_policy")
    if not record.get("approved") or not isinstance(policy, dict):
        raise SystemExit("STOP: Enron projection gate is not approved with a projection_policy")
    expected = {
        "unmapped_participant": "exclude_entire_event",
        "self_custodian_in_head": "remove",
        "message_copy_policy": "retain_distinct_maildir_records_after_duplicate_audit",
    }
    if {key: policy.get(key) for key in expected} != expected:
        raise SystemExit(f"STOP: required Enron projection policy is {expected}")
    try:
        start = datetime.fromisoformat(str(policy["timestamp_start_utc"]).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(policy["timestamp_end_utc"]).replace("Z", "+00:00"))
    except (KeyError, ValueError) as error:
        raise SystemExit(
            "STOP: projection policy needs ISO timestamp_start_utc and timestamp_end_utc"
        ) from error
    if start.tzinfo is None or end.tzinfo is None or end < start:
        raise SystemExit("STOP: Enron timestamp policy must be ordered and timezone-aware")
    return start, end, str(policy["message_copy_policy"])


def read_mapping() -> dict[str, str]:
    """Read reviewed address-to-custodian mappings with no ambiguous address assignment."""
    if not MAPPING.is_file():
        raise SystemExit(
            "STOP: reviewed custodian-address mapping is missing:\n"
            f"  {MAPPING.relative_to(PROJECT_ROOT)}"
        )
    mapping: dict[str, str] = {}
    with MAPPING.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"address", "custodian_mailbox", "approved"}
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(f"STOP: mapping columns must include {sorted(required)}")
        for row in reader:
            if row["approved"].strip().casefold() not in {"true", "yes", "1"}:
                continue
            address = row["address"].strip().casefold()
            custodian = row["custodian_mailbox"].strip()
            if not address or not custodian:
                raise SystemExit("STOP: approved mapping has an empty address or custodian")
            if address in mapping and mapping[address] != custodian:
                raise SystemExit(f"STOP: address maps to more than one custodian: {address}")
            mapping[address] = custodian
    if not mapping:
        raise SystemExit("STOP: mapping contains no approved address assignments")
    return mapping


def month_label(timestamp: datetime) -> str:
    """Return a calendar-month label after the approved timestamp-range filter."""
    return f"{timestamp.year:04d}-{timestamp.month:02d}"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(f"STOP: address-level Enron events are missing: {INPUT}")
    outputs = [PROJECTED_EVENTS, CORE_NODES, CORE_ARCS, MONTHLY_ARCS, SUMMARY, REPORT]
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise SystemExit(
            "STOP: custodian-projection output already exists; it will not be overwritten"
        )

    start, end, message_copy_policy = read_policy()
    mapping = read_mapping()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    source_events = 0
    projected_events = 0
    exclusions: Counter[str] = Counter()
    sent_activity: Counter[str] = Counter()
    received_activity: Counter[str] = Counter()
    buffer: list[dict[str, object]] = []
    writer = pq.ParquetWriter(PROJECTED_EVENTS, EVENT_SCHEMA, compression="zstd")

    try:
        source = pq.ParquetFile(INPUT)
        for batch in source.iter_batches(
            batch_size=BATCH_SIZE,
            columns=["event_id", "sent_at_utc", "sender_address", "head_addresses"],
        ):
            for record in batch.to_pylist():
                source_events += 1
                timestamp = record["sent_at_utc"]
                if timestamp is None or timestamp < start or timestamp > end:
                    exclusions["outside_approved_timestamp_range"] += 1
                    continue
                tail = mapping.get(str(record["sender_address"]).casefold())
                head = [
                    mapping.get(str(address).casefold()) for address in record["head_addresses"]
                ]
                if tail is None or any(value is None for value in head):
                    exclusions["unmapped_participant"] += 1
                    continue
                distinct_head = list(dict.fromkeys(value for value in head if value != tail))
                if not distinct_head:
                    exclusions["empty_head_after_self_custodian_removal"] += 1
                    continue
                buffer.append(
                    {
                        "event_id": str(record["event_id"]),
                        "sent_at_utc": timestamp,
                        "tail_custodian": tail,
                        "head_custodians": distinct_head,
                    }
                )
                projected_events += 1
                sent_activity[tail] += 1
                for head_custodian in distinct_head:
                    received_activity[head_custodian] += 1
                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
                    buffer.clear()
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
    except Exception:
        writer.close()
        if PROJECTED_EVENTS.exists():
            PROJECTED_EVENTS.unlink()
        raise
    writer.close()

    nodes = set(sent_activity) | set(received_activity)
    if len(nodes) < CORE_SIZE:
        raise SystemExit(
            f"STOP: projection retains {len(nodes):,} nodes; fewer than core-{CORE_SIZE}"
        )
    ranked = sorted(
        nodes, key=lambda node: (-(sent_activity[node] + received_activity[node]), node)
    )
    core = set(ranked[:CORE_SIZE])

    core_arc_counts: Counter[tuple[str, str]] = Counter()
    monthly_counts: Counter[tuple[str, str, str]] = Counter()
    core_event_count = 0
    for batch in pq.ParquetFile(PROJECTED_EVENTS).iter_batches(batch_size=BATCH_SIZE):
        for record in batch.to_pylist():
            tail = str(record["tail_custodian"])
            head = list(record["head_custodians"])
            if tail not in core or not all(value in core for value in head):
                continue
            core_event_count += 1
            month = month_label(record["sent_at_utc"])
            for value in head:
                core_arc_counts[(tail, value)] += 1
                monthly_counts[(month, tail, value)] += 1

    with CORE_NODES.open("x", newline="", encoding="utf-8") as handle:
        writer_csv = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "custodian_mailbox",
                "sent_activity",
                "received_activity",
                "total_activity",
            ],
            lineterminator="\n",
        )
        writer_csv.writeheader()
        for rank, node in enumerate(ranked[:CORE_SIZE], start=1):
            writer_csv.writerow(
                {
                    "rank": rank,
                    "custodian_mailbox": node,
                    "sent_activity": sent_activity[node],
                    "received_activity": received_activity[node],
                    "total_activity": sent_activity[node] + received_activity[node],
                }
            )

    pq.write_table(
        pa.Table.from_pylist(
            [
                {"tail_custodian": tail, "head_custodian": head, "interaction_count": count}
                for (tail, head), count in sorted(core_arc_counts.items())
            ],
            schema=ARC_SCHEMA,
        ),
        CORE_ARCS,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "month": month,
                    "tail_custodian": tail,
                    "head_custodian": head,
                    "interaction_count": count,
                }
                for (month, tail, head), count in sorted(monthly_counts.items())
            ],
            schema=MONTH_SCHEMA,
        ),
        MONTHLY_ARCS,
        compression="zstd",
    )

    summary = {
        "dataset_id": "enron_20150507",
        "address_level_events_read": source_events,
        "approved_mappings": len(mapping),
        "projection_timestamp_start_utc": start.isoformat(),
        "projection_timestamp_end_utc": end.isoformat(),
        "message_copy_policy": message_copy_policy,
        "custodian_events_retained": projected_events,
        "projection_exclusions": dict(exclusions),
        "projected_nodes": len(nodes),
        "core_rule": "top_100_by_sent_plus_received_activity_within_projected_custodian_nodes",
        "core_nodes": CORE_SIZE,
        "core_all_participant_events": core_event_count,
        "core_static_arcs": len(core_arc_counts),
        "core_months": len({month for month, _, _ in monthly_counts}),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""# Enron custodian projection and core-100 preparation

- Address-level events read: `{source_events:,}`
- Approved address-to-custodian mappings: `{len(mapping):,}`
- Projected native events retained: `{projected_events:,}`
- Projected custodian nodes: `{len(nodes):,}`
- Core-100 all-participant events: `{core_event_count:,}`
- Core-100 static arcs: `{len(core_arc_counts):,}`
- Calendar months with core ties: `{len({month for month, _, _ in monthly_counts}):,}`

The projection excludes any event with an unmapped participant and removes a recipient that
maps to the sender's custodian. It is the plan's primary custodian-node representation;
the earlier address-level graph remains an auditable provenance layer.
""",
        encoding="utf-8",
    )
    print("Enron custodian projection passed.")
    print(f"Projected native events retained: {projected_events:,}.")
    print(f"Projected nodes: {len(nodes):,}.")
    print(f"Core-100 static arcs: {len(core_arc_counts):,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
