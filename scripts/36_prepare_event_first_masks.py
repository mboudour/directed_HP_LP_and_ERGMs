#!/usr/bin/env python3
"""Create reproducible event-first native-event-type masks for directed HP.

The primary native-event target is a distinct ordered tail/head **event type**.
Every repeated message record of a selected type is withheld together. This avoids
the invalid evaluation in which an event type is nominally held out but an
identical message remains in the observed training hypergraph. The resulting
observed graph is always the dyadic projection of the observed native types.

MCAR samples event types uniformly without replacement. MNAR-out implements the
plan's oracle role-biased mechanism: an event type has inclusion probability
``min(1, lambda * sender_activity)``, where sender activity is calculated from
the full, cap-eligible native-event records and lambda is solved so the mean
inclusion probability equals the requested rate. Its realized rate is recorded,
not forced to the requested rate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path
from random import Random
from typing import Any

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class EventType:
    """One distinct, cap-eligible recorded tail/head event type."""

    event_type_id: str
    tail: tuple[str, ...]
    head: tuple[str, ...]
    occurrence_count: int

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return the observed directed dyads induced by this event type."""
        return frozenset(product(self.tail, self.head))


@dataclass(frozen=True, slots=True)
class InputAccounting:
    """Track filtering into the fixed-universe cap-eligible event-type target."""

    event_records_read: int
    excluded_empty_tail: int
    excluded_empty_head: int
    excluded_role_overlap: int
    excluded_outside_fixed_node_universe: int
    excluded_by_arity_cap: int
    cap_eligible_event_records: int
    cap_eligible_event_types: int


def parse_args() -> argparse.Namespace:
    """Parse a fully explicit local native-event masking request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--event-tail-column", required=True)
    parser.add_argument("--event-head-column", required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--tail-cap", type=int, required=True)
    parser.add_argument("--head-cap", type=int, required=True)
    parser.add_argument("--mask-rate", type=float, default=0.30)
    parser.add_argument("--mechanisms", default="mcar,mnar_out")
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.tail_cap < 1 or args.head_cap < 1:
        parser.error("--tail-cap and --head-cap must be at least 1.")
    if not math.isfinite(args.mask_rate) or not 0.0 < args.mask_rate < 1.0:
        parser.error("--mask-rate must be finite and strictly between 0 and 1.")
    if args.replicates < 1:
        parser.error("--replicates must be at least 1.")
    if isinstance(args.seed, bool):
        parser.error("--seed must be an integer.")
    return args


def resolve_path(path: Path) -> Path:
    """Resolve a project-relative command argument at the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render a reproducible repository-relative path if possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    """Hash a declared local input without loading it entirely into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, description: str) -> None:
    """Fail before output creation if a required prepared input is absent."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Load the fixed node universe and reject empty or duplicate identifiers."""
    require_file(path, "node table")
    nodes: dict[str, None] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks declared column {column!r}: {path}")
        for row in reader:
            node = row[column].strip()
            if not node:
                raise SystemExit("STOP: node table contains an empty actor ID.")
            if node in nodes:
                raise SystemExit(f"STOP: node table contains duplicate actor ID {node!r}.")
            nodes[node] = None
    if not nodes:
        raise SystemExit("STOP: node table contains no actors.")
    return tuple(nodes)


def canonical_role(value: object, role: str) -> tuple[str, ...]:
    """Canonicalize a nonempty scalar or Parquet-list event role without text parsing."""
    raw_values = value if isinstance(value, list) else [value]
    values = [str(member).strip() for member in raw_values if member is not None]
    if not values or any(not member for member in values):
        raise ValueError(f"native-event {role} contains an empty actor ID")
    return tuple(sorted(set(values)))


