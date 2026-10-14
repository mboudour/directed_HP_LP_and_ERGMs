#!/usr/bin/env python3
"""Build address-level Enron native email events under the audited header policy."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "parsed_headers.parquet"
OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "native_events_address_level.parquet"
)
TEMP_OUTPUT = OUTPUT.with_suffix(".parquet.tmp")
SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_level_event_build_summary.json"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_address_level_event_build.md"

SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("source_path", pa.string()),
        pa.field("custodian_mailbox", pa.string()),
        pa.field("raw_sha256", pa.string()),
        pa.field("message_id_raw", pa.string()),
        pa.field("sent_at_utc", pa.timestamp("us", tz="UTC")),
        pa.field("sender_address", pa.string()),
        pa.field("head_addresses", pa.list_(pa.string())),
        pa.field("head_size", pa.int16()),
        pa.field("to_address_count", pa.int16()),
        pa.field("cc_address_count", pa.int16()),
        pa.field("sender_removed_from_head", pa.bool_()),
    ]
)


def unique_preserving_order(addresses: list[str]) -> list[str]:
    """Deduplicate an address sequence while retaining its first-seen order."""
    return list(dict.fromkeys(addresses))


def arity_bin(size: int) -> str:
    """Create compact recipient-head arity bins for audit reporting."""
    return str(size) if size <= 4 else "5+"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: normalized Enron table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/04_normalize_enron_headers.py first."
        )

    existing_outputs = [path for path in (OUTPUT, TEMP_OUTPUT, SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: address-level event output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    input_records = 0
    native_events = 0
    excluded = Counter()
    head_arity = Counter()
    self_recipient_removed = 0
    unique_addresses: set[str] = set()
    event_times: list[object] = []
    buffer: list[dict[str, object]] = []

    try:
        with pq.ParquetWriter(TEMP_OUTPUT, SCHEMA, compression="zstd") as writer:
            parquet_file = pq.ParquetFile(INPUT)

            for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
                for record in batch.to_pylist():
                    input_records += 1

                    if record["date_parse_status"] != "ok_timezone_aware":
                        excluded["date_not_timezone_aware"] += 1
                        continue

                    sender_addresses = record["from_addresses"]
                    if len(sender_addresses) != 1 or int(record["from_parse_issue_count"]) > 0:
                        excluded["sender_not_exactly_one_clean_address"] += 1
                        continue

                    if (
                        int(record["to_parse_issue_count"]) > 0
                        or int(record["cc_parse_issue_count"]) > 0
                    ):
                        excluded["to_or_cc_address_parse_issue"] += 1
                        continue

                    sender = str(sender_addresses[0])
                    original_head = unique_preserving_order(
                        list(record["to_addresses"]) + list(record["cc_addresses"])
                    )

                    if not original_head:
                        excluded["no_to_or_cc_recipient"] += 1
                        continue

                    head = [address for address in original_head if address != sender]
                    sender_was_removed = len(head) != len(original_head)

                    if sender_was_removed:
                        self_recipient_removed += 1

                    if not head:
                        excluded["head_empty_after_sender_removal"] += 1
                        continue

                    event = {
                        "event_id": f"enron_20150507:{record['raw_sha256']}",
                        "source_path": record["source_path"],
                        "custodian_mailbox": record["custodian_mailbox"],
                        "raw_sha256": record["raw_sha256"],
                        "message_id_raw": record["message_id_raw"],
                        "sent_at_utc": record["sent_at_utc"],
                        "sender_address": sender,
                        "head_addresses": head,
                        "head_size": len(head),
                        "to_address_count": len(record["to_addresses"]),
                        "cc_address_count": len(record["cc_addresses"]),
                        "sender_removed_from_head": sender_was_removed,
                    }

                    buffer.append(event)
                    native_events += 1
                    head_arity[arity_bin(len(head))] += 1
                    unique_addresses.add(sender)
                    unique_addresses.update(head)
                    event_times.append(record["sent_at_utc"])

                    if len(buffer) >= BATCH_SIZE:
                        writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                        buffer.clear()

            if buffer:
                writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))

        if input_records != EXPECTED_RECORDS:
            raise SystemExit(
                "STOP: unexpected normalized-table row count.\n"
                f"Expected: {EXPECTED_RECORDS:,}\n"
                f"Found:    {input_records:,}"
            )

        TEMP_OUTPUT.replace(OUTPUT)

    except Exception:
        if TEMP_OUTPUT.exists():
            TEMP_OUTPUT.unlink()
        raise

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "output": str(OUTPUT.relative_to(PROJECT_ROOT)),
        "input_records": input_records,
        "native_events_written": native_events,
        "unique_address_level_nodes": len(unique_addresses),
        "event_time_span_utc": {
            "minimum": min(event_times).isoformat() if event_times else None,
            "maximum": max(event_times).isoformat() if event_times else None,
        },
        "head_arity_bins": {label: head_arity[label] for label in ("1", "2", "3", "4", "5+")},
        "sequential_exclusion_counts": {
            "date_not_timezone_aware": excluded["date_not_timezone_aware"],
            "sender_not_exactly_one_clean_address": (
                excluded["sender_not_exactly_one_clean_address"]
            ),
            "to_or_cc_address_parse_issue": (excluded["to_or_cc_address_parse_issue"]),
            "no_to_or_cc_recipient": excluded["no_to_or_cc_recipient"],
            "head_empty_after_sender_removal": (excluded["head_empty_after_sender_removal"]),
        },
        "events_with_sender_removed_from_head": self_recipient_removed,
        "header_policy": {
            "included_recipient_fields": ["To", "Cc"],
            "bcc": (
                "Excluded because the audited archive duplicates every non-empty "
                "Bcc field exactly in Cc."
            ),
            "sender_in_head": (
                "Removed to enforce a disjoint tail and head, while retaining "
                "other recipients in the same message."
            ),
            "alias_resolution": ("Not performed; nodes are canonical email addresses."),
            "event_deduplication": (
                "Not performed because archive and Message-ID audits found no duplicates."
            ),
        },
        "next_processing_step": (
            "Construct explicit address-level arcs and then define a "
            "reproducible core-selection or custodian-projection policy."
        ),
    }

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    exclusion_rows = "\n".join(
        f"| {label.replace('_', ' ')} | {count:,} |"
        for label, count in summary["sequential_exclusion_counts"].items()
    )
    arity_rows = "\n".join(
        f"| {label} | {count:,} |" for label, count in summary["head_arity_bins"].items()
    )

    REPORT.write_text(
        f"""# Enron address-level native-event build

