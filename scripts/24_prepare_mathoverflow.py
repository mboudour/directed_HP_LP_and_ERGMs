#!/usr/bin/env python3
"""Audit MathOverflow posts and conditionally reconstruct question-answer events."""

from __future__ import annotations

import argparse
import json
import sqlite3
import xml.etree.ElementTree as element_tree
from collections import Counter
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

BATCH_SIZE = 25_000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "raw" / "mathoverflow_stackexchange_2024" / "Posts.xml"
GATE = PROJECT_ROOT / "data" / "metadata" / "gates" / "mathoverflow_reconstruction_policy.json"
WORK_DIR = PROJECT_ROOT / "data" / "interim" / "mathoverflow_stackexchange_2024"
QUESTION_DB = WORK_DIR / "questions.sqlite"
OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mathoverflow_stackexchange_2024"
    / "native_events.parquet"
)
TEMP_OUTPUT = OUTPUT.with_suffix(".parquet.tmp")
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "mathoverflow_stackexchange_2024_audit.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "mathoverflow_stackexchange_2024_preparation.md"

EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("question_id", pa.string()),
        pa.field("question_created_at", pa.string()),
        pa.field("answer_window_days", pa.int16()),
        pa.field("tail_answerers", pa.list_(pa.string())),
        pa.field("head_asker", pa.string()),
        pa.field("construction", pa.string()),
    ]
)


