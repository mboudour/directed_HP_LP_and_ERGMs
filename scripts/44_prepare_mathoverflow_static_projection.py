#!/usr/bin/env python3
"""Build deterministic MathOverflow static arcs and an all-participant core from approved events."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

BATCH_SIZE = 25_000
DEFAULT_CORE_SIZE = 100
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mathoverflow_stackexchange_2024"
    / "native_events.parquet"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "mathoverflow_stackexchange_2024"
DEFAULT_SUMMARY = (
    PROJECT_ROOT / "data" / "metadata" / "mathoverflow_stackexchange_2024_static_projection.json"
)
DEFAULT_REPORT = (
    PROJECT_ROOT / "docs" / "data_audits" / "mathoverflow_stackexchange_2024_static_projection.md"
)

ARC_SCHEMA = pa.schema(
    [
        pa.field("tail", pa.string()),
        pa.field("head", pa.string()),
        pa.field("interaction_count", pa.int32()),
    ]
)


def display_path(path: Path) -> str:
    """Use a repository-relative path when available, otherwise retain the provided path."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    """Parse explicit source and output contracts for the static projection."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--core-size", type=int, default=DEFAULT_CORE_SIZE)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.core_size < 1:
        parser.error("--core-size must be at least one")
    return args


def output_paths(output_dir: Path) -> tuple[Path, Path, Path, Path]:
    """Return full-graph, core-graph, core-event, and node output locations."""
    return (
        output_dir / "static_arcs.parquet",
        output_dir / "core100_static_arcs.parquet",
        output_dir / "core100_native_events.parquet",
        output_dir / "core100_nodes.csv",
    )


def validate_event(record: dict[str, object]) -> tuple[str, tuple[str, ...], str]:
    """Check the reconstructed-event invariants before using its identities."""
    event_id = str(record.get("event_id") or "")
    raw_tail = record.get("tail_answerers")
    head = str(record.get("head_asker") or "")
    if not event_id or not isinstance(raw_tail, list) or not head:
        raise ValueError("event needs nonempty event_id, list tail_answerers, and head_asker")
    tail = tuple(str(value) for value in raw_tail)
    if not tail or any(not value for value in tail):
        raise ValueError(f"event has an empty tail participant: {event_id}")
    if len(set(tail)) != len(tail):
        raise ValueError(f"event repeats a tail participant: {event_id}")
    if head in tail:
        raise ValueError(f"event has overlapping tail/head roles: {event_id}")
    return event_id, tail, head


def prepare_outputs(paths: tuple[Path, ...], overwrite: bool) -> None:
    """Protect or deliberately replace only this driver's derived outputs."""
    existing = [path for path in paths if path.exists()]
    if existing and not overwrite:
        rendered = "\n  ".join(display_path(path) for path in existing)
        raise SystemExit(
            "STOP: MathOverflow static projection output already exists. "
            f"Pass --overwrite to replace only this driver's outputs:\n  {rendered}"
        )
    for path in existing:
        path.unlink()


def write_arc_table(counts: Counter[tuple[str, str]], path: Path) -> None:
    """Write deterministically sorted interaction-counted directed arcs."""
    rows = [
        {"tail": tail, "head": head, "interaction_count": count}
        for (tail, head), count in sorted(counts.items())
    ]
    pq.write_table(pa.Table.from_pylist(rows, schema=ARC_SCHEMA), path, compression="zstd")


