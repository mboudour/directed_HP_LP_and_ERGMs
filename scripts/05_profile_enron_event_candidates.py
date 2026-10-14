#!/usr/bin/env python3
"""Profile Enron event eligibility and recipient-header overlap without filtering."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "parsed_headers.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_event_candidate_profile.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_event_candidate_profile.md"


def count_bin(value: int) -> str:
    """Bin address-list cardinalities without exposing email addresses."""
    return str(value) if value <= 4 else "5+"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: normalized Enron table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/04_normalize_enron_headers.py first."
        )

    existing_outputs = [path for path in (SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            f"STOP: profile output already exists. This script will not overwrite it:\n  {rendered}"
        )

    record_count = 0
    timezone_aware_count = 0
    sender_cardinality = Counter()
    primary_recipient_cardinality = Counter()
    bcc_recipient_cardinality = Counter()
    address_issue_records = 0
    address_issue_total = 0

    to_cc_overlap_count = 0
    to_bcc_overlap_count = 0
    cc_bcc_overlap_count = 0
    both_cc_bcc_count = 0
    equal_nonempty_cc_bcc_count = 0

    sender_in_primary_head_count = 0
    strict_primary_candidate_count = 0
    strict_bcc_candidate_count = 0

    parquet_file = pq.ParquetFile(INPUT)

    for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
        for record in batch.to_pylist():
            record_count += 1

            sender = set(record["from_addresses"])
            to_recipients = set(record["to_addresses"])
            cc_recipients = set(record["cc_addresses"])
            bcc_recipients = set(record["bcc_addresses"])
            primary_head = to_recipients | cc_recipients

            date_is_usable = record["date_parse_status"] == "ok_timezone_aware"
            timezone_aware_count += date_is_usable

            sender_cardinality[count_bin(len(sender))] += 1
            primary_recipient_cardinality[count_bin(len(primary_head))] += 1
            bcc_recipient_cardinality[count_bin(len(bcc_recipients))] += 1

            issue_total = sum(
                int(record[f"{field}_parse_issue_count"]) for field in ("from", "to", "cc", "bcc")
            )
            address_issue_total += issue_total
            address_issue_records += issue_total > 0

            to_cc_overlap_count += bool(to_recipients & cc_recipients)
            to_bcc_overlap_count += bool(to_recipients & bcc_recipients)
            cc_bcc_overlap_count += bool(cc_recipients & bcc_recipients)

            if cc_recipients and bcc_recipients:
                both_cc_bcc_count += 1
                equal_nonempty_cc_bcc_count += cc_recipients == bcc_recipients

            sender_in_primary_head = bool(sender & primary_head)
            sender_in_primary_head_count += sender_in_primary_head

            strict_primary_candidate = (
                date_is_usable
                and len(sender) == 1
                and bool(primary_head)
                and not sender_in_primary_head
                and issue_total == 0
            )
            strict_primary_candidate_count += strict_primary_candidate

            strict_bcc_candidate = (
                date_is_usable
                and len(sender) == 1
                and bool(bcc_recipients)
                and not bool(sender & bcc_recipients)
                and issue_total == 0
            )
            strict_bcc_candidate_count += strict_bcc_candidate

    if record_count != EXPECTED_RECORDS:
        raise SystemExit(
            "STOP: unexpected normalized-table row count.\n"
            f"Expected: {EXPECTED_RECORDS:,}\n"
            f"Found:    {record_count:,}"
        )

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "records_profiled": record_count,
        "timezone_aware_dates": timezone_aware_count,
        "sender_cardinality_bins": dict(sorted(sender_cardinality.items())),
        "primary_to_cc_recipient_cardinality_bins": dict(
            sorted(primary_recipient_cardinality.items())
        ),
        "bcc_recipient_cardinality_bins": dict(sorted(bcc_recipient_cardinality.items())),
        "address_parse_issues": {
            "records_with_one_or_more_issues": address_issue_records,
            "issues_total": address_issue_total,
        },
        "recipient_header_overlap": {
            "to_cc_any_overlap": to_cc_overlap_count,
            "to_bcc_any_overlap": to_bcc_overlap_count,
            "cc_bcc_any_overlap": cc_bcc_overlap_count,
            "messages_with_both_cc_and_bcc": both_cc_bcc_count,
            "cc_bcc_exactly_equal_when_both_nonempty": equal_nonempty_cc_bcc_count,
        },
        "sender_in_primary_to_cc_head": sender_in_primary_head_count,
        "strict_primary_to_cc_event_candidates": strict_primary_candidate_count,
        "strict_bcc_event_candidates": strict_bcc_candidate_count,
        "candidate_definition": (
            "A strict primary candidate has a timezone-aware timestamp, exactly "
            "one syntactically usable sender, one or more To-or-Cc recipients, "
            "no sender in its own primary recipient set, and no address parsing "
            "issue. This is an audit count only; it performs no filtering."
        ),
        "policy_status": {
            "deduplication": "not performed",
            "alias_resolution": "not performed",
            "custodian_node_mapping": "not performed",
            "primary_recipient_policy": "To plus Cc, pending this profile review",
            "bcc_policy": "kept separate, pending this profile review",
        },
        "next_processing_step": (
            "Review aggregate recipient overlap and candidate counts, then freeze "
            "the header policy before constructing native-event records."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        f"""# Enron event-candidate header audit

