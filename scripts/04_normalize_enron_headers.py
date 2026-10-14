#!/usr/bin/env python3
"""Syntactically normalize Enron header fields without filtering any messages."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
OUTPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "parsed_headers.parquet"
TEMP_OUTPUT = OUTPUT.with_suffix(".parquet.tmp")
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_parsed_header_summary.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_parsed_headers.md"

SCHEMA = pa.schema(
    [
        pa.field("source_path", pa.string()),
        pa.field("custodian_mailbox", pa.string()),
        pa.field("raw_sha256", pa.string()),
        pa.field("message_id_raw", pa.string()),
        pa.field("sent_at_utc", pa.timestamp("us", tz="UTC")),
        pa.field("sent_at_naive", pa.timestamp("us")),
        pa.field("date_parse_status", pa.string()),
        pa.field("date_utc_offset_minutes", pa.int32()),
        pa.field("from_addresses", pa.list_(pa.string())),
        pa.field("to_addresses", pa.list_(pa.string())),
        pa.field("cc_addresses", pa.list_(pa.string())),
        pa.field("bcc_addresses", pa.list_(pa.string())),
        pa.field("from_address_count", pa.int16()),
        pa.field("to_address_count", pa.int16()),
        pa.field("cc_address_count", pa.int16()),
        pa.field("bcc_address_count", pa.int16()),
        pa.field("from_parse_issue_count", pa.int16()),
        pa.field("to_parse_issue_count", pa.int16()),
        pa.field("cc_parse_issue_count", pa.int16()),
        pa.field("bcc_parse_issue_count", pa.int16()),
    ]
)


def parse_addresses(value: str | None) -> tuple[list[str], int]:
    """
    Extract syntactically usable addresses from one header.

    This performs only lowercase normalization and removes repeated addresses
    within the same header. It does not resolve aliases or treat two distinct
    addresses as the same actor.
    """
    if value is None:
        return [], 0

    valid_addresses: list[str] = []
    issue_count = 0

    try:
        try:
            candidates = getaddresses([value], strict=False)
        except TypeError:
            candidates = getaddresses([value])
    except Exception:
        return [], 1

    for _, address in candidates:
        canonical = address.strip().casefold()
        local, separator, domain = canonical.rpartition("@")

        if not separator or not local or not domain or " " in canonical:
            if canonical:
                issue_count += 1
            continue

        valid_addresses.append(canonical)

    return list(dict.fromkeys(valid_addresses)), issue_count


def parse_date(
    value: str | None,
) -> tuple[object | None, object | None, str, int | None]:
    """
    Parse a Date header without inventing a timezone.

    Timezone-aware dates are converted to UTC. A date without timezone metadata
    is retained as a naive datetime and explicitly marked as timezone_missing.
    """
    if value is None:
        return None, None, "missing", None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None, None, "invalid", None

    if parsed is None:
        return None, None, "invalid", None

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, parsed, "timezone_missing", None

    offset_minutes = int(parsed.utcoffset().total_seconds() // 60)

    return (
        parsed.astimezone(UTC),
        None,
        "ok_timezone_aware",
        offset_minutes,
    )


def normalize_record(record: dict[str, object]) -> dict[str, object]:
    """Create one parsed-header record without excluding or merging messages."""
    sent_at_utc, sent_at_naive, date_status, offset_minutes = parse_date(record["date_raw"])

    from_addresses, from_issues = parse_addresses(record["from_raw"])
    to_addresses, to_issues = parse_addresses(record["to_raw"])
    cc_addresses, cc_issues = parse_addresses(record["cc_raw"])
    bcc_addresses, bcc_issues = parse_addresses(record["bcc_raw"])

    return {
        "source_path": record["source_path"],
        "custodian_mailbox": record["custodian_mailbox"],
        "raw_sha256": record["raw_sha256"],
        "message_id_raw": record["message_id_raw"],
        "sent_at_utc": sent_at_utc,
        "sent_at_naive": sent_at_naive,
        "date_parse_status": date_status,
        "date_utc_offset_minutes": offset_minutes,
        "from_addresses": from_addresses,
        "to_addresses": to_addresses,
        "cc_addresses": cc_addresses,
        "bcc_addresses": bcc_addresses,
        "from_address_count": len(from_addresses),
        "to_address_count": len(to_addresses),
        "cc_address_count": len(cc_addresses),
        "bcc_address_count": len(bcc_addresses),
        "from_parse_issue_count": from_issues,
        "to_parse_issue_count": to_issues,
        "cc_parse_issue_count": cc_issues,
        "bcc_parse_issue_count": bcc_issues,
    }


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: extracted Enron header table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/02_extract_enron_headers.py first."
        )

    existing_outputs = [path for path in (OUTPUT, TEMP_OUTPUT, SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: normalization output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    record_count = 0
    date_status_counts: Counter[str] = Counter()
    sender_count_distribution: Counter[int] = Counter()
    to_count_distribution: Counter[int] = Counter()
    cc_count_distribution: Counter[int] = Counter()
    bcc_count_distribution: Counter[int] = Counter()
    issue_counts: Counter[str] = Counter()
    valid_utc_times: list[object] = []
    buffer: list[dict[str, object]] = []

    try:
        with pq.ParquetWriter(TEMP_OUTPUT, SCHEMA, compression="zstd") as writer:
            parquet_file = pq.ParquetFile(INPUT)

            for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
                for raw_record in batch.to_pylist():
                    record = normalize_record(raw_record)
                    buffer.append(record)
                    record_count += 1

                    date_status_counts[str(record["date_parse_status"])] += 1
                    sender_count_distribution[int(record["from_address_count"])] += 1
                    to_count_distribution[int(record["to_address_count"])] += 1
                    cc_count_distribution[int(record["cc_address_count"])] += 1
                    bcc_count_distribution[int(record["bcc_address_count"])] += 1

                    for field in ("from", "to", "cc", "bcc"):
                        issue_counts[field] += int(record[f"{field}_parse_issue_count"])

                    if record["sent_at_utc"] is not None:
                        valid_utc_times.append(record["sent_at_utc"])

                if buffer:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                    buffer.clear()

        if record_count != EXPECTED_RECORDS:
            raise SystemExit(
                "STOP: unexpected normalized-record count.\n"
                f"Expected: {EXPECTED_RECORDS:,}\n"
                f"Found:    {record_count:,}"
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
        "records_written": record_count,
        "date_parse_status_counts": dict(sorted(date_status_counts.items())),
        "sender_address_count_distribution": dict(sorted(sender_count_distribution.items())),
        "to_address_count_distribution": dict(sorted(to_count_distribution.items())),
        "cc_address_count_distribution": dict(sorted(cc_count_distribution.items())),
        "bcc_address_count_distribution": dict(sorted(bcc_count_distribution.items())),
        "address_parse_issue_counts": dict(sorted(issue_counts.items())),
        "temporal_span_utc": {
            "minimum": min(valid_utc_times).isoformat() if valid_utc_times else None,
            "maximum": max(valid_utc_times).isoformat() if valid_utc_times else None,
        },
        "normalization_policy": {
            "address_normalization": "strip whitespace and lowercase only",
            "addresses_deduplicated_within_header": True,
            "alias_resolution": "not performed",
            "record_deduplication": "not performed",
            "recipient_policy": "not selected; To, Cc, and Bcc remain separate",
            "timezone_free_dates": "retained as naive datetimes; not assigned UTC",
        },
        "next_processing_step": (
            "Inspect address and temporal profiles, then define the custodian and "
            "recipient policy before constructing event candidates."
        ),
    }

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        f"""# Enron parsed-header audit