def main() -> None:
    """Build full and core static views without changing approved native events."""
    args = parse_args()
    events_path = args.events if args.events.is_absolute() else PROJECT_ROOT / args.events
    output_dir = (
        args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    )
    summary_path = args.summary if args.summary.is_absolute() else PROJECT_ROOT / args.summary
    report_path = args.report if args.report.is_absolute() else PROJECT_ROOT / args.report
    if not events_path.is_file():
        raise SystemExit(f"STOP: approved MathOverflow events are missing: {events_path}")

    full_arcs_path, core_arcs_path, core_events_path, nodes_path = output_paths(output_dir)
    outputs = (
        full_arcs_path,
        core_arcs_path,
        core_events_path,
        nodes_path,
        summary_path,
        report_path,
    )
    prepare_outputs(outputs, args.overwrite)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    source = pq.ParquetFile(events_path)
    required = {"event_id", "tail_answerers", "head_asker"}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: approved event table lacks required columns: {sorted(missing)}")

    sent_activity: Counter[str] = Counter()
    received_activity: Counter[str] = Counter()
    source_events = 0
    for batch in source.iter_batches(batch_size=BATCH_SIZE):
        for record in batch.to_pylist():
            _, tail, head = validate_event(record)
            source_events += 1
            for tail_node in tail:
                sent_activity[tail_node] += 1
            received_activity[head] += 1

    nodes = set(sent_activity) | set(received_activity)
    ranked = sorted(
        nodes,
        key=lambda node: (-(sent_activity[node] + received_activity[node]), node),
    )
    core_size = min(args.core_size, len(ranked))
    core = set(ranked[:core_size])
    if not core:
        raise SystemExit("STOP: no valid node remains after event validation")

    with nodes_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["rank", "node", "sent_activity", "received_activity", "total_activity"],
            lineterminator="\n",
        )
        writer.writeheader()
        for rank, node in enumerate(ranked[:core_size], start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "node": node,
                    "sent_activity": sent_activity[node],
                    "received_activity": received_activity[node],
                    "total_activity": sent_activity[node] + received_activity[node],
                }
            )

    full_arc_counts: Counter[tuple[str, str]] = Counter()
    core_arc_counts: Counter[tuple[str, str]] = Counter()
    core_event_count = 0
    buffer: list[dict[str, object]] = []
    writer = pq.ParquetWriter(core_events_path, source.schema_arrow, compression="zstd")
    try:
        for batch in source.iter_batches(batch_size=BATCH_SIZE):
            for record in batch.to_pylist():
                _, tail, head = validate_event(record)
                for tail_node in tail:
                    full_arc_counts[(tail_node, head)] += 1
                if head not in core or not all(tail_node in core for tail_node in tail):
                    continue
                core_event_count += 1
                buffer.append(record)
                for tail_node in tail:
                    core_arc_counts[(tail_node, head)] += 1
                if len(buffer) >= BATCH_SIZE:
                    writer.write_table(pa.Table.from_pylist(buffer, schema=source.schema_arrow))
                    buffer.clear()
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=source.schema_arrow))
    except Exception:
        writer.close()
        if core_events_path.exists():
            core_events_path.unlink()
        raise
    writer.close()

    write_arc_table(full_arc_counts, full_arcs_path)
    write_arc_table(core_arc_counts, core_arcs_path)
    summary = {
        "dataset_id": "mathoverflow_stackexchange_2024",
        "source_events": display_path(events_path),
        "source_native_events": source_events,
        "source_nodes": len(nodes),
        "source_static_arcs": len(full_arc_counts),
        "core_rule": "top_by_sent_plus_received_event_participation_stable_node_id_tiebreak",
        "requested_core_size": args.core_size,
        "core_nodes": core_size,
        "core_size_exception": core_size < args.core_size,
        "core_all_participant_events": core_event_count,
        "core_static_arcs": len(core_arc_counts),
        "event_construction": "reconstructed_distinct_answerers_to_question_asker_within_30_days",
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(
        f"""# MathOverflow static projection and core preparation

- Approved reconstructed native events read: `{source_events:,}`
- Nodes in the full reconstructed-event view: `{len(nodes):,}`
- Full static directed arcs: `{len(full_arc_counts):,}`
- Core rule: top `{core_size:,}` by sent-plus-received reconstructed-event participation
- Core all-participant native events: `{core_event_count:,}`
- Core static directed arcs: `{len(core_arc_counts):,}`
- Core-size exception: `{core_size < args.core_size}`

The core retains only events whose answerer tail and asker head all belong to
its fixed activity-ranked node universe. The static graph is derived from this
same all-participant core-event view. These are reconstructed question-answer
events, not observed multi-recipient messages.
""",
        encoding="utf-8",
    )
    print("MathOverflow static projection passed.")
    print(f"Approved native events read: {source_events:,}.")
    print(f"Core nodes: {core_size:,}; core static arcs: {len(core_arc_counts):,}.")
    print(f"Summary: {display_path(summary_path)}")
    print(f"Report: {display_path(report_path)}")


if __name__ == "__main__":
    main()
