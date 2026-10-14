#!/usr/bin/env python3
"""Profile MathOverflow reconstruction windows without materializing events."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as element_tree
from collections import Counter
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

DEFAULT_WINDOWS_DAYS = (1, 7, 30, 90, 365)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "mathoverflow_stackexchange_2024" / "Posts.xml"
DEFAULT_SUMMARY = PROJECT_ROOT / "data" / "metadata" / "mathoverflow_reconstruction_profile.json"
DEFAULT_REPORT = (
    PROJECT_ROOT
    / "docs"
    / "data_audits"
    / "mathoverflow_stackexchange_2024_reconstruction_profile.md"
)


def iso_timestamp(value: str | None) -> datetime | None:
    """Parse a Stack Exchange timestamp without modifying the source value."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def iter_post_attributes(path: Path) -> Iterator[dict[str, str]]:
    """Stream XML post attributes using bounded memory."""
    for _, element in element_tree.iterparse(path, events=("end",)):
        if element.tag == "row":
            yield element.attrib
            element.clear()


def quantile(sorted_values: list[float], probability: float) -> float | None:
    """Calculate a deterministic linear-interpolated quantile."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def arity_summary(arities: list[int]) -> dict[str, float | int | None]:
    """Summarize reconstructed tail arities without exposing user identifiers."""
    if not arities:
        return {"minimum": None, "median": None, "p95": None, "maximum": None}
    values = sorted(float(value) for value in arities)
    return {
        "minimum": int(values[0]),
        "median": quantile(values, 0.5),
        "p95": quantile(values, 0.95),
        "maximum": int(values[-1]),
    }


def parse_windows(value: str) -> tuple[int, ...]:
    """Validate explicit positive day windows for the descriptive profile."""
    try:
        windows = tuple(sorted({int(item.strip()) for item in value.split(",") if item.strip()}))
    except ValueError as error:
        raise argparse.ArgumentTypeError("windows must be comma-separated integers") from error
    if not windows or any(days <= 0 or days > 3650 for days in windows):
        raise argparse.ArgumentTypeError("windows must be positive day counts at most 3650")
    return windows


def profile(input_path: Path, windows_days: tuple[int, ...]) -> dict[str, object]:
    """Profile question-answer response timing and distinct-answerer group sizes."""
    post_types: Counter[str] = Counter()
    questions_total = 0
    questions_missing_owner = 0
    questions_invalid_date = 0
    questions: dict[str, tuple[str, float]] = {}

    for attributes in iter_post_attributes(input_path):
        post_type = attributes.get("PostTypeId", "missing")
        post_types[post_type] += 1
        if post_type != "1":
            continue
        questions_total += 1
        question_id = attributes.get("Id")
        asker = attributes.get("OwnerUserId")
        parsed = iso_timestamp(attributes.get("CreationDate"))
        if not asker:
            questions_missing_owner += 1
        if parsed is None:
            questions_invalid_date += 1
        if question_id and asker and parsed is not None:
            questions[question_id] = (asker, parsed.timestamp())

    answers_total = 0
    answers_missing_owner = 0
    answers_missing_parent = 0
    answers_invalid_date = 0
    answers_parent_not_eligible_question = 0
    answers_negative_elapsed = 0
    answers_by_asker = 0
    eligible_answer_records = 0
    duplicate_eligible_answer_records = 0
    first_elapsed_seconds_by_pair: dict[tuple[str, str], float] = {}

    for attributes in iter_post_attributes(input_path):
        if attributes.get("PostTypeId") != "2":
            continue
        answers_total += 1
        question_id = attributes.get("ParentId")
        answerer = attributes.get("OwnerUserId")
        parsed = iso_timestamp(attributes.get("CreationDate"))
        if not answerer:
            answers_missing_owner += 1
        if not question_id:
            answers_missing_parent += 1
        if parsed is None:
            answers_invalid_date += 1
        if not question_id or not answerer or parsed is None:
            continue
        question = questions.get(question_id)
        if question is None:
            answers_parent_not_eligible_question += 1
            continue
        asker, question_timestamp = question
        elapsed_seconds = parsed.timestamp() - question_timestamp
        if elapsed_seconds < 0:
            answers_negative_elapsed += 1
            continue
        if answerer == asker:
            answers_by_asker += 1
            continue
        eligible_answer_records += 1
        pair = (question_id, answerer)
        previous = first_elapsed_seconds_by_pair.get(pair)
        if previous is not None:
            duplicate_eligible_answer_records += 1
            if elapsed_seconds < previous:
                first_elapsed_seconds_by_pair[pair] = elapsed_seconds
        else:
            first_elapsed_seconds_by_pair[pair] = elapsed_seconds

    latency_days = sorted(seconds / 86_400 for seconds in first_elapsed_seconds_by_pair.values())
    latency_quantiles = {
        f"p{int(probability * 100):02d}": quantile(latency_days, probability)
        for probability in (0.25, 0.5, 0.75, 0.9, 0.95, 0.99)
    }

    window_profiles: list[dict[str, object]] = []
    for days in windows_days:
        groups: Counter[str] = Counter()
        retained_pairs = 0
        maximum_seconds = days * 86_400
        for (question_id, _answerer), elapsed_seconds in first_elapsed_seconds_by_pair.items():
            if elapsed_seconds <= maximum_seconds:
                retained_pairs += 1
                groups[question_id] += 1
        arities = list(groups.values())
        window_profiles.append(
            {
                "answer_window_days": days,
                "distinct_question_answerer_pairs": retained_pairs,
                "questions_with_at_least_one_answerer": len(groups),
                "questions_with_two_or_more_answerers": sum(arity >= 2 for arity in arities),
                "tail_arity": arity_summary(arities),
            }
        )

    return {
        "dataset_id": "mathoverflow_stackexchange_2024",
        "reconstruction_status": "profile_only_policy_unapproved_no_events_materialized",
        "posts": {"total": sum(post_types.values()), "post_type_counts": dict(post_types)},
        "questions": {
            "total": questions_total,
            "eligible_with_owner_and_valid_timestamp": len(questions),
            "missing_owner": questions_missing_owner,
            "invalid_timestamp": questions_invalid_date,
        },
        "answers": {
            "total": answers_total,
            "missing_owner": answers_missing_owner,
            "missing_parent": answers_missing_parent,
            "invalid_timestamp": answers_invalid_date,
            "parent_not_eligible_question": answers_parent_not_eligible_question,
            "negative_elapsed_time": answers_negative_elapsed,
            "answerer_is_asker": answers_by_asker,
            "eligible_records_before_duplicate_collapse": eligible_answer_records,
            "duplicate_eligible_answer_records": duplicate_eligible_answer_records,
            "distinct_question_answerer_pairs": len(first_elapsed_seconds_by_pair),
        },
        "first_distinct_answerer_latency_days": latency_quantiles,
        "window_profiles": window_profiles,
    }


def render_report(summary: dict[str, object]) -> str:
    """Render a non-sensitive report that separates evidence from a policy decision."""
    questions = summary["questions"]
    answers = summary["answers"]
    latency = summary["first_distinct_answerer_latency_days"]
    eligible_questions = questions["eligible_with_owner_and_valid_timestamp"]
    parent_not_eligible = answers["parent_not_eligible_question"]
    self_answers = answers["answerer_is_asker"]
    eligible_records = answers["eligible_records_before_duplicate_collapse"]
    duplicate_records = answers["duplicate_eligible_answer_records"]
    distinct_pairs = answers["distinct_question_answerer_pairs"]
    rows = []
    for profile in summary["window_profiles"]:
        arity = profile["tail_arity"]
        rows.append(
            "| {days} | {pairs:,} | {events:,} | {multi:,} | {median} | {p95} | {maximum} |".format(
                days=profile["answer_window_days"],
                pairs=profile["distinct_question_answerer_pairs"],
                events=profile["questions_with_at_least_one_answerer"],
                multi=profile["questions_with_two_or_more_answerers"],
                median="—" if arity["median"] is None else f"{arity['median']:.2f}",
                p95="—" if arity["p95"] is None else f"{arity['p95']:.2f}",
                maximum="—" if arity["maximum"] is None else str(arity["maximum"]),
            )
        )
    latency_text = ", ".join(
        f"{label}={value:.3f}" if value is not None else f"{label}=—"
        for label, value in latency.items()
    )
    table_header = (
        "| Window (days) | Distinct pairs | Questions with ≥1 answerer | "
        "Questions with ≥2 answerers | Median tail arity | P95 tail arity | Max tail arity |"
    )
    return f"""# MathOverflow reconstruction profile

