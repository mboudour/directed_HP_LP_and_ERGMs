#!/usr/bin/env python3
"""Prepare audited EU-core static, core-100, and temporal-panel inputs."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

EXPECTED_ROWS = 332_334
CORE_SIZE = 100
WINDOW_WIDTHS_DAYS = (14, 28, 30)
SECONDS_PER_DAY = 86_400
BATCH_SIZE = 25_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "data" / "raw" / "email_eu_core_temporal" / "email-Eu-core-temporal.txt"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "email_eu_core_temporal"
FULL_ARCS = OUTPUT_DIR / "full_static_arcs.parquet"
CORE_NODES = OUTPUT_DIR / "core100_nodes.csv"
CORE_ARCS = OUTPUT_DIR / "core100_static_arcs.parquet"
CORE_WINDOWS = {
    width: OUTPUT_DIR / f"core100_windows_{width}d.parquet" for width in WINDOW_WIDTHS_DAYS
}
SUMMARY = PROJECT_ROOT / "data" / "metadata" / "email_eu_core_temporal_preparation.json"
REPORT = PROJECT_ROOT / "docs" / "data_audits" / "email_eu_core_temporal_preparation.md"

ARC_SCHEMA = pa.schema(
    [
        pa.field("tail", pa.int32()),
        pa.field("head", pa.int32()),
        pa.field("interaction_count", pa.int32()),
    ]
)
WINDOW_SCHEMA = pa.schema(
    [
        pa.field("window_width_days", pa.int16()),
        pa.field("window_index", pa.int16()),
        pa.field("window_start_unix", pa.int64()),
        pa.field("tail", pa.int32()),
        pa.field("head", pa.int32()),
        pa.field("interaction_count", pa.int32()),
    ]
)


def read_rows(path: Path) -> list[tuple[int, int, int]]:
    """Read the documented three-column SNAP row format with strict validation."""
    rows: list[tuple[int, int, int]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            fields = stripped.split()
            if len(fields) != 3:
                raise ValueError(
                    f"row {line_number:,} has {len(fields)} fields; expected exactly three"
                )
            try:
                tail, head, timestamp = (int(field) for field in fields)
            except ValueError as error:
                raise ValueError(f"row {line_number:,} has a non-integer field") from error
            rows.append((tail, head, timestamp))
    return rows


def write_parquet_rows(path: Path, rows: list[dict[str, int]], schema: pa.Schema) -> None:
    """Write modest derived tables with a declared schema."""
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, path, compression="zstd")


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(
            "STOP: EU-core source file is missing:\n"
            f"  {INPUT}\n"
            "Preserve the downloaded archive and place its uncompressed text file there."
        )

    outputs = [FULL_ARCS, CORE_NODES, CORE_ARCS, *CORE_WINDOWS.values(), SUMMARY, REPORT]
    existing = [path for path in outputs if path.exists()]
    if existing:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing)
        raise SystemExit(
            "STOP: EU-core preparation output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    rows = read_rows(INPUT)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(
            "STOP: unexpected EU-core temporal-row count.\n"
            f"Expected: {EXPECTED_ROWS:,}\n"
            f"Found:    {len(rows):,}"
        )

    sent_activity: Counter[int] = Counter()
    received_activity: Counter[int] = Counter()
    full_arc_counts: Counter[tuple[int, int]] = Counter()
    sender_timestamp_counts: Counter[tuple[int, int]] = Counter()
    loop_rows = 0

    for tail, head, timestamp in rows:
        if tail == head:
            loop_rows += 1
            continue
        sent_activity[tail] += 1
        received_activity[head] += 1
        full_arc_counts[(tail, head)] += 1
        sender_timestamp_counts[(tail, timestamp)] += 1

    nodes = set(sent_activity) | set(received_activity)
    if len(nodes) < CORE_SIZE:
        raise SystemExit(f"STOP: only {len(nodes):,} nodes; cannot select core-{CORE_SIZE}")

    ranked_nodes = sorted(
        nodes,
        key=lambda node: (-(sent_activity[node] + received_activity[node]), node),
    )
    core = set(ranked_nodes[:CORE_SIZE])

    core_arc_counts: Counter[tuple[int, int]] = Counter()
    core_windows: dict[int, Counter[tuple[int, int, int]]] = {
        width: Counter() for width in WINDOW_WIDTHS_DAYS
    }
    first_timestamp = min(timestamp for _, _, timestamp in rows)
    core_row_count = 0

    for tail, head, timestamp in rows:
        if tail not in core or head not in core or tail == head:
            continue
        core_row_count += 1
        core_arc_counts[(tail, head)] += 1
        for width in WINDOW_WIDTHS_DAYS:
            window_index = (timestamp - first_timestamp) // (width * SECONDS_PER_DAY)
            core_windows[width][(window_index, tail, head)] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    full_rows = [
        {"tail": tail, "head": head, "interaction_count": count}
        for (tail, head), count in sorted(full_arc_counts.items())
    ]
    core_arc_rows = [
        {"tail": tail, "head": head, "interaction_count": count}
        for (tail, head), count in sorted(core_arc_counts.items())
    ]
    write_parquet_rows(FULL_ARCS, full_rows, ARC_SCHEMA)
    write_parquet_rows(CORE_ARCS, core_arc_rows, ARC_SCHEMA)

    with CORE_NODES.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["rank", "node", "sent_activity", "received_activity", "total_activity"],
            lineterminator="\n",
        )
        writer.writeheader()
        for rank, node in enumerate(ranked_nodes[:CORE_SIZE], start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "node": node,
                    "sent_activity": sent_activity[node],
                    "received_activity": received_activity[node],
                    "total_activity": sent_activity[node] + received_activity[node],
                }
            )

    panel_counts: dict[str, int] = {}
    for width, counts in core_windows.items():
        panel_rows = [
            {
                "window_width_days": width,
                "window_index": index,
                "window_start_unix": first_timestamp + index * width * SECONDS_PER_DAY,
                "tail": tail,
                "head": head,
                "interaction_count": count,
            }
            for (index, tail, head), count in sorted(counts.items())
        ]
        write_parquet_rows(CORE_WINDOWS[width], panel_rows, WINDOW_SCHEMA)
        panel_counts[str(width)] = len({index for index, _, _ in counts})

    bundled_rows = sum(count for count in sender_timestamp_counts.values() if count > 1)
    bundled_groups = sum(count > 1 for count in sender_timestamp_counts.values())
    summary = {
        "dataset_id": "email_eu_core_temporal",
        "source": str(INPUT.relative_to(PROJECT_ROOT)),
        "temporal_rows_read": len(rows),
        "self_loop_rows_removed": loop_rows,
        "nodes_after_loop_removal": len(nodes),
        "full_static_directed_arcs": len(full_arc_counts),
        "time_span_utc": {
            "minimum": datetime.fromtimestamp(first_timestamp, tz=UTC).isoformat(),
            "maximum": datetime.fromtimestamp(
                max(timestamp for _, _, timestamp in rows), tz=UTC
            ).isoformat(),
        },
        "core_rule": "top_100_by_sent_plus_received_temporal_row_activity",
        "core_nodes": CORE_SIZE,
        "core_temporal_rows": core_row_count,
        "core_static_directed_arcs": len(core_arc_counts),
        "window_width_days": list(WINDOW_WIDTHS_DAYS),
        "non_singleton_sender_timestamp_groups": bundled_groups,
        "rows_in_non_singleton_sender_timestamp_groups": bundled_rows,
        "native_event_status": (
            "Unsupported in the primary design because message identifiers and recipient "
            "bundles are absent. Timestamp bundles remain a sensitivity diagnostic only."
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    window_rows = "\n".join(
        f"| {width} | {panel_counts[str(width)]:,} |" for width in WINDOW_WIDTHS_DAYS
    )
    REPORT.write_text(
        f"""# EU-core preparation audit

## Derived objects

- Temporal rows read: `{len(rows):,}`
- Nodes after loop removal: `{len(nodes):,}`
- Full static directed arcs: `{len(full_arc_counts):,}`
- Core rule: top 100 actors by sent plus received row activity
- Core temporal rows: `{core_row_count:,}`
- Core static directed arcs: `{len(core_arc_counts):,}`

## Temporal panels

| Window width (days) | Nonempty core windows |
|---:|---:|
{window_rows}

## Recipient-bundle sensitivity diagnostic

There are `{bundled_groups:,}` repeated `(sender, timestamp)` groups comprising
`{bundled_rows:,}` rows. These are not treated as native events in the primary design,
because the dataset contains no message identifier and SNAP supplies one row per recipient.
""",
        encoding="utf-8",
    )

    print("EU-core preparation passed.")
    print(f"Temporal rows read: {len(rows):,}.")
    print(f"Full static directed arcs: {len(full_arc_counts):,}.")
    print(f"Core nodes: {CORE_SIZE:,}.")
    print(f"Core static directed arcs: {len(core_arc_counts):,}.")
    print(f"Summary: {SUMMARY.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {REPORT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
