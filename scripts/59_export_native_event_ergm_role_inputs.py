#!/usr/bin/env python3
"""Export fixed-participant role-assignment candidates for split-specific ERGM scoring.

The export reconstructs only the predeclared role partitions of each held-out
native event type.  It writes no candidate-level material to the published
bundle; its companion summarizer releases aggregate role metrics only.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
from itertools import product
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROLE_DRIVER = PROJECT_ROOT / "scripts" / "49_evaluate_native_event_role_assignment.py"


def load_role_driver() -> Any:
    """Load the existing role-partition policy without duplicating its definition."""
    spec = importlib.util.spec_from_file_location("native_event_role_assignment", ROLE_DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load native-event role-assignment utilities")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ROLE = load_role_driver()
SHARED = ROLE.shared


def parse_args() -> argparse.Namespace:
    """Parse a strict frozen-mask role-assignment ERGM export contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument(
        "--node-covariates",
        type=Path,
        help=(
            "Optional node table with party, state, and ideology attributes for political "
            "ERGM models."
        ),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def candidate_rows(target: Any) -> list[dict[str, object]]:
    """Expand all fixed-arity role partitions of one held-out event type."""
    rows: list[dict[str, object]] = []
    for index, (tail, head) in enumerate(ROLE.candidate_partitions(target), start=1):
        candidate_id = f"role_assignment::{target.candidate_id}_partition_{index:03d}"
        label = int((tail, head) == target.key)
        for candidate_tail, candidate_head in sorted(product(tail, head)):
            rows.append(
                {
                    "panel": "role_assignment",
                    "candidate_id": candidate_id,
                    "label": label,
                    "tail_nodes_json": json.dumps(tail),
                    "head_nodes_json": json.dumps(head),
                    "tail_arity": len(tail),
                    "head_arity": len(head),
                    "footprint_size": len(tail) * len(head),
                    "candidate_tail": candidate_tail,
                    "candidate_head": candidate_head,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty deterministic CSV with POSIX line endings."""
    if not rows:
        raise RuntimeError(f"cannot write an empty required table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create or intentionally replace the complete export directory."""
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise RuntimeError(f"output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def node_rows(
    nodes: list[str], node_column: str, covariates_path: Path | None
) -> list[dict[str, str]]:
    """Return nodes in fixed order, optionally with complete political attributes."""
    if covariates_path is None:
        return [{"id": node} for node in nodes]
    with covariates_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {node_column, "party_118_entry", "state", "dw_nominate_dim1"}
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise RuntimeError(
                "node covariate table lacks node, party_118_entry, state, "
                "or dw_nominate_dim1 fields"
            )
        records = list(reader)
    mapping = {str(row[node_column]): row for row in records}
    if len(mapping) != len(records) or set(mapping) != set(nodes):
        raise RuntimeError(
            "node covariate table must have exactly one row for every fixed-universe node"
        )
    return [
        {
            "id": node,
            "party": str(mapping[node]["party_118_entry"]),
            "state": str(mapping[node]["state"]),
            "ideology": str(mapping[node]["dw_nominate_dim1"]),
        }
        for node in nodes
    ]


def main() -> None:
    """Export role-assignment footprints for every complete frozen split."""
    args = parse_args()
    mask_dir = SHARED.resolve_path(args.mask_dir)
    nodes_path = SHARED.resolve_path(args.nodes)
    covariates_path = (
        SHARED.resolve_path(args.node_covariates) if args.node_covariates is not None else None
    )
    output_dir = SHARED.resolve_path(args.output_dir)
    prepare_output_dir(output_dir, args.overwrite)

    nodes = SHARED.read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    write_csv(output_dir / "nodes.csv", node_rows(nodes, args.node_column, covariates_path))

    split_summary: list[dict[str, object]] = []
    for split_dir in SHARED.split_directories(mask_dir):
        mechanism, replicate = SHARED.split_identity(split_dir)
        heldout = SHARED.read_type_table(split_dir / "heldout_event_types.csv", label=1)
        arcs = SHARED.read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        rows = [row for target in heldout for row in candidate_rows(target)]
        unique_dyads = sorted(
            {(str(row["candidate_tail"]), str(row["candidate_head"])) for row in rows}
        )
        split_output = output_dir / "splits" / split_dir.name
        split_output.mkdir(parents=True)
        write_csv(
            split_output / "train_edges.csv",
            [{"from": tail, "to": head} for tail, head in sorted(arcs)],
        )
        write_csv(split_output / "candidate_footprints.csv", rows)
        write_csv(
            split_output / "candidate_dyads.csv",
            [
                {"candidate_tail": tail, "candidate_head": head, "label": 0}
                for tail, head in unique_dyads
            ],
        )
        split_summary.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "split": split_dir.name,
                "heldout_event_types": len(heldout),
                "role_partition_candidates": len({str(row["candidate_id"]) for row in rows}),
                "candidate_footprint_dyads": len(rows),
                "unique_candidate_dyads": len(unique_dyads),
            }
        )

    write_csv(output_dir / "split_summary.csv", split_summary)
    manifest = {
        "driver": "scripts/59_export_native_event_ergm_role_inputs.py",
        "dataset_id": args.dataset_id,
        "target": "fixed_participant_fixed_arity_role_assignment",
        "source_masks": SHARED.recorded_path(mask_dir),
        "candidate_rule": (
            "all fixed-arity tail/head partitions of every held-out event's known participant set"
        ),
        "contract": {
            "nodes": "nodes.csv[id]",
            "training_network": "splits/<split>/train_edges.csv[from,to]",
            "candidate_footprints": "splits/<split>/candidate_footprints.csv",
            "candidate_dyads": (
                "splits/<split>/candidate_dyads.csv[candidate_tail,candidate_head,label]"
            ),
        },
        "node_covariates": (
            SHARED.recorded_path(covariates_path) if covariates_path is not None else None
        ),
        "privacy": (
            "Candidate-level role files are computation intermediates, not published aggregates."
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Native-event ERGM role-assignment input export passed.")
    print(f"Dataset: {args.dataset_id}; splits: {len(split_summary)}.")
    print(f"Output bundle: {SHARED.recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
