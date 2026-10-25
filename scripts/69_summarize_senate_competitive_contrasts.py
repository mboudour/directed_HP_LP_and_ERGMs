#!/usr/bin/env python3
"""Summarize matched Senate ERGM-versus-heuristic contrasts safely.

The input directories contain local, per-mask aggregate metric rows.  This
script releases only one actor-free contrast row per mechanism, panel, metric,
and method pair.  It resamples whole masks within a fixed network.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS = ("pr_auc", "roc_auc")
COMPARISONS = (
    ("random", "lifted_adamic_adar_total_mean"),
    ("sponsor_substitution", "lifted_degree_product_mean"),
)


def parse_args() -> argparse.Namespace:
    """Parse paths and inference controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--heuristic-dir", type=Path, required=True)
    parser.add_argument("--hard-panel-dir", type=Path, required=True)
    parser.add_argument("--ergm-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-reps", type=int, default=10_000)
    parser.add_argument("--permutation-reps", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20_261_026)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for name in ("bootstrap_reps", "permutation_reps"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive.")
    return args


def resolved(path: Path) -> Path:
    """Resolve a project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_local_metrics(root: Path, filename: str, panel: str) -> pd.DataFrame:
    """Load all completed local per-mask metric files for one candidate panel."""
    rows: list[pd.DataFrame] = []
    for path in sorted(root.glob(f"*_replicate_*/{filename}")):
        frame = pd.read_csv(path)
        if "panel" not in frame.columns:
            frame["panel"] = panel
        rows.append(frame)
    if not rows:
        raise SystemExit(f"STOP: no local metric files found in {root}: {filename}")
    return pd.concat(rows, ignore_index=True)


def confidence_and_test(
    values: np.ndarray,
    bootstrap_reps: int,
    permutation_reps: int,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    """Return mean difference, percentile interval, and sign-flip p value."""
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError("paired values must be finite and nonempty")
    bootstrap_indices = rng.integers(0, values.size, size=(bootstrap_reps, values.size))
    bootstrap_means = values[bootstrap_indices].mean(axis=1)
    observed = float(values.mean())
    low, high = np.quantile(bootstrap_means, [0.025, 0.975])
    signs = rng.choice(np.array([-1.0, 1.0]), size=(permutation_reps, values.size))
    null_means = (signs * values).mean(axis=1)
    p_value = (float(np.count_nonzero(np.abs(null_means) >= abs(observed))) + 1.0) / (
        permutation_reps + 1.0
    )
    return observed, float(low), float(high), p_value


def main() -> None:
    """Build safe paired contrast records from completed Senate primary masks."""
    args = parse_args()
    heuristic_dir = resolved(args.heuristic_dir)
    hard_panel_dir = resolved(args.hard_panel_dir)
    ergm_dir = resolved(args.ergm_dir)
    output_dir = resolved(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: output directory exists; pass --overwrite: {output_dir}")
        for path in output_dir.iterdir():
            if path.is_file() or path.is_symlink():
                path.unlink()
            else:
                shutil.rmtree(path)
    output_dir.mkdir(parents=True, exist_ok=True)

    local_random = load_local_metrics(heuristic_dir, "metrics.csv", "random")
    local_hard = load_local_metrics(
        hard_panel_dir, "sponsor_substitution_metrics.csv", "sponsor_substitution"
    )
    local = pd.concat([local_random, local_hard], ignore_index=True)
    local["metric_status"] = local["metric_status"].fillna("calculated")
    ergm = pd.read_csv(ergm_dir / "ranking_metrics.csv")
    ergm = ergm.loc[
        (ergm["model"] == "M4c")
        & (ergm["score"] == "L1g")
        & (ergm["metric"].isin(METRICS))
        & (ergm["status"] == "calculated"),
        ["mechanism", "replicate", "panel", "metric", "value"],
    ].rename(columns={"value": "ergm_value"})

    rng = np.random.default_rng(args.seed)
    output_rows: list[dict[str, object]] = []
    for panel, local_score in COMPARISONS:
        for metric in METRICS:
            local_subset = local.loc[
                (local["panel"] == panel)
                & (local["score"] == local_score)
                & (local["metric"] == metric)
                & (local["metric_status"] == "calculated"),
                ["mechanism", "replicate", "value"],
            ].rename(columns={"value": "local_value"})
            paired = ergm.loc[(ergm["panel"] == panel) & (ergm["metric"] == metric)].merge(
                local_subset, on=["mechanism", "replicate"], how="inner", validate="one_to_one"
            )
            for mechanism, group in paired.groupby("mechanism", sort=True):
                differences = group["ergm_value"].to_numpy() - group["local_value"].to_numpy()
                mean, low, high, p_value = confidence_and_test(
                    differences, args.bootstrap_reps, args.permutation_reps, rng
                )
                output_rows.append(
                    {
                        "dataset_id": args.dataset_id,
                        "mechanism": mechanism,
                        "panel": panel,
                        "metric": metric,
                        "ergm_method": "M4c::L1g",
                        "local_method": local_score,
                        "paired_masks": int(differences.size),
                        "mean_difference": mean,
                        "bootstrap_ci_low": low,
                        "bootstrap_ci_high": high,
                        "paired_sign_flip_p_value": p_value,
                        "bootstrap_reps": args.bootstrap_reps,
                        "permutation_reps": args.permutation_reps,
                    }
                )
    output = pd.DataFrame(output_rows).sort_values(["panel", "mechanism", "metric"])
    output.to_csv(output_dir / "competitive_contrasts.csv", index=False)
    manifest = {
        "dataset_id": args.dataset_id,
        "driver": "scripts/69_summarize_senate_competitive_contrasts.py",
        "estimand": "within-fixed-network mean of matched-mask M4c L1g minus declared local score",
        "resampling_unit": "whole frozen mask within the Senate network",
        "privacy": (
            "Only aggregate contrast rows are emitted; no candidate or actor records are copied."
        ),
        "comparisons": {panel: score for panel, score in COMPARISONS},
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Senate competitive contrasts written: {output_dir}")
    print(f"Rows: {len(output)}")


if __name__ == "__main__":
    main()
