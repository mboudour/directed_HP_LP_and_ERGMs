#!/usr/bin/env python3
"""Export a bounded, explicit chronological panel for the temporal R check.

The agreed paper uses temporal data only as a bounded chronological check. This script
exports a selected consecutive range of prepared, dichotomized panel ties and its node
universe. It deliberately does not fit a temporal model or silently choose a forecasting
horizon.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "eu_core": {
        "input": "data/processed/email_eu_core_temporal/core100_windows_30d.parquet",
        "nodes": "data/processed/email_eu_core_temporal/core100_nodes.csv",
        "node_column": "node",
        "time_column": "window_index",
        "tail_column": "tail",
        "head_column": "head",
    },
    "enron": {
        "input": "data/processed/enron_20150507/custodian_core100_monthly_arcs.parquet",
        "nodes": "data/processed/enron_20150507/custodian_core100_nodes.csv",
        "node_column": "custodian_mailbox",
        "time_column": "month",
        "tail_column": "tail_custodian",
        "head_column": "head_custodian",
    },
}


def parse_args() -> argparse.Namespace:
    """Parse an explicit bounded chronological export specification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=sorted(DATASETS))
    parser.add_argument(
        "--input", type=Path, help="Prepared panel Parquet; overrides the dataset default."
    )
    parser.add_argument(
        "--nodes", type=Path, help="Prepared node CSV; overrides the dataset default."
    )
    parser.add_argument(
        "--time-column", help="Prepared panel time column; overrides the dataset default."
    )
    parser.add_argument(
        "--tail-column", help="Prepared panel tail column; overrides the dataset default."
    )
    parser.add_argument(
        "--head-column", help="Prepared panel head column; overrides the dataset default."
    )
    parser.add_argument(
        "--node-column", help="Prepared node CSV ID column; overrides the dataset default."
    )
    parser.add_argument(
        "--start",
        help="First prepared panel label to include; default is the first observed panel.",
    )
    parser.add_argument(
        "--panel-count",
        type=int,
        default=3,
        help="Consecutive observed panel labels to include; default 3.",
    )
    parser.add_argument("--output-dir", type=Path, help="New local output directory.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.panel_count < 2:
        parser.error("--panel-count must be at least 2, so the temporal check has a transition.")
    return args


def resolve(path: Path | None, fallback: str) -> Path:
    """Resolve a user path or default project-local prepared artifact."""
    if path is None:
        return PROJECT_ROOT / fallback
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Record project-relative paths when available, absolute otherwise."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read the frozen core node universe, preserving isolates."""
    if not path.is_file():
        raise SystemExit(f"STOP: prepared node table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks required column {column!r}: {path}")
        nodes = tuple(
            dict.fromkeys(str(row[column]).strip() for row in reader if str(row[column]).strip())
        )
    if len(nodes) < 2:
        raise SystemExit("STOP: temporal check requires at least two declared nodes.")
    return nodes


def read_panel_rows(
    path: Path,
    *,
    time_column: str,
    tail_column: str,
    head_column: str,
) -> dict[str, set[tuple[str, str]]]:
    """Read and dichotomize prepared panel ties without altering labels or order."""
    if not path.is_file():
        raise SystemExit(f"STOP: prepared temporal panel is missing: {path}")
    source = pq.ParquetFile(path)
    required = {time_column, tail_column, head_column}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: temporal panel lacks columns {sorted(missing)}: {path}")
    panels: dict[str, set[tuple[str, str]]] = {}
    for batch in source.iter_batches(
        columns=[time_column, tail_column, head_column], batch_size=50_000
    ):
        for row in batch.to_pylist():
            time = str(row[time_column])
            tail = str(row[tail_column])
            head = str(row[head_column])
            if tail != head:
                panels.setdefault(time, set()).add((tail, head))
    if not panels:
        raise SystemExit("STOP: no loop-free ties exist in the prepared panel table.")
    return panels


def sorted_panel_labels(labels: list[str]) -> list[str]:
    """Sort numeric time labels numerically, else lexical labels deterministically."""
    try:
        return [label for _, label in sorted((int(label), label) for label in labels)]
    except ValueError:
        return sorted(labels)


def main() -> None:
    """Write selected panel ties and nodes in the exact temporal R-driver CSV contract."""
    args = parse_args()
    spec = DATASETS[args.dataset]
    input_path = resolve(args.input, spec["input"])
    nodes_path = resolve(args.nodes, spec["nodes"])
    time_column = args.time_column or spec["time_column"]
    tail_column = args.tail_column or spec["tail_column"]
    head_column = args.head_column or spec["head_column"]
    node_column = args.node_column or spec["node_column"]
    output_dir = (
        args.output_dir or PROJECT_ROOT / "results" / "phase2" / f"{args.dataset}_temporal_check"
    )
    output_dir = output_dir if output_dir.is_absolute() else PROJECT_ROOT / output_dir
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise SystemExit(f"STOP: output directory is nonempty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = read_nodes(nodes_path, node_column)
    panels = read_panel_rows(
        input_path,
        time_column=time_column,
        tail_column=tail_column,
        head_column=head_column,
    )
    labels = sorted_panel_labels(list(panels))
    start = str(args.start) if args.start is not None else labels[0]
    if start not in labels:
        raise SystemExit(f"STOP: --start={start!r} is not an observed prepared panel label.")
    start_index = labels.index(start)
    selected = labels[start_index : start_index + args.panel_count]
    if len(selected) != args.panel_count:
        raise SystemExit(
            f"STOP: only {len(selected)} panel(s) available from start {start!r}; "
            f"requested {args.panel_count}."
        )
    outside_nodes = {node for label in selected for arc in panels[label] for node in arc} - set(
        nodes
    )
    if outside_nodes:
        raise SystemExit(
            "STOP: selected prepared ties contain nodes outside the declared universe: "
            + ", ".join(sorted(outside_nodes)[:10])
        )

    panel_csv = output_dir / "panel_edges.csv"
    with panel_csv.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["time", "from", "to"], lineterminator="\n")
        writer.writeheader()
        for label in selected:
            writer.writerows(
                {"time": label, "from": tail, "to": head} for tail, head in sorted(panels[label])
            )
    node_csv = output_dir / "nodes.csv"
    with node_csv.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"id": node} for node in nodes)

    summary = {
        "dataset": args.dataset,
        "purpose": "bounded_chronological_check_input_only",
        "input_panel": recorded(input_path),
        "input_nodes": recorded(nodes_path),
        "selected_panel_labels": selected,
        "panel_count": len(selected),
        "transitions": len(selected) - 1,
        "nodes": len(nodes),
        "dichotomized_ties_by_panel": {label: len(panels[label]) for label in selected},
        "outputs": {"panel_edges": recorded(panel_csv), "nodes": recorded(node_csv)},
        "r_driver": "r/models/temporal_lagged_check.R",
        "limitations": [
            "The export selects existing prepared panel labels only; it does not forecast future "
            "ties.",
            "No node, time, or tie subsetting is performed beyond the explicitly recorded "
            "selected panel range.",
            "The temporal R driver must be run separately and remains a bounded lagged-only "
            "check, not a full forecasting study.",
        ],
    }
    (output_dir / "temporal_input_manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Temporal-panel export complete.")
    print(f"Dataset: {args.dataset}")
    print(f"Selected panels: {', '.join(selected)}")
    print(f"Nodes: {len(nodes):,}; transitions: {len(selected) - 1:,}")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
