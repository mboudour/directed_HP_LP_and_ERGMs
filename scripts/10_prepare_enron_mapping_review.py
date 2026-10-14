#!/usr/bin/env python3
"""Prepare a local review bundle for ambiguous Enron custodian-address evidence."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_CUSTODIANS = 150
SUPPORT_THRESHOLD = 0.90
TOP_CANDIDATES_PER_CUSTODIAN = 3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "enron_20150507"
    / "audits"
    / "enron_20150507_custodian_address_evidence.csv"
)
HEADERS = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
LOCAL_REVIEW = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "enron_20150507"
    / "audits"
    / "enron_20150507_custodian_mapping_review.csv"
)
SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_custodian_mapping_review_summary.json"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_custodian_mapping_review.md"


def review_reasons(
    top_row: dict[str, str] | None,
    colliding_addresses: set[str],
) -> list[str]:
    """Return documented reasons that a custodian requires manual review."""
    if top_row is None:
        return ["no_rank_one_candidate"]

    reasons: list[str] = []

    if float(top_row["support_share"]) < SUPPORT_THRESHOLD:
        reasons.append("support_below_90_percent")

    if top_row["candidate_sender_address"] in colliding_addresses:
        reasons.append("top_address_shared_across_custodians")

    return reasons


def main() -> None:
    if not EVIDENCE.is_file():
        raise SystemExit(
            "STOP: custodian-address evidence table not found:\n"
            f"  {EVIDENCE}\n"
            "Run scripts/08_audit_enron_custodian_address_evidence.py first."
        )

    if not HEADERS.is_file():
        raise SystemExit(
            "STOP: extracted Enron header table not found:\n"
            f"  {HEADERS}\n"
            "Run scripts/02_extract_enron_headers.py first."
        )

    existing_outputs = [path for path in (LOCAL_REVIEW, SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: mapping-review output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    rows_by_custodian: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

    with EVIDENCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["rank"]) <= TOP_CANDIDATES_PER_CUSTODIAN:
                rows_by_custodian[row["custodian_mailbox"]].append(row)

    top_rows = {
        custodian: next(
            (row for row in rows if int(row["rank"]) == 1),
            None,
        )
        for custodian, rows in rows_by_custodian.items()
    }

    address_to_custodians: defaultdict[str, list[str]] = defaultdict(list)

    for custodian, row in top_rows.items():
        if row is not None:
            address_to_custodians[row["candidate_sender_address"]].append(custodian)

    colliding_addresses = {
        address for address, custodians in address_to_custodians.items() if len(custodians) > 1
    }

    source_custodians: set[str] = set()
    parquet_file = pq.ParquetFile(HEADERS)

    for batch in parquet_file.iter_batches(columns=["custodian_mailbox"]):
        source_custodians.update(str(value) for value in batch.column(0).to_pylist())

    if len(source_custodians) != EXPECTED_CUSTODIANS:
        raise SystemExit(
            "STOP: unexpected number of custodian mailboxes in the header table.\n"
            f"Expected: {EXPECTED_CUSTODIANS}\n"
            f"Found:    {len(source_custodians)}"
        )

    unknown_evidence_custodians = sorted(set(rows_by_custodian) - source_custodians)
    if unknown_evidence_custodians:
        raise SystemExit(
            "STOP: the evidence table contains custodians absent from the header table."
        )

    review_rows: list[dict[str, object]] = []
    automatic_high_confidence = 0
    requires_review = 0
    no_rank_one_candidate = 0
    support_below_threshold = 0
    shared_top_address = 0

    for custodian in sorted(source_custodians):
        top_row = top_rows.get(custodian)
        reasons = review_reasons(top_row, colliding_addresses)

        if not reasons:
            automatic_high_confidence += 1
            continue

        requires_review += 1
        no_rank_one_candidate += reasons == ["no_rank_one_candidate"]
        support_below_threshold += "support_below_90_percent" in reasons
        shared_top_address += "top_address_shared_across_custodians" in reasons

        if top_row is None:
            review_rows.append(
                {
                    "custodian_mailbox": custodian,
                    "review_reasons": ";".join(reasons),
                    "rank": "",
                    "candidate_sender_address": "",
                    "supporting_sent_like_messages": "",
                    "eligible_sent_like_messages": "",
                    "support_share": "",
                    "second_rank_supporting_messages": "",
                }
            )
            continue

        for row in rows_by_custodian[custodian]:
            review_rows.append(
                {
                    "custodian_mailbox": custodian,
                    "review_reasons": ";".join(reasons),
                    "rank": row["rank"],
                    "candidate_sender_address": (row["candidate_sender_address"]),
                    "supporting_sent_like_messages": (row["supporting_sent_like_messages"]),
                    "eligible_sent_like_messages": (row["eligible_sent_like_messages"]),
                    "support_share": row["support_share"],
                    "second_rank_supporting_messages": (row["second_rank_supporting_messages"]),
                }
            )

    summary = {
        "dataset_id": "enron_20150507",
        "support_threshold": SUPPORT_THRESHOLD,
        "source_custodian_mailboxes": len(source_custodians),
        "automatic_high_confidence_candidates": automatic_high_confidence,
        "custodians_requiring_review": requires_review,
        "review_reason_counts": {
            "no_rank_one_candidate": no_rank_one_candidate,
            "support_below_90_percent": support_below_threshold,
            "top_address_shared_across_custodians": shared_top_address,
        },
        "local_review_table_rows": len(review_rows),
        "mapping_status": (
            "No mapping is assigned by this script. The local review table is "
            "an evidence bundle, not a final identity map."
        ),
    }

    LOCAL_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    review_fields = [
        "custodian_mailbox",
        "review_reasons",
        "rank",
        "candidate_sender_address",
        "supporting_sent_like_messages",
        "eligible_sent_like_messages",
        "support_share",
        "second_rank_supporting_messages",
    ]

    with LOCAL_REVIEW.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=review_fields,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(review_rows)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        f"""# Enron custodian-mapping review bundle

## Scope

This script prepares a local review table for ambiguous custodian-address evidence. It
assigns no address to a custodian, filters no message, and creates no event table.

- Source custodian mailboxes: `{len(source_custodians):,}`
- Provisionally high-confidence candidates: `{automatic_high_confidence:,}`
- Custodians requiring review: `{requires_review:,}`
- No rank-one candidate: `{no_rank_one_candidate:,}`
- Top support below 90%: `{support_below_threshold:,}`
- Top address shared by multiple custodians: `{shared_top_address:,}`

## Local review table

The local-only table is written to
`data/interim/enron_20150507/audits/enron_20150507_custodian_mapping_review.csv`.
It includes the top three candidate addresses and their support for each flagged
custodian. It remains ignored by Git because it contains email addresses.

## Review rule

A custodian is included in this review bundle if it has no rank-one candidate, has
rank-one support below `{SUPPORT_THRESHOLD:.0%}`, or shares its rank-one address with
another custodian. The threshold is an audit triage rule only; it is not a final
identity-resolution decision.
""",
        encoding="utf-8",
    )

    print("Enron custodian-mapping review bundle passed.")
    print(f"Source custodian mailboxes: {len(source_custodians):,}.")
    print(f"Provisionally high-confidence candidates: {automatic_high_confidence:,}.")
    print(f"Custodians requiring review: {requires_review:,}.")
    print(f"No rank-one candidate: {no_rank_one_candidate:,}.")
    print(f"Top support below 90%: {support_below_threshold:,}.")
    print(f"Shared top address: {shared_top_address:,}.")
    print(f"Local review table: {LOCAL_REVIEW.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
