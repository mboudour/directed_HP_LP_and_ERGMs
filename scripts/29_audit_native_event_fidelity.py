#!/usr/bin/env python3
"""Audit agreement between recorded directed events and a capped concept section.

The driver compares observed native event *types* with formal concepts of the
aggregated directed relation without treating either as a substitute for the other.
It implements the representation-fidelity diagnostics required before native-event
and concept-recovery evaluations are scaled: exact role equality, footprint agreement,
best role-sensitive matches, aggregation/merging, contained-concept fragmentation,
and role distortion. Inputs must already be prepared and privacy-controlled locally.
"""

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
from statistics import mean, median
from typing import Any

import pyarrow.parquet as pq

from directed_hp.hypergraphs.formal_concepts import enumerate_formal_concepts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_CANDIDATES = 250_000


@dataclass(frozen=True, slots=True)
class NativeEventType:
    """A canonical tail/head type with its observed event-record multiplicity."""

    tail: tuple[str, ...]
    head: tuple[str, ...]
    occurrence_count: int

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return the event type's directed Cartesian footprint."""
        return frozenset(product(self.tail, self.head))


def parse_args() -> argparse.Namespace:
    """Parse an explicit prepared-input fidelity-audit contract."""
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
    parser.add_argument("--tail-cap", type=int, required=True)
    parser.add_argument("--head-cap", type=int, required=True)
    parser.add_argument("--max-concept-candidates", type=int, default=DEFAULT_MAX_CANDIDATES)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for option in ("tail_cap", "head_cap", "max_concept_candidates"):
        if getattr(args, option) < 1:
            parser.error(f"--{option.replace('_', '-')} must be at least 1.")
    return args


def resolve_path(path: Path) -> Path:
    """Resolve project-relative values from the recorded command contract."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render repository-relative paths where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    """Hash a frozen prepared input in bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, description: str) -> None:
    """Fail before writing when a declared prepared input is absent."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read the fixed actor universe, preserving its declared ordering."""
    require_file(path, "node table")
    ordered: dict[str, None] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks declared column {column!r}: {path}")
        for row in reader:
            value = row[column].strip()
            if not value:
                raise SystemExit("STOP: node table contains an empty actor ID.")
            if value in ordered:
                raise SystemExit(f"STOP: node table contains duplicate actor ID {value!r}.")
            ordered[value] = None
    if not ordered:
        raise SystemExit("STOP: node table contains no actor IDs.")
    return tuple(ordered)


def read_arcs(
    path: Path, tail_column: str, head_column: str, nodes: set[str]
) -> tuple[tuple[str, str], ...]:
    """Read a loop-free, deduplicated static relation under the fixed node universe."""
    require_file(path, "static directed-arc table")
    source = pq.ParquetFile(path)
    required = {tail_column, head_column}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: static arc table lacks columns {sorted(missing)}: {path}")
    arcs: dict[tuple[str, str], None] = {}
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            tail = str(row[tail_column]).strip()
            head = str(row[head_column]).strip()
            if not tail or not head:
                raise SystemExit("STOP: static arc table contains an empty endpoint.")
            if tail not in nodes or head not in nodes:
                raise SystemExit(
                    "STOP: static arc table references an actor outside the node table."
                )
            if tail == head:
                raise SystemExit("STOP: static arc table contains a self-loop.")
            arcs[(tail, head)] = None
    if not arcs:
        raise SystemExit("STOP: static arc table contains no loop-free arcs.")
    return tuple(arcs)


def canonical_head(value: object) -> tuple[str, ...]:
    """Canonicalize a list-like recorded head without silently parsing text encodings."""
    if not isinstance(value, list):
        raise SystemExit("STOP: native-event head column must be a Parquet list column.")
    members = [str(member).strip() for member in value]
    if any(not member for member in members):
        raise SystemExit("STOP: native-event head contains an empty actor ID.")
    return tuple(sorted(set(members)))


