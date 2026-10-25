#!/usr/bin/env python3
"""Run the reproducible static LP/concept/masking pilot for one prepared dataset.

This driver intentionally performs the plan's **bounded pilot**, not the final
publication-scale grid. It creates a local output bundle containing: a frozen static
arc input, optional formal-concept fidelity diagnostics, deterministic missingness
replicates, OI/OO/II and directed Adamic--Adar scores, random-negative LP metrics, and
CSV files ready for the static R ERGM ladder. It never bypasses a source's data gate.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from directed_hp.evaluation.metrics import pr_auc, roc_auc
from directed_hp.hypergraphs.formal_concepts import augmented_section, enumerate_formal_concepts
from directed_hp.lp.directed_scores import DirectedScoreEngine
from directed_hp.masking.directed_masks import MaskingMechanism, mask_arc_first

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = 20_261_013
DEFAULT_REPLICATES = 3
DEFAULT_MASK_RATE = 0.30

DATASET_DEFAULTS: dict[str, dict[str, str]] = {
    "eu_core": {
        "arcs": "data/processed/email_eu_core_temporal/core100_static_arcs.parquet",
        "nodes": "data/processed/email_eu_core_temporal/core100_nodes.csv",
        "node_column": "node",
        "tail_column": "tail",
        "head_column": "head",
    },
    "enron": {
        "arcs": "data/processed/enron_20150507/custodian_core100_static_arcs.parquet",
        "nodes": "data/processed/enron_20150507/custodian_core100_nodes.csv",
        "node_column": "custodian_mailbox",
        "tail_column": "tail_custodian",
        "head_column": "head_custodian",
    },
    "caviar": {
        "arcs": "data/processed/caviar/directed_valued_arcs.parquet",
        "nodes": "data/processed/caviar/nodes.csv",
        "node_column": "id",
        "tail_column": "tail",
        "head_column": "head",
    },
    "mathoverflow": {
        "arcs": "data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet",
        "nodes": "data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv",
        "node_column": "node",
        "tail_column": "tail",
        "head_column": "head",
    },
    "ciel": {
        "arcs": "data/processed/ciel/directed_valued_arcs.parquet",
        "nodes": "",
        "node_column": "",
        "tail_column": "tail",
        "head_column": "head",
    },
    "senate_118_s_bills": {
        "arcs": "data/processed/senate_118_s_bills/static_arcs.parquet",
        "nodes": "data/processed/senate_118_s_bills/nodes.csv",
        "node_column": "node",
        "tail_column": "tail",
        "head_column": "head",
    },
}

PREDICTION_SCHEMA = pa.schema(
    [
        pa.field("replicate", pa.int16()),
        pa.field("mechanism", pa.string()),
        pa.field("candidate_tail", pa.string()),
        pa.field("candidate_head", pa.string()),
        pa.field("label", pa.int8()),
        pa.field("panel", pa.string()),
        pa.field("oi", pa.int32()),
        pa.field("oo", pa.int32()),
        pa.field("ii", pa.int32()),
        pa.field("common_neighbor_total", pa.int32()),
        pa.field("adamic_adar_oi", pa.float64()),
        pa.field("adamic_adar_oo", pa.float64()),
        pa.field("adamic_adar_ii", pa.float64()),
        pa.field("adamic_adar_total", pa.float64()),
    ]
)


def parse_args() -> argparse.Namespace:
    """Parse the explicit pilot contract; no hidden source-data assumptions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=sorted(DATASET_DEFAULTS))
    parser.add_argument(
        "--arcs", type=Path, help="Prepared Parquet arc table; overrides dataset default."
    )
    parser.add_argument(
        "--nodes", type=Path, help="Optional prepared CSV node table; overrides dataset default."
    )
    parser.add_argument("--tail-column", help="Arc-table tail column; overrides dataset default.")
    parser.add_argument("--head-column", help="Arc-table head column; overrides dataset default.")
    parser.add_argument("--node-column", help="Node-table ID column; overrides dataset default.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="New local results folder; default is results/phase2/<dataset>_static_pilot.",
    )
    parser.add_argument("--mask-rate", type=float, default=DEFAULT_MASK_RATE)
    parser.add_argument(
        "--mechanism", choices=[item.value for item in MaskingMechanism], default="mcar"
    )
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--tail-cap", type=int, default=2)
    parser.add_argument("--head-cap", type=int, default=2)
    parser.add_argument("--max-concept-candidates", type=int, default=1_000_000)
    parser.add_argument("--skip-concepts", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not 0.0 <= args.mask_rate <= 1.0:
        parser.error("--mask-rate must be between 0 and 1.")
    if args.replicates < 1:
        parser.error("--replicates must be at least 1.")
    if args.seed < 0:
        parser.error("--seed must be non-negative.")
    if args.tail_cap < 1 or args.head_cap < 1:
        parser.error("--tail-cap and --head-cap must be at least 1.")
    if args.max_concept_candidates < 1:
        parser.error("--max-concept-candidates must be at least 1.")
    return args


def resolve_path(value: Path | None, fallback: str) -> Path | None:
    """Resolve an optional local path relative to the repository root."""
    if value is not None:
        return value if value.is_absolute() else PROJECT_ROOT / value
    if not fallback:
        return None
    return PROJECT_ROOT / fallback


def recorded_path(path: Path) -> str:
    """Use a repository-relative path when possible, otherwise retain an absolute one."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_arcs(path: Path, tail_column: str, head_column: str) -> tuple[tuple[str, str], ...]:
    """Read a simple prepared Parquet arc table, remove loops, and deduplicate."""
    if not path.is_file():
        raise SystemExit(f"STOP: prepared arc table is missing: {path}")
    source = pq.ParquetFile(path)
    missing = {tail_column, head_column} - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(
            f"STOP: arc table {path} lacks columns {sorted(missing)}; "
            f"available columns are {source.schema_arrow.names}."
        )
    ordered: dict[tuple[str, str], None] = {}
    loops = 0
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            tail = str(row[tail_column])
            head = str(row[head_column])
            if tail == head:
                loops += 1
                continue
            ordered.setdefault((tail, head), None)
    if not ordered:
        raise SystemExit("STOP: no loop-free arcs remain after reading prepared table.")
    if loops:
        print(f"Note: ignored {loops:,} self-loop rows in prepared arc table.")
    return tuple(ordered)


def read_nodes(
    path: Path | None, node_column: str, arcs: tuple[tuple[str, str], ...]
) -> tuple[str, ...]:
    """Read the full prepared node universe where available, preserving isolates."""
    inferred = {node for arc in arcs for node in arc}
    if path is None:
        return tuple(sorted(inferred))
    if not path.is_file():
        raise SystemExit(f"STOP: prepared node table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or node_column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table must contain column {node_column!r}: {path}")
        ordered: dict[str, None] = {}
        for row in reader:
            node = str(row[node_column]).strip()
            if node:
                ordered.setdefault(node, None)
    nodes = tuple(ordered)
    if not nodes:
        raise SystemExit("STOP: prepared node table has no nonempty node IDs.")
    unknown = inferred - set(nodes)
    if unknown:
        raise SystemExit(
            "STOP: arc table contains nodes absent from the declared node table: "
            + ", ".join(sorted(unknown)[:10])
        )
    return nodes


def negative_pool(
    nodes: tuple[str, ...], full_arcs: set[tuple[str, str]]
) -> tuple[tuple[str, str], ...]:
    """Generate true nonedges for a static LP random-negative panel."""
    return tuple(
        (tail, head)
        for tail in nodes
        for head in nodes
        if tail != head and (tail, head) not in full_arcs
    )


def choose_negatives(
    pool: tuple[tuple[str, str], ...], count: int, seed: int
) -> tuple[tuple[str, str], ...]:
    """Select deterministic without-replacement random negatives without pandas overhead."""
    if count > len(pool):
        raise SystemExit(
            f"STOP: require {count:,} true nonedges but static candidate pool has only "
            f"{len(pool):,}."
        )
    # NumPy is already a locked project dependency and uses an isolated RNG stream.
    import numpy as np

    positions = np.random.default_rng(seed).choice(len(pool), size=count, replace=False)
    return tuple(pool[int(position)] for position in positions)


def write_r_inputs(
    output_dir: Path, arcs: tuple[tuple[str, str], ...], nodes: tuple[str, ...]
) -> None:
    """Write the portable CSV contract consumed by the static R ERGM driver."""
    r_dir = output_dir / "r_inputs"
    r_dir.mkdir(parents=True, exist_ok=True)
    with (r_dir / "static_edges.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["from", "to"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"from": tail, "to": head} for tail, head in arcs)
    with (r_dir / "nodes.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"id": node} for node in nodes)


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    """Create a fresh pilot bundle, replacing it only on an explicit request."""
    if output_dir.exists() and not output_dir.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            raise SystemExit(
                f"STOP: output directory is nonempty: {output_dir}\n"
                "Pass --overwrite only after preserving or removing the previous run."
            )
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def write_concept_fidelity(
    output_dir: Path,
    arcs: tuple[tuple[str, str], ...],
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Record bounded formal-concept fidelity without claiming a concept predictor."""
    formal = enumerate_formal_concepts(
        arcs,
        max_tail_arity=args.tail_cap,
        max_head_arity=args.head_cap,
        max_candidates=args.max_concept_candidates,
    )
    augmented = augmented_section(
        arcs,
        max_tail_arity=args.tail_cap,
        max_head_arity=args.head_cap,
        max_candidates=args.max_concept_candidates,
    )
    covered = {arc for concept in formal for arc in concept.footprint}
    output = output_dir / "concept_section.csv"
    with output.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["section", "tail", "head", "tail_size", "head_size", "footprint_size"],
            lineterminator="\n",
        )
        writer.writeheader()
        for section_name, concepts in (("formal", formal), ("augmented", augmented)):
            for concept in concepts:
                writer.writerow(
                    {
                        "section": section_name,
                        "tail": "|".join(map(str, concept.tail)),
                        "head": "|".join(map(str, concept.head)),
                        "tail_size": len(concept.tail),
                        "head_size": len(concept.head),
                        "footprint_size": len(concept.footprint),
                    }
                )
    return {
        "formal_concepts": len(formal),
        "augmented_section_pairs": len(augmented),
        "formal_footprint_covered_arcs": len(covered),
        "formal_footprint_coverage": len(covered) / len(arcs),
        "tail_cap": args.tail_cap,
        "head_cap": args.head_cap,
        "concept_section": recorded_path(output),
        "interpretation": (
            "Formal-section coverage measures representation fidelity only. "
            "The augmented section adds observed singleton arcs to guarantee arc coverage; "
            "it is not itself a formal-concept-only target set."
        ),
    }