def read_event_types(
    path: Path,
    *,
    tail_column: str,
    head_column: str,
    node_set: set[str],
    tail_cap: int,
    head_cap: int,
) -> tuple[tuple[EventType, ...], InputAccounting]:
    """Build the privacy-minimizing, distinct event-type target table."""
    require_file(path, "native-event table")
    source = pq.ParquetFile(path)
    missing = {tail_column, head_column} - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: native-event table lacks columns {sorted(missing)}: {path}")

    raw_counts: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    counts: Counter[str] = Counter()
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            counts["event_records_read"] += 1
            try:
                tail = canonical_role(row[tail_column], "tail")
            except ValueError:
                counts["excluded_empty_tail"] += 1
                continue
            try:
                head = canonical_role(row[head_column], "head")
            except ValueError:
                counts["excluded_empty_head"] += 1
                continue
            if set(tail).intersection(head):
                counts["excluded_role_overlap"] += 1
                continue
            if tail[0] not in node_set or any(member not in node_set for member in head):
                counts["excluded_outside_fixed_node_universe"] += 1
                continue
            if len(tail) > tail_cap or len(head) > head_cap:
                counts["excluded_by_arity_cap"] += 1
                continue
            raw_counts[(tail, head)] += 1
            counts["cap_eligible_event_records"] += 1

    event_types = tuple(
        EventType(
            event_type_id=f"event_type_{index:05d}",
            tail=tail,
            head=head,
            occurrence_count=occurrence_count,
        )
        for index, ((tail, head), occurrence_count) in enumerate(
            sorted(raw_counts.items()), start=1
        )
    )
    counts["cap_eligible_event_types"] = len(event_types)
    if len(event_types) < 2:
        raise SystemExit("STOP: at least two cap-eligible native event types are required.")
    return (
        event_types,
        InputAccounting(
            event_records_read=counts["event_records_read"],
            excluded_empty_tail=counts["excluded_empty_tail"],
            excluded_empty_head=counts["excluded_empty_head"],
            excluded_role_overlap=counts["excluded_role_overlap"],
            excluded_outside_fixed_node_universe=counts["excluded_outside_fixed_node_universe"],
            excluded_by_arity_cap=counts["excluded_by_arity_cap"],
            cap_eligible_event_records=counts["cap_eligible_event_records"],
            cap_eligible_event_types=counts["cap_eligible_event_types"],
        ),
    )


def parse_mechanisms(value: str) -> tuple[str, ...]:
    """Validate a deterministic mechanism sequence without silent duplication."""
    mechanisms = tuple(item.strip().casefold() for item in value.split(",") if item.strip())
    allowed = {"mcar", "mnar_in", "mnar_out"}
    if not mechanisms or set(mechanisms) - allowed:
        raise SystemExit(
            "STOP: --mechanisms must be a comma-separated subset of mcar,mnar_out,mnar_in."
        )
    if len(set(mechanisms)) != len(mechanisms):
        raise SystemExit("STOP: --mechanisms must not repeat a mechanism.")
    return mechanisms


def type_selection_probabilities(
    event_types: tuple[EventType, ...], rate: float, mechanism: str
) -> tuple[list[float], dict[str, int]]:
    """Compute oracle MNAR selection probabilities for active source or target roles."""
    if mechanism not in {"mnar_out", "mnar_in"}:
        raise ValueError("oracle selection probabilities require MNAR-out or MNAR-in")
    role_activity: Counter[str] = Counter()
    for event in event_types:
        if mechanism == "mnar_out":
            members = event.tail
            contribution = event.occurrence_count * len(event.head)
        else:
            members = event.head
            contribution = event.occurrence_count * len(event.tail)
        for member in members:
            role_activity[member] += contribution
    weights = [
        sum(
            role_activity[member]
            for member in (event.tail if mechanism == "mnar_out" else event.head)
        )
        / len(event.tail if mechanism == "mnar_out" else event.head)
        for event in event_types
    ]
    if any(weight <= 0 for weight in weights):
        raise RuntimeError("each cap-eligible event type must have positive sender activity")

    target = rate * len(event_types)
    lower = 0.0
    upper = 1.0 / min(weights)
    while sum(min(1.0, upper * weight) for weight in weights) < target:
        upper *= 2.0
    for _ in range(80):
        midpoint = (lower + upper) / 2.0
        expected = sum(min(1.0, midpoint * weight) for weight in weights)
        if expected < target:
            lower = midpoint
        else:
            upper = midpoint
    probabilities = [min(1.0, upper * weight) for weight in weights]
    return probabilities, dict(sorted(role_activity.items()))


