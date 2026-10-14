#!/usr/bin/env python3
"""Profile Enron maildir folders before custodian-address mapping."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_RECORDS = 517_401
BATCH_SIZE = 25_000
SENT_FOLDER_TOKENS = {"sent", "sentitem", "sentitems", "sentmail"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_folder_profile.json"
DETAILS = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_folder_counts.csv"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_folder_profile.md"


def normalize_folder_token(value: str) -> str:
    """Normalize a folder-label component for taxonomy matching."""
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def is_sent_like(folder_path: str | None) -> bool:
    """Flag paths containing a conventional sent-mail folder component."""
    if not folder_path:
        return False

    return any(
        normalize_folder_token(component) in SENT_FOLDER_TOKENS
        for component in folder_path.split("/")
    )


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: extracted Enron header table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/02_extract_enron_headers.py first."
        )

    existing_outputs = [path for path in (SUMMARY, DETAILS, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: folder-profile output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    record_count = 0
    mailbox_counts: Counter[str] = Counter()
    folder_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    sent_like_folder_counts: Counter[str] = Counter()
    sent_like_mailbox_counts: Counter[str] = Counter()

    parquet_file = pq.ParquetFile(INPUT)

    for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["custodian_mailbox", "folder_path"],
    ):
        for record in batch.to_pylist():
            record_count += 1

            custodian = str(record["custodian_mailbox"])
            folder_path = record["folder_path"] or "(root)"
            top_level = folder_path.split("/", maxsplit=1)[0]

            mailbox_counts[custodian] += 1
            folder_counts[folder_path] += 1
            top_level_counts[top_level] += 1

            original_folder_path = record["folder_path"]
            if is_sent_like(original_folder_path):
                sent_like_folder_counts[folder_path] += 1
                sent_like_mailbox_counts[custodian] += 1

    if record_count != EXPECTED_RECORDS:
        raise SystemExit(
            "STOP: unexpected extracted-header row count.\n"
            f"Expected: {EXPECTED_RECORDS:,}\n"
            f"Found:    {record_count:,}"
        )

    folder_rows = [
        {
            "folder_path": folder_path,
            "message_files": count,
            "sent_like": is_sent_like(None if folder_path == "(root)" else folder_path),
        }
        for folder_path, count in folder_counts.most_common()
    ]

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "records_profiled": record_count,
        "custodian_mailboxes": len(mailbox_counts),
        "unique_folder_paths": len(folder_counts),
        "unique_top_level_folder_labels": len(top_level_counts),
        "sent_folder_token_rule": sorted(SENT_FOLDER_TOKENS),
        "sent_like_message_files": sum(sent_like_folder_counts.values()),
        "sent_like_folder_paths": len(sent_like_folder_counts),
        "custodians_with_one_or_more_sent_like_files": len(sent_like_mailbox_counts),
        "next_processing_step": (
            "Inspect the observed folder taxonomy, then define the sent-folder rule "
            "used to collect evidence for a custodian-to-address mapping."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with DETAILS.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["folder_path", "message_files", "sent_like"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(folder_rows)

    top_level_rows = "\n".join(
        f"| `{folder}` | {count:,} |" for folder, count in top_level_counts.most_common(20)
    )

    sent_like_rows = "\n".join(
        f"| `{folder}` | {count:,} |" for folder, count in sent_like_folder_counts.most_common(20)
    )

    REPORT.write_text(
        f"""# Enron maildir-folder taxonomy audit

## Scope

This audit examines maildir folder labels only. It does not parse address content, infer
custodian identities, create event records, or apply any filter.

- Records profiled: `{record_count:,}`
- Custodian mailboxes: `{len(mailbox_counts):,}`
- Unique folder paths: `{len(folder_counts):,}`
- Sent-like message files: `{sum(sent_like_folder_counts.values()):,}`
- Custodians with sent-like files: `{len(sent_like_mailbox_counts):,}`

The provisional sent-folder rule flags any folder-path component that normalizes to one of:
`{", ".join(sorted(SENT_FOLDER_TOKENS))}`. It is an audit flag only, not yet a mapping rule.

## Twenty most frequent top-level folder labels

| Top-level folder | Message files |
|---|---:|
{top_level_rows}

## Twenty most frequent sent-like folder paths

| Folder path | Message files |
|---|---:|
{sent_like_rows}

## Next decision

The next stage will use an explicit, recorded sent-folder rule to gather candidate sender
addresses for each custodian mailbox. It will report confidence and ambiguity rather than
silently mapping addresses to custodians.
""",
        encoding="utf-8",
    )

    print(f"Enron folder-taxonomy audit passed: {record_count:,} records.")
    print(f"Custodian mailboxes: {len(mailbox_counts):,}.")
    print(f"Unique folder paths: {len(folder_counts):,}.")
    print(f"Unique top-level folder labels: {len(top_level_counts):,}.")
    print(
        "Sent-like message files under the provisional token rule: "
        f"{sum(sent_like_folder_counts.values()):,}."
    )
    print(f"Sent-like folder paths: {len(sent_like_folder_counts):,}.")
    print(f"Custodians with one or more sent-like files: {len(sent_like_mailbox_counts):,}.")
    print(f"Folder-count table: {DETAILS.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