def iso_timestamp(value: str | None) -> datetime | None:
    """Parse Stack Exchange timestamps conservatively for audit and window rules."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def iter_post_attributes(path: Path):
    """Yield post-row attributes with bounded memory."""
    for _, element in element_tree.iterparse(path, events=("end",)):
        if element.tag == "row":
            yield element.attrib
            element.clear()


def required_policy() -> int:
    """Read and validate the user-reviewed reconstruction policy record."""
    if not GATE.is_file():
        raise SystemExit(
            "STOP: reconstruction is blocked without a MathOverflow policy record:\n"
            f"  {GATE.relative_to(PROJECT_ROOT)}"
        )
    policy = json.loads(GATE.read_text(encoding="utf-8"))
    if policy.get("approved") is not True:
        raise SystemExit("STOP: MathOverflow policy record is not approved")
    expected = {
        "comments": "excluded",
        "anonymous_user": "exclude",
        "duplicate_answerer": "collapse_per_question",
        "deleted_post": "retain_rows_present_in_public_dump",
    }
    if policy.get("policies") != expected:
        raise SystemExit(
            "STOP: MathOverflow policy does not match the implemented reconstruction rule.\n"
            f"Required policies: {json.dumps(expected, sort_keys=True)}"
        )
    days = policy.get("answer_window_days")
    if not isinstance(days, int) or days <= 0 or days > 3650:
        raise SystemExit("STOP: answer_window_days must be an integer from 1 through 3650")
    return days


def build_question_database() -> tuple[int, int, int]:
    """Store valid questions locally for an exact streaming answer join."""
    if QUESTION_DB.exists():
        raise SystemExit(f"STOP: temporary question database already exists: {QUESTION_DB}")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(QUESTION_DB)
    connection.execute(
        "CREATE TABLE questions ("
        "question_id TEXT PRIMARY KEY, asker TEXT, created_at TEXT, unix_time REAL"
        ")"
    )
    question_rows = 0
    invalid_questions = 0
    anonymous_questions = 0
    batch: list[tuple[str, str, str, float]] = []

    try:
        for attributes in iter_post_attributes(INPUT):
            if attributes.get("PostTypeId") != "1":
                continue
            question_rows += 1
            question_id = attributes.get("Id")
            asker = attributes.get("OwnerUserId")
            created_at = attributes.get("CreationDate")
            parsed = iso_timestamp(created_at)
            if not question_id or not asker or parsed is None:
                invalid_questions += 1
                if not asker:
                    anonymous_questions += 1
                continue
            batch.append((question_id, asker, created_at, parsed.timestamp()))
            if len(batch) >= BATCH_SIZE:
                connection.executemany("INSERT OR IGNORE INTO questions VALUES (?, ?, ?, ?)", batch)
                batch.clear()
        if batch:
            connection.executemany("INSERT OR IGNORE INTO questions VALUES (?, ?, ?, ?)", batch)
        connection.commit()
        valid_questions = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    finally:
        connection.close()
    return question_rows, valid_questions, invalid_questions + anonymous_questions * 0


def reconstruct_events(answer_window_days: int) -> int:
    """Join answers to questions and write distinct-answerer directed events."""
    connection = sqlite3.connect(QUESTION_DB)
    connection.execute(
        "CREATE TABLE answerers ("
        "question_id TEXT, answerer TEXT, PRIMARY KEY (question_id, answerer)"
        ")"
    )
    accepted_answers = 0
    batch: list[tuple[str, str]] = []
    max_seconds = answer_window_days * 86_400

    try:
        for attributes in iter_post_attributes(INPUT):
            if attributes.get("PostTypeId") != "2":
                continue
            question_id = attributes.get("ParentId")
            answerer = attributes.get("OwnerUserId")
            parsed = iso_timestamp(attributes.get("CreationDate"))
            if not question_id or not answerer or parsed is None:
                continue
            row = connection.execute(
                "SELECT asker, unix_time FROM questions WHERE question_id = ?", (question_id,)
            ).fetchone()
            if row is None:
                continue
            asker, question_time = row
            elapsed = parsed.timestamp() - question_time
            if elapsed < 0 or elapsed > max_seconds or answerer == asker:
                continue
            batch.append((question_id, answerer))
            accepted_answers += 1
            if len(batch) >= BATCH_SIZE:
                connection.executemany("INSERT OR IGNORE INTO answerers VALUES (?, ?)", batch)
                batch.clear()
        if batch:
            connection.executemany("INSERT OR IGNORE INTO answerers VALUES (?, ?)", batch)
        connection.commit()

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        writer = pq.ParquetWriter(TEMP_OUTPUT, EVENT_SCHEMA, compression="zstd")
        buffer: list[dict[str, object]] = []
        current_question: str | None = None
        current_asker: str | None = None
        current_created: str | None = None
        answerers: list[str] = []
        events = 0

        cursor = connection.execute(
            "SELECT q.question_id, q.asker, q.created_at, a.answerer "
            "FROM questions AS q JOIN answerers AS a ON q.question_id = a.question_id "
            "ORDER BY q.question_id, a.answerer"
        )
        for question_id, asker, created_at, answerer in cursor:
            if current_question is not None and question_id != current_question:
                buffer.append(
                    {
                        "event_id": f"mathoverflow:{current_question}:window_{answer_window_days}d",
                        "question_id": current_question,
                        "question_created_at": current_created,
                        "answer_window_days": answer_window_days,
                        "tail_answerers": answerers,
                        "head_asker": current_asker,
                        "construction": "reconstructed_distinct_answerers_to_asker",
                    }
                )
                events += 1
                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
                    buffer.clear()
                answerers = []
            current_question = question_id
            current_asker = asker
            current_created = created_at
            answerers.append(answerer)
        if current_question is not None:
            buffer.append(
                {
                    "event_id": f"mathoverflow:{current_question}:window_{answer_window_days}d",
                    "question_id": current_question,
                    "question_created_at": current_created,
                    "answer_window_days": answer_window_days,
                    "tail_answerers": answerers,
                    "head_asker": current_asker,
                    "construction": "reconstructed_distinct_answerers_to_asker",
                }
            )
            events += 1
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
        writer.close()
        TEMP_OUTPUT.replace(OUTPUT)
    finally:
        connection.close()
    return accepted_answers


def audit(build_events: bool) -> None:
    """Create a streaming post audit and optionally the explicitly reconstructed events."""
    if not INPUT.is_file():
        raise SystemExit(f"STOP: MathOverflow Posts.xml is missing: {INPUT}")
    if SUMMARY.exists() or REPORT.exists() or (build_events and OUTPUT.exists()):
        raise SystemExit(
            "STOP: MathOverflow output already exists; this script will not overwrite it"
        )

    post_types: Counter[str] = Counter()
    missing_owner = 0
    invalid_dates = 0
    answer_missing_parent = 0
    total_rows = 0
    for attributes in iter_post_attributes(INPUT):
        total_rows += 1
        post_types[attributes.get("PostTypeId", "missing")] += 1
        if not attributes.get("OwnerUserId"):
            missing_owner += 1
        if attributes.get("CreationDate") and iso_timestamp(attributes.get("CreationDate")) is None:
            invalid_dates += 1
        if attributes.get("PostTypeId") == "2" and not attributes.get("ParentId"):
            answer_missing_parent += 1

    answer_window_days: int | None = None
    accepted_answers: int | None = None
    if build_events:
        answer_window_days = required_policy()
        _, _, _ = build_question_database()
        accepted_answers = reconstruct_events(answer_window_days)

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset_id": "mathoverflow_stackexchange_2024",
        "posts_rows_read": total_rows,
        "post_type_counts": dict(post_types),
        "missing_owner_user_id": missing_owner,
        "invalid_creation_dates": invalid_dates,
        "answers_missing_parent_id": answer_missing_parent,
        "reconstructed_events_built": build_events,
        "answer_window_days": answer_window_days,
        "accepted_answers_within_window": accepted_answers,
        "analysis_status": (
            "reconstructed_events_built_after_approved_policy"
            if build_events
            else "audit_only_pending_reconstruction_policy"
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    type_rows = "\n".join(f"| {kind} | {count:,} |" for kind, count in sorted(post_types.items()))
    REPORT.write_text(
        f"""# MathOverflow preparation audit

- Post rows read: `{total_rows:,}`
- Missing owner IDs: `{missing_owner:,}`
- Invalid creation dates: `{invalid_dates:,}`
- Answers missing a parent ID: `{answer_missing_parent:,}`
- Reconstructed events built: `{build_events}`

| PostTypeId | Rows |
|---|---:|
{type_rows}

Comments are excluded. A question-answer group is an analyst-defined reconstruction, not
a recorded multi-recipient event. It is built only after an approved answer-window and
post/user-treatment policy record exists.
""",
        encoding="utf-8",
    )
    print("MathOverflow audit passed.")
    print(f"Post rows read: {total_rows:,}.")
    print(f"Reconstructed events built: {build_events}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-reconstructed-events", action="store_true")
    args = parser.parse_args()
    audit(args.build_reconstructed_events)


if __name__ == "__main__":
    main()
