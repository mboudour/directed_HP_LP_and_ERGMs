#!/usr/bin/env python3
"""Audit a capped directed formal-concept section for one prepared static graph.

The driver creates reproducible, local-only representation evidence required before
masked hyperlink experiments are scaled. It enumerates concepts with caps applied by
the project formal-concept module before closure, reports arity/role-overlap and arc
multiplicity distributions, and writes the resulting concept list for later targets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from statistics import median

import pyarrow.parquet as pq

from directed_hp.hypergraphs.formal_concepts import DirectedFormalConcept, enumerate_formal_concepts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAX_CANDIDATES = 250_000
OUTPUT_FILES = (
    "concepts.csv",
    "arity_distribution.csv",
    "arc_multiplicity.csv",
    "summary.json",
    "summary.md",
)


def display_path(path: Path) -> str:
    """Use a repository-relative path where possible without rejecting external fixtures."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    """Parse an explicit graph and enumeration contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Stable dataset identifier.")
    parser.add_argument("--edges", required=True, type=Path, help="Parquet edge table.")
    parser.add_argument(
        "--nodes", required=True, type=Path, help="CSV table defining the node universe."
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Output directory owned by this driver."
    )
    parser.add_argument("--source-col", default="tail", help="Source column in --edges.")
    parser.add_argument("--target-col", default="head", help="Target column in --edges.")
    parser.add_argument("--node-col", default="node", help="Node-ID column in --nodes.")
    parser.add_argument(
        "--tail-cap", type=int, required=True, help="Positive maximum formal-concept tail arity."
    )
    parser.add_argument(
        "--head-cap", type=int, required=True, help="Positive maximum formal-concept head arity."
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help=f"Maximum cap-first seed candidates (default: {DEFAULT_MAX_CANDIDATES:,}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only files produced by this driver in --output-dir.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 digest for a declared input file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_positive(value: int, label: str) -> int:
    """Reject zero, negative, and accidental non-integer arity caps."""
    if value < 1:
        raise SystemExit(f"STOP: {label} must be at least 1; received {value}.")
    return value


def read_nodes(path: Path, node_col: str) -> tuple[str, ...]:
    """Read a declared fixed node universe with lexical canonical ordering."""
    if not path.is_file():
        raise SystemExit(f"STOP: node table is missing: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or node_col not in reader.fieldnames:
            raise SystemExit(f"STOP: node column {node_col!r} is absent from {path}.")
        nodes = [str(row[node_col]).strip() for row in reader]
    if not nodes or any(not node for node in nodes):
        raise SystemExit("STOP: node table must contain one non-empty ID on every row.")
    if len(nodes) != len(set(nodes)):
        raise SystemExit("STOP: node table contains duplicate IDs.")
    return tuple(sorted(nodes))


def read_edges(
    path: Path,
    source_col: str,
    target_col: str,
    nodes: set[str],
) -> tuple[tuple[str, str], ...]:
    """Read, validate, deduplicate, and canonically order a binary arc relation."""
    if not path.is_file():
        raise SystemExit(f"STOP: edge table is missing: {path}")
    schema = pq.ParquetFile(path).schema_arrow
    required = {source_col, target_col}
    if missing := required - set(schema.names):
        raise SystemExit(f"STOP: edge table is missing required columns: {sorted(missing)}")
    arcs: set[tuple[str, str]] = set()
    for batch in pq.ParquetFile(path).iter_batches(columns=[source_col, target_col]):
        sources = batch.column(0).to_pylist()
        targets = batch.column(1).to_pylist()
        for source, target in zip(sources, targets, strict=True):
            tail, head = str(source).strip(), str(target).strip()
            if not tail or not head:
                raise SystemExit("STOP: edge table has an empty endpoint.")
            if tail == head:
                raise SystemExit("STOP: edge table contains a self-loop; remove loops upstream.")
            if tail not in nodes or head not in nodes:
                raise SystemExit("STOP: edge endpoint is absent from the declared node universe.")
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit("STOP: edge table contains no non-self directed arcs.")
    return tuple(sorted(arcs))


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create an output directory without deleting any file this driver does not own."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    existing = [path / name for name in OUTPUT_FILES if (path / name).exists()]
    if existing and not overwrite:
        rendered = "\n  ".join(str(item) for item in existing)
        raise SystemExit(
            "STOP: formal-concept audit output already exists. Pass --overwrite to replace only "
            f"this driver's files:\n  {rendered}"
        )
    for item in existing:
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def json_nodes(nodes: Iterable[str]) -> str:
    """Serialize an ordered role set without a delimiter collision risk."""
    return json.dumps(list(nodes), ensure_ascii=False, separators=(",", ","))


def percentile(values: list[int], probability: float) -> float | None:
    """Return a deterministic linear-interpolated percentile for non-empty integers."""
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower, upper = int(index), min(int(index) + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    """Write a deterministic LF-terminated CSV."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def concept_rows(concepts: tuple[DirectedFormalConcept, ...]) -> list[dict[str, object]]:
    """Convert immutable concepts into a stable row contract for downstream targets."""
    rows: list[dict[str, object]] = []
    for concept_id, concept in enumerate(concepts, start=1):
        tail = tuple(str(node) for node in concept.tail)
        head = tuple(str(node) for node in concept.head)
        rows.append(
            {
                "concept_id": concept_id,
                "tail_nodes_json": json_nodes(tail),
                "head_nodes_json": json_nodes(head),
                "tail_arity": len(tail),
                "head_arity": len(head),
                "total_role_arity": len(tail) + len(head),
                "footprint_arcs": len(tail) * len(head),
                "role_overlap_nodes": len(set(tail) & set(head)),
            }
        )
    return rows


def main() -> None:
    """Run one cap-first, deterministic representation audit."""
    args = parse_args()
    tail_cap = validate_positive(args.tail_cap, "--tail-cap")
    head_cap = validate_positive(args.head_cap, "--head-cap")
    if args.max_candidates < 1:
        raise SystemExit("STOP: --max-candidates must be positive.")

    output_dir = (
        args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    )
    edge_path = args.edges if args.edges.is_absolute() else PROJECT_ROOT / args.edges
    node_path = args.nodes if args.nodes.is_absolute() else PROJECT_ROOT / args.nodes
    nodes = read_nodes(node_path, args.node_col)
    arcs = read_edges(edge_path, args.source_col, args.target_col, set(nodes))
    prepare_output(output_dir, args.overwrite)

    try:
        concepts = enumerate_formal_concepts(
            arcs,
            nodes=nodes,
            max_tail_arity=tail_cap,
            max_head_arity=head_cap,
            max_candidates=args.max_candidates,
        )
    except ValueError as error:
        raise SystemExit(
            f"STOP: cap-first formal-concept enumeration refused this request: {error}"
        ) from error

    rows = concept_rows(concepts)
    write_csv(
        output_dir / "concepts.csv",
        [
            "concept_id",
            "tail_nodes_json",
            "head_nodes_json",
            "tail_arity",
            "head_arity",
            "total_role_arity",
            "footprint_arcs",
            "role_overlap_nodes",
        ],
        rows,
    )

    arity = Counter((row["tail_arity"], row["head_arity"]) for row in rows)
    arity_footprints: Counter[tuple[int, int]] = Counter()
    for row in rows:
        arity_footprints[(int(row["tail_arity"]), int(row["head_arity"]))] += int(
            row["footprint_arcs"]
        )
    arity_rows = [
        {
            "tail_arity": tail,
            "head_arity": head,
            "concepts": arity[(tail, head)],
            "concept_footprint_arcs": arity_footprints[(tail, head)],
        }
        for tail, head in sorted(arity)
    ]
    write_csv(
        output_dir / "arity_distribution.csv",
        ["tail_arity", "head_arity", "concepts", "concept_footprint_arcs"],
        arity_rows,
    )

    multiplicity: Counter[tuple[str, str]] = Counter()
    for concept in concepts:
        for tail in concept.tail:
            for head in concept.head:
                multiplicity[(str(tail), str(head))] += 1
    multiplicity_rows = [
        {"tail": tail, "head": head, "concept_count": multiplicity[(tail, head)]}
        for tail, head in arcs
    ]
    write_csv(
        output_dir / "arc_multiplicity.csv",
        ["tail", "head", "concept_count"],
        multiplicity_rows,
    )

    multiplicities = [int(row["concept_count"]) for row in multiplicity_rows]
    covered_arcs = sum(value > 0 for value in multiplicities)
    summary = {
        "dataset_id": args.dataset,
        "driver": "scripts/28_audit_formal_concepts.py",
        "input": {
            "edges": display_path(edge_path),
            "nodes": display_path(node_path),
            "edges_sha256": sha256(edge_path),
            "nodes_sha256": sha256(node_path),
            "source_column": args.source_col,
            "target_column": args.target_col,
            "node_column": args.node_col,
        },
        "enumeration": {
            "algorithm": "cap_first_directed_galois_closure",
            "tail_cap": tail_cap,
            "head_cap": head_cap,
            "max_candidates": args.max_candidates,
            "caps_applied_during_enumeration": True,
        },
        "graph": {"nodes": len(nodes), "directed_arcs": len(arcs), "self_loops": 0},
        "concepts": {
            "count": len(concepts),
            "multi_role_count": sum(
                int(row["tail_arity"]) > 1 or int(row["head_arity"]) > 1 for row in rows
            ),
            "role_overlap_count": sum(int(row["role_overlap_nodes"]) > 0 for row in rows),
            "capped_footprint_arc_coverage": covered_arcs / len(arcs),
            "capped_footprint_arcs_covered": covered_arcs,
            "arc_concept_multiplicity": {
                "minimum": min(multiplicities),
                "median": median(multiplicities),
                "p95": percentile(multiplicities, 0.95),
                "maximum": max(multiplicities),
            },
        },
        "output": {
            "concepts": "concepts.csv",
            "arity_distribution": "arity_distribution.csv",
            "arc_multiplicity": "arc_multiplicity.csv",
        },
        "interpretation": (
            "This is a representation audit of capped formal concepts, not a native-event "
            "analysis and not a hyperlink-prediction score. A capped section need not cover "
            "every observed arc; coverage and overlap are reported explicitly."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    multi_role_count = summary["concepts"]["multi_role_count"]
    role_overlap_count = summary["concepts"]["role_overlap_count"]
    coverage = summary["concepts"]["capped_footprint_arc_coverage"]
    (output_dir / "summary.md").write_text(
        "# Capped directed formal-concept audit\n\n"
        f"- Dataset: `{args.dataset}`\n"
        f"- Fixed node universe: `{len(nodes):,}` nodes\n"
        f"- Observed binary directed arcs: `{len(arcs):,}`\n"
        f"- Cap-first enumeration: `|T| ≤ {tail_cap}`, `|H| ≤ {head_cap}`\n"
        f"- Concepts emitted: `{len(concepts):,}`\n"
        f"- Concepts with tail or head arity greater than one: `{multi_role_count:,}`\n"
        f"- Concepts with a node in both roles: `{role_overlap_count:,}`\n"
        f"- Observed arcs covered by capped concept footprints: `{covered_arcs:,}/{len(arcs):,}` "
        f"(`{coverage:.3%}`)\n"
        f"- Arc concept multiplicity (min / median / p95 / max): "
        f"`{min(multiplicities)} / {median(multiplicities)} / "
        f"{percentile(multiplicities, 0.95):.2f} / {max(multiplicities)}`\n\n"
        "The cap is applied during enumeration rather than to an already enumerated concept "
        "set. This output is a required representation diagnostic before choosing analysis "
        "caps and running missingness experiments. It does not assert that formal concepts "
        "are recorded group events.\n",
        encoding="utf-8",
    )
    print("Capped formal-concept audit passed.")
    print(f"Dataset: {args.dataset}.")
    print(f"Nodes: {len(nodes):,}; directed arcs: {len(arcs):,}.")
    print(f"Caps: tail={tail_cap}, head={head_cap}; concepts: {len(concepts):,}.")
    print(f"Output bundle: {display_path(output_dir)}")


if __name__ == "__main__":
    main()