def read_native_event_types(
    path: Path,
    tail_column: str,
    head_column: str,
    nodes: set[str],
    tail_cap: int,
    head_cap: int,
) -> tuple[list[NativeEventType], dict[str, int]]:
    """Filter events to the fixed universe and group equal tail/head event types."""
    require_file(path, "native-event table")
    source = pq.ParquetFile(path)
    required = {tail_column, head_column}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: native-event table lacks columns {sorted(missing)}: {path}")

    counts: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    accounting: Counter[str] = Counter()
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            accounting["event_records_read"] += 1
            tail_value = row[tail_column]
            if tail_value is None or not str(tail_value).strip():
                accounting["excluded_empty_tail"] += 1
                continue
            tail = (str(tail_value).strip(),)
            head = canonical_head(row[head_column])
            if not head:
                accounting["excluded_empty_head"] += 1
                continue
            if tail[0] not in nodes or any(member not in nodes for member in head):
                accounting["excluded_outside_fixed_node_universe"] += 1
                continue
            if set(tail).intersection(head):
                accounting["excluded_role_overlap"] += 1
                continue
            accounting["fixed_universe_event_records"] += 1
            if len(tail) > tail_cap or len(head) > head_cap:
                accounting["excluded_by_arity_cap_event_records"] += 1
                continue
            counts[(tail, head)] += 1
            accounting["cap_eligible_event_records"] += 1

    event_types = [
        NativeEventType(tail=tail, head=head, occurrence_count=count)
        for (tail, head), count in sorted(counts.items())
    ]
    accounting["cap_eligible_event_types"] = len(event_types)
    if not event_types:
        raise SystemExit(
            "STOP: no fixed-universe native event types satisfy the selected arity caps."
        )
    return event_types, dict(sorted(accounting.items()))