def select_event_type_indices(
    event_types: tuple[EventType, ...], mechanism: str, rate: float, seed: int
) -> tuple[frozenset[int], list[float], dict[str, int] | None]:
    """Draw one valid event-type mask and preserve each unit's selection probability."""
    random = Random(seed)
    if mechanism == "mcar":
        count = min(math.floor(rate * len(event_types)), len(event_types) - 1)
        if count < 1:
            raise SystemExit("STOP: requested MCAR rate selects no event types.")
        indices = frozenset(random.sample(range(len(event_types)), count))
        return indices, [count / len(event_types)] * len(event_types), None

    probabilities, sender_activity = type_selection_probabilities(event_types, rate, mechanism)
    selected = frozenset(
        index for index, probability in enumerate(probabilities) if random.random() < probability
    )
    if not selected or len(selected) == len(event_types):
        raise SystemExit(
            "STOP: MNAR-out draw produced an unusable all-observed or all-held-out split; "
            "change the seed or increase the target population."
        )
    return selected, probabilities, sender_activity


def union_arcs(event_types: tuple[EventType, ...]) -> frozenset[tuple[str, str]]:
    """Project event types to their unique observed directed arcs."""
    return frozenset(arc for event in event_types for arc in event.footprint)


def degree_maps(
    arcs: frozenset[tuple[str, str]], nodes: tuple[str, ...]
) -> tuple[
    dict[str, int],
    dict[str, int],
    dict[str, frozenset[tuple[str, str]]],
    dict[str, frozenset[tuple[str, str]]],
]:
    """Calculate fixed-universe degree and incident-arc maps for realised-rate reports."""
    outgoing: dict[str, set[tuple[str, str]]] = {node: set() for node in nodes}
    incoming: dict[str, set[tuple[str, str]]] = {node: set() for node in nodes}
    for tail, head in arcs:
        outgoing[tail].add((tail, head))
        incoming[head].add((tail, head))
    return (
        {node: len(outgoing[node]) for node in nodes},
        {node: len(incoming[node]) for node in nodes},
        {node: frozenset(outgoing[node]) for node in nodes},
        {node: frozenset(incoming[node]) for node in nodes},
    )


