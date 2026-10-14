#!/usr/bin/env python3
"""Audit evidence for Enron custodian-mailbox to sender-address mapping."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000
SENT_FOLDER_TOKENS = {"sent", "sentitem", "sentitems", "sentmail"}
TOP_CANDIDATES_PER_CUSTODIAN = 3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "parsed_headers.parquet"
DETAILS = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "enron_20150507"
    / "audits"
    / "enron_20150507_custodian_address_evidence.csv"
)
SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_custodian_address_evidence_summary.json"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_custodian_address_evidence.md"


def normalize_folder_token(value: str) -> str:
    """Normalize one maildir-folder component for taxonomy matching."""
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def source_path_parts(source_path: str) -> tuple[str, list[str]]:
    """Return the maildir custodian and nested folder components."""
    parts = source_path.split("/")

    if len(parts) < 3 or parts[0] != "maildir":
        raise ValueError(f"Unexpected maildir path: {source_path}")

    return parts[1], parts[2:-1]


def is_sent_like(source_path: str) -> bool:
    """Identify a sent-like path using the audited provisional token rule."""
    _, folder_components = source_path_parts(source_path)

    return any(
        normalize_folder_token(component) in SENT_FOLDER_TOKENS for component in folder_components
    )


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: normalized Enron table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/04_normalize_enron_headers.py first."
        )

    existing_outputs = [path for path in (DETAILS, SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: custodian-evidence output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    record_count = 0
    custodians: set[str] = set()
    sent_like_counts: Counter[str] = Counter()
    eligible_evidence_counts: Counter[str] = Counter()
    ineligible_sent_like_counts: Counter[str] = Counter()
    address_votes: defaultdict[str, Counter[str]] = defaultdict(Counter)

    parquet_file = pq.ParquetFile(INPUT)

    for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=[
            "source_path",
            "from_addresses",
            "from_parse_issue_count",
        ],
    ):
        for record in batch.to_pylist():
            record_count += 1

            source_path = str(record["source_path"])
            custodian, _ = source_path_parts(source_path)
            custodians.add(custodian)

            if not is_sent_like(source_path):
                continue

            sent_like_counts[custodian] += 1
            sender_addresses = record["from_addresses"]

            if len(sender_addresses) == 1 and int(record["from_parse_issue_count"]) == 0:
                sender_address = str(sender_addresses[0])
                address_votes[custodian][sender_address] += 1
                eligible_evidence_counts[custodian] += 1
            else:
                ineligible_sent_like_counts[custodian] += 1

    if record_count != EXPECTED_RECORDS:
        raise SystemExit(
            "STOP: unexpected normalized-table row count.\n"
            f"Expected: {EXPECTED_RECORDS:,}\n"
            f"Found:    {record_count:,}"
        )

    detail_rows: list[dict[str, object]] = []
    custodians_with_unique_top = 0
    custodians_with_tied_top = 0
    custodians_with_evidence = 0
    high_support_top_candidates = 0

    for custodian in sorted(custodians):
        ranked_candidates = address_votes[custodian].most_common()
        eligible_count = eligible_evidence_counts[custodian]

        if ranked_candidates:
            custodians_with_evidence += 1

        top_count = ranked_candidates[0][1] if ranked_candidates else 0
        second_count = ranked_candidates[1][1] if len(ranked_candidates) > 1 else 0
        unique_top = bool(ranked_candidates) and top_count > second_count
        top_share = top_count / eligible_count if eligible_count else 0.0

        custodians_with_unique_top += unique_top
        custodians_with_tied_top += bool(ranked_candidates) and not unique_top
        high_support_top_candidates += unique_top and top_share >= 0.90

        for rank, (address, support_count) in enumerate(
            ranked_candidates[:TOP_CANDIDATES_PER_CUSTODIAN],
            start=1,
        ):
            detail_rows.append(
                {
                    "custodian_mailbox": custodian,
                    "rank": rank,
                    "candidate_sender_address": address,
                    "supporting_sent_like_messages": support_count,
                    "eligible_sent_like_messages": eligible_count,
                    "support_share": round(support_count / eligible_count, 6),
                    "unique_top_candidate": unique_top,
                    "second_rank_supporting_messages": second_count,
                }
            )

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "records_profiled": record_count,
        "sent_folder_token_rule": sorted(SENT_FOLDER_TOKENS),
        "custodian_mailboxes": len(custodians),
        "custodians_with_sent_like_files": sum(count > 0 for count in sent_like_counts.values()),
        "sent_like_message_files": sum(sent_like_counts.values()),
        "eligible_sender_evidence_messages": sum(eligible_evidence_counts.values()),
        "ineligible_sent_like_message_files": sum(ineligible_sent_like_counts.values()),
        "custodians_with_eligible_sender_evidence": custodians_with_evidence,
        "custodians_with_unique_top_candidate": custodians_with_unique_top,
        "custodians_with_tied_top_candidate": custodians_with_tied_top,
        "custodians_with_unique_top_support_at_least_90_percent": (high_support_top_candidates),
        "custodians_without_eligible_sender_evidence": (len(custodians) - custodians_with_evidence),
        "mapping_status": (
            "Evidence audit only. Candidate addresses have not been assigned to "
            "custodians, and aliases have not been resolved."
        ),
        "next_processing_step": (
            "Review support and ambiguity distributions, then freeze a documented "
            "custodian-address mapping rule with an explicit treatment of unresolved "
            "or low-confidence custodians."
        ),
    }

    for path in (DETAILS, SUMMARY, REPORT):
        path.parent.mkdir(parents=True, exist_ok=True)

    detail_fields = [
        "custodian_mailbox",
        "rank",
        "candidate_sender_address",
        "supporting_sent_like_messages",
        "eligible_sent_like_messages",
        "support_share",
        "unique_top_candidate",
        "second_rank_supporting_messages",
    ]

    with DETAILS.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=detail_fields)
        writer.writeheader()
        writer.writerows(detail_rows)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        f"""# Enron custodian-address evidence audit

