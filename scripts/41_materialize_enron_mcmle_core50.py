#!/usr/bin/env python3
"""Materialize the approved nested Enron core-50 for MCMLE feasibility only."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

CORE_SIZE = 50
BATCH_SIZE = 25_000
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVENTS = (
    PROJECT_ROOT / "data" / "processed" / "enron_20150507" / "custodian_native_events.parquet"
)
SOURCE_NODES = (
    PROJECT_ROOT / "data" / "processed" / "enron_20150507" / "custodian_core100_nodes.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "enron_20150507"
OUTPUT_NODES = OUTPUT_DIR / "custodian_mcmle_core50_nodes.csv"
OUTPUT_EVENTS = OUTPUT_DIR / "custodian_mcmle_core50_native_events.parquet"
OUTPUT_ARCS = OUTPUT_DIR / "custodian_mcmle_core50_static_arcs.parquet"
OUTPUT_MONTHLY_ARCS = OUTPUT_DIR / "custodian_mcmle_core50_monthly_arcs.parquet"
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_mcmle_core50.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_mcmle_core50.md"

EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string()),
        pa.field("sent_at_utc", pa.timestamp("us", tz="UTC")),
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodians", pa.list_(pa.string())),
    ]
)
ARC_SCHEMA = pa.schema(
    [
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodian", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)
MONTHLY_ARC_SCHEMA = pa.schema(
    [
        pa.field("month", pa.string()),
        pa.field("tail_custodian", pa.string()),
        pa.field("head_custodian", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)


def parse_args() -> argparse.Namespace:
    """Parse the explicit output-refresh request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only outputs derived by this MCMLE-feasibility core builder.",
    )
    return parser.parse_args()


def month_label(timestamp: object) -> str:
    """Convert a timezone-aware event timestamp to its calendar-month label."""
    return f"{timestamp.year:04d}-{timestamp.month:02d}"


def read_nested_core() -> list[dict[str, str]]:
    """Select the deterministic top core-size subset of the already approved core-100."""
    if not SOURCE_NODES.is_file():
        raise SystemExit(
            "STOP: strict Enron core-100 nodes are missing; run phase2-enron-primary first: "
            f"{SOURCE_NODES.relative_to(PROJECT_ROOT)}"
        )
    with SOURCE_NODES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "rank",
        "custodian_mailbox",
        "sent_activity",
        "received_activity",
        "total_activity",
    }
    if not rows or rows[0].keys() is None or required - set(rows[0]):
        raise SystemExit(f"STOP: core-100 node CSV must contain {sorted(required)}")
    try:
        ranked = sorted(rows, key=lambda row: int(row["rank"]))
    except ValueError as error:
        raise SystemExit("STOP: core-100 node CSV has a non-integer rank") from error
    selected = ranked[:CORE_SIZE]
    selected_nodes = [row["custodian_mailbox"].strip() for row in selected]
    if (
        len(selected) != CORE_SIZE
        or len(set(selected_nodes)) != CORE_SIZE
        or any(not node for node in selected_nodes)
    ):
        source = SOURCE_NODES.relative_to(PROJECT_ROOT)
        raise SystemExit(f"STOP: expected {CORE_SIZE} unique ranked core nodes in {source}")
    expected_ranks = list(range(1, CORE_SIZE + 1))
    actual_ranks = [int(row["rank"]) for row in selected]
    if actual_ranks != expected_ranks:
        raise SystemExit(
            "STOP: MCMLE feasibility core must be the nested rank-1 through "
            f"rank-{CORE_SIZE} subset of the primary core-100."
        )
    return selected


def prepare_outputs(overwrite: bool) -> None:
    """Protect existing derived feasibility outputs unless explicit replacement is requested."""
    outputs = [
        OUTPUT_NODES,
        OUTPUT_EVENTS,
        OUTPUT_ARCS,
        OUTPUT_MONTHLY_ARCS,
        SUMMARY,
        REPORT,
    ]
    existing = [path for path in outputs if path.exists()]
    if existing and not overwrite:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing)
        raise SystemExit(
            "STOP: MCMLE-feasibility core outputs already exist. Pass --overwrite to replace:\n"
            f"  {rendered}"
        )
    for path in existing:
        path.unlink()


