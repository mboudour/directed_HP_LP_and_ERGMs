#!/usr/bin/env python3
"""Summarize footprint-survival and reversal-reciprocity diagnostics safely.

The script consumes frozen split-level candidates and conditional ERGM scores,
then emits only actor-free aggregate results. It does not alter any primary
panel, mask, or fitting specification.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from directed_hp.evaluation.metrics import pr_auc, roc_auc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
M4_MODEL = "M4c"
M4_SCORE = "L1g"


def parse_args() -> argparse.Namespace:
    """Parse one primary-core diagnostic contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--heuristic-dir", type=Path, required=True)
    parser.add_argument("--hard-panel-dir", type=Path, required=True)
    parser.add_argument("--ergm-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve one project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def split_identity(name: str) -> tuple[str, int]:
    """Parse the mechanism and replicate encoded in a split directory name."""
    left, right = name.rsplit("_replicate_", maxsplit=1)
    if not right.isdigit():
        raise ValueError(f"invalid split directory name: {name}")
    return left, int(right)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create or deliberately replace an aggregate output directory."""
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise RuntimeError(f"output directory is nonempty: {path}")
        for child in path.iterdir():
            child.unlink()
    path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a nonempty CSV with named fields."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"empty CSV: {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a deterministic nonempty aggregate CSV."""
    if not rows:
        raise RuntimeError(f"cannot write empty aggregate output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def m4_scores(ergm_dir: Path) -> dict[tuple[str, int, str, str], float]:
    """Index M4c geometric footprint scores by split, panel, and candidate."""
    path = ergm_dir / "event_footprint_scores.csv"
    scores: dict[tuple[str, int, str, str], float] = {}
    for row in read_csv(path):
        if row["model"] != M4_MODEL:
            continue
        key = (row["mechanism"], int(row["replicate"]), row["panel"], row["candidate_id"])
        if key in scores:
            raise RuntimeError(f"duplicate M4c event score: {key}")
        scores[key] = float(row[M4_SCORE])
    if not scores:
        raise RuntimeError(f"M4c scores not found in {path}")
    return scores


def metric_values(labels: list[int], scores: list[float]) -> dict[str, float]:
    """Compute ranking metrics when both label classes are present."""
    if not labels or not {0, 1}.issubset(set(labels)):
        return {}
    return {"pr_auc": pr_auc(labels, scores), "roc_auc": roc_auc(labels, scores)}


def summary_rows(
    split_metrics: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Summarize valid split metrics without treating candidates as replicates."""
    groups: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in split_metrics:
        key = (
            str(row["mechanism"]),
            str(row["survival_stratum"]),
            str(row["score"]),
            str(row["metric"]),
        )
        groups[key].append(float(row["value"]))
    return [
        {
            "mechanism": mechanism,
            "survival_stratum": stratum,
            "score": score,
            "metric": metric,
            "completed_masks": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, stratum, score, metric), values in sorted(groups.items())
    ]


def contrast_rows(split_metrics: list[dict[str, object]]) -> list[dict[str, object]]:
    """Calculate matched PR-AUC contrasts within survival strata and masks."""
    lookup = {
        (
            str(row["mechanism"]),
            int(row["replicate"]),
            str(row["survival_stratum"]),
            str(row["score"]),
        ): float(row["value"])
        for row in split_metrics
        if row["metric"] == "pr_auc"
    }
    rows: list[dict[str, object]] = []
    for reference in ("directed_aa_total", "degree_product_mean"):
        groups: dict[tuple[str, str], list[float]] = defaultdict(list)
        for mechanism, replicate, stratum, score in lookup:
            if score != "M4c::L1g":
                continue
            ref_key = (mechanism, replicate, stratum, reference)
            if ref_key in lookup:
                groups[(mechanism, stratum)].append(
                    lookup[(mechanism, replicate, stratum, score)] - lookup[ref_key]
                )
        for (mechanism, stratum), values in sorted(groups.items()):
            rows.append(
                {
                    "mechanism": mechanism,
                    "survival_stratum": stratum,
                    "contrast": f"M4c::L1g minus {reference}",
                    "completed_masks": len(values),
                    "mean_pr_auc_difference": mean(values),
                    "sd": stdev(values) if len(values) > 1 else 0.0,
                }
            )
    return rows


def survival_diagnostics(
    heuristic_dir: Path,
    scores: dict[tuple[str, int, str, str], float],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Compute random-panel ranking summaries by complete-footprint survival."""
    split_metrics: list[dict[str, object]] = []
    coverage: list[dict[str, object]] = []
    for split_dir in sorted(path for path in heuristic_dir.iterdir() if path.is_dir()):
        mechanism, replicate = split_identity(split_dir.name)
        rows = read_csv(split_dir / "candidate_predictions.csv")
        by_stratum: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            stratum = (
                "B=1 complete footprint survives"
                if int(row["already_observed_footprint"])
                else "B=0 at least one arc absent"
            )
            by_stratum[stratum].append(row)
        for stratum, stratum_rows in sorted(by_stratum.items()):
            labels = [int(row["label"]) for row in stratum_rows]
            coverage.append(
                {
                    "mechanism": mechanism,
                    "replicate": replicate,
                    "survival_stratum": stratum,
                    "candidates": len(stratum_rows),
                    "positives": sum(labels),
                    "negatives": len(labels) - sum(labels),
                }
            )
            score_values = {
                "directed_aa_total": [
                    float(row["lifted_adamic_adar_total_mean"]) for row in stratum_rows
                ],
                "degree_product_mean": [
                    float(row["lifted_degree_product_mean"]) for row in stratum_rows
                ],
                "already_observed_footprint": [
                    float(row["already_observed_footprint"]) for row in stratum_rows
                ],
                "M4c::L1g": [
                    scores[(mechanism, replicate, "random", f"random::{row['candidate_id']}")]
                    for row in stratum_rows
                ],
            }
            for score_name, values in score_values.items():
                for metric, value in metric_values(labels, values).items():
                    split_metrics.append(
                        {
                            "mechanism": mechanism,
                            "replicate": replicate,
                            "survival_stratum": stratum,
                            "score": score_name,
                            "metric": metric,
                            "value": value,
                        }
                    )
    return split_metrics, summary_rows(split_metrics), coverage


def sign_preference(positive: float, reversal: float) -> float:
    """Return one, one-half, or zero for the positive orientation preference."""
    if positive > reversal:
        return 1.0
    if positive < reversal:
        return 0.0
    return 0.5


def reversal_diagnostics(
    hard_dir: Path,
    scores: dict[tuple[str, int, str, str], float],
) -> list[dict[str, object]]:
    """Describe reversal preference by footprint-survival pattern and reciprocal support."""
    grouped: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    for split_dir in sorted(path for path in hard_dir.iterdir() if path.is_dir()):
        mechanism, replicate = split_identity(split_dir.name)
        rows = read_csv(split_dir / "reversal_orientation_candidate_predictions.csv")
        pairs: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            pairs[row["paired_source_event_type_id"]].append(row)
        for source_id, pair in pairs.items():
            if len(pair) != 2:
                raise RuntimeError(f"reversal pair is incomplete for {split_dir.name}:{source_id}")
            positive = next((row for row in pair if int(row["label"]) == 1), None)
            reversal = next((row for row in pair if int(row["label"]) == 0), None)
            if positive is None or reversal is None:
                raise RuntimeError(
                    f"reversal pair lacks binary labels for {split_dir.name}:{source_id}"
                )
            pos_survives = int(positive["already_observed_footprint"]) == 1
            rev_survives = int(reversal["already_observed_footprint"]) == 1
            if pos_survives and rev_survives:
                pattern = "both footprints survive"
            elif pos_survives:
                pattern = "positive footprint only survives"
            elif rev_survives:
                pattern = "reversal footprint only survives"
            else:
                pattern = "neither footprint survives"
            pos_m4 = scores[
                (
                    mechanism,
                    replicate,
                    "reversal_orientation",
                    f"reversal_orientation::{positive['candidate_id']}",
                )
            ]
            rev_m4 = scores[
                (
                    mechanism,
                    replicate,
                    "reversal_orientation",
                    f"reversal_orientation::{reversal['candidate_id']}",
                )
            ]
            pos_reverse = float(positive["lifted_reverse_arc_mean"])
            rev_reverse = float(reversal["lifted_reverse_arc_mean"])
            grouped[(mechanism, pattern)].append(
                {
                    "m4c_positive_preference": sign_preference(pos_m4, rev_m4),
                    "reverse_arc_positive_preference": sign_preference(pos_reverse, rev_reverse),
                    "positive_survival": float(pos_survives),
                    "reversal_survival": float(rev_survives),
                }
            )
    rows: list[dict[str, object]] = []
    for (mechanism, pattern), values in sorted(grouped.items()):
        rows.append(
            {
                "mechanism": mechanism,
                "survival_pattern": pattern,
                "pair_evaluations": len(values),
                "M4c_orientation_accuracy": mean(row["m4c_positive_preference"] for row in values),
                "reverse_arc_orientation_accuracy": mean(
                    row["reverse_arc_positive_preference"] for row in values
                ),
                "positive_footprint_survival": mean(row["positive_survival"] for row in values),
                "reversal_footprint_survival": mean(row["reversal_survival"] for row in values),
            }
        )
    return rows


def main() -> None:
    """Write actor-free survival and reciprocal-orientation diagnostic summaries."""
    args = parse_args()
    heuristic_dir = resolve(args.heuristic_dir)
    hard_dir = resolve(args.hard_panel_dir)
    ergm_dir = resolve(args.ergm_dir)
    output_dir = resolve(args.output_dir)
    prepare_output_dir(output_dir, args.overwrite)
    scores = m4_scores(ergm_dir)
    split_metrics, survival_summary, coverage = survival_diagnostics(heuristic_dir, scores)
    survival_contrasts = contrast_rows(split_metrics)
    reversal_summary = reversal_diagnostics(hard_dir, scores)
    write_csv(output_dir / "survival_stratified_split_metrics.csv", split_metrics)
    write_csv(output_dir / "survival_stratified_summary.csv", survival_summary)
    write_csv(output_dir / "survival_stratified_contrasts.csv", survival_contrasts)
    write_csv(output_dir / "survival_stratified_coverage.csv", coverage)
    write_csv(output_dir / "reversal_survival_reciprocity_summary.csv", reversal_summary)
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/61_summarize_survival_and_reversal_diagnostics.py",
                "dataset_id": args.dataset_id,
                "survival_definition": (
                    "B(e)=1 iff every candidate footprint arc is present "
                    "in the split-observed projection"
                ),
                "role": (
                    "descriptive secondary diagnostics; no primary masks "
                    "or candidate labels are changed"
                ),
                "privacy": "Only actor-free aggregate summaries are emitted.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Survival and reversal diagnostics passed.")
    print(f"Dataset: {args.dataset_id}; aggregate output: {output_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
