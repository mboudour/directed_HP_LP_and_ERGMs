#!/usr/bin/env python3
"""Compare native-event/formal-concept fidelity against directed degree-preserving rewires."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from random import Random
from statistics import mean, stdev

import pyarrow.parquet as pq

from directed_hp.hypergraphs.formal_concepts import enumerate_formal_concepts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class EventType:
    """A unique cap-eligible native tail/head type."""

    tail: tuple[str, ...]
    head: tuple[str, ...]

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return its dyadic projection."""
        return frozenset(product(self.tail, self.head))


def parse_args() -> argparse.Namespace:
    """Parse a fully specified degree-preserving rewiring contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--arcs", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--event-tail-column", required=True)
    parser.add_argument("--event-head-column", required=True)
    parser.add_argument("--arc-tail-column", required=True)
    parser.add_argument("--arc-head-column", required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--tail-cap", type=int, default=3)
    parser.add_argument("--head-cap", type=int, default=3)
    parser.add_argument("--max-concept-candidates", type=int, default=250_000)
    parser.add_argument("--rewires", type=int, default=100)
    parser.add_argument("--swaps-per-arc", type=int, default=10)
    parser.add_argument("--max-attempts-per-swap", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20_261_013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for option in (
        "tail_cap",
        "head_cap",
        "max_concept_candidates",
        "rewires",
        "swaps_per_arc",
        "max_attempts_per_swap",
    ):
        if getattr(args, option) < 1:
            parser.error(f"--{option.replace('_', '-')} must be positive.")
    if args.seed < 0:
        parser.error("--seed must be non-negative.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative command arguments."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render repository-relative paths whenever possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    """Hash a required source in bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read an ordered, duplicate-free node universe."""
    if not path.is_file():
        raise SystemExit(f"STOP: node table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks {column!r}: {path}")
        values = [str(row[column]).strip() for row in reader]
    if not values or any(not value for value in values) or len(values) != len(set(values)):
        raise SystemExit("STOP: node table must contain unique non-empty IDs.")
    return tuple(values)


def read_arcs(
    path: Path, tail_column: str, head_column: str, nodes: set[str]
) -> tuple[tuple[str, str], ...]:
    """Read a deduplicated loop-free directed relation."""
    if not path.is_file():
        raise SystemExit(f"STOP: static arc table is missing: {path}")
    source = pq.ParquetFile(path)
    if {tail_column, head_column} - set(source.schema_arrow.names):
        raise SystemExit("STOP: static arc table lacks declared endpoint columns.")
    arcs: set[tuple[str, str]] = set()
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            tail, head = str(row[tail_column]).strip(), str(row[head_column]).strip()
            if not tail or not head or tail == head or tail not in nodes or head not in nodes:
                raise SystemExit("STOP: static arc table has an invalid endpoint.")
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit("STOP: static arc table contains no usable arcs.")
    return tuple(sorted(arcs))


def role(value: object, name: str) -> tuple[str, ...]:
    """Canonicalize scalar or Parquet-list event roles without string-list parsing."""
    members = value if isinstance(value, list) else [value]
    cleaned = tuple(sorted({str(item).strip() for item in members if item is not None}))
    if not cleaned or any(not item for item in cleaned):
        raise ValueError(f"empty {name} role")
    return cleaned


def read_events(
    path: Path, tail_column: str, head_column: str, nodes: set[str], tail_cap: int, head_cap: int
) -> tuple[EventType, ...]:
    """Read cap-eligible unique native event types in the fixed node universe."""
    if not path.is_file():
        raise SystemExit(f"STOP: native-event table is missing: {path}")
    source = pq.ParquetFile(path)
    if {tail_column, head_column} - set(source.schema_arrow.names):
        raise SystemExit("STOP: native-event table lacks declared role columns.")
    types: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            try:
                tail, head = role(row[tail_column], "tail"), role(row[head_column], "head")
            except ValueError:
                continue
            if set(tail).intersection(head) or any(item not in nodes for item in tail + head):
                continue
            if len(tail) <= tail_cap and len(head) <= head_cap:
                types.add((tail, head))
    if not types:
        raise SystemExit("STOP: no cap-eligible native event types remain.")
    return tuple(EventType(tail, head) for tail, head in sorted(types))


def role_similarity(left: EventType, tail: tuple[str, ...], head: tuple[str, ...]) -> float:
    """Return the planned average role-sensitive Jaccard score."""
    left_tail, left_head = set(left.tail), set(left.head)
    right_tail, right_head = set(tail), set(head)
    return 0.5 * (
        len(left_tail.intersection(right_tail)) / len(left_tail.union(right_tail))
        + len(left_head.intersection(right_head)) / len(left_head.union(right_head))
    )


def metric_values(
    events: tuple[EventType, ...],
    arcs: tuple[tuple[str, str], ...],
    nodes: tuple[str, ...],
    tail_cap: int,
    head_cap: int,
    max_candidates: int,
) -> dict[str, float]:
    """Calculate native-event/concept fidelity statistics for one relation."""
    concepts = enumerate_formal_concepts(
        arcs,
        nodes=nodes,
        max_tail_arity=tail_cap,
        max_head_arity=head_cap,
        max_candidates=max_candidates,
    )
    if not concepts:
        raise ValueError("rewire contains no capped formal concepts")
    pairs = {(tuple(map(str, item.tail)), tuple(map(str, item.head))) for item in concepts}
    event_pairs = {(item.tail, item.head) for item in events}
    exact = len(pairs.intersection(event_pairs))
    event_footprint = frozenset(arc for item in events for arc in item.footprint)
    concept_footprint = frozenset(arc for item in concepts for arc in item.footprint)
    intersection = event_footprint.intersection(concept_footprint)
    union = event_footprint.union(concept_footprint)
    event_best = [
        max(role_similarity(event, tail, head) for tail, head in pairs) for event in events
    ]
    concept_best = [
        max(role_similarity(event, tail, head) for event in events) for tail, head in pairs
    ]
    return {
        "formal_concepts": float(len(pairs)),
        "exact_pairs": float(exact),
        "concept_precision": exact / len(pairs),
        "event_recall": exact / len(events),
        "footprint_jaccard": len(intersection) / len(union),
        "native_footprint_coverage": len(intersection) / len(event_footprint),
        "concept_footprint_coverage": len(intersection) / len(concept_footprint),
        "mean_event_to_concept_role_similarity": mean(event_best),
        "mean_concept_to_event_role_similarity": mean(concept_best),
        "spurious_closure_concepts": float(len(pairs) - exact),
    }


def degree_signature(
    nodes: tuple[str, ...], arcs: tuple[tuple[str, str], ...]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return ordered out- and in-degree sequences."""
    outdegree, indegree = Counter(), Counter()
    for tail, head in arcs:
        outdegree[tail] += 1
        indegree[head] += 1
    return tuple(outdegree[node] for node in nodes), tuple(indegree[node] for node in nodes)