## Scope

This audit collects evidence from sent-like maildir folders only. It does **not** map
addresses to custodians, resolve aliases, filter records, or construct events.

- Custodian mailboxes: `{len(custodians):,}`
- Custodians with sent-like files: `{summary["custodians_with_sent_like_files"]:,}`
- Sent-like files: `{summary["sent_like_message_files"]:,}`
- Eligible single-sender evidence files: `{summary["eligible_sender_evidence_messages"]:,}`
- Custodians with any eligible sender evidence: `{custodians_with_evidence:,}`
- Custodians with a unique top candidate: `{custodians_with_unique_top:,}`
- Unique top candidates supported by at least 90% of a custodian's evidence:
  `{high_support_top_candidates:,}`
- Custodians without eligible evidence: `{summary["custodians_without_eligible_sender_evidence"]:,}`

## Evidence rule

A row contributes one vote for a candidate sender address only when it is in a sent-like
folder, has exactly one syntactically valid From address, and has no From-address parsing
issue. The sent-like taxonomy rule is: `{", ".join(sorted(SENT_FOLDER_TOKENS))}`.

The detailed CSV contains only the top three candidate addresses per custodian, with
support counts and shares. It is an audit table, not a final identity map.
""",
        encoding="utf-8",
    )

    print(f"Enron custodian-address audit passed: {record_count:,} records.")
    print(f"Custodian mailboxes: {len(custodians):,}.")
    print(f"Sent-like message files: {sum(sent_like_counts.values()):,}.")
    print(f"Eligible single-sender evidence files: {sum(eligible_evidence_counts.values()):,}.")
    print(f"Custodians with eligible sender evidence: {custodians_with_evidence:,}.")
    print(f"Custodians with a unique top candidate: {custodians_with_unique_top:,}.")
    print(f"Unique top candidates with at least 90% support: {high_support_top_candidates:,}.")
    print(
        "Custodians without eligible sender evidence: "
        f"{len(custodians) - custodians_with_evidence:,}."
    )
    print(f"Evidence table: {DETAILS.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
