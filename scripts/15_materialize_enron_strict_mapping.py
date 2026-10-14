#!/usr/bin/env python3
"""Materialize the approved strict Enron custodian mapping and projection gate.

A mapping is approved only when the rank-one sender address has unique top support
of at least 90% in sent-like folders and is not the rank-one address of another
custodian. This implements the researcher's approved strict primary policy. The
address-bearing mapping remains local and ignored by Git; only aggregate gate
metadata and audit text are version-controlled.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq
import yaml

EXPECTED_CUSTODIANS = 150
SUPPORT_THRESHOLD = 0.90
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
TEMPORAL_POLICY = PROJECT_ROOT / "configs" / "enron_temporal_policy.yaml"
MAPPING = PROJECT_ROOT / "data" / "processed" / "enron_20150507" / "custodian_address_map.csv"
GATE = PROJECT_ROOT / "data" / "metadata" / "gates" / "enron_custodian_projection.json"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_strict_mapping.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_strict_mapping.md"
OUTPUTS = (MAPPING, GATE, SUMMARY, REPORT)


def parse_args() -> argparse.Namespace:
    """Parse the explicit deterministic refresh flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the mapping, gate, summary, and report produced by this driver.",
    )
    return parser.parse_args()


def bool_from_csv(value: str) -> bool:
    """Parse a CSV boolean without accepting ambiguous text."""
    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise SystemExit(f"STOP: expected a CSV boolean, found {value!r}.")


