#!/usr/bin/env python3
"""Run Regime C footprint-free formal-concept recovery stress tests."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from random import Random
from statistics import mean, stdev
from typing import Any

from directed_hp.hypergraphs.formal_concepts import enumerate_formal_concepts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT46 = PROJECT_ROOT / "scripts" / "46_run_arcfirst_concept_recovery.py"
spec = importlib.util.spec_from_file_location("concept_recovery", SCRIPT46)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load shared concept-recovery utilities")
shared = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = shared
spec.loader.exec_module(shared)


def args() -> argparse.Namespace:
    """Parse a fixed candidate-isolation stress-test contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=sorted(shared.DATASET_DEFAULTS), required=True)
    parser.add_argument("--tail-cap", type=int, default=3)
    parser.add_argument("--head-cap", type=int, default=3)
    parser.add_argument("--max-concept-candidates", type=int, default=250_000)
    parser.add_argument("--target-fraction", type=float, default=0.30)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20_261_013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    value = parser.parse_args()
    if value.tail_cap < 1 or value.head_cap < 1 or value.max_concept_candidates < 1:
        parser.error("arity caps and maximum candidates must be positive")
    if not 0 < value.target_fraction <= 1 or value.replicates < 1 or value.max_weak_distance < 1:
        parser.error("target fraction, replicates, and weak distance must be positive")
    return value


