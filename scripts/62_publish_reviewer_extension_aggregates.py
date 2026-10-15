#!/usr/bin/env python3
"""Publish aggregate-only summaries for manuscript reviewer extensions.

This utility converts untracked split-level intermediate outputs into
actor-free aggregate tables. It never copies candidate IDs, dyads, event
roles, fitted objects, or source records to the tracked publication bundle.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("enron", "mathoverflow")


def parse_args() -> argparse.Namespace:
    """Parse the fixed reviewer-extension publication destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/published/phase2_20261015/manuscript_reviewer_extensions"),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative path from the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create or deliberately replace the aggregate publication directory."""
    if path.exists() and not path.is_dir():
        raise RuntimeError(f"output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise RuntimeError(f"output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path, columns: set[str]) -> pd.DataFrame:
    """Read a tabular input only after verifying its explicit output contract."""
    if not path.is_file():
        raise RuntimeError(f"missing input: {path}")
    frame = pd.read_csv(path)
    missing = columns.difference(frame.columns)
    if missing:
        raise RuntimeError(f"input lacks required columns {sorted(missing)}: {path}")
    return frame


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    """Write a deterministic actor-free aggregate CSV."""
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")


def intermediate_ladder() -> pd.DataFrame:
    """Aggregate M2/M4 random-panel ranking metrics from all 30 masks."""
    summaries: list[pd.DataFrame] = []
    for dataset in DATASETS:
        path = (
            PROJECT_ROOT
            / "results"
            / "models"
            / f"{dataset}_native_event_ergm_intermediate"
            / "ranking_metrics.csv"
        )
        frame = read_csv(path, {"mechanism", "model", "panel", "score", "metric", "value"})
        frame = frame[(frame["panel"] == "random") & (frame["score"] == "L1g")]
        grouped = (
            frame.groupby(["mechanism", "model", "metric"])["value"]
            .agg(completed_masks="count", mean="mean", sd="std")
            .reset_index()
        )
        grouped.insert(0, "dataset", dataset)
        summaries.append(grouped)
    return pd.concat(summaries, ignore_index=True).sort_values(
        ["dataset", "model", "mechanism", "metric"], ignore_index=True
    )


def role_assignment() -> pd.DataFrame:
    """Combine already-aggregate M4c fixed-participant role metrics."""
    summaries: list[pd.DataFrame] = []
    required = {
        "mechanism",
        "score",
        "event_evaluations",
        "weighted_top1_accuracy",
        "weighted_mrr",
        "completed_masks",
    }
    for dataset in DATASETS:
        path = (
            PROJECT_ROOT
            / "results"
            / "phase2"
            / f"{dataset}_native_event_ergm_role_assignment"
            / "metric_summary.csv"
        )
        frame = read_csv(path, required)
        frame.insert(0, "dataset", dataset)
        summaries.append(frame)
    return pd.concat(summaries, ignore_index=True).sort_values(["dataset", "mechanism"])


def mtt_logistic() -> pd.DataFrame:
    """Combine actor-free split-specific transitive-triple logistic summaries."""
    summaries: list[pd.DataFrame] = []
    required = {
        "mechanism",
        "completed_masks",
        "positive_theta_masks",
        "theta_triple_mean",
        "theta_triple_sd",
        "theta_triple_min",
        "theta_triple_max",
        "rank_relation",
    }
    for dataset in DATASETS:
        path = (
            PROJECT_ROOT
            / "results"
            / "models"
            / f"{dataset}_mtt_logistic"
            / "mechanism_summary.csv"
        )
        frame = read_csv(path, required)
        frame.insert(0, "dataset", dataset)
        summaries.append(frame)
    return pd.concat(summaries, ignore_index=True).sort_values(["dataset", "mechanism"])


def diagnostics() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Combine actor-free survival and reversal diagnostic outputs."""
    contrast_frames: list[pd.DataFrame] = []
    reversal_frames: list[pd.DataFrame] = []
    for dataset in DATASETS:
        directory = PROJECT_ROOT / "results" / "phase2" / f"{dataset}_survival_reversal_diagnostics"
        contrasts = read_csv(
            directory / "survival_stratified_contrasts.csv",
            {
                "mechanism",
                "survival_stratum",
                "contrast",
                "completed_masks",
                "mean_pr_auc_difference",
                "bootstrap_reps",
                "bootstrap_ci_lower",
                "bootstrap_ci_upper",
            },
        )
        reversal = read_csv(
            directory / "reversal_survival_reciprocity_summary.csv",
            {"mechanism", "survival_pattern", "pair_evaluations", "M4c_orientation_accuracy"},
        )
        contrasts.insert(0, "dataset", dataset)
        reversal.insert(0, "dataset", dataset)
        contrast_frames.append(contrasts)
        reversal_frames.append(reversal)
    return (
        pd.concat(contrast_frames, ignore_index=True).sort_values(
            ["dataset", "mechanism", "survival_stratum", "contrast"], ignore_index=True
        ),
        pd.concat(reversal_frames, ignore_index=True).sort_values(
            ["dataset", "mechanism", "survival_pattern"], ignore_index=True
        ),
    )


def main() -> None:
    """Build the safe, source-controlled reviewer-extension aggregate bundle."""
    args = parse_args()
    output_dir = resolve(args.output_dir)
    prepare_output_dir(output_dir, args.overwrite)
    ladder = intermediate_ladder()
    roles = role_assignment()
    mtt = mtt_logistic()
    survival, reversal = diagnostics()
    write_csv(ladder, output_dir / "intermediate_ergm_ladder.csv")
    write_csv(roles, output_dir / "ergm_role_assignment.csv")
    write_csv(mtt, output_dir / "mtt_logistic.csv")
    write_csv(survival, output_dir / "survival_stratified_contrasts.csv")
    write_csv(reversal, output_dir / "reversal_survival_reciprocity.csv")
    (output_dir / "MANIFEST.json").write_text(
        json.dumps(
            {
                "driver": "scripts/62_publish_reviewer_extension_aggregates.py",
                "status": "completed",
                "sources": {
                    "intermediate_ladder": "results/models/*_native_event_ergm_intermediate",
                    "ergm_role_assignment": "results/phase2/*_native_event_ergm_role_assignment",
                    "mtt_logistic": "results/models/*_mtt_logistic",
                    "survival_reversal_diagnostics": (
                        "results/phase2/*_survival_reversal_diagnostics"
                    ),
                },
                "privacy": (
                    "Published files contain aggregate scores, counts, "
                    "and summary statistics only; "
                    "they exclude candidate rows, identities, raw records, and fitted objects."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Reviewer-extension aggregate publication passed.")
    print(f"Output bundle: {output_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