def directed_rewire(
    arcs: tuple[tuple[str, str], ...], swaps: int, max_attempts_per_swap: int, seed: int
) -> tuple[tuple[tuple[str, str], ...], int]:
    """Perform simple directed double-edge swaps while preserving every in/out degree."""
    random = Random(seed)
    edges = list(arcs)
    present = set(edges)
    successful = 0
    attempts = 0
    max_attempts = swaps * max_attempts_per_swap
    while successful < swaps and attempts < max_attempts:
        attempts += 1
        first, second = random.sample(range(len(edges)), 2)
        source_a, target_b = edges[first]
        source_c, target_d = edges[second]
        if len({source_a, target_b, source_c, target_d}) < 4:
            continue
        new_first, new_second = (source_a, target_d), (source_c, target_b)
        if new_first in present or new_second in present:
            continue
        present.remove(edges[first])
        present.remove(edges[second])
        edges[first], edges[second] = new_first, new_second
        present.add(new_first)
        present.add(new_second)
        successful += 1
    if successful != swaps:
        raise RuntimeError(
            f"only {successful} of {swaps} requested degree-preserving swaps succeeded"
        )
    return tuple(sorted(edges)), attempts


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create an explicit owned result directory."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a stable nonempty aggregate table."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run the fixed-native-events directed-rewiring null comparison."""
    args = parse_args()
    events_path, arcs_path, nodes_path, output = map(
        resolve, (args.events, args.arcs, args.nodes, args.output_dir)
    )
    prepare_output(output, args.overwrite)
    nodes = read_nodes(nodes_path, args.node_column)
    arcs = read_arcs(arcs_path, args.arc_tail_column, args.arc_head_column, set(nodes))
    events = read_events(
        events_path,
        args.event_tail_column,
        args.event_head_column,
        set(nodes),
        args.tail_cap,
        args.head_cap,
    )
    observed = metric_values(
        events, arcs, nodes, args.tail_cap, args.head_cap, args.max_concept_candidates
    )
    signature = degree_signature(nodes, arcs)
    swaps = len(arcs) * args.swaps_per_arc
    null_rows: list[dict[str, object]] = []
    for replicate in range(1, args.rewires + 1):
        rewired, attempts = directed_rewire(
            arcs, swaps, args.max_attempts_per_swap, args.seed + replicate
        )
        if degree_signature(nodes, rewired) != signature:
            raise RuntimeError("degree-preserving rewiring invariant failed")
        metrics = metric_values(
            events, rewired, nodes, args.tail_cap, args.head_cap, args.max_concept_candidates
        )
        null_rows.append(
            {"replicate": replicate, "successful_swaps": swaps, "attempts": attempts, **metrics}
        )
    write_csv(output / "rewire_metrics.csv", null_rows)
    comparison_rows: list[dict[str, object]] = []
    for metric, observed_value in observed.items():
        values = [float(row[metric]) for row in null_rows]
        null_mean, null_sd = mean(values), stdev(values) if len(values) > 1 else 0.0
        comparison_rows.append(
            {
                "metric": metric,
                "observed": observed_value,
                "null_mean": null_mean,
                "null_sd": null_sd,
                "z_score": (observed_value - null_mean) / null_sd if null_sd else math.nan,
                "empirical_p_greater_or_equal": (
                    1 + sum(value >= observed_value for value in values)
                )
                / (1 + len(values)),
            }
        )
    write_csv(output / "observed_vs_rewire_null.csv", comparison_rows)
    summary = {
        "dataset_id": args.dataset_id,
        "status": "completed",
        "null_model": "simple directed double-edge swaps preserving each node's in- and out-degree",
        "rewires": args.rewires,
        "swaps_per_rewire": swaps,
        "caps": {"tail": args.tail_cap, "head": args.head_cap},
        "inputs": {
            "events": {"path": recorded(events_path), "sha256": sha256(events_path)},
            "arcs": {"path": recorded(arcs_path), "sha256": sha256(arcs_path)},
            "nodes": {"path": recorded(nodes_path), "sha256": sha256(nodes_path)},
        },
        "observed": observed,
        "outputs": {
            "per_rewire": "rewire_metrics.csv",
            "comparison": "observed_vs_rewire_null.csv",
        },
        "limitation": (
            "This is a degree-sequence chance comparison for static representation fidelity, "
            "not a temporal or missingness null."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "summary.md").write_text(
        "# Degree-preserving rewiring null for representation fidelity\n\n"
        f"- Dataset: `{args.dataset_id}`\n- Directed rewires: `{args.rewires}`\n"
        f"- Successful double-edge swaps per rewire: `{swaps:,}`\n"
        "- Native event types are held fixed; only the aggregated directed relation is rewired.\n\n"
        "| Metric | Observed | Null mean | Null SD | z | Empirical p (>= observed) |\n"
        "|---|---:|---:|---:|---:|---:|\n"
        + "".join(
            f"| {row['metric']} | {float(row['observed']):.6f} | {float(row['null_mean']):.6f} | "
            f"{float(row['null_sd']):.6f} | {float(row['z_score']):.3f} | "
            f"{float(row['empirical_p_greater_or_equal']):.6f} |\n"
            for row in comparison_rows
        )
        + "\nPositive z values indicate greater observed agreement than the "
        "degree-preserving null. The one-sided empirical p column is descriptive and "
        "is not a multiple-testing correction.\n",
        encoding="utf-8",
    )
    print("Degree-preserving fidelity rewiring null passed.")
    print(f"Dataset: {args.dataset_id}; rewires: {args.rewires}; swaps/rewire: {swaps}.")
    print(f"Output bundle: {recorded(output)}")


if __name__ == "__main__":
    main()