def concept_key(concept: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Normalize one concept as the shared scorer's candidate identity."""
    return tuple(map(str, concept.tail)), tuple(map(str, concept.head))


def footprint(key: tuple[tuple[str, ...], tuple[str, ...]]) -> frozenset[tuple[str, str]]:
    """Return a directed candidate footprint."""
    return frozenset((tail, head) for tail in key[0] for head in key[1])


def select_disjoint(
    full_keys: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...], target_count: int, seed: int
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    """Select a seeded greedy family with pairwise arc-disjoint non-singleton footprints."""
    random = Random(seed)
    candidates = [key for key in full_keys if len(footprint(key)) > 1]
    random.shuffle(candidates)
    selected: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    removed: set[tuple[str, str]] = set()
    for key in candidates:
        if not footprint(key).intersection(removed):
            selected.append(key)
            removed.update(footprint(key))
            if len(selected) >= target_count:
                break
    return tuple(selected)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty aggregate-only CSV."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Select disjoint concepts, delete every target footprint, and score recovery."""
    value = args()
    defaults = shared.DATASET_DEFAULTS[value.dataset]
    arcs = shared.read_arcs(
        PROJECT_ROOT / defaults["arcs"],
        defaults["tail_column"],
        defaults["head_column"],
        set(shared.read_nodes(PROJECT_ROOT / defaults["nodes"], defaults["node_column"])),
    )
    nodes = shared.read_nodes(PROJECT_ROOT / defaults["nodes"], defaults["node_column"])
    output = value.output_dir if value.output_dir.is_absolute() else PROJECT_ROOT / value.output_dir
    shared.prepare_output_dir(output, value.overwrite)
    full = enumerate_formal_concepts(
        arcs,
        nodes=nodes,
        max_tail_arity=value.tail_cap,
        max_head_arity=value.head_cap,
        max_candidates=value.max_concept_candidates,
    )
    full_keys = tuple(sorted(concept_key(item) for item in full))
    eligible = tuple(key for key in full_keys if len(footprint(key)) > 1)
    requested = max(1, round(len(eligible) * value.target_fraction))
    metric_rows: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    for replicate in range(1, value.replicates + 1):
        selected = select_disjoint(full_keys, requested, value.seed + replicate - 1)
        removed = frozenset(arc for key in selected for arc in footprint(key))
        observed_arcs = tuple(sorted(set(arcs) - removed))
        observed = enumerate_formal_concepts(
            observed_arcs,
            nodes=nodes,
            max_tail_arity=value.tail_cap,
            max_head_arity=value.head_cap,
            max_candidates=value.max_concept_candidates,
        )
        observed_keys = {concept_key(item) for item in observed}
        reached = shared.weak_reachability(nodes, observed_arcs, value.max_weak_distance)
        positives = tuple(
            shared.candidate_from_key(key, 1, f"selected_concept_{index:05d}")
            for index, key in enumerate(selected, start=1)
            if key not in observed_keys
            and shared.is_local(shared.candidate_from_key(key, 1, None), reached)
        )
        if not positives:
            raise SystemExit(
                f"STOP: no selected footprint-free targets remain local in replicate {replicate}"
            )
        outdegree, indegree = shared.observed_degrees(nodes, observed_arcs)
        random_pos, random_neg = shared.random_negative_panel(
            positives, nodes, set(full_keys), reached, value.seed + 10_000 + replicate
        )
        degree_pos, degree_neg = shared.degree_matched_negative_panel(
            positives,
            nodes,
            set(full_keys),
            reached,
            outdegree,
            indegree,
            value.seed + 20_000 + replicate,
        )
        split_dir = output / f"replicate_{replicate:03d}"
        split_dir.mkdir()
        for panel, panel_pos, panel_neg in (
            ("random", random_pos, random_neg),
            ("degree_matched", degree_pos, degree_neg),
        ):
            if not panel_neg:
                continue
            predictions = shared.score_candidates(panel_pos + panel_neg, observed_arcs)
            for row in predictions:
                row.update({"replicate": replicate, "panel": panel})
            shared.write_csv(split_dir / f"{panel}_predictions.csv", predictions)
            metrics = shared.metric_rows(predictions, "footprint_free", replicate, panel)
            shared.write_csv(split_dir / f"{panel}_metrics.csv", metrics)
            metric_rows.extend(metrics)
        manifest = {
            "regime": "footprint_free",
            "dataset": value.dataset,
            "replicate": replicate,
            "selection": "seeded greedy pairwise arc-disjoint capped formal concepts",
            "full_capped_concepts": len(full_keys),
            "eligible_nonsingleton_concepts": len(eligible),
            "requested_targets": requested,
            "selected_targets": len(selected),
            "local_eligible_targets": len(positives),
            "removed_arcs": len(removed),
            "removed_arc_rate": len(removed) / len(arcs),
            "observed_arcs": len(observed_arcs),
            "training_concepts_sharing_removed_arcs": len(set(full_keys) - observed_keys),
        }
        (split_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        split_rows.append(
            {
                "replicate": replicate,
                **manifest,
                "random_panel_positives": len(random_pos),
                "degree_panel_positives": len(degree_pos),
            }
        )
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in metric_rows:
        grouped[(str(row["panel"]), str(row["score"]), str(row["metric"]))].append(
            float(row["value"])
        )
    summary_rows = [
        {
            "panel": panel,
            "score": score,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (panel, score, metric), values in sorted(grouped.items())
    ]
    write_csv(output / "split_summary.csv", split_rows)
    write_csv(output / "metric_summary.csv", summary_rows)
    (output / "summary.md").write_text(
        "# Footprint-free directed formal-concept stress test\n\n"
        f"- Dataset: `{value.dataset}`\n- Full capped concepts: `{len(full_keys)}`\n"
        f"- Requested selected target fraction: `{value.target_fraction:.3f}`\n"
        "- Selected target footprints are pairwise arc-disjoint; every target arc is removed from the observed graph.\n"
        "- Any original concept sharing a removed target arc is absent from the training concept section.\n"
        "- Scores are uncalibrated lifted directed-LP rankings; this is a strict Regime C stress test.\n\n"
        "| Replicate | Selected | Local targets | Removed arcs | Removed arc rate | Random panel positives | Degree panel positives |\n"
        "|---:|---:|---:|---:|---:|---:|---:|\n"
        + "".join(
            "| {replicate} | {selected_targets} | {local_eligible_targets} | {removed_arcs} | {removed_arc_rate:.4f} | {random_panel_positives} | {degree_panel_positives} |\n".format(
                **row
            )
            for row in split_rows
        )
        + "\nMetric summaries are in `metric_summary.csv`; unavailable panel cells are not replaced with easier negatives.\n",
        encoding="utf-8",
    )
    print("Footprint-free stress test passed.")
    print(f"Dataset: {value.dataset}; completed splits: {len(split_rows)}.")
    print(f"Output bundle: {shared.display_path(output)}")


if __name__ == "__main__":
    main()