## Scope

This is a descriptive profile only. It does not create, exclude, merge, or deduplicate
events. It does not resolve email aliases or restrict the actor set to custodian mailboxes.

- Records profiled: `{record_count:,}`
- Timezone-aware timestamps: `{timezone_aware_count:,}`
- Strict primary To-plus-Cc candidates: `{strict_primary_candidate_count:,}`
- Strict Bcc candidates: `{strict_bcc_candidate_count:,}`

A strict candidate is defined only for audit purposes: exactly one parsed sender, a
timezone-aware date, at least one recipient, no sender-recipient self-overlap, and no
address parsing issue.

## Recipient-header overlap

| Aggregate check | Messages |
|---|---:|
| To and Cc share at least one recipient | {to_cc_overlap_count:,} |
| To and Bcc share at least one recipient | {to_bcc_overlap_count:,} |
| Cc and Bcc share at least one recipient | {cc_bcc_overlap_count:,} |
| Both Cc and Bcc are non-empty | {both_cc_bcc_count:,} |
| Non-empty Cc and Bcc recipient sets are exactly equal | {equal_nonempty_cc_bcc_count:,} |

No recipient header is silently discarded here. The primary analysis policy remains
provisional: To plus Cc, with Bcc excluded from the public primary network and retained
as a separately documented sensitivity field.

## Additional checks

| Check | Messages |
|---|---:|
| Sender appears in its own To-plus-Cc recipient set | {sender_in_primary_head_count:,} |
| Records with one or more address parsing issues | {address_issue_records:,} |
| Total address parsing issues | {address_issue_total:,} |
""",
        encoding="utf-8",
    )

    print(f"Enron event-candidate profile passed: {record_count:,} records.")
    print(f"Timezone-aware timestamps: {timezone_aware_count:,}.")
    print(f"Strict To-plus-Cc candidates: {strict_primary_candidate_count:,}.")
    print(f"Strict Bcc candidates: {strict_bcc_candidate_count:,}.")
    print(f"Messages with both Cc and Bcc: {both_cc_bcc_count:,}.")
    print(f"Messages where non-empty Cc and Bcc sets are equal: {equal_nonempty_cc_bcc_count:,}.")
    print(f"Messages with To/Cc overlap: {to_cc_overlap_count:,}.")
    print(f"Messages with Cc/Bcc overlap: {cc_bcc_overlap_count:,}.")
    print(f"Messages with sender in To-plus-Cc recipients: {sender_in_primary_head_count:,}.")
    print(f"Address-issue records: {address_issue_records:,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
