#!/usr/bin/env python3
"""Profile retained Enron event timestamps before a custodian projection policy is chosen.

This audit is deliberately aggregate-only. It neither selects a timestamp range nor
filters an event. It provides the counts needed to make the plan's time-range decision
from the native-event candidate table rather than from the raw date extrema alone.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq

EXPECTED_EVENTS = 490_141
BATCH_SIZE = 25_000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "native_events_address_level.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_event_timestamp_profile.json"
YEAR_COUNTS = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_event_timestamp_year_counts.csv"
MONTH_COUNTS = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_event_timestamp_month_counts.csv"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_event_timestamp_profile.md"
OUTPUTS = (SUMMARY, YEAR_COUNTS, MONTH_COUNTS, REPORT)


def display_path(path: Path) -> str:
    """Use a repository-relative path where possible without rejecting external fixtures."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    """Parse the explicit rerun flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only aggregate timestamp-profile outputs produced by this driver.",
    )
    return parser.parse_args()


def prepare_outputs(overwrite: bool) -> None:
    """Protect existing audit evidence unless an explicit deterministic refresh is requested."""
    existing = [path for path in OUTPUTS if path.exists()]
    if existing and not overwrite:
        rendered = "\n  ".join(display_path(path) for path in existing)
        raise SystemExit(
            "STOP: timestamp-profile output already exists. Pass --overwrite to replace only "
            f"this driver's files:\n  {rendered}"
        )
    for path in existing:
        path.unlink()
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write a compact aggregate CSV with portable LF line endings."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Profile the retained address-level event dates without selecting a policy."""
    args = parse_args()
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: address-level Enron event table is missing:\n"
            f"  {INPUT.relative_to(PROJECT_ROOT)}\n"
            "Run scripts/11_build_enron_address_level_events.py first."
        )
    prepare_outputs(args.overwrite)

    input_schema = pq.ParquetFile(INPUT).schema_arrow
    if "sent_at_utc" not in input_schema.names:
        raise SystemExit("STOP: event table is missing the sent_at_utc column.")

    records = 0
    missing_timestamps = 0
    yearly: Counter[int] = Counter()
    monthly: Counter[str] = Counter()
    first: datetime | None = None
    last: datetime | None = None

    for batch in pq.ParquetFile(INPUT).iter_batches(
        batch_size=BATCH_SIZE,
        columns=["sent_at_utc"],
    ):
        for timestamp in batch.column(0).to_pylist():
            records += 1
            if timestamp is None:
                missing_timestamps += 1
                continue
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise SystemExit("STOP: native-event table contains a timezone-free timestamp.")
            yearly[timestamp.year] += 1
            monthly[timestamp.strftime("%Y-%m")] += 1
            first = timestamp if first is None or timestamp < first else first
            last = timestamp if last is None or timestamp > last else last

    if records != EXPECTED_EVENTS:
        raise SystemExit(
            "STOP: unexpected address-level event count.\n"
            f"Expected: {EXPECTED_EVENTS:,}\n"
            f"Found:    {records:,}"
        )
    if missing_timestamps:
        raise SystemExit(
            "STOP: a retained native-event table must have no missing timestamps; "
            f"found {missing_timestamps:,}."
        )
    assert first is not None and last is not None

    year_rows = [{"year": year, "native_events": yearly[year]} for year in sorted(yearly)]
    month_rows = [{"month": month, "native_events": monthly[month]} for month in sorted(monthly)]
    write_csv(YEAR_COUNTS, ["year", "native_events"], year_rows)
    write_csv(MONTH_COUNTS, ["month", "native_events"], month_rows)

    summary = {
        "dataset_id": "enron_20150507",
        "driver": "scripts/14_profile_enron_event_timestamps.py",
        "input": display_path(INPUT),
        "address_level_events_profiled": records,
        "missing_timestamps": missing_timestamps,
        "timestamp_span_utc": {"minimum": first.isoformat(), "maximum": last.isoformat()},
        "calendar_years_observed": list(sorted(yearly)),
        "calendar_year_counts": {str(year): yearly[year] for year in sorted(yearly)},
        "calendar_month_count": len(monthly),
        "policy_status": (
            "No timestamp range has been selected. Use the aggregate year/month outputs to "
            "choose and record an inclusive, timezone-aware policy before custodian projection."
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    year_table = "\n".join(f"| {year} | {yearly[year]:,} |" for year in sorted(yearly))
    REPORT.write_text(
        "# Enron address-level event timestamp profile\n\n"
        "## Scope\n\n"
        "This audit counts dates in the already retained address-level native-event candidates. "
        "It does not remove events, select a study period, or approve the custodian projection.\n\n"
        f"- Address-level native events profiled: `{records:,}`\n"
        f"- Missing timestamps: `{missing_timestamps:,}`\n"
        f"- Earliest timestamp: `{first.isoformat()}`\n"
        f"- Latest timestamp: `{last.isoformat()}`\n"
        f"- Distinct calendar months with one or more events: `{len(monthly):,}`\n\n"
        "## Counts by calendar year\n\n"
        "| Year | Native events |\n|---:|---:|\n"
        f"{year_table}\n\n"
        "## Required next decision\n\n"
        "Before the primary custodian-node projection, record one inclusive, timezone-aware "
        "timestamp interval in the Enron gate file. The chosen interval must be justified from "
        "these aggregate counts and applied before monthly panels are created.\n",
        encoding="utf-8",
    )

    print("Enron event timestamp profile passed.")
    print(f"Address-level native events profiled: {records:,}.")
    print(f"Timestamp span: {first.isoformat()} to {last.isoformat()}.")
    print(f"Calendar years observed: {', '.join(str(year) for year in sorted(yearly))}.")
    print(f"Year counts: {display_path(YEAR_COUNTS)}")
    print(f"Summary: {display_path(SUMMARY)}")
    print(f"Audit report: {display_path(REPORT)}")


if __name__ == "__main__":
    main()