def run_replicates(
    arcs: tuple[tuple[str, str], ...],
    nodes: tuple[str, ...],
    full_arc_set: set[tuple[str, str]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create masking replicates, LP predictions, and random-negative metrics."""
    pool = negative_pool(nodes, full_arc_set)
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    mechanism = MaskingMechanism(args.mechanism)

    for replicate in range(1, args.replicates + 1):
        mask_seed = args.seed + replicate - 1
        mask = mask_arc_first(arcs, rate=args.mask_rate, mechanism=mechanism, seed=mask_seed)
        positives = tuple((str(tail), str(head)) for tail, head in mask.held_out_arcs)
        if not positives:
            raise SystemExit(
                "STOP: masking produced no held-out arcs. Increase the mask rate or use a "
                "larger network."
            )
        negatives = choose_negatives(pool, len(positives), args.seed + 10_000 + replicate)
        candidates = positives + negatives
        labels = [1] * len(positives) + [0] * len(negatives)
        engine = DirectedScoreEngine(mask.observed_arcs, nodes=nodes)

        component_scores: dict[str, list[float]] = {
            "oi": [],
            "oo": [],
            "ii": [],
            "common_neighbor_total": [],
            "adamic_adar_oi": [],
            "adamic_adar_oo": [],
            "adamic_adar_ii": [],
            "adamic_adar_total": [],
        }
        for (tail, head), label in zip(candidates, labels, strict=True):
            score = engine.score(tail, head)
            row = {
                "replicate": replicate,
                "mechanism": args.mechanism,
                "candidate_tail": str(tail),
                "candidate_head": str(head),
                "label": label,
                "panel": "random_true_nonedges",
                "oi": score.common_neighbors.oi,
                "oo": score.common_neighbors.oo,
                "ii": score.common_neighbors.ii,
                "common_neighbor_total": score.common_neighbors.total,
                "adamic_adar_oi": score.adamic_adar.oi,
                "adamic_adar_oo": score.adamic_adar.oo,
                "adamic_adar_ii": score.adamic_adar.ii,
                "adamic_adar_total": score.adamic_adar.total,
            }
            prediction_rows.append(row)
            for name in component_scores:
                component_scores[name].append(float(row[name]))

        for method, scores in component_scores.items():
            metric_rows.append(
                {
                    "replicate": replicate,
                    "method": method,
                    "panel": "random_true_nonedges",
                    "roc_auc": roc_auc(labels, scores),
                    "pr_auc": pr_auc(labels, scores),
                    "positives": len(positives),
                    "negatives": len(negatives),
                    **asdict(mask.accounting),
                }
            )
    return metric_rows, prediction_rows


def main() -> None:
    """Run the static pilot, refusing to overwrite a prior output bundle."""
    args = parse_args()
    defaults = DATASET_DEFAULTS[args.dataset]
    arc_path = resolve_path(args.arcs, defaults["arcs"])
    node_path = resolve_path(args.nodes, defaults["nodes"])
    tail_column = args.tail_column or defaults["tail_column"]
    head_column = args.head_column or defaults["head_column"]
    node_column = args.node_column or defaults["node_column"]
    output_dir = (
        args.output_dir or PROJECT_ROOT / "results" / "phase2" / f"{args.dataset}_static_pilot"
    )
    output_dir = output_dir if output_dir.is_absolute() else PROJECT_ROOT / output_dir

    prepare_output_dir(output_dir, args.overwrite)

    arcs = read_arcs(arc_path, tail_column, head_column)
    nodes = read_nodes(node_path, node_column, arcs)
    full_arc_set = set(arcs)
    if len(nodes) < 3:
        raise SystemExit("STOP: static pilot requires at least three nodes.")

    write_r_inputs(output_dir, arcs, nodes)
    concept_summary = (
        {"status": "skipped"}
        if args.skip_concepts
        else write_concept_fidelity(output_dir, arcs, args)
    )
    metric_rows, prediction_rows = run_replicates(arcs, nodes, full_arc_set, args)
    pq.write_table(
        pa.Table.from_pylist(prediction_rows, schema=PREDICTION_SCHEMA),
        output_dir / "arc_lp_predictions.parquet",
        compression="zstd",
    )
    with (output_dir / "arc_lp_metrics.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(metric_rows)

    manifest = {
        "dataset": args.dataset,
        "pilot_type": "static_arc_lp_and_representation_fidelity",
        "input_arcs": recorded_path(arc_path),
        "input_nodes": recorded_path(node_path) if node_path else None,
        "tail_column": tail_column,
        "head_column": head_column,
        "nodes": len(nodes),
        "static_arcs": len(arcs),
        "possible_nonloop_dyads": len(nodes) * (len(nodes) - 1),
        "true_nonedge_pool": len(negative_pool(nodes, full_arc_set)),
        "masking": {
            "regime": "arc_first",
            "mechanism": args.mechanism,
            "requested_rate": args.mask_rate,
            "replicates": args.replicates,
            "seed": args.seed,
        },
        "scores": [
            "oi",
            "oo",
            "ii",
            "common_neighbor_total",
            "adamic_adar_oi",
            "adamic_adar_oo",
            "adamic_adar_ii",
            "adamic_adar_total",
        ],
        "negative_panel": "random_true_nonedges",
        "concept_fidelity": concept_summary,
        "r_inputs": {
            "edges": "r_inputs/static_edges.csv",
            "nodes": "r_inputs/nodes.csv",
            "driver": "r/models/static_directed_ergm_ladder.R",
        },
        "limitations": [
            "This bounded pilot evaluates static arc LP only. It is not a hyperlink-event "
            "evaluation.",
            "The final plan additionally requires event-first masks, target-specific hard panels, "
            "ERGM score lifts, conditional simulation, and pilot-gate review.",
            "AUC values evaluate uncalibrated heuristic scores; log loss is reserved for "
            "calibrated probabilities such as ERGM conditional scores.",
        ],
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Static Phase 2 pilot complete.")
    print(f"Dataset: {args.dataset}")
    print(f"Nodes: {len(nodes):,}; static arcs: {len(arcs):,}")
    print(f"Replicates: {args.replicates}; mechanism: {args.mechanism}")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