This is a **profile only**. It creates no native events and does not approve an
answer-window, anonymous-user, deleted-post, or duplicate-answerer policy.

## Eligible source records

- Eligible questions with an owner and valid timestamp: `{eligible_questions:,}`
- Questions with missing owner: `{questions["missing_owner"]:,}`
- Answer rows: `{answers["total"]:,}`
- Answers with missing owner: `{answers["missing_owner"]:,}`
- Answers with missing parent: `{answers["missing_parent"]:,}`
- Answers whose parent is not an eligible question: `{parent_not_eligible:,}`
- Self-answers excluded from the proposed answerer → asker relation: `{self_answers:,}`
- Eligible answer records before duplicate-answerer collapse: `{eligible_records:,}`
- Duplicate eligible answer records: `{duplicate_records:,}`
- Distinct question–answerer pairs: `{distinct_pairs:,}`

## First distinct-answerer latency

Values are elapsed calendar days from question creation to the answerer's first
eligible answer to that question: {latency_text}.

## Descriptive window sensitivity

{table_header}
|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The later event construction, if approved, must use exactly one declared window,
exclude anonymous users, collapse duplicate answerers per question, retain only
rows present in this public dump, and retain no comments. These profiles provide
evidence for that choice; they do not select it.
"""


def main() -> None:
    """Run the profile while preserving immutable output records by default."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--windows-days",
        type=parse_windows,
        default=DEFAULT_WINDOWS_DAYS,
        help="Comma-separated descriptive answer windows; default: 1,7,30,90,365",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"STOP: MathOverflow Posts.xml is missing: {args.input}")
    outputs = (args.summary, args.report)
    if not args.overwrite and any(path.exists() for path in outputs):
        raise SystemExit("STOP: reconstruction-profile output already exists; pass --overwrite")

    summary = profile(args.input, args.windows_days)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(render_report(summary), encoding="utf-8")
    print("MathOverflow reconstruction profile passed.")
    distinct_pairs = summary["answers"]["distinct_question_answerer_pairs"]
    print(f"Distinct question-answerer pairs: {distinct_pairs:,}.")
    print(f"Summary: {args.summary}")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
