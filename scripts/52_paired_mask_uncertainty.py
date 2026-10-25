#!/usr/bin/env python3
"""Estimate within-dataset paired score differences across frozen mask replicates.

The unit of resampling is the entire mask replicate, never a candidate, event, or
network dyad. This script reports percentile bootstrap confidence intervals for
mean paired differences and a Monte-Carlo paired sign-flip permutation test.
It is deliberately a within-dataset diagnostic: results must not be pooled as if
masks from different datasets were independent networks.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The native heuristic reference is fixed before reading results: the aggregate
# directed Adamic--Adar score corresponds to the all-configuration LP baseline.
HEURISTIC_REFERENCE = "lifted_adamic_adar_total_mean"
# The ERGM reference is the edges-only factorized footprint score.
ERGM_REFERENCE = "M0::L1"


def parse_args() -> argparse.Namespace:
    """Parse source-controlled paired-inference options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--kind", choices=("native_heuristic", "native_ergm"), required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-reps", type=int, default=10_000)
    parser.add_argument("--permutation-reps", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument(
        "--reference-method",
        help=(
            "Optional score name used as the matched reference. The default remains "
            "the source-family reference declared in this script."
        ),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.bootstrap_reps < 1_000 or args.permutation_reps < 1_000:
        parser.error("bootstrap and permutation repetitions must each be at least 1,000.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative input and output paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render project-relative paths where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a required, nonempty CSV table."""
    if not path.is_file():
        raise SystemExit(f"STOP: required paired-inference table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"STOP: required paired-inference table has no rows: {path}")
    return rows


def source_rows(kind: str, input_dir: Path) -> list[dict[str, str]]:
    """Normalize heuristic or ERGM replicate metric rows to a shared contract."""
    if kind == "native_heuristic":
        rows: list[dict[str, str]] = []
        for metrics_path in sorted(input_dir.glob("*_replicate_*/metrics.csv")):
            for row in read_csv(metrics_path):
                rows.append(
                    {
                        "mechanism": row["mechanism"],
                        "replicate": row["replicate"],
                        "panel": "random",
                        "metric": row["metric"],
                        "method": row["score"],
                        "value": row["value"],
                        "status": row.get("metric_status", "calculated"),
                    }
                )
        if not rows:
            raise SystemExit(f"STOP: no split metrics found below {input_dir}")
        return rows
    rows = []
    for row in read_csv(input_dir / "ranking_metrics.csv"):
        rows.append(
            {
                "mechanism": row["mechanism"],
                "replicate": row["replicate"],
                "panel": row["panel"],
                "metric": row["metric"],
                "method": f"{row['model']}::{row['score']}",
                "value": row["value"],
                "status": row["status"],
            }
        )
    return rows


def reference_for(kind: str) -> str:
    """Return the predeclared comparison reference for one source family."""
    return HEURISTIC_REFERENCE if kind == "native_heuristic" else ERGM_REFERENCE


def percentile_bootstrap(
    values: np.ndarray, repetitions: int, rng: np.random.Generator
) -> tuple[float, float]:
    """Return a deterministic percentile bootstrap interval for a paired mean."""
    indices = rng.integers(0, values.size, size=(repetitions, values.size))
    replicates = values[indices].mean(axis=1)
    low, high = np.quantile(replicates, (0.025, 0.975), method="linear")
    return float(low), float(high)


def sign_flip_p_value(values: np.ndarray, repetitions: int, rng: np.random.Generator) -> float:
    """Return two-sided Monte-Carlo p-value under a paired sign-flip null."""
    observed = abs(float(values.mean()))
    if values.size <= 16:
        signs = np.array(
            [
                [1 if (mask >> bit) & 1 else -1 for bit in range(values.size)]
                for mask in range(2**values.size)
            ],
            dtype=float,
        )
        null = np.abs((signs * values).mean(axis=1))
        return float(np.mean(null >= observed))
    signs = rng.choice(np.array((-1.0, 1.0)), size=(repetitions, values.size))
    null = np.abs((signs * values).mean(axis=1))
    return float((1 + np.count_nonzero(null >= observed)) / (repetitions + 1))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty, Unix-ended aggregate CSV."""
    if not rows:
        raise RuntimeError(f"cannot write an empty paired-inference table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run paired comparisons using one frozen-mask sequence per dataset."""
    args = parse_args()
    input_dir, output_dir = resolve(args.input_dir), resolve(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: paired-inference output exists: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    rows = source_rows(args.kind, input_dir)
    grouped: dict[tuple[str, str, str], dict[str, dict[int, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        if row["status"] != "calculated":
            continue
        try:
            value = float(row["value"])
            replicate = int(row["replicate"])
        except ValueError as error:
            raise SystemExit(f"STOP: invalid paired metric row: {row}") from error
        if not math.isfinite(value):
            continue
        key = (row["mechanism"], row["panel"], row["metric"])
        if replicate in grouped[key][row["method"]]:
            raise SystemExit(f"STOP: duplicate method/replicate row for {key}: {row['method']}")
        grouped[key][row["method"]][replicate] = value

    reference = args.reference_method or reference_for(args.kind)
    rng = np.random.default_rng(args.seed)
    output_rows: list[dict[str, object]] = []
    for (mechanism, panel, metric), methods in sorted(grouped.items()):
        if reference not in methods:
            continue
        reference_values = methods[reference]
        for method in sorted(methods):
            if method == reference:
                continue
            common = sorted(set(reference_values).intersection(methods[method]))
            if len(common) < 2:
                continue
            delta = np.array(
                [methods[method][replicate] - reference_values[replicate] for replicate in common]
            )
            ci_low, ci_high = percentile_bootstrap(delta, args.bootstrap_reps, rng)
            p_value = sign_flip_p_value(delta, args.permutation_reps, rng)
            output_rows.append(
                {
                    "dataset_id": args.dataset_id,
                    "kind": args.kind,
                    "mechanism": mechanism,
                    "panel": panel,
                    "metric": metric,
                    "comparison_method": method,
                    "reference_method": reference,
                    "paired_masks": len(common),
                    "mean_difference": float(delta.mean()),
                    "bootstrap_ci_low": ci_low,
                    "bootstrap_ci_high": ci_high,
                    "paired_sign_flip_p_value": p_value,
                    "permutation_reps": args.permutation_reps,
                    "bootstrap_reps": args.bootstrap_reps,
                }
            )
    if not output_rows:
        raise SystemExit("STOP: no finite paired comparisons were available.")
    write_csv(output_dir / "paired_differences.csv", output_rows)
    manifest = {
        "driver": "scripts/52_paired_mask_uncertainty.py",
        "dataset_id": args.dataset_id,
        "kind": args.kind,
        "source": recorded_path(input_dir),
        "resampling_unit": "frozen whole-mask replicate",
        "reference_method": reference,
        "bootstrap": {
            "method": "percentile",
            "repetitions": args.bootstrap_reps,
            "confidence_level": 0.95,
        },
        "permutation_test": {
            "method": "two_sided_paired_sign_flip",
            "repetitions": args.permutation_reps,
        },
        "scope": "within-dataset inference only; no masks are pooled across datasets as independent networks",
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Paired frozen-mask uncertainty analysis",
        "",
        f"- Dataset: `{args.dataset_id}`",
        f"- Source family: `{args.kind}`",
        f"- Fixed reference: `{reference}`",
        "- Resampling unit: the whole frozen mask replicate.",
        f"- Interval: 95% percentile bootstrap ({args.bootstrap_reps:,} replications).",
        f"- Test: two-sided paired sign-flip permutation ({args.permutation_reps:,} replications).",
        "- Scope: within-dataset comparisons only; mask replicates are never treated as independent networks across datasets.",
        "",
        "See `paired_differences.csv` for all predeclared reference contrasts.",
        "",
    ]
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Paired frozen-mask uncertainty analysis passed.")
    print(f"Dataset: {args.dataset_id}; comparisons: {len(output_rows):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
