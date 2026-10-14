#!/usr/bin/env python3
"""Determine whether Enron Bcc values are already duplicated in raw extracted headers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_bcc_audit.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_bcc_audit.md"


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: Enron extracted-header table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/02_extract_enron_headers.py first."
        )

    existing_outputs = [path for path in (SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: Bcc audit output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    counts: Counter[str] = Counter()
    record_count = 0

    parquet_file = pq.ParquetFile(INPUT)

    for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["cc_raw", "bcc_raw"],
    ):
        for record in batch.to_pylist():
            record_count += 1

            cc_value = record["cc_raw"]
            bcc_value = record["bcc_raw"]

            if cc_value is not None:
                counts["cc_nonempty"] += 1

            if bcc_value is not None:
                counts["bcc_nonempty"] += 1

            if cc_value is not None and bcc_value is not None:
                counts["both_nonempty"] += 1
                counts["exact_cleaned_raw_equal"] += cc_value == bcc_value
            elif cc_value is not None:
                counts["cc_only"] += 1
            elif bcc_value is not None:
                counts["bcc_only"] += 1

    if record_count != EXPECTED_RECORDS:
        raise SystemExit(
            "STOP: unexpected extracted-header row count.\n"
            f"Expected: {EXPECTED_RECORDS:,}\n"
            f"Found:    {record_count:,}"
        )

    all_bcc_duplicates_cc = (
        counts["bcc_nonempty"] > 0
        and counts["bcc_nonempty"] == counts["both_nonempty"]
        and counts["bcc_nonempty"] == counts["exact_cleaned_raw_equal"]
    )

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "records_profiled": record_count,
        "cc_nonempty": counts["cc_nonempty"],
        "bcc_nonempty": counts["bcc_nonempty"],
        "both_cc_and_bcc_nonempty": counts["both_nonempty"],
        "cc_only": counts["cc_only"],
        "bcc_only": counts["bcc_only"],
        "exact_cleaned_raw_cc_bcc_equal_when_both_nonempty": (counts["exact_cleaned_raw_equal"]),
        "all_nonempty_bcc_values_duplicate_cc": all_bcc_duplicates_cc,
        "interpretation": (
            "The fields compared here are the extracted Cc and Bcc header values "
            "before address parsing. Equality therefore cannot have been introduced "
            "by the syntactic address normalizer."
        ),
        "policy_implication": (
            "If all_nonempty_bcc_values_duplicate_cc is true, Bcc is not an "
            "independent information field in this archive and is excluded from "
            "the primary and sensitivity event definitions."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    verdict = (
        "**Confirmed: every non-empty extracted Bcc header is exactly equal to its "
        "extracted Cc header.**"
        if all_bcc_duplicates_cc
        else ("**Not confirmed: at least some extracted Bcc headers differ from Cc.**")
    )

    REPORT.write_text(
        f"""# Enron Bcc-header audit

## Result

{verdict}

## Aggregate counts

| Header condition | Records |
|---|---:|
| Cc non-empty | {counts["cc_nonempty"]:,} |
| Bcc non-empty | {counts["bcc_nonempty"]:,} |
| Both Cc and Bcc non-empty | {counts["both_nonempty"]:,} |
| Cc only | {counts["cc_only"]:,} |
| Bcc only | {counts["bcc_only"]:,} |
| Both non-empty and exactly equal | {counts["exact_cleaned_raw_equal"]:,} |

## Interpretation

This check uses `cc_raw` and `bcc_raw` from the extracted-header table, before address
normalization. Therefore, exact equality cannot have been created by lowercase conversion,
within-header deduplication, or recipient-set construction.

If confirmed, Bcc is a corpus-export duplicate of Cc rather than an independent recipient
field. The Enron primary event policy is then one sender and the deduplicated union of To
and Cc recipients. Bcc is excluded rather than presented as a misleading sensitivity
analysis.
""",
        encoding="utf-8",
    )

    print(f"Enron Bcc audit passed: {record_count:,} records.")
    print(f"Cc non-empty: {counts['cc_nonempty']:,}.")
    print(f"Bcc non-empty: {counts['bcc_nonempty']:,}.")
    print(f"Both Cc and Bcc non-empty: {counts['both_nonempty']:,}.")
    print(
        "Both non-empty and exactly equal before address parsing: "
        f"{counts['exact_cleaned_raw_equal']:,}."
    )
    print(f"Cc-only records: {counts['cc_only']:,}.")
    print(f"Bcc-only records: {counts['bcc_only']:,}.")
    print(f"All Bcc values duplicate Cc: {all_bcc_duplicates_cc}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
