#!/usr/bin/env python3
"""Score grammar-preserving Senate sponsor-substitution hard negatives.

For a singleton-sponsor Senate bill, the hard negative exchanges the sponsor with
one original co-sponsor. It retains exactly one sponsor and the same participant
set. Reversal is deliberately absent: for a 1-to-h bill with h greater than one,
a reversal would create h sponsors and violate the recorded legislative grammar.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HARD_PANEL_DRIVER = PROJECT_ROOT / "scripts" / "38_run_native_event_hard_panels.py"
PANEL = "sponsor_substitution"


def load_hard_panel_module() -> Any:
    """Import tested generic hard-panel primitives without changing their public CLI."""
    spec = importlib.util.spec_from_file_location("generic_hard_panels", HARD_PANEL_DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import generic hard-panel driver: {HARD_PANEL_DRIVER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    """Parse the single-tail Senate panel contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", default="node")
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.max_weak_distance < 1:
        parser.error("--max-weak-distance must be at least 1.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render project-relative provenance paths when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty result table with deterministic Unix line endings."""
    if not rows:
        raise RuntimeError(f"cannot write empty result table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output(path: Path, overwrite: bool) -> None:
    """Refuse accidental blending of panel outputs from different mask requests."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: Senate hard-panel output is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def aggregate_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate scoring metrics by mechanism and score over whole frozen masks."""
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["mechanism"]), str(row["score"]), str(row["metric"]))].append(
            float(row["value"])
        )
    return [
        {
            "panel": PANEL,
            "mechanism": mechanism,
            "score": score,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, score, metric), values in sorted(grouped.items())
    ]


def main() -> None:
    """Evaluate one paired sponsor-substitution negative per valid held-out event type."""
    args = parse_args()
    hard = load_hard_panel_module()
    mask_dir, node_path, output_dir = (
        resolve(args.mask_dir),
        resolve(args.nodes),
        resolve(args.output_dir),
    )
    if not mask_dir.is_dir():
        raise SystemExit(f"STOP: event-first mask directory is missing: {mask_dir}")
    prepare_output(output_dir, args.overwrite)
    nodes = hard.read_nodes(node_path, args.node_column)
    node_set = set(nodes)
    all_metrics: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []

    for split_dir in hard.split_directories(mask_dir):
        mechanism, replicate = hard.split_identity(split_dir)
        observed = hard.read_type_table(split_dir / "observed_event_types.csv", label=0)
        heldout = hard.read_type_table(split_dir / "heldout_event_types.csv", label=1)
        all_types = observed + heldout
        if any(len(candidate.tail) != 1 for candidate in all_types):
            raise SystemExit(
                "STOP: Senate sponsor-substitution requires exactly one sponsor in every "
                "event type."
            )
        if {candidate.key for candidate in observed}.intersection(
            candidate.key for candidate in heldout
        ):
            raise SystemExit("STOP: frozen split leaks held-out types into observed event types.")
        if any(
            node not in node_set
            for candidate in all_types
            for node in candidate.tail + candidate.head
        ):
            raise SystemExit(
                "STOP: event type references an actor outside the declared node universe."
            )
        arcs = hard.read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        reachable = hard.weak_reachability(nodes, arcs, args.max_weak_distance)
        positives = tuple(candidate for candidate in heldout if hard.is_local(candidate, reachable))
        if not positives:
            raise SystemExit(f"STOP: no candidate-eligible held-out types in {split_dir.name}")
        seed = args.seed + 20_011 * replicate + (0 if mechanism == "mcar" else 10_009)
        pairs = hard.role_exchange_pairs(
            positives,
            {candidate.key for candidate in all_types},
            reachable,
            seed,
        )
        if any(len(negative.tail) != 1 for _, negative in pairs):
            raise RuntimeError("sponsor-substitution emitted an invalid multi-sponsor negative")
        split_output = output_dir / split_dir.name
        split_output.mkdir()
        if pairs:
            candidates = tuple(candidate for pair in pairs for candidate in pair)
            predictions = hard.prediction_rows(candidates, arcs, PANEL)
            metrics = hard.metric_rows(predictions, PANEL, mechanism, replicate)
            write_csv(split_output / f"{PANEL}_candidate_predictions.csv", predictions)
            write_csv(split_output / f"{PANEL}_metrics.csv", metrics)
            all_metrics.extend(metrics)
        split_manifest = {
            "source_mask_split": recorded(split_dir),
            "mechanism": mechanism,
            "replicate": replicate,
            "panel": PANEL,
            "candidate_eligible_positive_types": len(positives),
            "pairs": len(pairs),
            "negative_rule": (
                "exchange the singleton sponsor with one original co-sponsor; retain singleton "
                "tail, participant set, head arity, split-specific weak-distance locality, and "
                "exclusion from all known native-event types"
            ),
            "reversal_orientation": (
                "not evaluated; it violates the singleton-sponsor grammar for 1-to-h bills"
            ),
            "metric_contract": "ranking only; heuristic scores are uncalibrated",
        }
        (split_output / "manifest.json").write_text(
            json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        coverage_rows.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "heldout_positive_types": len(heldout),
                "candidate_eligible_positive_types": len(positives),
                "positive_eligibility_rate": len(positives) / len(heldout),
                "sponsor_substitution_pairs": len(pairs),
            }
        )
    if not all_metrics:
        raise SystemExit("STOP: no valid Senate sponsor-substitution pairs were available.")
    summary_metrics = aggregate_metrics(all_metrics)
    write_csv(output_dir / "split_summary.csv", coverage_rows)
    write_csv(output_dir / "metric_summary.csv", summary_metrics)
    manifest = {
        "driver": "scripts/67_run_senate_sponsor_substitution.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "target": "native_event_type",
        "source_masks": recorded(mask_dir),
        "hard_panel": PANEL,
        "tail_grammar": "exactly one sponsor",
        "reversal_orientation": "not evaluated because it would violate the Senate event grammar",
        "candidate_universe": "weak distance two in each split's observed projection",
        "negative_exclusion": "all observed and held-out native event types",
        "splits_completed": len(coverage_rows),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Senate sponsor-substitution hard-negative benchmark",
        "",
        f"- Dataset: `{args.dataset_id}`",
        "- Each pair retains one sponsor and the same bill participants by exchanging the sponsor "
        "with one original co-sponsor.",
        "- Reversal/orientation is absent because it would turn a 1-to-h bill into h-to-1 roles.",
        "",
        "## Coverage",
        "",
        "| Mechanism | Replicate | Eligible held-out types | Sponsor-substitution pairs |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        "| {mechanism} | {replicate} | {candidate_eligible_positive_types} | "
        "{sponsor_substitution_pairs} |".format(**row)
        for row in coverage_rows
    )
    lines.extend(
        [
            "",
            "## Ranking metrics across completed replicates",
            "",
            "| Mechanism | Score | Metric | Replicates | Mean | SD |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    lines.extend(
        "| {mechanism} | {score} | {metric} | {completed_replicates} | {mean:.4f} | "
        "{sd:.4f} |".format(**row)
        for row in summary_metrics
    )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Senate sponsor-substitution hard-negative benchmark passed.")
    print(f"Dataset: {args.dataset_id}; frozen splits: {len(coverage_rows):,}.")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
