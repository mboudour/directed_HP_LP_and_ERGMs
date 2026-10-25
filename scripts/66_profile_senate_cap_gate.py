#!/usr/bin/env python3
"""Profile Senate head caps before freezing a primary missingness benchmark.

The profile keeps every source event intact, then reports how an exclusion-based
head cap changes retained bill records, distinct ordered coalition types, static
footprint coverage, grammar-valid random negatives, sponsor substitutions, and
fixed-participant sponsor-identification alternatives. It does not truncate any
coalition and it does not select the primary cap.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from collections import Counter
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Event:
    """One prepared singleton-sponsor, original-co-sponsor bill event."""

    sponsor: str
    head: tuple[str, ...]

    @property
    def key(self) -> tuple[str, tuple[str, ...]]:
        """Return the event's canonical ordered role-set identity."""
        return self.sponsor, self.head

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return sponsor-to-original-co-sponsor arcs induced by this bill."""
        return frozenset(product((self.sponsor,), self.head))


def parse_args() -> argparse.Namespace:
    """Parse explicit fixed-universe prepared inputs and cap candidates."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument(
        "--events",
        type=Path,
        default=Path("data/processed/senate_118_s_bills/native_events.parquet"),
    )
    parser.add_argument(
        "--nodes",
        type=Path,
        default=Path("data/processed/senate_118_s_bills/nodes.csv"),
    )
    parser.add_argument(
        "--arcs",
        type=Path,
        default=Path("data/processed/senate_118_s_bills/static_arcs.parquet"),
    )
    parser.add_argument("--caps", default="1,2,3,5,10")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results/phase2/senate_118_s_bills_cap_gate")
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        caps = tuple(sorted({int(item.strip()) for item in args.caps.split(",") if item.strip()}))
    except ValueError as error:
        parser.error(f"--caps must be comma-separated positive integers: {error}")
    if not caps or any(cap < 1 for cap in caps):
        parser.error("--caps must contain at least one positive integer.")
    args.caps = caps
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative file paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render a repository-relative provenance path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_nodes(path: Path) -> tuple[str, ...]:
    """Read a fixed Bioguide universe from the prepared node CSV."""
    if not path.is_file():
        raise SystemExit(f"STOP: node table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "node" not in reader.fieldnames:
            raise SystemExit("STOP: Senate node table lacks the node column.")
        nodes = tuple(sorted(row["node"].strip() for row in reader))
    if not nodes or any(not node for node in nodes) or len(nodes) != len(set(nodes)):
        raise SystemExit("STOP: Senate node table has empty or duplicate IDs.")
    return nodes


def read_events(path: Path, nodes: set[str]) -> tuple[Event, ...]:
    """Read scalar sponsor and list original-cosponsor roles from prepared Parquet."""
    if not path.is_file():
        raise SystemExit(f"STOP: native event table is missing: {path}")
    source = pq.ParquetFile(path)
    required = {"tail_sponsor_bioguide", "head_original_cosponsors_bioguide"}
    if missing := required - set(source.schema_arrow.names):
        raise SystemExit(f"STOP: native event table lacks columns {sorted(missing)}")
    events: list[Event] = []
    for batch in source.iter_batches(columns=sorted(required), batch_size=50_000):
        for row in batch.to_pylist():
            sponsor = str(row["tail_sponsor_bioguide"] or "").strip()
            raw_head = row["head_original_cosponsors_bioguide"]
            if not sponsor or not isinstance(raw_head, list):
                raise SystemExit("STOP: malformed prepared Senate role values.")
            head = tuple(sorted({str(item).strip() for item in raw_head if item is not None}))
            if not head or any(not item for item in head) or sponsor in head:
                raise SystemExit("STOP: prepared Senate event violates the role policy.")
            if sponsor not in nodes or any(item not in nodes for item in head):
                raise SystemExit(
                    "STOP: prepared event references a node outside the fixed universe."
                )
            events.append(Event(sponsor=sponsor, head=head))
    if not events:
        raise SystemExit("STOP: native event table is empty.")
    return tuple(events)


def read_arcs(path: Path, nodes: set[str]) -> frozenset[tuple[str, str]]:
    """Read the full prepared binary static directed projection."""
    if not path.is_file():
        raise SystemExit(f"STOP: static arc table is missing: {path}")
    source = pq.ParquetFile(path)
    if {"tail", "head"} - set(source.schema_arrow.names):
        raise SystemExit("STOP: Senate static arc table lacks tail/head columns.")
    arcs: set[tuple[str, str]] = set()
    for batch in source.iter_batches(columns=["tail", "head"], batch_size=50_000):
        for row in batch.to_pylist():
            tail, head = str(row["tail"]).strip(), str(row["head"]).strip()
            if not tail or not head or tail == head or tail not in nodes or head not in nodes:
                raise SystemExit("STOP: malformed prepared Senate static arc.")
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit("STOP: Senate static projection has no arcs.")
    return frozenset(arcs)


def unique_types(events: tuple[Event, ...]) -> tuple[Event, ...]:
    """Collapse repeated bill records to the benchmark's ordered event-type target."""
    by_key = {event.key: event for event in events}
    return tuple(by_key[key] for key in sorted(by_key))


def sponsor_substitution_capacity(
    types: tuple[Event, ...], full_keys: set[tuple[str, tuple[str, ...]]]
) -> tuple[int, int]:
    """Count type positives and valid unseen sponsor swaps under the Senate grammar."""
    eligible_types = 0
    alternatives = 0
    for event in types:
        valid = 0
        for substitute in event.head:
            candidate = (
                substitute,
                tuple(sorted((set(event.head) - {substitute}) | {event.sponsor})),
            )
            if candidate not in full_keys:
                valid += 1
        eligible_types += int(valid > 0)
        alternatives += valid
    return eligible_types, alternatives


def rows_for_cap(
    cap: int,
    events: tuple[Event, ...],
    all_types: tuple[Event, ...],
    all_arcs: frozenset[tuple[str, str]],
    nodes: tuple[str, ...],
) -> dict[str, object]:
    """Summarize a strict no-truncation head cap and its candidate implications."""
    retained_records = tuple(event for event in events if len(event.head) <= cap)
    retained_types = unique_types(retained_records)
    cap_arcs = frozenset(arc for event in retained_records for arc in event.footprint)
    full_keys = {event.key for event in all_types}
    sponsor_types, sponsor_alternatives = sponsor_substitution_capacity(retained_types, full_keys)
    random_capacity = sum(
        len(nodes) * math.comb(len(nodes) - 1, head_size)
        - sum(len(event.head) == head_size for event in all_types)
        for head_size in sorted({len(event.head) for event in retained_types})
    )
    return {
        "head_cap": cap,
        "retained_event_records": len(retained_records),
        "record_retention": len(retained_records) / len(events),
        "retained_event_types": len(retained_types),
        "type_retention": len(retained_types) / len(all_types),
        "cap_projection_arcs": len(cap_arcs),
        "full_static_arc_coverage": len(cap_arcs.intersection(all_arcs)) / len(all_arcs),
        "grammar_valid_random_non_event_capacity": random_capacity,
        "sponsor_substitution_eligible_event_types": sponsor_types,
        "sponsor_substitution_valid_alternatives": sponsor_alternatives,
        "role_assignment_event_types": len(retained_types),
        "role_assignment_partitions": sum(len(event.head) + 1 for event in retained_types),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty deterministic CSV output."""
    if not rows:
        raise RuntimeError(f"cannot write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create or explicitly replace the cap-gate result directory."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}; pass --overwrite.")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Profile declared Senate caps without changing or truncating event data."""
    args = parse_args()
    event_path, node_path, arc_path, output_dir = (
        resolve(args.events),
        resolve(args.nodes),
        resolve(args.arcs),
        resolve(args.output_dir),
    )
    prepare_output(output_dir, args.overwrite)
    nodes = read_nodes(node_path)
    events = read_events(event_path, set(nodes))
    arcs = read_arcs(arc_path, set(nodes))
    all_types = unique_types(events)
    cap_rows = [rows_for_cap(cap, events, all_types, arcs, nodes) for cap in args.caps]
    head_records = Counter(len(event.head) for event in events)
    head_types = Counter(len(event.head) for event in all_types)
    arity_rows = [
        {
            "head_arity": arity,
            "event_records": head_records[arity],
            "event_types": head_types[arity],
            "record_fraction": head_records[arity] / len(events),
            "type_fraction": head_types[arity] / len(all_types),
        }
        for arity in sorted(set(head_records) | set(head_types))
    ]
    write_csv(output_dir / "head_arity_distribution.csv", arity_rows)
    write_csv(output_dir / "cap_profile.csv", cap_rows)
    summary = {
        "dataset_id": args.dataset_id,
        "status": "completed_pending_formal_concept_feasibility",
        "driver": "scripts/66_profile_senate_cap_gate.py",
        "inputs": {
            "events": recorded(event_path),
            "nodes": recorded(node_path),
            "static_arcs": recorded(arc_path),
        },
        "event_target": {
            "records": len(events),
            "distinct_ordered_types": len(all_types),
            "tail_arity": 1,
            "head_cap_policy": "exclusion_only; no coalition is truncated",
        },
        "static_projection": {"nodes": len(nodes), "directed_arcs": len(arcs)},
        "caps": cap_rows,
        "candidate_interpretation": {
            "random_capacity": (
                "All grammar-valid singleton-sponsor/nonoverlapping-head non-event types in the "
                "full fixed universe at retained observed head arities; it precedes split-specific "
                "weak-distance restrictions."
            ),
            "sponsor_substitution": (
                "An unseen candidate created by swapping the recorded sponsor with one recorded "
                "original co-sponsor, preserving the one-sponsor grammar and participant set."
            ),
            "role_assignment": (
                "All singleton-tail partitions of a known event participant set; h+1 candidate "
                "sponsor assignments for a head of size h."
            ),
        },
        "next_gate": (
            "Run cap-first formal-concept enumeration at each viable cap and a one-split "
            "end-to-end candidate/ERGM pilot before freezing the primary Senate head cap."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Senate cap-first event and candidate profile",
        "",
        f"- Dataset: `{args.dataset_id}`",
        f"- Fixed actor universe: `{len(nodes):,}` persons",
        f"- Valid nonempty-head bill records: `{len(events):,}`",
        f"- Distinct ordered sponsor/head types: `{len(all_types):,}`",
        f"- Full static sponsor-to-original-co-sponsor arcs: `{len(arcs):,}`",
        "- Cap policy: events above the cap are excluded; no head is shortened.",
        "",
        "## Original co-sponsor head arity",
        "",
        "| Head size | Bill records | Ordered types | Record fraction | Type fraction |",
        "|---:|---:|---:|---:|---:|",
    ]
    lines.extend(
        "| {head_arity} | {event_records:,} | {event_types:,} | {record_fraction:.3%} | "
        "{type_fraction:.3%} |".format(**row)
        for row in arity_rows
    )
    lines.extend(
        [
            "",
            "## Strict cap profile",
            "",
            "| Head cap | Records retained | Record retention | Types retained | Type retention | "
            "Static arc coverage | Sponsor-substitution types | Role partitions |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    lines.extend(
        "| {head_cap} | {retained_event_records:,} | {record_retention:.3%} | "
        "{retained_event_types:,} | {type_retention:.3%} | {full_static_arc_coverage:.3%} | "
        "{sponsor_substitution_eligible_event_types:,} | {role_assignment_partitions:,} |".format(
            **row
        )
        for row in cap_rows
    )
    lines.extend(
        [
            "",
            "The profile establishes retention and grammar feasibility only. Formal-concept "
            "enumeration and split-specific candidate/ERGM pilot results are separate cap-gate "
            "requirements; this report does not select a primary cap.",
            "",
        ]
    )
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Senate cap-first profile passed.")
    print(f"Dataset: {args.dataset_id}; event records: {len(events):,}; types: {len(all_types):,}.")
    print(f"Caps: {', '.join(str(cap) for cap in args.caps)}.")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