def degree_deciles(degrees: dict[str, int]) -> dict[str, int]:
    """Assign deterministic equal-count deciles, splitting tied values by actor ID."""
    ordered = sorted(degrees, key=lambda node: (degrees[node], node))
    total = len(ordered)
    return {node: min(10, (index * 10) // total + 1) for index, node in enumerate(ordered)}


def type_table_rows(
    event_types: tuple[EventType, ...],
    *,
    selected: frozenset[int],
    probabilities: list[float],
    observed_arcs: frozenset[tuple[str, str]],
    outdegree: dict[str, int],
    indegree: dict[str, int],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Render observed and held-out type tables with target-leakage diagnostics."""
    observed_rows: list[dict[str, object]] = []
    heldout_rows: list[dict[str, object]] = []
    for index, event in enumerate(event_types):
        footprint = event.footprint
        surviving = len(footprint.intersection(observed_arcs))
        row = {
            "event_type_id": event.event_type_id,
            "tail_nodes_json": json.dumps(event.tail),
            "head_nodes_json": json.dumps(event.head),
            "tail_arity": len(event.tail),
            "head_arity": len(event.head),
            "occurrence_count": event.occurrence_count,
            "footprint_size": len(footprint),
            "mean_full_tail_outdegree": sum(outdegree[node] for node in event.tail)
            / len(event.tail),
            "mean_full_head_indegree": sum(indegree[node] for node in event.head) / len(event.head),
            "selection_probability": probabilities[index],
        }
        if index in selected:
            heldout_rows.append(
                {
                    **row,
                    "surviving_observed_footprint_arcs": surviving,
                    "removed_footprint_arcs": len(footprint) - surviving,
                    "already_observed_footprint": surviving == len(footprint),
                }
            )
        else:
            observed_rows.append(row)
    return observed_rows, heldout_rows


def strata_rows(
    event_types: tuple[EventType, ...],
    selected: frozenset[int],
    tail_deciles: dict[str, int],
    head_deciles: dict[str, int],
) -> list[dict[str, object]]:
    """Report type/role removal rates by required arity and degree strata."""
    strata: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    for index, event in enumerate(event_types):
        masked = int(index in selected)
        for stratum, value in (
            ("tail_arity", str(len(event.tail))),
            ("head_arity", str(len(event.head))),
        ):
            strata[(stratum, value)][0] += 1
            strata[(stratum, value)][1] += masked
        for sender in event.tail:
            strata[("tail_outdegree_decile", str(tail_deciles[sender]))][0] += 1
            strata[("tail_outdegree_decile", str(tail_deciles[sender]))][1] += masked
        for recipient in event.head:
            strata[("head_indegree_decile", str(head_deciles[recipient]))][0] += 1
            strata[("head_indegree_decile", str(head_deciles[recipient]))][1] += masked
    return [
        {
            "stratum": stratum,
            "value": value,
            "eligible_units": total,
            "held_out_units": heldout,
            "realized_rate": heldout / total,
        }
        for (stratum, value), (total, heldout) in sorted(strata.items())
    ]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write stable CSV output and reject an accidental empty required table."""
    if not rows:
        raise RuntimeError(f"cannot write a required empty output table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_arcs(path: Path, arcs: frozenset[tuple[str, str]]) -> None:
    """Write a deterministic simple directed arc table."""
    write_csv(path, [{"tail": tail, "head": head} for tail, head in sorted(arcs)])


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Avoid mixing a new run with an older set of frozen mask splits."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: event-first mask output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def percentage(numerator: int, denominator: int) -> float:
    """Compute a guarded report proportion for a declared denominator."""
    return numerator / denominator if denominator else 0.0


def one_mask(
    *,
    event_types: tuple[EventType, ...],
    nodes: tuple[str, ...],
    mechanism: str,
    replicate: int,
    seed: int,
    rate: float,
    output_dir: Path,
    full_arcs: frozenset[tuple[str, str]],
    outdegree: dict[str, int],
    indegree: dict[str, int],
    outgoing: dict[str, frozenset[tuple[str, str]]],
    incoming: dict[str, frozenset[tuple[str, str]]],
    tail_deciles: dict[str, int],
    head_deciles: dict[str, int],
) -> dict[str, object]:
    """Materialize one frozen native-event-type split and full realised-rate evidence."""
    mechanism_offset = {"mcar": 0, "mnar_out": 52_361, "mnar_in": 104_729}[mechanism]
    split_seed = seed + 104_729 * replicate + mechanism_offset
    selected, probabilities, sender_activity = select_event_type_indices(
        event_types, mechanism, rate, split_seed
    )
    observed_types = tuple(
        event for index, event in enumerate(event_types) if index not in selected
    )
    heldout_types = tuple(event for index, event in enumerate(event_types) if index in selected)
    observed_arcs = union_arcs(observed_types)
    removed_arcs = full_arcs - observed_arcs
    if observed_arcs.union(removed_arcs) != full_arcs:
        raise RuntimeError("arc reconciliation failed for an event-first mask")

    split_dir = output_dir / f"{mechanism}_replicate_{replicate:03d}"
    split_dir.mkdir()
    observed_rows, heldout_rows = type_table_rows(
        event_types,
        selected=selected,
        probabilities=probabilities,
        observed_arcs=observed_arcs,
        outdegree=outdegree,
        indegree=indegree,
    )
    write_csv(split_dir / "observed_event_types.csv", observed_rows)
    write_csv(split_dir / "heldout_event_types.csv", heldout_rows)
    write_arcs(split_dir / "observed_arcs.csv", observed_arcs)
    write_arcs(split_dir / "removed_arcs.csv", removed_arcs)
    write_csv(
        split_dir / "removal_strata.csv",
        strata_rows(event_types, selected, tail_deciles, head_deciles),
    )

    heldout_records = sum(event.occurrence_count for event in heldout_types)
    already_observed_types = sum(bool(row["already_observed_footprint"]) for row in heldout_rows)
    already_observed_records = sum(
        int(row["occurrence_count"])
        for row in heldout_rows
        if bool(row["already_observed_footprint"])
    )
    active_out = [node for node in nodes if outgoing[node]]
    active_in = [node for node in nodes if incoming[node]]
    nodes_losing_out = [node for node in active_out if outgoing[node].intersection(removed_arcs)]
    nodes_losing_in = [node for node in active_in if incoming[node].intersection(removed_arcs)]
    summary = {
        "mechanism": mechanism,
        "replicate": replicate,
        "seed": split_seed,
        "requested_type_mask_rate": rate,
        "eligible_event_types": len(event_types),
        "heldout_event_types": len(heldout_types),
        "observed_event_types": len(observed_types),
        "realized_event_type_mask_rate": percentage(len(heldout_types), len(event_types)),
        "eligible_event_records": sum(event.occurrence_count for event in event_types),
        "heldout_event_records": heldout_records,
        "realized_event_record_mask_rate": percentage(
            heldout_records, sum(event.occurrence_count for event in event_types)
        ),
        "full_projection_arcs": len(full_arcs),
        "observed_projection_arcs": len(observed_arcs),
        "removed_projection_arcs": len(removed_arcs),
        "realized_arc_removal_rate": percentage(len(removed_arcs), len(full_arcs)),
        "heldout_event_types_with_already_observed_footprint": already_observed_types,
        "already_observed_footprint_type_fraction": percentage(
            already_observed_types, len(heldout_types)
        ),
        "already_observed_footprint_record_fraction": percentage(
            already_observed_records, heldout_records
        ),
        "active_nodes": len({node for arc in full_arcs for node in arc}),
        "nodes_losing_outgoing_arc": len(nodes_losing_out),
        "fraction_active_nodes_losing_outgoing_arc": percentage(
            len(nodes_losing_out), len(active_out)
        ),
        "nodes_losing_incoming_arc": len(nodes_losing_in),
        "fraction_active_nodes_losing_incoming_arc": percentage(
            len(nodes_losing_in), len(active_in)
        ),
        "oracle_sender_activity": sender_activity,
        "files": {
            "observed_event_types": "observed_event_types.csv",
            "heldout_event_types": "heldout_event_types.csv",
            "observed_arcs": "observed_arcs.csv",
            "removed_arcs": "removed_arcs.csv",
            "removal_strata": "removal_strata.csv",
        },
    }
    (split_dir / "manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def write_summary_markdown(path: Path, dataset_id: str, summaries: list[dict[str, object]]) -> None:
    """Render a compact, directly inspectable realised-rate table."""
    rows = [
        "# Event-first native-event-type mask summary",
        "",
        f"- Dataset: `{dataset_id}`",
        "- Unit sampled: a distinct ordered tail/head native event type; all duplicate message "
        "records of a selected type are withheld together.",
        "- MCAR is exact fixed-count type sampling. MNAR-out and MNAR-in are planned oracle "
        "independent inclusion mechanisms, so their realised type rates can differ from nominal.",
        "- An already-observed footprint is not leakage: it means at least one observed event "
        "of a different type induces every dyad of the held-out event type.",
        "",
        "| Mechanism | Replicate | Type rate | Record rate | Arc-removal rate | "
        "Held-out types with surviving complete footprint | Active nodes losing out / in arcs |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        rows.append(
            "| {mechanism} | {replicate} | {type_rate:.4f} | {record_rate:.4f} | "
            "{arc_rate:.4f} | {surviving}/{heldout} | {out_nodes}/{in_nodes} |".format(
                mechanism=summary["mechanism"],
                replicate=summary["replicate"],
                type_rate=float(summary["realized_event_type_mask_rate"]),
                record_rate=float(summary["realized_event_record_mask_rate"]),
                arc_rate=float(summary["realized_arc_removal_rate"]),
                surviving=summary["heldout_event_types_with_already_observed_footprint"],
                heldout=summary["heldout_event_types"],
                out_nodes=summary["nodes_losing_outgoing_arc"],
                in_nodes=summary["nodes_losing_incoming_arc"],
            )
        )
    rows.extend(
        [
            "",
            "`removal_strata.csv` in each split reports removal by tail/head arity and role "
            "degree decile. The degree deciles use deterministic equal-count actor ranks on "
            "the full cap-eligible native-event projection.",
            "",
        ]
    )
    path.write_text("\n".join(rows), encoding="utf-8")


def main() -> None:
    """Create all requested primary event-first splits with complete provenance."""
    args = parse_args()
    mechanisms = parse_mechanisms(args.mechanisms)
    events_path = resolve_path(args.events)
    nodes_path = resolve_path(args.nodes)
    output_dir = resolve_path(args.output_dir)
    prepare_output_dir(output_dir, args.overwrite)

    nodes = read_nodes(nodes_path, args.node_column)
    event_types, accounting = read_event_types(
        events_path,
        tail_column=args.event_tail_column,
        head_column=args.event_head_column,
        node_set=set(nodes),
        tail_cap=args.tail_cap,
        head_cap=args.head_cap,
    )
    full_arcs = union_arcs(event_types)
    outdegree, indegree, outgoing, incoming = degree_maps(full_arcs, nodes)
    tail_deciles = degree_deciles(outdegree)
    head_deciles = degree_deciles(indegree)

    summaries: list[dict[str, object]] = []
    for mechanism in mechanisms:
        for replicate in range(1, args.replicates + 1):
            summaries.append(
                one_mask(
                    event_types=event_types,
                    nodes=nodes,
                    mechanism=mechanism,
                    replicate=replicate,
                    seed=args.seed,
                    rate=args.mask_rate,
                    output_dir=output_dir,
                    full_arcs=full_arcs,
                    outdegree=outdegree,
                    indegree=indegree,
                    outgoing=outgoing,
                    incoming=incoming,
                    tail_deciles=tail_deciles,
                    head_deciles=head_deciles,
                )
            )

    top_manifest: dict[str, Any] = {
        "driver": "scripts/36_prepare_event_first_masks.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "target": "native_event_type",
        "input_policy": {
            "duplicate_message_records": "group_equal_tail_head_records_then_hold_"
            "each_selected_type_out_in_full",
            "role_policy": "require_nonempty_disjoint_tail_and_head_within_fixed_node_universe",
            "mnar_out_weight": "mean_full_tail_participant_activity_per_event_type",
            "mnar_in_weight": "mean_full_head_participant_activity_per_event_type",
            "tail_cap": args.tail_cap,
            "head_cap": args.head_cap,
        },
        "inputs": {
            "events": {"path": recorded_path(events_path), "sha256": sha256_file(events_path)},
            "nodes": {"path": recorded_path(nodes_path), "sha256": sha256_file(nodes_path)},
        },
        "input_accounting": asdict(accounting),
        "fixed_node_universe": len(nodes),
        "full_cap_eligible_projection_arcs": len(full_arcs),
        "requested_type_mask_rate": args.mask_rate,
        "mechanisms": list(mechanisms),
        "replicates": args.replicates,
        "seed": args.seed,
        "split_summaries": summaries,
        "limitations": [
            "This creates evaluation masks and realised-rate diagnostics; it does not score "
            "native events.",
            "MNAR-out and MNAR-in use full-data role activity by design and are therefore oracle "
            "missingness simulations.",
            "The native-event target is restricted to the declared fixed node universe and "
            "arity caps.",
            "Candidate generation, negative panels, probability calibration, and role-assignment "
            "scoring remain separate steps.",
        ],
    }
    write_csv(output_dir / "split_summary.csv", summaries)
    (output_dir / "manifest.json").write_text(
        json.dumps(top_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary_markdown(output_dir / "summary.md", args.dataset_id, summaries)
    print("Event-first native-event-type masking passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Cap-eligible native event records: {accounting.cap_eligible_event_records:,}.")
    print(f"Cap-eligible native event types: {len(event_types):,}.")
    print(f"Full cap-eligible projection arcs: {len(full_arcs):,}.")
    print(f"Masks written: {len(summaries):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
