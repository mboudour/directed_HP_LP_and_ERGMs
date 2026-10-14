#!/usr/bin/env python3
"""Profile Enron custodian-address evidence before freezing the identity map."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

EXPECTED_CUSTODIANS = 150
THRESHOLDS = (1.00, 0.99, 0.95, 0.90, 0.75, 0.50)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "enron_20150507"
    / "audits"
    / "enron_20150507_custodian_address_evidence.csv"
)
EVIDENCE_SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_custodian_address_evidence_summary.json"
)
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_custodian_mapping_confidence.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_custodian_mapping_confidence.md"


def confidence_bin(support_share: float) -> str:
    """Assign a readable support-share bin."""
    if support_share == 1.0:
        return "100%"
    if support_share >= 0.99:
        return "99–<100%"
    if support_share >= 0.95:
        return "95–<99%"
    if support_share >= 0.90:
        return "90–<95%"
    if support_share >= 0.75:
        return "75–<90%"
    if support_share >= 0.50:
        return "50–<75%"
    return "<50%"


def percentage_label(threshold: float) -> str:
    """Render a proportion as an integer percentage label."""
    return f"{threshold:.0%}"


def main() -> None:
    if not EVIDENCE.is_file():
        raise SystemExit(
            "STOP: custodian-address evidence table not found:\n"
            f"  {EVIDENCE}\n"
            "Run scripts/08_audit_enron_custodian_address_evidence.py first."
        )

    if not EVIDENCE_SUMMARY.is_file():
        raise SystemExit(
            "STOP: custodian-address evidence summary not found:\n"
            f"  {EVIDENCE_SUMMARY}\n"
            "Run scripts/08_audit_enron_custodian_address_evidence.py first."
        )

    existing_outputs = [path for path in (SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: mapping-confidence output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    evidence_summary = json.loads(EVIDENCE_SUMMARY.read_text(encoding="utf-8"))
    source_custodian_count = int(evidence_summary["custodian_mailboxes"])

    if source_custodian_count != EXPECTED_CUSTODIANS:
        raise SystemExit(
            "STOP: unexpected custodian count in the evidence summary.\n"
            f"Expected: {EXPECTED_CUSTODIANS}\n"
            f"Found:    {source_custodian_count}"
        )

    top_rows: list[dict[str, str]] = []

    with EVIDENCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if int(row["rank"]) == 1:
                top_rows.append(row)

    if not top_rows:
        raise SystemExit("STOP: the evidence table has no rank-one candidate rows.")

    custodians = [row["custodian_mailbox"] for row in top_rows]
    duplicate_custodians = [
        custodian for custodian, count in Counter(custodians).items() if count > 1
    ]

    if duplicate_custodians:
        raise SystemExit(
            "STOP: more than one rank-one candidate was found for at least one custodian."
        )

    support_shares = [float(row["support_share"]) for row in top_rows]
    support_gaps = [
        int(row["supporting_sent_like_messages"]) - int(row["second_rank_supporting_messages"])
        for row in top_rows
    ]

    confidence_bins = Counter(confidence_bin(share) for share in support_shares)

    threshold_counts = {
        percentage_label(threshold): sum(share >= threshold for share in support_shares)
        for threshold in THRESHOLDS
    }

    address_to_custodians: defaultdict[str, list[str]] = defaultdict(list)

    for row in top_rows:
        address_to_custodians[row["candidate_sender_address"]].append(row["custodian_mailbox"])

    collision_groups = [
        custodians for custodians in address_to_custodians.values() if len(custodians) > 1
    ]

    summary = {
        "dataset_id": "enron_20150507",
        "evidence_input": str(EVIDENCE.relative_to(PROJECT_ROOT)),
        "source_custodian_mailboxes": source_custodian_count,
        "custodians_with_rank_one_candidate": len(top_rows),
        "custodians_without_rank_one_candidate": (source_custodian_count - len(top_rows)),
        "support_share_bins": {
            label: confidence_bins[label]
            for label in (
                "100%",
                "99–<100%",
                "95–<99%",
                "90–<95%",
                "75–<90%",
                "50–<75%",
                "<50%",
            )
        },
        "threshold_counts": threshold_counts,
        "minimum_support_share": min(support_shares),
        "median_support_share": median(support_shares),
        "minimum_top_minus_second_support_gap": min(support_gaps),
        "candidate_addresses_shared_by_multiple_custodians": len(collision_groups),
        "custodians_in_shared_address_collisions": sum(len(group) for group in collision_groups),
        "mapping_status": (
            "Profile only. No candidate address is assigned to a custodian, and "
            "no alias-resolution rule is applied."
        ),
        "next_decision": (
            "Use the support distribution and collision result to choose a "
            "documented custodian-address inclusion and ambiguity policy."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    bin_rows = "\n".join(
        f"| {label} | {summary['support_share_bins'][label]:,} |"
        for label in summary["support_share_bins"]
    )

    threshold_rows = "\n".join(
        f"| At least {label} | {count:,} |" for label, count in threshold_counts.items()
    )

    REPORT.write_text(
        f"""# Enron custodian-mapping confidence profile

## Scope

This audit profiles the rank-one candidate address for each custodian. It does not assign
an address to a custodian, resolve aliases, or create an event table.

- Source custodian mailboxes: `{source_custodian_count:,}`
- Rank-one candidate mappings: `{len(top_rows):,}`
- Custodians without a rank-one candidate: `{source_custodian_count - len(top_rows):,}`
- Candidate addresses shared by multiple custodians: `{len(collision_groups):,}`
- Custodians involved in a shared-address collision:
  `{sum(len(group) for group in collision_groups):,}`

## Rank-one support distribution

| Support share | Custodians |
|---|---:|
{bin_rows}

## Threshold counts

| Requirement | Custodians |
|---|---:|
{threshold_rows}

The lowest rank-one support share is `{min(support_shares):.3f}`. The median is
`{median(support_shares):.3f}`. The smallest gap between first- and second-ranked
candidate support is `{min(support_gaps):,}` message files.

## Interpretation

This profile informs a later documented mapping policy. A high support share alone is not
an identity proof, and a shared top candidate across mailbox directories must be resolved
or excluded explicitly. No mapping has been frozen by this script.
""",
        encoding="utf-8",
    )

    print("Enron custodian-mapping confidence profile passed.")
    print(f"Source custodian mailboxes: {source_custodian_count:,}.")
    print(f"Rank-one candidate mappings: {len(top_rows):,}.")
    print(
        f"Mappings supported by at least 90% of sent-folder evidence: {threshold_counts['90%']:,}."
    )
    print(f"Lowest rank-one support share: {min(support_shares):.3f}.")
    print(f"Median rank-one support share: {median(support_shares):.3f}.")
    print(f"Top candidate addresses shared across custodians: {len(collision_groups):,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
