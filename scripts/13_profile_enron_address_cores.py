#!/usr/bin/env python3
"""Profile nested Enron address-level core candidates without selecting one."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

THRESHOLDS = (1, 2, 5, 10, 20, 50)
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCS = PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "address_level_directed_arcs.parquet"
EVENTS = (
    PROJECT_ROOT / "data" / "interim" / "enron_20150507" / "native_events_address_level.parquet"
)
ARC_SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_level_arc_aggregation_summary.json"
)
EVENT_SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_level_event_build_summary.json"
)
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "enron_20150507_address_core_profile.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "enron_20150507_address_core_profile.md"


def decimal_or_na(value: float | None, digits: int = 6) -> str:
    """Format an optional proportion for a Markdown audit table."""
    if value is None:
        return "n/a"

    return f"{value:.{digits}f}"


def percent_or_na(value: float | None) -> str:
    """Format an optional proportion as a percentage for a Markdown audit table."""
    if value is None:
        return "n/a"

    return f"{value:.3%}"


def main() -> None:
    required_inputs = (ARCS, EVENTS, ARC_SUMMARY, EVENT_SUMMARY)
    missing_inputs = [path for path in required_inputs if not path.is_file()]

    if missing_inputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in missing_inputs)
        raise SystemExit(f"STOP: required input is missing:\n  {rendered}")

    existing_outputs = [path for path in (SUMMARY, REPORT) if path.exists()]

    if existing_outputs:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing_outputs)
        raise SystemExit(
            "STOP: core-profile output already exists. "
            "This script will not overwrite it:\n"
            f"  {rendered}"
        )

    expected_arcs = int(json.loads(ARC_SUMMARY.read_text(encoding="utf-8"))["unique_directed_arcs"])
    expected_events = int(
        json.loads(EVENT_SUMMARY.read_text(encoding="utf-8"))["native_events_written"]
    )

    arc_set: set[tuple[str, str]] = set()
    out_neighbors: dict[str, set[str]] = {}
    in_neighbors: dict[str, set[str]] = {}

    arc_file = pq.ParquetFile(ARCS)

    for batch in arc_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["tail_address", "head_address"],
    ):
        for record in batch.to_pylist():
            tail = str(record["tail_address"])
            head = str(record["head_address"])

            arc_set.add((tail, head))
            out_neighbors.setdefault(tail, set()).add(head)
            in_neighbors.setdefault(head, set()).add(tail)
            out_neighbors.setdefault(head, set())
            in_neighbors.setdefault(tail, set())

    if len(arc_set) != expected_arcs:
        raise SystemExit(
            f"STOP: arc-count mismatch.\nExpected: {expected_arcs:,}\nFound:    {len(arc_set):,}"
        )

    nodes = set(out_neighbors) | set(in_neighbors)

    core_nodes = {
        threshold: {
            node
            for node in nodes
            if len(out_neighbors[node]) >= threshold and len(in_neighbors[node]) >= threshold
        }
        for threshold in THRESHOLDS
    }

    stats = {
        threshold: {
            "nodes": len(core),
            "induced_arcs": 0,
            "reciprocal_unordered_pairs": 0,
            "events_with_sender_in_core": 0,
            "events_all_participants_in_core": 0,
            "recipient_addresses_in_core": 0,
            "recipient_addresses_total": 0,
        }
        for threshold, core in core_nodes.items()
    }

    for threshold, core in core_nodes.items():
        induced_arcs = sum(tail in core and head in core for tail, head in arc_set)

        reciprocal_pairs = sum(
            tail < head and tail in core and head in core and (head, tail) in arc_set
            for tail, head in arc_set
        )

        stats[threshold]["induced_arcs"] = induced_arcs
        stats[threshold]["reciprocal_unordered_pairs"] = reciprocal_pairs

    event_count = 0
    event_file = pq.ParquetFile(EVENTS)

    for batch in event_file.iter_batches(
        batch_size=BATCH_SIZE,
        columns=["sender_address", "head_addresses"],
    ):
        for record in batch.to_pylist():
            event_count += 1

            sender = str(record["sender_address"])
            head = list(record["head_addresses"])

            for threshold, core in core_nodes.items():
                sender_in_core = sender in core
                head_in_core = [address in core for address in head]

                stats[threshold]["events_with_sender_in_core"] += sender_in_core
                stats[threshold]["events_all_participants_in_core"] += sender_in_core and all(
                    head_in_core
                )
                stats[threshold]["recipient_addresses_in_core"] += sum(head_in_core)
                stats[threshold]["recipient_addresses_total"] += len(head)

    if event_count != expected_events:
        raise SystemExit(
            f"STOP: event-count mismatch.\nExpected: {expected_events:,}\nFound:    {event_count:,}"
        )

    rows: list[dict[str, object]] = []

    for threshold in THRESHOLDS:
        stat = stats[threshold]
        node_count = int(stat["nodes"])
        induced_arcs = int(stat["induced_arcs"])
        possible_arcs = node_count * (node_count - 1)
        recipient_total = int(stat["recipient_addresses_total"])

        rows.append(
            {
                "minimum_unique_in_and_out_degree": threshold,
                "nodes": node_count,
                "induced_arcs": induced_arcs,
                "density_excluding_loops": (
                    induced_arcs / possible_arcs if possible_arcs else None
                ),
                "reciprocal_unordered_pairs": int(stat["reciprocal_unordered_pairs"]),
                "events_with_sender_in_core": int(stat["events_with_sender_in_core"]),
                "events_all_participants_in_core": int(stat["events_all_participants_in_core"]),
                "recipient_address_retention": (
                    int(stat["recipient_addresses_in_core"]) / recipient_total
                    if recipient_total
                    else None
                ),
            }
        )

    summary = {
        "dataset_id": "enron_20150507",
        "candidate_rule": (
            "A node belongs to candidate core k if it has at least k distinct "
            "observed in-neighbors and at least k distinct observed out-neighbors "
            "in the complete address-level graph. Cores are nested descriptive "
            "candidates; no threshold is selected by this profile."
        ),
        "source_nodes": len(nodes),
        "source_arcs": len(arc_set),
        "source_native_events": event_count,
        "threshold_rows": rows,
        "next_decision": (
            "Choose a core threshold after comparing candidate size, density, "
            "reciprocity, and native-event coverage. The selected core must be "
            "documented before ERGM estimation or formal-concept enumeration."
        ),
    }

    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    SUMMARY.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    table_rows = "\n".join(
        "| {k} | {nodes:,} | {arcs:,} | {density} | {reciprocal:,} | "
        "{sender_events:,} | {complete_events:,} | "
        "{recipient_retention} |".format(
            k=row["minimum_unique_in_and_out_degree"],
            nodes=row["nodes"],
            arcs=row["induced_arcs"],
            density=decimal_or_na(row["density_excluding_loops"]),
            reciprocal=row["reciprocal_unordered_pairs"],
            sender_events=row["events_with_sender_in_core"],
            complete_events=row["events_all_participants_in_core"],
            recipient_retention=percent_or_na(row["recipient_address_retention"]),
        )
        for row in rows
    )

    REPORT.write_text(
        f"""# Enron address-level core-candidate profile

