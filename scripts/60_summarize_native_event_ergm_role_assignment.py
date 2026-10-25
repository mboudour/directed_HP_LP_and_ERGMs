#!/usr/bin/env python3
"""Summarize M4c and uniform fixed-participant role-assignment scores safely.

Candidate-level role assignments are read only from the untracked computation
bundle.  The output contains aggregate, actor-free counts and tie-aware role
accuracy suitable for the manuscript.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PANEL = "role_assignment"
DEFAULT_MODEL = "M4c"
DEFAULT_SCORE = "L1g"


def parse_args() -> argparse.Namespace:
    """Parse one M4c role-assignment output bundle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--ergm-score-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--score", default=DEFAULT_SCORE)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve project-relative paths from the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create or intentionally replace an aggregate output directory."""
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise RuntimeError(f"output directory is nonempty: {path}")
        for child in path.iterdir():
            if child.is_dir():
                import shutil

                shutil.rmtree(child)
            else:
                child.unlink()
    path.mkdir(parents=True, exist_ok=True)


def role_event_id(candidate_id: str) -> str:
    """Recover an opaque event namespace from the deterministic candidate ID."""
    prefix = f"{PANEL}::"
    if not candidate_id.startswith(prefix) or "_partition_" not in candidate_id:
        raise ValueError(f"invalid role-assignment candidate id: {candidate_id}")
    return candidate_id[len(prefix) :].rsplit("_partition_", maxsplit=1)[0]


def expected_metrics(values: list[float], labels: list[int]) -> tuple[float, float]:
    """Return tie-aware top-one accuracy and reciprocal rank for one event."""
    if len(values) != len(labels) or labels.count(1) != 1:
        raise ValueError("each role-assignment group must contain exactly one correct partition")
    correct = values[labels.index(1)]
    above = sum(value > correct for value in values)
    tied = sum(value == correct for value in values)
    top1 = 1.0 / tied if above == 0 else 0.0
    reciprocal_rank = mean(1.0 / rank for rank in range(above + 1, above + tied + 1))
    return top1, reciprocal_rank


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a deterministic nonempty aggregate table."""
    if not rows:
        raise RuntimeError(f"cannot write empty aggregate table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Aggregate M4c geometric scores and uniform expectations without candidates."""
    args = parse_args()
    score_dir = resolve(args.ergm_score_dir)
    output_dir = resolve(args.output_dir)
    model, score = args.model, args.score
    scores_path = score_dir / "event_footprint_scores.csv"
    if not scores_path.is_file():
        raise RuntimeError(f"missing ERGM footprint scores: {scores_path}")
    prepare_output_dir(output_dir, args.overwrite)

    groups: dict[tuple[str, int, str], list[dict[str, object]]] = defaultdict(list)
    with scores_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "split",
            "mechanism",
            "replicate",
            "model",
            "panel",
            "candidate_id",
            "label",
            score,
        }
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise RuntimeError("ERGM score table lacks the required role-assignment fields")
        for row in reader:
            if row["model"] != model or row["panel"] != PANEL:
                continue
            value = float(row[score])
            if not math.isfinite(value):
                raise RuntimeError("role-assignment ERGM score is nonfinite")
            key = (row["mechanism"], int(row["replicate"]), role_event_id(row["candidate_id"]))
            groups[key].append({"label": int(row["label"]), "value": value})

    if not groups:
        raise RuntimeError(f"no {model} role-assignment scores were found")

    per_event: list[dict[str, object]] = []
    for (mechanism, replicate, _event_id), rows in sorted(groups.items()):
        values = [float(row["value"]) for row in rows]
        labels = [int(row["label"]) for row in rows]
        top1, reciprocal_rank = expected_metrics(values, labels)
        per_event.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "role_partition_candidates": len(rows),
                "top1_accuracy": top1,
                "mrr": reciprocal_rank,
                "uniform_top1_accuracy": 1.0 / len(rows),
                "uniform_mrr": mean(1.0 / rank for rank in range(1, len(rows) + 1)),
            }
        )

    split_rows: list[dict[str, object]] = []
    by_split: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in per_event:
        by_split[(str(row["mechanism"]), int(row["replicate"]))].append(row)
    for (mechanism, replicate), rows in sorted(by_split.items()):
        split_rows.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "event_evaluations": len(rows),
                "top1_accuracy": mean(float(row["top1_accuracy"]) for row in rows),
                "mrr": mean(float(row["mrr"]) for row in rows),
                "uniform_top1_accuracy": mean(float(row["uniform_top1_accuracy"]) for row in rows),
                "uniform_mrr": mean(float(row["uniform_mrr"]) for row in rows),
                "mean_partition_count": mean(int(row["role_partition_candidates"]) for row in rows),
            }
        )

    summary_rows: list[dict[str, object]] = []
    by_mechanism: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in per_event:
        by_mechanism[str(row["mechanism"])].append(row)
    for mechanism, rows in sorted(by_mechanism.items()):
        values_top1 = [float(row["top1_accuracy"]) for row in rows]
        values_mrr = [float(row["mrr"]) for row in rows]
        uniform_top1 = [float(row["uniform_top1_accuracy"]) for row in rows]
        uniform_mrr = [float(row["uniform_mrr"]) for row in rows]
        completed_masks = len({int(row["replicate"]) for row in rows})
        summary_rows.append(
            {
                "mechanism": mechanism,
                "score": f"{model}::{score}",
                "event_evaluations": len(rows),
                "weighted_top1_accuracy": mean(values_top1),
                "event_level_top1_sd": stdev(values_top1) if len(values_top1) > 1 else 0.0,
                "weighted_mrr": mean(values_mrr),
                "event_level_mrr_sd": stdev(values_mrr) if len(values_mrr) > 1 else 0.0,
                "completed_masks": completed_masks,
            }
        )
        summary_rows.append(
            {
                "mechanism": mechanism,
                "score": "uniform_chance",
                "event_evaluations": len(rows),
                "weighted_top1_accuracy": mean(uniform_top1),
                "event_level_top1_sd": stdev(uniform_top1) if len(uniform_top1) > 1 else 0.0,
                "weighted_mrr": mean(uniform_mrr),
                "event_level_mrr_sd": stdev(uniform_mrr) if len(uniform_mrr) > 1 else 0.0,
                "completed_masks": completed_masks,
            }
        )

    write_csv(output_dir / "split_summary.csv", split_rows)
    write_csv(output_dir / "metric_summary.csv", summary_rows)
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/60_summarize_native_event_ergm_role_assignment.py",
                "dataset_id": args.dataset_id,
                "model": model,
                "score": score,
                "target": "fixed_participant_fixed_arity_role_assignment",
                "ties": "uniform tie-breaking expectation",
                "uniform_chance": "top-1=1/number_of_partitions; MRR=mean(1/rank)",
                "privacy": "Only actor-free aggregate results are emitted.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Native-event ERGM role-assignment summary passed.")
    print(f"Dataset: {args.dataset_id}; event evaluations: {len(per_event)}.")
    print(f"Output bundle: {output_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
