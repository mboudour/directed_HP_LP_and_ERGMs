#!/usr/bin/env python3
"""Profile Enron header extraction before defining deduplication rules."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

BATCH_SIZE = 25_000
MAX_ANOMALY_ROWS = 500

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_header_profile.json"
ANOMALIES = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "enron_20150507"
    / "audits"
    / "enron_20150507_header_anomaly_register.csv"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_header_profile.md"

HEADER_FIELDS = (
    "message_id_raw",
    "date_raw",
    "from_raw",
    "to_raw",
    "cc_raw",
    "bcc_raw",
)


def duplicate_summary(groups: dict[str, int]) -> dict[str, int]:
    """Summarize repeated values without retaining message/header content."""
    repeated_counts = [count for count in groups.values() if count > 1]

    return {
        "unique_values": len(groups),
        "duplicate_groups": len(repeated_counts),
        "records_in_duplicate_groups": sum(repeated_counts),
        "extra_records_beyond_first": sum(count - 1 for count in repeated_counts),
        "largest_group_size": max(repeated_counts, default=1),
    }


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: header table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/02_extract_enron_headers.py first."
        )

    existing_outputs = [path for path in (SUMMARY, ANOMALIES, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            f"STOP: profile output already exists. This script will not overwrite it:\n  {rendered}"
        )

    parquet_file = pq.ParquetFile(INPUT)

    record_count = 0
    missing_counts: Counter[str] = Counter()
    missingness_patterns: Counter[tuple[str, ...]] = Counter()
    raw_hash_counts: defaultdict[str, int] = defaultdict(int)
    message_id_counts: defaultdict[str, int] = defaultdict(int)

    parse_error_count = 0
    parser_defect_total = 0
    truncated_header_count = 0
    unterminated_header_count = 0
    anomaly_total = 0
    anomaly_rows: list[dict[str, object]] = []

    for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
        for record in batch.to_pylist():
            record_count += 1

            missing_fields = tuple(field for field in HEADER_FIELDS if record[field] is None)
            missingness_patterns[missing_fields] += 1

            for field in missing_fields:
                missing_counts[field] += 1

            raw_hash_counts[str(record["raw_sha256"])] += 1

            message_id = record["message_id_raw"]
            if message_id is not None:
                message_id_counts[str(message_id)] += 1

            parse_error_count += record["parse_error"] is not None
            parser_defect_total += int(record["parser_defect_count"])
            truncated_header_count += bool(record["header_truncated"])
            unterminated_header_count += not bool(record["header_terminated"])

            anomalous = (
                record["parse_error"] is not None
                or bool(record["header_truncated"])
                or not bool(record["header_terminated"])
                or record["message_id_raw"] is None
                or record["date_raw"] is None
                or record["from_raw"] is None
            )

            if anomalous:
                anomaly_total += 1

                if len(anomaly_rows) < MAX_ANOMALY_ROWS:
                    anomaly_rows.append(
                        {
                            "source_path": record["source_path"],
                            "custodian_mailbox": record["custodian_mailbox"],
                            "message_bytes": record["message_bytes"],
                            "raw_sha256": record["raw_sha256"],
                            "has_message_id": record["message_id_raw"] is not None,
                            "has_date": record["date_raw"] is not None,
                            "has_from": record["from_raw"] is not None,
                            "has_to": record["to_raw"] is not None,
                            "has_cc": record["cc_raw"] is not None,
                            "has_bcc": record["bcc_raw"] is not None,
                            "header_truncated": record["header_truncated"],
                            "header_terminated": record["header_terminated"],
                            "parser_defect_count": record["parser_defect_count"],
                            "parse_error": record["parse_error"] or "",
                        }
                    )

    if record_count != 517_401:
        raise SystemExit(
            "STOP: unexpected header-table row count.\n"
            f"Expected: 517,401\nFound:    {record_count:,}"
        )

    raw_duplicates = duplicate_summary(raw_hash_counts)
    message_id_duplicates = duplicate_summary(message_id_counts)

    patterns = [
        {
            "missing_fields": list(pattern),
            "records": count,
        }
        for pattern, count in missingness_patterns.most_common()
    ]

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "records_profiled": record_count,
        "missing_header_counts": dict(sorted(missing_counts.items())),
        "missingness_patterns": patterns,
        "raw_sha256_duplicates": raw_duplicates,
        "message_id_duplicates_nonmissing_only": message_id_duplicates,
        "parse_error_count": parse_error_count,
        "parser_defect_total": parser_defect_total,
        "header_truncated_count": truncated_header_count,
        "header_unterminated_count": unterminated_header_count,
        "anomaly_records_total": anomaly_total,
        "anomaly_rows_written": len(anomaly_rows),
        "anomaly_row_limit": MAX_ANOMALY_ROWS,
        "interpretation": (
            "Raw SHA-256 duplicates indicate byte-identical message files. "
            "Repeated Message-ID values are recorded separately because they can "
            "represent copies, legitimate retransmissions, or identifier reuse; "
            "they are not automatically deduplicated."
        ),
        "next_processing_step": (
            "Define and implement an explicit message-level deduplication policy "
            "after inspecting these aggregate results."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    anomaly_fields = [
        "source_path",
        "custodian_mailbox",
        "message_bytes",
        "raw_sha256",
        "has_message_id",
        "has_date",
        "has_from",
        "has_to",
        "has_cc",
        "has_bcc",
        "header_truncated",
        "header_terminated",
        "parser_defect_count",
        "parse_error",
    ]

    with ANOMALIES.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=anomaly_fields)
        writer.writeheader()
        writer.writerows(anomaly_rows)

    top_patterns = "\n".join(
        f"| {', '.join(item['missing_fields']) if item['missing_fields'] else 'none'} "
        f"| {item['records']:,} |"
        for item in patterns[:10]
    )

    REPORT.write_text(
        f"""# Enron header-profile audit

