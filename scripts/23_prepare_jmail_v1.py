#!/usr/bin/env python3
"""Audit Jmail v1 and build restricted native events only after explicit approval."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED_ROWS = 1_781_028
BATCH_SIZE = 25_000
REQUIRED_COLUMNS = {
    "id",
    "doc_id",
    "message_index",
    "sender",
    "to_recipients",
    "cc_recipients",
    "bcc_recipients",
    "sent_at",
    "email_drop_id",
    "release_batch",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "raw" / "jmail_v1_2026_02" / "emails-slim.parquet"
GATE = PROJECT_ROOT / "data" / "metadata" / "gates" / "jmail_v1_admissibility.json"
OUTPUT = PROJECT_ROOT / "data" / "processed" / "jmail_v1_2026_02" / "native_events.parquet"
TEMP_OUTPUT = OUTPUT.with_suffix(".parquet.tmp")
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "jmail_v1_2026_02_audit.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "jmail_v1_2026_02_preparation.md"

EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("doc_id", pa.string()),
        pa.field("message_index", pa.string()),
        pa.field("email_drop_id", pa.string()),
        pa.field("release_batch", pa.string()),
        pa.field("sent_at_raw", pa.string()),
        pa.field("sender", pa.string()),
        pa.field("head", pa.list_(pa.string())),
    ]
)


def canonical_address(value: object) -> str | None:
    """Apply the gate-declared conservative string canonicalization."""
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold()
    return normalized or None


def recipient_list(value: Any) -> list[str]:
    """Parse one documented JSON-array recipient field strictly."""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("invalid JSON recipient array") from error
    elif isinstance(value, list):
        decoded = value
    else:
        raise ValueError("recipient array is neither JSON text nor a list")
    if not isinstance(decoded, list):
        raise ValueError("recipient field does not decode to a list")
    output: list[str] = []
    for item in decoded:
        address = canonical_address(item)
        if address is None:
            raise ValueError("recipient list contains an empty or non-string item")
        output.append(address)
    return output


def timestamp_is_parseable(value: object) -> bool:
    """Audit ISO-like timestamps without choosing a temporal-analysis policy."""
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def approved_event_policy() -> dict[str, object]:
    """Load a reviewed gate record and validate the currently supported policy."""
    if not GATE.is_file():
        raise SystemExit(
            "STOP: restricted event construction is blocked without a Jmail gate record:\n"
            f"  {GATE.relative_to(PROJECT_ROOT)}"
        )
    record = json.loads(GATE.read_text(encoding="utf-8"))
    policy = record.get("event_policy")
    if not record.get("approved") or not isinstance(policy, dict):
        raise SystemExit("STOP: Jmail gate record is not approved with an event_policy object")
    expected = {
        "identity_normalization": "strip_casefold",
        "deduplication": "first_by_id",
        "included_recipient_fields": ["to_recipients", "cc_recipients"],
        "bcc": "excluded",
    }
    if policy != expected:
        raise SystemExit(
            "STOP: Jmail gate policy differs from the implemented reproducible policy.\n"
            f"Required: {json.dumps(expected, sort_keys=True)}"
        )
    return record


def audit_and_optionally_build(build_events: bool) -> None:
    """Create a non-sensitive audit and, only when approved, local restricted events."""
    if not INPUT.is_file():
        raise SystemExit(f"STOP: Jmail v1 source is missing: {INPUT}")
    if SUMMARY.exists() or REPORT.exists() or (build_events and OUTPUT.exists()):
        raise SystemExit("STOP: Jmail output already exists; this script will not overwrite it")

    gate_record: dict[str, object] | None = None
    if build_events:
        gate_record = approved_event_policy()

    source = pq.ParquetFile(INPUT)
    missing_columns = REQUIRED_COLUMNS - set(source.schema_arrow.names)
    if missing_columns:
        raise SystemExit(f"STOP: Jmail source lacks required columns: {sorted(missing_columns)}")

    records = 0
    identifiers: set[str] = set()
    duplicate_ids = 0
    missing_id = 0
    malformed_fields: Counter[str] = Counter()
    missing_sender = 0
    timestamp_invalid = 0
    valid_candidate_events = 0
    excluded: Counter[str] = Counter()
    seen_event_ids: set[str] = set()
    buffer: list[dict[str, object]] = []

    if build_events:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        writer = pq.ParquetWriter(TEMP_OUTPUT, EVENT_SCHEMA, compression="zstd")
    else:
        writer = None

    try:
        for batch in source.iter_batches(batch_size=BATCH_SIZE, columns=sorted(REQUIRED_COLUMNS)):
            for record in batch.to_pylist():
                records += 1
                message_id = canonical_address(record["id"])
                if message_id is None:
                    missing_id += 1
                elif message_id in identifiers:
                    duplicate_ids += 1
                else:
                    identifiers.add(message_id)

                sender = canonical_address(record["sender"])
                if sender is None:
                    missing_sender += 1
                if not timestamp_is_parseable(record["sent_at"]):
                    timestamp_invalid += 1

                parsed: dict[str, list[str]] = {}
                malformed_primary_field = False
                for field in ("to_recipients", "cc_recipients", "bcc_recipients"):
                    try:
                        parsed[field] = recipient_list(record[field])
                    except ValueError:
                        malformed_fields[field] += 1
                        parsed[field] = []
                        malformed_primary_field |= field in {"to_recipients", "cc_recipients"}

                if sender is None or message_id is None:
                    excluded["missing_sender_or_id"] += 1
                    continue
                if malformed_primary_field:
                    excluded["malformed_to_or_cc"] += 1
                    continue
                head = list(dict.fromkeys(parsed["to_recipients"] + parsed["cc_recipients"]))
                if sender in head:
                    head = [address for address in head if address != sender]
                if not head:
                    excluded["empty_head_after_policy"] += 1
                    continue
                valid_candidate_events += 1

                if not build_events:
                    continue
                if message_id in seen_event_ids:
                    excluded["duplicate_id_after_first"] += 1
                    continue
                seen_event_ids.add(message_id)
                buffer.append(
                    {
                        "event_id": message_id,
                        "doc_id": str(record["doc_id"] or ""),
                        "message_index": str(record["message_index"] or ""),
                        "email_drop_id": str(record["email_drop_id"] or ""),
                        "release_batch": str(record["release_batch"] or ""),
                        "sent_at_raw": str(record["sent_at"] or ""),
                        "sender": sender,
                        "head": head,
                    }
                )
                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
                    buffer.clear()
        if writer is not None and buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
    finally:
        if writer is not None:
            writer.close()

    if records != EXPECTED_ROWS:
        if TEMP_OUTPUT.exists():
            TEMP_OUTPUT.unlink()
        raise SystemExit(
            f"STOP: unexpected Jmail row count.\nExpected: {EXPECTED_ROWS:,}\nFound:    {records:,}"
        )
    if build_events:
        TEMP_OUTPUT.replace(OUTPUT)

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset_id": "jmail_v1_2026_02",
        "records_read": records,
        "unique_nonempty_ids": len(identifiers),
        "duplicate_nonempty_ids": duplicate_ids,
        "missing_ids": missing_id,
        "missing_sender": missing_sender,
        "invalid_or_missing_timestamps": timestamp_invalid,
        "malformed_recipient_fields": dict(malformed_fields),
        "candidate_events_under_to_plus_cc_policy": valid_candidate_events,
        "restricted_event_output_built": build_events,
        "gate_record_used": str(GATE.relative_to(PROJECT_ROOT)) if gate_record else None,
        "analysis_status": (
            "restricted_native_events_built_after_approved_gate"
            if build_events
            else "audit_only_pending_admissibility_gate"
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""# Jmail v1 preparation audit

- Records read: `{records:,}`
- Unique nonempty message IDs: `{len(identifiers):,}`
- Duplicate nonempty message IDs: `{duplicate_ids:,}`
- Missing message IDs: `{missing_id:,}`
- Missing senders: `{missing_sender:,}`
- Invalid or missing timestamps: `{timestamp_invalid:,}`
- Candidate events under the To-plus-Cc policy: `{valid_candidate_events:,}`
- Restricted native events built: `{build_events}`

The structured source can support native-event reconstruction only after the explicit
provenance, licensing, entity-resolution, deduplication, and recipient-policy gate is
approved. Bcc remains excluded from the primary public-network policy.
""",
        encoding="utf-8",
    )
    print("Jmail v1 audit passed.")
    print(f"Records read: {records:,}.")
    print(f"Candidate events under To-plus-Cc policy: {valid_candidate_events:,}.")
    print(f"Restricted event output built: {build_events}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-restricted-events", action="store_true")
    args = parser.parse_args()
    audit_and_optionally_build(args.build_restricted_events)


if __name__ == "__main__":
    main()
