#!/usr/bin/env python3
"""Extract reproducible Enron message-header records without retaining bodies."""

from __future__ import annotations

import hashlib
import json
import tarfile
from collections import Counter
from email import policy
from email.parser import BytesHeaderParser
from pathlib import Path
from typing import BinaryIO

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED_MESSAGE_FILES = 517_401
BATCH_SIZE = 5_000
MAX_HEADER_BYTES = 2 * 1024 * 1024
MAX_HEADER_LINE_BYTES = 1024 * 1024

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = PROJECT_ROOT / "data" / "external" / "enron_20150507" / "enron_mail_20150507.tar.gz"
OUTPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "message_headers.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_header_extraction_summary.json"

SCHEMA = pa.schema(
    [
        pa.field("source_path", pa.string()),
        pa.field("custodian_mailbox", pa.string()),
        pa.field("folder_path", pa.string()),
        pa.field("file_name", pa.string()),
        pa.field("message_bytes", pa.int64()),
        pa.field("raw_sha256", pa.string()),
        pa.field("message_id_raw", pa.string()),
        pa.field("date_raw", pa.string()),
        pa.field("from_raw", pa.string()),
        pa.field("to_raw", pa.string()),
        pa.field("cc_raw", pa.string()),
        pa.field("bcc_raw", pa.string()),
        pa.field("subject_raw", pa.string()),
        pa.field("header_bytes", pa.int32()),
        pa.field("header_truncated", pa.bool_()),
        pa.field("header_terminated", pa.bool_()),
        pa.field("parser_defect_count", pa.int16()),
        pa.field("parse_error", pa.string()),
    ]
)


def clean_header(value: object | None) -> str | None:
    """Return a single-line header value while preserving its substantive content."""
    if value is None:
        return None

    cleaned = str(value).replace("\r", " ").replace("\n", " ")
    cleaned = " ".join(cleaned.split())
    return cleaned or None


def read_headers_and_hash(
    handle: BinaryIO,
) -> tuple[bytes, str, int, bool, bool]:
    """
    Read only the header block for parsing, but hash the complete raw message.

    The full-message SHA-256 permits exact-duplicate detection later without
    retaining a second copy of any message body.
    """
    digest = hashlib.sha256()
    header_chunks: list[bytes] = []
    header_bytes = 0
    header_truncated = False
    header_terminated = False

    while True:
        line = handle.readline(MAX_HEADER_LINE_BYTES + 1)

        if not line:
            break

        digest.update(line)

        if header_bytes + len(line) <= MAX_HEADER_BYTES:
            header_chunks.append(line)
        else:
            header_truncated = True

        header_bytes += len(line)

        if line in (b"\n", b"\r\n"):
            header_terminated = True
            break

    for block in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(block)

    return (
        b"".join(header_chunks),
        digest.hexdigest(),
        header_bytes,
        header_truncated,
        header_terminated,
    )


def parse_member(
    tar: tarfile.TarFile,
    member: tarfile.TarInfo,
) -> dict[str, object]:
    """Create one header-only record for a raw Enron maildir message."""
    parts = member.name.split("/")
    handle = tar.extractfile(member)

    if handle is None:
        raise RuntimeError(f"Could not read archive member: {member.name}")

    with handle:
        (
            header_bytes,
            raw_sha256,
            header_size,
            header_truncated,
            header_terminated,
        ) = read_headers_and_hash(handle)

    record: dict[str, object] = {
        "source_path": member.name,
        "custodian_mailbox": parts[1],
        "folder_path": "/".join(parts[2:-1]) or None,
        "file_name": parts[-1],
        "message_bytes": member.size,
        "raw_sha256": raw_sha256,
        "message_id_raw": None,
        "date_raw": None,
        "from_raw": None,
        "to_raw": None,
        "cc_raw": None,
        "bcc_raw": None,
        "subject_raw": None,
        "header_bytes": header_size,
        "header_truncated": header_truncated,
        "header_terminated": header_terminated,
        "parser_defect_count": 0,
        "parse_error": None,
    }

    try:
        message = BytesHeaderParser(policy=policy.default).parsebytes(header_bytes)

        record.update(
            {
                "message_id_raw": clean_header(message.get("Message-ID")),
                "date_raw": clean_header(message.get("Date")),
                "from_raw": clean_header(message.get("From")),
                "to_raw": clean_header(message.get("To")),
                "cc_raw": clean_header(message.get("Cc")),
                "bcc_raw": clean_header(message.get("Bcc")),
                "subject_raw": clean_header(message.get("Subject")),
                "parser_defect_count": len(message.defects),
            }
        )
    except Exception as error:
        record["parse_error"] = f"{type(error).__name__}: {error}"

    return record