## Scope

This audit profiles the header-only intermediate table. It does not remove, merge, or
alter messages. It does not retain any message body or header content in the anomaly
register.

- Input records: `{record_count:,}`
- Header parse errors: `{parse_error_count:,}`
- Total parser defects: `{parser_defect_total:,}`
- Truncated headers: `{truncated_header_count:,}`
- Unterminated headers: `{unterminated_header_count:,}`
- Anomalous records: `{anomaly_total:,}`

## Duplicate indicators — not yet a deduplication decision

### Exact raw SHA-256

- Unique values: `{raw_duplicates["unique_values"]:,}`
- Duplicate groups: `{raw_duplicates["duplicate_groups"]:,}`
- Records in duplicate groups: `{raw_duplicates["records_in_duplicate_groups"]:,}`
- Extra records beyond the first copy:
  `{raw_duplicates["extra_records_beyond_first"]:,}`

### Non-missing Message-ID

- Unique values: `{message_id_duplicates["unique_values"]:,}`
- Duplicate groups: `{message_id_duplicates["duplicate_groups"]:,}`
- Records in duplicate groups:
  `{message_id_duplicates["records_in_duplicate_groups"]:,}`
- Extra records beyond the first copy:
  `{message_id_duplicates["extra_records_beyond_first"]:,}`

Exact raw SHA-256 duplicates are byte-identical raw message files. Repeated
`Message-ID` values are reported separately because they can indicate copies,
retransmissions, or reuse; they will not be removed without an explicit policy.

## Header-missingness patterns

| Missing fields | Records |
|---|---:|
{top_patterns}

## Privacy-preserving anomaly register

The anomaly register under `data/interim/enron_20150507/audits/` contains source paths,
sizes, hashes, and parsing flags only. It contains no message body, address, date, or
subject content.
""",
        encoding="utf-8",
    )

    print(f"Enron header profile passed: {record_count:,} records.")
    print(
        "Exact raw duplicates: "
        f"{raw_duplicates['duplicate_groups']:,} groups; "
        f"{raw_duplicates['records_in_duplicate_groups']:,} records; "
        f"{raw_duplicates['extra_records_beyond_first']:,} extra copies."
    )
    print(
        "Duplicate Message-ID groups: "
        f"{message_id_duplicates['duplicate_groups']:,}; "
        f"{message_id_duplicates['records_in_duplicate_groups']:,} records."
    )
    print(f"Anomalous records: {anomaly_total:,}.")
    print(f"Header parse errors: {parse_error_count:,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Anomaly register: {ANOMALIES.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