## Scope

This is a syntactic normalization stage. It keeps all `{record_count:,}` source records
and performs no message deduplication, alias resolution, recipient-policy choice, or event
construction.

- Input: `{INPUT.relative_to(PROJECT_ROOT)}`
- Output: `{OUTPUT.relative_to(PROJECT_ROOT)}`

## Date parsing

| Status | Records |
|---|---:|
| Timezone-aware and converted to UTC | {date_status_counts["ok_timezone_aware"]:,} |
| Timezone missing; retained as naive datetime | {date_status_counts["timezone_missing"]:,} |
| Invalid date header | {date_status_counts["invalid"]:,} |
| Missing date header | {date_status_counts["missing"]:,} |

Earliest timezone-aware timestamp: `{summary["temporal_span_utc"]["minimum"]}`
Latest timezone-aware timestamp: `{summary["temporal_span_utc"]["maximum"]}`

## Address parsing

| Header | Messages with one or more usable addresses | Parsing issues |
|---|---:|---:|
| From | {record_count - sender_count_distribution[0]:,} | {issue_counts["from"]:,} |
| To | {record_count - to_count_distribution[0]:,} | {issue_counts["to"]:,} |
| Cc | {record_count - cc_count_distribution[0]:,} | {issue_counts["cc"]:,} |
| Bcc | {record_count - bcc_count_distribution[0]:,} | {issue_counts["bcc"]:,} |

Address parsing only lowercases syntactically usable addresses. It does not map aliases,
mailboxes, or organizations to actors. To, Cc, and Bcc are still separate because the
recipient policy has not yet been chosen.
""",
        encoding="utf-8",
    )

    print("Enron header normalization passed.")
    print(f"records written: {record_count:,}")
    print(f"timezone-aware dates: {date_status_counts['ok_timezone_aware']:,}")
    print(f"timezone-free dates: {date_status_counts['timezone_missing']:,}")
    print(f"invalid dates: {date_status_counts['invalid']:,}")
    print(f"missing dates: {date_status_counts['missing']:,}")
    print(f"messages with valid sender address: {record_count - sender_count_distribution[0]:,}")
    print(f"messages with valid To recipient: {record_count - to_count_distribution[0]:,}")
    print(f"messages with valid Cc recipient: {record_count - cc_count_distribution[0]:,}")
    print(f"messages with valid Bcc recipient: {record_count - bcc_count_distribution[0]:,}")
    print(f"address parse issues: {sum(issue_counts.values()):,}")
    print(f"normalized table: {OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
