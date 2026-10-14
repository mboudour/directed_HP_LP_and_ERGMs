#!/usr/bin/env python3
"""Aggregate audited Enron native events into an address-level directed multigraph."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import median

import pyarrow as pa
import pyarrow.parquet as pq

BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "native_events_address_level.parquet"
EVENT_SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_level_event_build_summary.json"
)
OUTPUT = (
    PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "address_level_directed_arcs.parquet"
)
TEMP_OUTPUT = OUTPUT.with_suffix(".parquet.tmp")
SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_level_arc_aggregation_summary.json"
)
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_address_level_arc_aggregation.md"

SCHEMA = pa.schema(
    [
        pa.field("tail_address", pa.string()),
        pa.field("head_address", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: address-level event table not found:\n"
            f"  {INPUT}\n"
            "Run scripts/11_build_enron_address_level_events.py first."
        )

    if not EVENT_SUMMARY.is_file():
        raise SystemExit(
            "STOP: address-level event summary not found:\n"
            f"  {EVENT_SUMMARY}\n"
            "Run scripts/11_build_enron_address_level_events.py first."
        )

    existing_outputs = [path for path in (OUTPUT, TEMP_OUTPUT, SUMMARY, REPORT) if path.exists()]
    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: address-level arc output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    expected_events = int(
        json.loads(EVENT_SUMMARY.read_text(encoding="utf-8"))["native_events_written"]
    )

    arc_counts: Counter[tuple[str, str]] = Counter()
    nodes: set[str] = set()
    event_count = 0
    arc_occurrences = 0
    self_arcs = 0

    parquet_file = pq.ParquetFile(INPUT)

    for batch in parquet_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["sender_address", "head_addresses"],
    ):
        for record in batch.to_pylist():
            event_count += 1

            tail = str(record["sender_address"])
            heads = list(record["head_addresses"])

            nodes.add(tail)
            nodes.update(heads)
            arc_occurrences += len(heads)
            self_arcs += sum(tail == head for head in heads)
            arc_counts.update((tail, head) for head in heads)

    if event_count != expected_events:
        raise SystemExit(
            f"STOP: event-count mismatch.\nExpected: {expected_events:,}\nFound:    {event_count:,}"
        )

    if self_arcs:
        raise SystemExit(
            "STOP: self arcs found despite the native-event construction rule.\n"
            f"Self arcs: {self_arcs:,}"
        )

    sorted_arc_keys = sorted(arc_counts)

    out_degree = Counter(tail for tail, _ in arc_counts)
    in_degree = Counter(head for _, head in arc_counts)

    reciprocal_pairs = sum(
        1 for tail, head in arc_counts if tail < head and (head, tail) in arc_counts
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    try:
        with pq.ParquetWriter(TEMP_OUTPUT, SCHEMA, compression="zstd") as writer:
            for start in range(0, len(sorted_arc_keys), BATCH_SIZE):
                arc_keys = sorted_arc_keys[start : start + BATCH_SIZE]

                rows = [
                    {
                        "tail_address": tail,
                        "head_address": head,
                        "interaction_count": arc_counts[(tail, head)],
                    }
                    for tail, head in arc_keys
                ]

                writer.write_table(pa.Table.from_pylist(rows, schema=SCHEMA))

        TEMP_OUTPUT.replace(OUTPUT)

    except Exception:
        if TEMP_OUTPUT.exists():
            TEMP_OUTPUT.unlink()
        raise

    node_count = len(nodes)
    arc_count = len(arc_counts)
    possible_arcs = node_count * (node_count - 1)

    summary = {
        "dataset_id": "enron_20150507",
        "input": str(INPUT.relative_to(PROJECT_ROOT)),
        "output": str(OUTPUT.relative_to(PROJECT_ROOT)),
        "native_events_read": event_count,
        "event_to_arc_occurrences": arc_occurrences,
        "unique_address_level_nodes": node_count,
        "unique_directed_arcs": arc_count,
        "self_arcs": self_arcs,
        "reciprocal_unordered_pairs": reciprocal_pairs,
        "reciprocal_directed_arcs": 2 * reciprocal_pairs,
        "directed_density_excluding_loops": arc_count / possible_arcs,
        "interaction_count_total": sum(arc_counts.values()),
        "median_unique_out_degree": median(out_degree.values()),
        "median_unique_in_degree": median(in_degree.values()),
        "maximum_unique_out_degree": max(out_degree.values()),
        "maximum_unique_in_degree": max(in_degree.values()),
        "aggregation_policy": (
            "Each native event contributes one directed arc from its sender to each "
            "recipient in its disjoint To-plus-Cc head."
        ),
        "next_processing_step": (
            "Select and audit a reproducible Enron core before ERGM estimation or "
            "formal-concept enumeration."
        ),
    }

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    REPORT.write_text(
        f"""# Enron address-level directed-arc aggregation

## Scope

The address-level native events are aggregated into a directed graph. An arc exists for
every sender-recipient pair observed in one or more retained native events. The Parquet
output remains local because it contains addresses.

- Native events read: `{event_count:,}`
- Event-to-arc occurrences: `{arc_occurrences:,}`
- Unique address-level nodes: `{node_count:,}`
- Unique directed arcs: `{arc_count:,}`
- Self arcs: `{self_arcs:,}`
- Reciprocal unordered pairs: `{reciprocal_pairs:,}`
- Directed density, excluding loops:
  `{summary["directed_density_excluding_loops"]:.8f}`

## Aggregation rule

Each event contributes one arc from its sender to every address in its To-plus-Cc head.
Arc weights equal the number of retained native events containing that ordered dyad.
This creates the address-level graph only; it does not resolve aliases or choose the
smaller core graph used for concept enumeration and ERGM estimation.
""",
        encoding="utf-8",
    )

    print("Enron address-level arc aggregation passed.")
    print(f"Native events read: {event_count:,}.")
    print(f"Event-to-arc occurrences: {arc_occurrences:,}.")
    print(f"Unique address-level nodes: {node_count:,}.")
    print(f"Unique directed arcs: {arc_count:,}.")
    print(f"Reciprocal unordered pairs: {reciprocal_pairs:,}.")
    print(f"Self arcs: {self_arcs:,}.")
    print(f"Arc table: {OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
