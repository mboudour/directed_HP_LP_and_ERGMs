#!/usr/bin/env python3
"""Export frozen native-event panels for split-specific ERGM footprint scoring.

Each output split retains only the observed event projection as the ERGM training
network. Candidate tail/head types are read from already frozen random and hard
panels and expanded to their directed footprints. No event record, completed
network, or source edge list is read after masking.

The companion R driver fits ERGMs to these train edges and returns conditional
dyad probabilities. It aggregates them only into graph-footprint scores: L1
(arithmetic mean), L1g (geometric mean), and L2 (factorized product). Those are
not probabilities that the email event itself occurred.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import product
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PANEL_NAMES = ("random", "reversal_orientation", "role_exchange")


@dataclass(frozen=True, slots=True)
class EventCandidate:
    """One panel-labelled native event type before footprint expansion."""

    panel: str
    candidate_id: str
    tail: tuple[str, ...]
    head: tuple[str, ...]
    label: int

    @property
    def footprint(self) -> tuple[tuple[str, str], ...]:
        """Return the deterministic ordered directed footprint of the event candidate."""
        return tuple(sorted(product(self.tail, self.head)))


def parse_args() -> argparse.Namespace:
    """Parse explicit source and output contracts for ERGM footprint scoring inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--heuristic-dir", type=Path, required=True)
    parser.add_argument("--hard-panel-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument(
        "--political-covariates",
        type=Path,
        help=(
            "Optional Senate node covariate CSV with node, party, state, ideology, majority "
            "caucus, and seniority fields. It is normalized for political ERGM inputs."
        ),
    )
    parser.add_argument(
        "--panels",
        default=",".join(DEFAULT_PANEL_NAMES),
        help=(
            "Comma-separated frozen panels to export. Must include random; default: "
            f"{','.join(DEFAULT_PANEL_NAMES)}."
        ),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    panels = tuple(panel.strip() for panel in args.panels.split(",") if panel.strip())
    if not panels or panels[0] != "random" or len(set(panels)) != len(panels):
        parser.error("--panels must start with random and contain unique nonempty panel names.")
    if any(not panel.replace("_", "").isalnum() for panel in panels):
        parser.error("--panels may contain only letters, digits, and underscores.")
    args.panels = panels
    return args


def resolve_path(path: Path) -> Path:
    """Resolve a project-relative path against the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Return a repository-relative provenance path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path, description: str) -> None:
    """Fail before writing outputs if a declared frozen artifact is missing."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, node_column: str) -> tuple[str, ...]:
    """Read the fixed actor universe, preserving labels as opaque strings."""
    require_file(path, "node table")
    values: dict[str, None] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or node_column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks declared column {node_column!r}: {path}")
        for row in reader:
            value = row[node_column].strip()
            if not value:
                raise SystemExit("STOP: node table contains an empty node ID.")
            if value in values:
                raise SystemExit(f"STOP: node table contains duplicate node ID {value!r}.")
            values[value] = None
    if len(values) < 2:
        raise SystemExit("STOP: at least two nodes are required for ERGM footprint scoring.")
    return tuple(values)


def read_political_covariates(path: Path, nodes: tuple[str, ...]) -> list[dict[str, object]]:
    """Read an audited complete Senate covariate table and normalize output field names."""
    require_file(path, "political covariate table")
    required = {
        "node",
        "party_118_entry",
        "majority_caucus_entry",
        "state",
        "dw_nominate_dim1",
        "senate_service_years_at_118_entry",
    }
    values: dict[str, dict[str, object]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(
                f"STOP: political covariate table lacks required fields {sorted(required)}: {path}"
            )
        for row in reader:
            node = row["node"].strip()
            party = row["party_118_entry"].strip()
            state = row["state"].strip()
            try:
                ideology = float(row["dw_nominate_dim1"])
                majority_caucus = int(row["majority_caucus_entry"])
                seniority_years = float(row["senate_service_years_at_118_entry"])
            except ValueError as error:
                raise SystemExit(
                    f"STOP: invalid political covariate value for {node!r}."
                ) from error
            if majority_caucus not in {0, 1} or seniority_years < 0:
                raise SystemExit(f"STOP: invalid political covariate range for {node!r}.")
            if not node or not party or not state or node in values:
                raise SystemExit(
                    "STOP: political covariate table has empty or duplicate node values."
                )
            values[node] = {
                "id": node,
                "party": party,
                "state": state,
                "ideology": ideology,
                "majority_caucus": majority_caucus,
                "seniority_years": seniority_years,
            }
    if set(values) != set(nodes):
        missing = sorted(set(nodes) - set(values))
        extra = sorted(set(values) - set(nodes))
        raise SystemExit(
            "STOP: political covariate node set differs from ERGM node set; "
            f"missing={missing[:10]}, extra={extra[:10]}."
        )
    return [values[node] for node in nodes]


def read_observed_arcs(path: Path, node_set: set[str]) -> tuple[tuple[str, str], ...]:
    """Read the observed split-specific simple directed projection."""
    require_file(path, "event-first observed arc table")
    arcs: set[tuple[str, str]] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or {"tail", "head"} - set(reader.fieldnames):
            raise SystemExit(f"STOP: observed arc table requires tail/head columns: {path}")
        for row in reader:
            tail, head = row["tail"].strip(), row["head"].strip()
            if not tail or not head or tail == head:
                raise SystemExit("STOP: observed arc table has an invalid endpoint.")
            if tail not in node_set or head not in node_set:
                raise SystemExit(
                    "STOP: observed arc table references an actor outside the node table."
                )
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit(f"STOP: observed arc table is empty: {path}")
    return tuple(sorted(arcs))


def parse_role_json(value: str, name: str) -> tuple[str, ...]:
    """Decode a stored tail/head list and enforce a canonical event identity."""
    try:
        raw = json.loads(value)
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: invalid {name} JSON in panel: {value!r}") from error
    if not isinstance(raw, list) or not raw:
        raise SystemExit(f"STOP: {name} must be a nonempty JSON list.")
    roles = tuple(sorted(str(member).strip() for member in raw))
    if any(not member for member in roles) or len(set(roles)) != len(roles):
        raise SystemExit(f"STOP: {name} contains an empty or duplicate actor ID.")
    return roles


def panel_path(panel: str, split_name: str, heuristic_dir: Path, hard_panel_dir: Path) -> Path:
    """Locate the native-event panel source produced by its own benchmark driver."""
    if panel == "random":
        return heuristic_dir / split_name / "candidate_predictions.csv"
    return hard_panel_dir / split_name / f"{panel}_candidate_predictions.csv"


def read_panel(path: Path, panel: str, node_set: set[str]) -> tuple[EventCandidate, ...]:
    """Read a frozen event panel without trusting its generated score columns."""
    require_file(path, f"{panel} candidate panel")
    required = {"candidate_id", "tail_nodes_json", "head_nodes_json", "label"}
    candidates: list[EventCandidate] = []
    keys: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(f"STOP: {panel} candidate panel lacks required columns: {path}")
        for row in reader:
            candidate_id = row["candidate_id"].strip()
            tail = parse_role_json(row["tail_nodes_json"], "tail_nodes_json")
            head = parse_role_json(row["head_nodes_json"], "head_nodes_json")
            label = row["label"].strip()
            if label not in {"0", "1"}:
                raise SystemExit(f"STOP: {panel} panel label must be 0 or 1.")
            if not candidate_id or set(tail).intersection(head):
                raise SystemExit(f"STOP: {panel} panel has invalid candidate roles or ID.")
            if any(node not in node_set for node in tail + head):
                raise SystemExit(f"STOP: {panel} panel references an actor outside node table.")
            candidate = EventCandidate(panel, candidate_id, tail, head, int(label))
            key = candidate.tail, candidate.head
            if key in keys:
                raise SystemExit(f"STOP: {panel} panel repeats a native event candidate.")
            keys.add(key)
            candidates.append(candidate)
    labels = {candidate.label for candidate in candidates}
    if labels != {0, 1}:
        raise SystemExit(
            f"STOP: {panel} panel must contain at least one positive and one negative."
        )
    return tuple(candidates)


def discover_splits(mask_dir: Path) -> tuple[Path, ...]:
    """Discover complete event-first split directories deterministically."""
    required = {"observed_arcs.csv", "observed_event_types.csv", "heldout_event_types.csv"}
    splits = tuple(
        directory
        for directory in sorted(mask_dir.iterdir())
        if directory.is_dir() and required <= {path.name for path in directory.iterdir()}
    )
    if not splits:
        raise SystemExit(f"STOP: no complete event-first split directories in {mask_dir}")
    return splits


def split_identity(name: str) -> tuple[str, int]:
    """Parse the missingness mechanism and replicate from a frozen split name."""
    parts = name.rsplit("_replicate_", maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        raise SystemExit(f"STOP: invalid event-first split directory name: {name}")
    return parts[0], int(parts[1])


def write_csv(path: Path, rows: Iterable[dict[str, object]]) -> int:
    """Write a nonempty stable CSV and return its number of data rows."""
    rows = list(rows)
    if not rows:
        raise RuntimeError(f"cannot write required empty CSV: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Ensure a rerun intentionally replaces the complete ERGM-input bundle."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: native-event ERGM input directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Export all frozen panel footprints to a strict, R-readable contract."""
    args = parse_args()
    mask_dir = resolve_path(args.mask_dir)
    heuristic_dir = resolve_path(args.heuristic_dir)
    hard_panel_dir = resolve_path(args.hard_panel_dir)
    nodes_path = resolve_path(args.nodes)
    political_covariates_path = (
        resolve_path(args.political_covariates) if args.political_covariates else None
    )
    output_dir = resolve_path(args.output_dir)
    for directory, name in (
        (mask_dir, "event-first mask directory"),
        (heuristic_dir, "random native-event panel directory"),
        (hard_panel_dir, "hard native-event panel directory"),
    ):
        if not directory.is_dir():
            raise SystemExit(f"STOP: {name} is missing: {directory}")
    prepare_output_dir(output_dir, args.overwrite)
    nodes = read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    node_rows: list[dict[str, object]] = (
        read_political_covariates(political_covariates_path, nodes)
        if political_covariates_path
        else [{"id": node} for node in nodes]
    )
    write_csv(output_dir / "nodes.csv", node_rows)

    split_summary: list[dict[str, object]] = []
    for split_dir in discover_splits(mask_dir):
        mechanism, replicate = split_identity(split_dir.name)
        split_output = output_dir / "splits" / split_dir.name
        split_output.mkdir(parents=True)
        arcs = read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        write_csv(
            split_output / "train_edges.csv",
            ({"from": tail, "to": head} for tail, head in arcs),
        )
        panel_rows: list[dict[str, object]] = []
        unique_dyads: set[tuple[str, str]] = set()
        panel_counts: dict[str, int] = {}
        for panel in args.panels:
            candidates = read_panel(
                panel_path(panel, split_dir.name, heuristic_dir, hard_panel_dir), panel, node_set
            )
            panel_counts[panel] = len(candidates)
            for candidate in candidates:
                namespace_id = f"{panel}::{candidate.candidate_id}"
                for tail, head in candidate.footprint:
                    unique_dyads.add((tail, head))
                    panel_rows.append(
                        {
                            "panel": panel,
                            "candidate_id": namespace_id,
                            "label": candidate.label,
                            "tail_nodes_json": json.dumps(candidate.tail),
                            "head_nodes_json": json.dumps(candidate.head),
                            "tail_arity": len(candidate.tail),
                            "head_arity": len(candidate.head),
                            "footprint_size": len(candidate.footprint),
                            "candidate_tail": tail,
                            "candidate_head": head,
                        }
                    )
        write_csv(split_output / "candidate_footprints.csv", panel_rows)
        write_csv(
            split_output / "candidate_dyads.csv",
            (
                {"candidate_tail": tail, "candidate_head": head, "label": 0}
                for tail, head in sorted(unique_dyads)
            ),
        )
        split_summary.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "split": split_dir.name,
                "training_arcs": len(arcs),
                **{f"{panel}_candidates": panel_counts[panel] for panel in args.panels},
                "candidate_footprint_dyad_rows": len(panel_rows),
                "unique_candidate_dyads": len(unique_dyads),
            }
        )

    write_csv(output_dir / "split_summary.csv", split_summary)
    manifest = {
        "driver": "scripts/39_export_native_event_ergm_inputs.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "target": "native_event_type",
        "sources": {
            "event_first_masks": recorded_path(mask_dir),
            "random_panel": recorded_path(heuristic_dir),
            "hard_panels": recorded_path(hard_panel_dir),
            "node_table": recorded_path(nodes_path),
            "political_covariates": (
                recorded_path(political_covariates_path) if political_covariates_path else None
            ),
        },
        "contract": {
            "nodes": (
                "nodes.csv[id,party,state,ideology,majority_caucus,seniority_years]"
                if political_covariates_path
                else "nodes.csv[id]"
            ),
            "per_split_train_network": "splits/<split>/train_edges.csv[from,to]",
            "per_split_footprints": "splits/<split>/candidate_footprints.csv",
            "per_split_unique_dyads": "splits/<split>/candidate_dyads.csv["
            "candidate_tail,candidate_head,label]",
        },
        "panels": list(args.panels),
        "limitations": [
            "The export reads only frozen split artifacts; it never recreates a complete graph.",
            "Candidate footprints are graph footprints, not observed-event probability targets.",
            "The R stage must fit each split's observed projection independently and must not "
            "use full-network ERGM coefficients.",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Native-event ERGM input export passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Frozen splits exported: {len(split_summary):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