def jaccard(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    """Return a nonempty finite-set Jaccard similarity."""
    left_set = set(left)
    right_set = set(right)
    return len(left_set.intersection(right_set)) / len(left_set.union(right_set))


def role_similarity(
    tail: tuple[str, ...],
    head: tuple[str, ...],
    candidate_tail: tuple[str, ...],
    candidate_head: tuple[str, ...],
) -> tuple[float, float, float]:
    """Calculate the plan's role-sensitive similarity and its two components."""
    tail_similarity = jaccard(tail, candidate_tail)
    head_similarity = jaccard(head, candidate_head)
    return (tail_similarity + head_similarity) / 2, tail_similarity, head_similarity


def quantile(values: list[float], probability: float) -> float:
    """Return deterministic linear-interpolated quantiles without an extra dependency."""
    if not values:
        return math.nan
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def numeric_summary(values: list[float]) -> dict[str, float | None]:
    """Summarize a finite diagnostic vector for JSON and Markdown outputs."""
    if not values:
        return {"minimum": None, "median": None, "mean": None, "p95": None, "maximum": None}
    return {
        "minimum": min(values),
        "median": median(values),
        "mean": mean(values),
        "p95": quantile(values, 0.95),
        "maximum": max(values),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Write non-sensitive, stable diagnostic records with Unix line endings."""
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Protect an existing result bundle unless replacement is explicit."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: fidelity-audit output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Create the bounded native-event/formal-concept representation audit."""
    args = parse_args()
    events_path = resolve_path(args.events)
    arcs_path = resolve_path(args.arcs)
    nodes_path = resolve_path(args.nodes)
    output_dir = resolve_path(args.output_dir)
    prepare_output_dir(output_dir, args.overwrite)

    nodes = read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    arcs = read_arcs(arcs_path, args.arc_tail_column, args.arc_head_column, node_set)
    events, event_accounting = read_native_event_types(
        events_path,
        args.event_tail_column,
        args.event_head_column,
        node_set,
        args.tail_cap,
        args.head_cap,
    )
    concepts = enumerate_formal_concepts(
        arcs,
        nodes=nodes,
        max_tail_arity=args.tail_cap,
        max_head_arity=args.head_cap,
        max_candidates=args.max_concept_candidates,
    )
    if not concepts:
        raise SystemExit("STOP: no formal concepts satisfy the selected caps.")

    event_by_pair = {(event.tail, event.head): event for event in events}
    event_ids = {pair: index for index, pair in enumerate(sorted(event_by_pair), start=1)}
    concept_pairs = [
        (tuple(map(str, concept.tail)), tuple(map(str, concept.head))) for concept in concepts
    ]
    concept_by_pair = {pair: index for index, pair in enumerate(concept_pairs, start=1)}
    exact_pairs = set(event_by_pair).intersection(concept_by_pair)

    formal_footprint = frozenset(arc for concept in concepts for arc in concept.footprint)
    native_footprint = frozenset(arc for event in events for arc in event.footprint)
    observed_arcs = frozenset(arcs)
    if not native_footprint <= observed_arcs:
        raise SystemExit(
            "STOP: a cap-eligible native-event footprint is absent from the static arcs."
        )
    if not formal_footprint <= observed_arcs:
        raise SystemExit("STOP: a formal-concept footprint is absent from the static arcs.")

    event_rows: list[dict[str, object]] = []
    event_role_scores: list[float] = []
    event_fragment_counts: list[float] = []
    event_role_distortions = 0
    for pair, event in sorted(event_by_pair.items()):
        event_id = event_ids[pair]
        best_index, best = max(
            enumerate(concept_pairs, start=1),
            key=lambda item: (role_similarity(event.tail, event.head, *item[1])[0], -item[0]),
        )
        best_score, tail_score, head_score = role_similarity(event.tail, event.head, *best)
        best_footprint = frozenset(product(best[0], best[1]))
        contained = sum(
            1
            for candidate in concept_pairs
            if frozenset(product(candidate[0], candidate[1])) < event.footprint
        )
        role_distorted = bool(
            set(event.tail).intersection(best[1]) or set(event.head).intersection(best[0])
        )
        event_role_scores.append(best_score)
        event_fragment_counts.append(float(contained))
        event_role_distortions += int(role_distorted)
        event_rows.append(
            {
                "native_event_type_id": event_id,
                "occurrence_count": event.occurrence_count,
                "tail_arity": len(event.tail),
                "head_arity": len(event.head),
                "exact_formal_concept_match": pair in exact_pairs,
                "best_concept_id": best_index,
                "best_role_similarity": best_score,
                "best_tail_jaccard": tail_score,
                "best_head_jaccard": head_score,
                "best_footprint_jaccard": len(event.footprint.intersection(best_footprint))
                / len(event.footprint.union(best_footprint)),
                "strictly_contained_concept_count": contained,
                "best_match_role_distorted": role_distorted,
            }
        )

    concept_rows: list[dict[str, object]] = []
    concept_role_scores: list[float] = []
    aggregation_types: list[float] = []
    aggregation_occurrences: list[float] = []
    for concept_index, pair in enumerate(concept_pairs, start=1):
        best_pair, best_event = max(
            sorted(event_by_pair.items()),
            key=lambda item: (role_similarity(*item[0], *pair)[0], -event_ids[item[0]]),
        )
        best_score, tail_score, head_score = role_similarity(*best_pair, *pair)
        footprint = frozenset(product(pair[0], pair[1]))
        contributing = [event for event in events if event.footprint.intersection(footprint)]
        type_count = len(contributing)
        occurrence_count = sum(event.occurrence_count for event in contributing)
        concept_role_scores.append(best_score)
        aggregation_types.append(float(type_count))
        aggregation_occurrences.append(float(occurrence_count))
        concept_rows.append(
            {
                "formal_concept_id": concept_index,
                "tail_arity": len(pair[0]),
                "head_arity": len(pair[1]),
                "exact_native_event_match": pair in exact_pairs,
                "best_native_event_type_id": event_ids[best_pair],
                "best_role_similarity": best_score,
                "best_tail_jaccard": tail_score,
                "best_head_jaccard": head_score,
                "contributing_native_event_types": type_count,
                "contributing_native_event_occurrences": occurrence_count,
            }
        )

    union = native_footprint.union(formal_footprint)
    footprint_intersection = native_footprint.intersection(formal_footprint)
    summary: dict[str, Any] = {
        "driver": "scripts/29_audit_native_event_fidelity.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "inputs": {
            "native_events": {
                "path": recorded_path(events_path),
                "sha256": sha256_file(events_path),
            },
            "static_arcs": {"path": recorded_path(arcs_path), "sha256": sha256_file(arcs_path)},
            "nodes": {"path": recorded_path(nodes_path), "sha256": sha256_file(nodes_path)},
        },
        "caps": {
            "tail": args.tail_cap,
            "head": args.head_cap,
            "max_concept_candidates": args.max_concept_candidates,
        },
        "fixed_node_universe": len(nodes),
        "static_arcs": len(arcs),
        "native_events": {
            **event_accounting,
            "cap_eligible_event_type_occurrences": sum(event.occurrence_count for event in events),
        },
        "formal_concepts": {"count": len(concepts)},
        "exact_tail_head_equality": {
            "matching_pairs": len(exact_pairs),
            "concept_precision": len(exact_pairs) / len(concepts),
            "native_event_type_recall": len(exact_pairs) / len(events),
        },
        "footprint_agreement": {
            "native_event_cap_footprint_arcs": len(native_footprint),
            "formal_concept_footprint_arcs": len(formal_footprint),
            "intersection_arcs": len(footprint_intersection),
            "union_arcs": len(union),
            "jaccard": len(footprint_intersection) / len(union),
            "native_event_footprint_covered_by_concepts": len(footprint_intersection)
            / len(native_footprint),
            "formal_concept_footprint_covered_by_native_events": len(footprint_intersection)
            / len(formal_footprint),
        },
        "best_role_similarity": {
            "native_event_to_concept": numeric_summary(event_role_scores),
            "concept_to_native_event": numeric_summary(concept_role_scores),
        },
        "cover_structure": {
            "native_event_types_with_two_or_more_strictly_contained_concepts": sum(
                count >= 2 for count in event_fragment_counts
            ),
            "strictly_contained_concepts_per_native_event_type": numeric_summary(
                event_fragment_counts
            ),
            "formal_concepts_with_two_or_more_contributing_native_event_types": sum(
                count >= 2 for count in aggregation_types
            ),
            "aggregation_ratio_native_event_types": numeric_summary(aggregation_types),
            "aggregation_ratio_native_event_occurrences": numeric_summary(aggregation_occurrences),
            "best_event_to_concept_role_distortions": event_role_distortions,
            "spurious_closure_formal_concepts_without_exact_native_event": len(concepts)
            - len(exact_pairs),
        },
        "outputs": {
            "event_to_concept_matches": "event_to_concept_matches.csv",
            "concept_to_event_aggregation": "concept_to_event_aggregation.csv",
            "summary_json": "summary.json",
            "summary_markdown": "summary.md",
        },
        "limitations": [
            "The capped concept section is a derived representation, not a reconstruction "
            "of recorded messages.",
            "Exact equality is assessed on tail/head event types; repeated records contribute "
            "occurrence counts but do not create new types.",
            "This audit has no degree-preserving-rewiring comparison and makes no "
            "chance-corrected fidelity claim.",
            "Containment fragmentation and aggregation ratio are descriptive cover diagnostics, "
            "not a unique inverse of the dyadic projection.",
        ],
    }
    write_csv(
        output_dir / "event_to_concept_matches.csv",
        list(event_rows[0]),
        event_rows,
    )
    write_csv(
        output_dir / "concept_to_event_aggregation.csv",
        list(concept_rows[0]),
        concept_rows,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "summary.md").write_text(
        "# Native-event and formal-concept fidelity audit\n\n"
        f"- Dataset: `{args.dataset_id}`\n"
        f"- Fixed node universe: `{len(nodes):,}`\n"
        f"- Static directed arcs: `{len(arcs):,}`\n"
        f"- Caps: `|T| <= {args.tail_cap}`, `|H| <= {args.head_cap}`\n"
        f"- Cap-eligible recorded event records: "
        f"`{sum(event.occurrence_count for event in events):,}`\n"
        f"- Cap-eligible recorded event types: `{len(events):,}`\n"
        f"- Formal concepts: `{len(concepts):,}`\n\n"
        "## Exact role equality\n\n"
        f"- Matching tail/head pairs: `{len(exact_pairs):,}`\n"
        f"- Formal-concept precision against recorded event types: "
        f"`{summary['exact_tail_head_equality']['concept_precision']:.6f}`\n"
        f"- Recorded event-type recall by formal concepts: "
        f"`{summary['exact_tail_head_equality']['native_event_type_recall']:.6f}`\n\n"
        "## Footprint agreement\n\n"
        f"- Native-event cap footprint arcs: `{len(native_footprint):,}`\n"
        f"- Formal-concept footprint arcs: `{len(formal_footprint):,}`\n"
        f"- Footprint Jaccard: `{summary['footprint_agreement']['jaccard']:.6f}`\n"
        f"- Native footprint covered by concepts: "
        f"`{summary['footprint_agreement']['native_event_footprint_covered_by_concepts']:.6f}`\n"
        f"- Concept footprint covered by native events: "
        f"`{summary['footprint_agreement']['formal_concept_footprint_covered_by_native_events']:.6f}`\n\n"
        "## Cover diagnostics\n\n"
        f"- Concepts without an exact recorded-event type: "
        f"`{summary['cover_structure']['spurious_closure_formal_concepts_without_exact_native_event']:,}`\n"
        f"- Concepts with at least two contributing recorded event types: "
        f"`{summary['cover_structure']['formal_concepts_with_two_or_more_contributing_native_event_types']:,}`\n"
        f"- Event types with two or more strictly contained concept footprints: "
        f"`{summary['cover_structure']['native_event_types_with_two_or_more_strictly_contained_concepts']:,}`\n"
        f"- Best event-to-concept role-distortion cases: "
        f"`{summary['cover_structure']['best_event_to_concept_role_distortions']:,}`\n\n"
        "This is a representation-fidelity diagnostic. It does not assert that formal concepts "
        "are observed email groups or that native events can be reconstructed from the aggregate "
        "directed graph.\n",
        encoding="utf-8",
    )
    print("Native-event/formal-concept fidelity audit passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Cap-eligible native event types: {len(events):,}.")
    print(f"Formal concepts: {len(concepts):,}.")
    print(f"Exact tail/head matches: {len(exact_pairs):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