def display_path(path: Path) -> str:
    """Render repository-relative paths in diagnostics."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def prepare_outputs(overwrite: bool) -> None:
    """Protect a prior local mapping unless deterministic overwrite is explicit."""
    existing = [path for path in OUTPUTS if path.exists()]
    if existing and not overwrite:
        rendered = "\n  ".join(display_path(path) for path in existing)
        raise SystemExit(
            "STOP: strict mapping output already exists. Pass --overwrite to refresh only "
            f"this driver's files:\n  {rendered}"
        )
    for path in existing:
        path.unlink()
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)


def read_custodians() -> set[str]:
    """Read the fixed source-mailbox universe without retaining message content."""
    if not HEADERS.is_file():
        raise SystemExit(f"STOP: Enron header table is missing: {display_path(HEADERS)}")
    custodians: set[str] = set()
    for batch in pq.ParquetFile(HEADERS).iter_batches(columns=["custodian_mailbox"]):
        custodians.update(str(value).strip() for value in batch.column(0).to_pylist())
    if len(custodians) != EXPECTED_CUSTODIANS or "" in custodians:
        raise SystemExit(
            "STOP: unexpected source custodian-mailbox universe; "
            f"expected {EXPECTED_CUSTODIANS}, found {len(custodians)}."
        )
    return custodians


def read_rank_one_evidence(custodians: set[str]) -> dict[str, dict[str, str]]:
    """Read exactly one documented rank-one candidate for each available custodian."""
    if not EVIDENCE.is_file():
        raise SystemExit(f"STOP: custodian evidence table is missing: {display_path(EVIDENCE)}")
    required = {
        "custodian_mailbox",
        "rank",
        "candidate_sender_address",
        "supporting_sent_like_messages",
        "eligible_sent_like_messages",
        "support_share",
        "unique_top_candidate",
    }
    ranked: dict[str, dict[str, str]] = {}
    with EVIDENCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(f"STOP: evidence columns must include {sorted(required)}")
        for row in reader:
            custodian = row["custodian_mailbox"].strip()
            if custodian not in custodians:
                raise SystemExit("STOP: evidence includes a custodian outside the header universe.")
            if int(row["rank"]) != 1:
                continue
            if custodian in ranked:
                raise SystemExit(f"STOP: multiple rank-one evidence rows for {custodian!r}.")
            ranked[custodian] = row
    return ranked


def read_temporal_policy() -> dict[str, object]:
    """Validate the separately versioned, already approved timestamp-only policy."""
    if not TEMPORAL_POLICY.is_file():
        raise SystemExit(f"STOP: temporal policy is missing: {display_path(TEMPORAL_POLICY)}")
    policy = yaml.safe_load(TEMPORAL_POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or policy.get("status") != "approved_for_timestamp_filter_only":
        raise SystemExit("STOP: Enron temporal policy is not approved for the timestamp filter.")
    inclusion = policy.get("inclusion")
    if not isinstance(inclusion, dict):
        raise SystemExit("STOP: Enron temporal policy has no inclusion section.")
    start = inclusion.get("timestamp_start_utc")
    end = inclusion.get("timestamp_end_utc")
    if not isinstance(start, str) or not isinstance(end, str):
        raise SystemExit("STOP: Enron temporal policy has invalid UTC endpoints.")
    return {"timestamp_start_utc": start, "timestamp_end_utc": end}


def select_rows(
    custodians: set[str],
    rank_one: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    """Apply the approved automatic rule and preserve every excluded custodian locally."""
    address_to_custodians: defaultdict[str, set[str]] = defaultdict(set)
    for custodian, row in rank_one.items():
        address_to_custodians[row["candidate_sender_address"].strip().casefold()].add(custodian)

    rows: list[dict[str, object]] = []
    for custodian in sorted(custodians):
        candidate = rank_one.get(custodian)
        if candidate is None:
            rows.append(
                {
                    "custodian_mailbox": custodian,
                    "address": "",
                    "approved": False,
                    "selection_status": "excluded_no_rank_one_candidate",
                    "support_share": "",
                    "supporting_sent_like_messages": "",
                    "eligible_sent_like_messages": "",
                }
            )
            continue

        address = candidate["candidate_sender_address"].strip().casefold()
        support = float(candidate["support_share"])
        unique_top = bool_from_csv(candidate["unique_top_candidate"])
        shared = len(address_to_custodians[address]) > 1
        reasons: list[str] = []
        if not unique_top:
            reasons.append("rank_one_not_unique")
        if support < SUPPORT_THRESHOLD:
            reasons.append("support_below_90_percent")
        if shared:
            reasons.append("rank_one_address_shared")
        approved = not reasons
        rows.append(
            {
                "custodian_mailbox": custodian,
                "address": address,
                "approved": approved,
                "selection_status": "approved_strict_automatic"
                if approved
                else "excluded_" + "_and_".join(reasons),
                "support_share": candidate["support_share"],
                "supporting_sent_like_messages": candidate["supporting_sent_like_messages"],
                "eligible_sent_like_messages": candidate["eligible_sent_like_messages"],
            }
        )

    approved_addresses = [str(row["address"]) for row in rows if row["approved"]]
    if len(approved_addresses) != len(set(approved_addresses)):
        raise SystemExit("STOP: strict rule would approve an address for more than one custodian.")
    if not approved_addresses:
        raise SystemExit("STOP: strict rule approved no mappings.")
    return rows


def write_mapping(rows: list[dict[str, object]]) -> None:
    """Write the local-only address-bearing mapping in a strict projection contract."""
    fieldnames = [
        "address",
        "custodian_mailbox",
        "approved",
        "selection_status",
        "support_share",
        "supporting_sent_like_messages",
        "eligible_sent_like_messages",
    ]
    with MAPPING.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fieldnames})


def main() -> None:
    """Build the approved strict map and its non-sensitive projection gate."""
    args = parse_args()
    custodians = read_custodians()
    rank_one = read_rank_one_evidence(custodians)
    temporal_policy = read_temporal_policy()
    prepare_outputs(args.overwrite)
    rows = select_rows(custodians, rank_one)
    write_mapping(rows)

    approved = [row for row in rows if row["approved"]]
    excluded = [row for row in rows if not row["approved"]]
    exclusion_counts = defaultdict(int)
    for row in excluded:
        exclusion_counts[str(row["selection_status"])] += 1
    gate = {
        "dataset_id": "enron_20150507",
        "approved": True,
        "approval_record": "researcher_approval_2026-10-14",
        "mapping_policy": {
            "approved_rule": (
                "unique rank-one sent-folder sender address with support at least 0.90 and "
                "no rank-one address shared across custodians"
            ),
            "support_threshold": SUPPORT_THRESHOLD,
            "source_custodian_mailboxes": len(custodians),
            "approved_mappings": len(approved),
            "excluded_custodians": len(excluded),
            "exclusion_counts": dict(sorted(exclusion_counts.items())),
        },
        "projection_policy": {
            "unmapped_participant": "exclude_entire_event",
            "self_custodian_in_head": "remove",
            "message_copy_policy": "retain_distinct_maildir_records_after_duplicate_audit",
            "timestamp_policy": display_path(TEMPORAL_POLICY),
            **temporal_policy,
        },
        "status": (
            "Approved strict primary Enron policy. The address-bearing mapping is local-only; "
            "this gate preserves only aggregate selection evidence."
        ),
    }
    GATE.write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "dataset_id": "enron_20150507",
        "mapping_file": display_path(MAPPING),
        "gate_file": display_path(GATE),
        "source_custodian_mailboxes": len(custodians),
        "custodians_with_rank_one_evidence": len(rank_one),
        "approved_mappings": len(approved),
        "excluded_custodians": len(excluded),
        "exclusion_counts": dict(sorted(exclusion_counts.items())),
        "policy": "strict_primary_custodian_projection",
        "timestamp_inclusion_utc": temporal_policy,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Enron strict custodian mapping\n\n"
        "## Approved primary policy\n\n"
        "The researcher approved a strict primary custodian-node projection on 2026-10-14. "
        "An address is mapped only when it is the unique rank-one sender candidate from a "
        "custodian's sent-like folders, has at least 90% support, and is not rank-one for any "
        "other custodian. All other custodians are excluded from the primary node universe.\n\n"
        f"- Source custodian mailboxes: `{len(custodians):,}`\n"
        f"- Custodians with a rank-one candidate: `{len(rank_one):,}`\n"
        f"- Approved address-to-custodian mappings: `{len(approved):,}`\n"
        f"- Excluded custodians: `{len(excluded):,}`\n"
        f"- Timestamp interval: `{temporal_policy['timestamp_start_utc']}` through "
        f"`{temporal_policy['timestamp_end_utc']}` inclusive\n\n"
        "## Projection rule\n\n"
        "A retained primary native event must have an approved mapped sender and approved "
        "mapped identities for every `To`/`Cc` recipient. An event with an unmapped participant "
        "is excluded in full. A recipient mapped to the sender's custodian is removed. Distinct "
        "maildir records are retained after the completed raw-SHA and Message-ID duplicate "
        "audits.\n\n"
        "The address-bearing mapping file remains local and ignored by Git. The gate file stores "
        "only non-sensitive aggregate policy evidence.\n",
        encoding="utf-8",
    )

    print("Enron strict custodian mapping passed.")
    print(f"Source custodians: {len(custodians):,}.")
    print(f"Approved mappings: {len(approved):,}.")
    print(f"Excluded custodians: {len(excluded):,}.")
    print(f"Mapping: {display_path(MAPPING)}")
    print(f"Gate: {display_path(GATE)}")
    print(f"Summary: {display_path(SUMMARY)}")
    print(f"Audit report: {display_path(REPORT)}")


if __name__ == "__main__":
    main()