def main() -> None:
    if not ARCHIVE.is_file():
        raise SystemExit(f"STOP: Enron archive not found:\n  {ARCHIVE}")

    existing_outputs = [path for path in (OUTPUT, SUMMARY) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: generated output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)

    record_count = 0
    mailbox_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    parse_error_count = 0
    parser_defect_count = 0
    truncated_header_count = 0
    unterminated_header_count = 0
    buffer: list[dict[str, object]] = []

    with pq.ParquetWriter(OUTPUT, SCHEMA, compression="zstd") as writer:
        with tarfile.open(ARCHIVE, mode="r|gz") as tar:
            for member in tar:
                parts = member.name.split("/")

                if not member.isfile() or len(parts) < 3 or parts[0] != "maildir":
                    continue

                record = parse_member(tar, member)
                buffer.append(record)
                record_count += 1
                mailbox_counts[str(record["custodian_mailbox"])] += 1

                for field in (
                    "message_id_raw",
                    "date_raw",
                    "from_raw",
                    "to_raw",
                    "cc_raw",
                    "bcc_raw",
                ):
                    if record[field] is None:
                        missing_counts[field] += 1

                parse_error_count += record["parse_error"] is not None
                parser_defect_count += int(record["parser_defect_count"])
                truncated_header_count += bool(record["header_truncated"])
                unterminated_header_count += not bool(record["header_terminated"])

                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                    buffer.clear()

                if record_count % 25_000 == 0:
                    print(f"Processed {record_count:,} of {EXPECTED_MESSAGE_FILES:,} messages.")

        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))

    if record_count != EXPECTED_MESSAGE_FILES:
        raise SystemExit(
            "STOP: unexpected number of extracted message records.\n"
            f"Expected: {EXPECTED_MESSAGE_FILES:,}\n"
            f"Found:    {record_count:,}"
        )

    summary = {
        "dataset_id": "enron_20150507",
        "source_archive": str(ARCHIVE.relative_to(PROJECT_ROOT)),
        "output_parquet": str(OUTPUT.relative_to(PROJECT_ROOT)),
        "record_unit": "one regular maildir message file",
        "records_written": record_count,
        "custodian_mailboxes": len(mailbox_counts),
        "missing_header_counts": dict(sorted(missing_counts.items())),
        "parse_error_count": parse_error_count,
        "parser_defect_count": parser_defect_count,
        "header_truncated_count": truncated_header_count,
        "header_unterminated_count": unterminated_header_count,
        "body_handling": (
            "Bodies are neither stored nor emitted; full raw-message SHA-256 values "
            "were calculated for later exact-duplicate analysis."
        ),
        "next_processing_step": (
            "Profile header completeness, parse addresses and timestamps, then define "
            "the message-level deduplication policy."
        ),
    }

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Enron header extraction passed.")
    print(f"records written: {record_count:,}")
    print(f"custodian mailboxes: {len(mailbox_counts):,}")
    print(f"missing Message-ID: {missing_counts['message_id_raw']:,}")
    print(f"missing Date: {missing_counts['date_raw']:,}")
    print(f"missing From: {missing_counts['from_raw']:,}")
    print(f"header parse errors: {parse_error_count:,}")
    print(f"intermediate table: {OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"summary: {SUMMARY.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
