#!/usr/bin/env python3
"""Audit the downloaded Enron archive without changing source data."""

from __future__ import annotations

import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path

EXPECTED_SHA256 = "b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7"
EXPECTED_MESSAGE_FILES = 517_401

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT_ROOT / "data" / "external" / "enron_20150507" / "enron_mail_20150507.tar.gz"
MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_archive_manifest.json"
AUDIT_PATH = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not ARCHIVE.is_file():
        raise SystemExit(
            "STOP: Enron archive not found at:\n"
            f"  {ARCHIVE}\n"
            "Expected file: data/external/enron_20150507/"
            "enron_mail_20150507.tar.gz"
        )

    archive_sha256 = sha256(ARCHIVE)
    if archive_sha256 != EXPECTED_SHA256:
        raise SystemExit(
            "STOP: Enron archive checksum does not match the registered source.\n"
            f"Expected: {EXPECTED_SHA256}\n"
            f"Found:    {archive_sha256}"
        )

    total_members = 0
    directory_members = 0
    regular_file_members = 0
    maildir_message_files = 0
    maildir_uncompressed_bytes = 0
    mailbox_counts: Counter[str] = Counter()

    with tarfile.open(ARCHIVE, mode="r|gz") as tar:
        for member in tar:
            total_members += 1

            if member.isdir():
                directory_members += 1
                continue

            if not member.isfile():
                continue

            regular_file_members += 1
            parts = member.name.split("/")

            if len(parts) >= 3 and parts[0] == "maildir":
                maildir_message_files += 1
                maildir_uncompressed_bytes += member.size
                mailbox_counts[parts[1]] += 1

    if maildir_message_files != EXPECTED_MESSAGE_FILES:
        raise SystemExit(
            "STOP: unexpected number of regular message files in maildir.\n"
            f"Expected: {EXPECTED_MESSAGE_FILES:,}\n"
            f"Found:    {maildir_message_files:,}"
        )

    manifest = {
        "dataset_id": "enron_20150507",
        "archive_path": str(ARCHIVE.relative_to(PROJECT_ROOT)),
        "archive_sha256": archive_sha256,
        "archive_bytes": ARCHIVE.stat().st_size,
        "tar_members_total": total_members,
        "tar_directory_members": directory_members,
        "tar_regular_file_members": regular_file_members,
        "maildir_message_files": maildir_message_files,
        "maildir_uncompressed_bytes": maildir_uncompressed_bytes,
        "custodian_mailboxes": len(mailbox_counts),
        "top_10_custodian_mailboxes_by_file_count": mailbox_counts.most_common(10),
        "source_status": "verified_downloaded_archive",
        "next_processing_step": (
            "Extract to data/interim and parse message headers without modifying the archive."
        ),
    }

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    top_mailboxes = "\n".join(
        f"| `{mailbox}` | {count:,} |" for mailbox, count in mailbox_counts.most_common(10)
    )

    AUDIT_PATH.write_text(
        f"""# Enron email archive — source audit

## Verified source archive

- Archive: `{ARCHIVE.relative_to(PROJECT_ROOT)}`
- SHA-256: `{archive_sha256}`
- Archive size: `{ARCHIVE.stat().st_size:,}` bytes
- Archive structure: Unix `maildir`
- Regular message files: `{maildir_message_files:,}`
- Custodian mailboxes: `{len(mailbox_counts):,}`
- Uncompressed regular-message content: `{maildir_uncompressed_bytes:,}` bytes

## Analytical status

The archive has been verified as the registered Enron source. It is retained unchanged
under `data/external/`.

The unit of the next processing stage will be one raw message file. That stage will extract
headers only and preserve source-relative path, message identifier, sender, recipient
headers, date fields, and parsing-status flags. It will not yet construct a network.

## Largest custodian mailboxes by raw file count

| Custodian mailbox | Message files |
|---|---:|
{top_mailboxes}

## Next gate

Before Enron enters native-event, static missingness, or chronological analyses, the next
script must extract and profile message headers, then define deduplication and the
To/Cc/Bcc recipient policy.
""",
        encoding="utf-8",
    )

    print("Enron archive audit passed.")
    print(f"SHA-256: {archive_sha256}")
    print(f"maildir message files: {maildir_message_files:,}")
    print(f"custodian mailboxes: {len(mailbox_counts):,}")
    print(f"manifest: {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")
    print(f"audit: {AUDIT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