## Scope

This build creates an address-level native-event table from normalized message headers.
No email addresses are placed in the tracked summary or audit report; the event table
remains local and ignored by Git.

- Input header records: `{input_records:,}`
- Native events written: `{native_events:,}`
- Unique address-level nodes: `{len(unique_addresses):,}`
- Earliest event timestamp: `{summary["event_time_span_utc"]["minimum"]}`
- Latest event timestamp: `{summary["event_time_span_utc"]["maximum"]}`

## Header policy

Each retained event has one sender and a non-empty recipient head built from the ordered,
deduplicated union of To and Cc. Bcc is excluded because its non-empty values are exact
copies of Cc in this archive. If the sender appears in To or Cc, that self-address is
removed from the head to enforce tail-head disjointness; all other recipients remain.

No alias resolution is applied: nodes are canonical email addresses at this stage.

## Sequential exclusions

| First unmet requirement | Records |
|---|---:|
{exclusion_rows}

## Recipient-head arity

| Head size | Native events |
|---|---:|
{arity_rows}

## Provenance

- Event identifier: `enron_20150507:` followed by the raw-message SHA-256.
- Time: original timezone-aware Date header converted to UTC.
- Body content: never retained.
- Event table: `data/interim/enron_20150507/native_events_address_level.parquet`.
""",
        encoding="utf-8",
    )

    print("Enron address-level event build passed.")
    print(f"Input header records: {input_records:,}.")
    print(f"Native events written: {native_events:,}.")
    print(f"Unique address-level nodes: {len(unique_addresses):,}.")
    print(f"Events with sender removed from recipient head: {self_recipient_removed:,}.")
    print(f"Excluded for To/Cc address parse issues: {excluded['to_or_cc_address_parse_issue']:,}.")
    print(f"Excluded for no To/Cc recipient: {excluded['no_to_or_cc_recipient']:,}.")
    print(
        "Excluded because head was empty after sender removal: "
        f"{excluded['head_empty_after_sender_removal']:,}."
    )
    print(f"Event table: {OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