## Scope

This audit evaluates nested candidate cores. It does not select, export, or fit any core.

- Source nodes: `{len(nodes):,}`
- Source arcs: `{len(arc_set):,}`
- Source native events: `{event_count:,}`

A node belongs to candidate core `k` if it has at least `k` distinct observed in-neighbors
and at least `k` distinct observed out-neighbors in the complete address-level graph.

| k | Nodes | Arcs | Density | Recip. pairs | Sender events | Full events | Recipient retention |
|---:|---:|---:|---:|---:|---:|---:|---:|
{table_rows}

## Interpretation

The table is a decision aid for reproducible core selection. “Full events” requires the
sender and every recipient of a native event to be in the candidate core; “recipient
retention” is less restrictive and counts recipient positions whose addresses remain in
the core. No threshold has been selected by this script.
""",
        encoding="utf-8",
    )

    print("Enron address-core profile passed.")
    print(f"Source nodes: {len(nodes):,}.")
    print(f"Source arcs: {len(arc_set):,}.")
    print(f"Source native events: {event_count:,}.")

    for row in rows:
        print(
            f"k={row['minimum_unique_in_and_out_degree']}: "
            f"nodes={row['nodes']:,}; arcs={row['induced_arcs']:,}; "
            "all-participant events="
            f"{row['events_all_participants_in_core']:,}."
        )

    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