def write_nodes(rows: list[dict[str, str]]) -> None:
    """Write the nested primary-core metadata without recalculating activity ranks."""
    OUTPUT_NODES.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_NODES.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "custodian_mailbox",
                "sent_activity",
                "received_activity",
                "total_activity",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Build a nested, fixed-node core-50 strictly for MCMLE feasibility assessment."""
    args = parse_args()
    if not SOURCE_EVENTS.is_file():
        raise SystemExit(
            "STOP: strict projected Enron events are missing; run phase2-enron-primary first: "
            f"{SOURCE_EVENTS.relative_to(PROJECT_ROOT)}"
        )
    core_rows = read_nested_core()
    core_nodes = {row["custodian_mailbox"] for row in core_rows}
    prepare_outputs(args.overwrite)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    write_nodes(core_rows)

    retained_events = 0
    source_events = 0
    excluded_outside_core = 0
    arc_counts: Counter[tuple[str, str]] = Counter()
    monthly_arc_counts: Counter[tuple[str, str, str]] = Counter()
    buffer: list[dict[str, object]] = []
    writer = pq.ParquetWriter(OUTPUT_EVENTS, EVENT_SCHEMA, compression="zstd")
    try:
        source = pq.ParquetFile(SOURCE_EVENTS)
        for batch in source.iter_batches(batch_size=BATCH_SIZE):
            for record in batch.to_pylist():
                source_events += 1
                tail = str(record["tail_custodian"])
                heads = [str(value) for value in record["head_custodians"]]
                if tail not in core_nodes or not all(head in core_nodes for head in heads):
                    excluded_outside_core += 1
                    continue
                retained_events += 1
                buffer.append(
                    {
                        "event_id": str(record["event_id"]),
                        "sent_at_utc": record["sent_at_utc"],
                        "tail_custodian": tail,
                        "head_custodians": heads,
                    }
                )
                month = month_label(record["sent_at_utc"])
                for head in heads:
                    arc_counts[(tail, head)] += 1
                    monthly_arc_counts[(month, tail, head)] += 1
                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
                    buffer.clear()
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=EVENT_SCHEMA))
    except Exception:
        writer.close()
        if OUTPUT_EVENTS.exists():
            OUTPUT_EVENTS.unlink()
        raise
    writer.close()

    pq.write_table(
        pa.Table.from_pylist(
            [
                {"tail_custodian": tail, "head_custodian": head, "interaction_count": count}
                for (tail, head), count in sorted(arc_counts.items())
            ],
            schema=ARC_SCHEMA,
        ),
        OUTPUT_ARCS,
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "month": month,
                    "tail_custodian": tail,
                    "head_custodian": head,
                    "interaction_count": count,
                }
                for (month, tail, head), count in sorted(monthly_arc_counts.items())
            ],
            schema=MONTHLY_ARC_SCHEMA,
        ),
        OUTPUT_MONTHLY_ARCS,
        compression="zstd",
    )

    summary = {
        "dataset_id": "enron_20150507",
        "purpose": "mcmle_feasibility_only_not_primary_benchmark_core",
        "parent_core_rule": (
            "top_100_by_sent_plus_received_activity_within_projected_custodian_nodes"
        ),
        "nested_core_rule": "rank_1_through_50_subset_of_primary_core_100",
        "core_nodes": CORE_SIZE,
        "source_projected_events": source_events,
        "retained_all_participant_events": retained_events,
        "excluded_events_with_participant_outside_core": excluded_outside_core,
        "static_directed_arcs": len(arc_counts),
        "nonempty_calendar_months": len({month for month, _, _ in monthly_arc_counts}),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        f"""# Enron nested core-{CORE_SIZE} for MCMLE feasibility

- Purpose: **MCMLE feasibility and conditional-joint-score sensitivity only**
- Parent node rule: top-100 by sent-plus-received activity in the strict projected custodian network
- Nested node rule: parent ranks `1` through `{CORE_SIZE}` without reranking or tuning
- Fixed nodes: `{CORE_SIZE}`
- Strict projected events read: `{source_events:,}`
- All-participant events retained: `{retained_events:,}`
- Events excluded because a participant lies outside the nested core: `{excluded_outside_core:,}`
- Static directed arcs: `{len(arc_counts):,}`
- Nonempty calendar months: `{len({month for month, _, _ in monthly_arc_counts}):,}`

This is not a replacement for the primary core-100 benchmark. It exists because
M2 and M4 MCMLE did not mix on the core-100 pilot. All primary masking, heuristic,
MPLE, formal-concept, and native-event results remain defined on the core-100 unless
an explicit later decision changes that scope.
""",
        encoding="utf-8",
    )
    print("Enron MCMLE-feasibility core materialization passed.")
    print(f"Fixed nested core nodes: {CORE_SIZE}.")
    print(f"All-participant events retained: {retained_events:,}.")
    print(f"Static directed arcs: {len(arc_counts):,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
