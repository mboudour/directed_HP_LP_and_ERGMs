#!/usr/bin/env python3
"""Summarize safe aggregate metrics from Enron conditional-RHEM sensitivity runs.

The driver never reads or emits actor identifiers, event identities, candidate
receiver sets, or Eventnet covariate rows.  It combines only each run's
aggregate ranking metrics, model status, and run manifest into a tracked,
aggregate-only Paper 2 result bundle.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "published" / "paper2_temporal_20261030"
METRICS = ("mean_log_score", "top1_tie_adjusted", "mrr_tie_adjusted", "mean_rank")


@dataclass(frozen=True)
class RunSpec:
    """One aggregate sensitivity result source and its substantive label."""

    label: str
    path: Path
    dimension: str


def parse_args() -> argparse.Namespace:
    """Parse exact result bundle locations for three required sensitivity runs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True, help="Primary seeded ascending run.")
    parser.add_argument(
        "--sampling-sensitivity",
        type=Path,
        required=True,
        help="Independent Eventnet random-seed ascending run.",
    )
    parser.add_argument(
        "--tie-sensitivity",
        type=Path,
        required=True,
        help="Same-seed descending within-timestamp-order run.",
    )
    parser.add_argument(
        "--footprint-collapse-sensitivity",
        type=Path,
        help="Optional same-timestamp identical-footprint collapse run.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve potentially project-relative paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Represent a path relative to the project if possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a nonempty aggregate CSV with a header."""
    if not path.is_file():
        raise SystemExit(f"STOP: required aggregate file is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"STOP: aggregate file has no rows: {path}")
    return rows


def read_run(spec: RunSpec) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load and validate one aggregate-only RHEM evaluation bundle."""
    metrics = read_csv(spec.path / "ranking_metrics.csv")
    statuses = read_csv(spec.path / "model_status.csv")
    manifest_path = spec.path / "run_manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"STOP: RHEM run manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("observation") != "CONDITIONAL_SENDER_SET":
        raise SystemExit(f"STOP: expected conditional-sender RHEM result: {spec.path}")
    failed = [
        row
        for row in statuses
        if row.get("status") not in {"fit_succeeded", "fit_succeeded_nonfinite_terms_dropped"}
    ]
    if failed:
        raise SystemExit(f"STOP: RHEM run has failed model folds: {spec.path}")
    required = {"model", "fold", "scope", "choice_sets", *METRICS}
    if any(set(row) < required for row in metrics):
        raise SystemExit(f"STOP: RHEM metrics schema is incomplete: {spec.path}")
    rows: list[dict[str, Any]] = []
    for row in metrics:
        parsed: dict[str, Any] = {
            "variant": spec.label,
            "sensitivity_dimension": spec.dimension,
            "model": row["model"],
            "fold": row["fold"],
            "scope": row["scope"],
            "choice_sets": int(row["choice_sets"]),
        }
        parsed.update({metric: float(row[metric]) for metric in METRICS})
        if parsed["choice_sets"] < 1:
            raise SystemExit(f"STOP: nonpositive evaluated choice-set count: {spec.path}")
        rows.append(parsed)
    return rows, manifest


def weighted_mean(rows: list[dict[str, Any]], field: str) -> float:
    """Compute a choice-set-weighted mean across folds without pseudo-replication."""
    total = sum(row["choice_sets"] for row in rows)
    return sum(row["choice_sets"] * row[field] for row in rows) / total


def safe_write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    """Write a deterministic aggregate CSV."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_variant(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pool each model/scope across predeclared chronological folds."""
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(
            (row["variant"], row["sensitivity_dimension"], row["model"], row["scope"]), []
        ).append(row)
    summary: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        result = {
            "variant": key[0],
            "sensitivity_dimension": key[1],
            "model": key[2],
            "scope": key[3],
            "folds": len(group),
            "choice_sets": sum(row["choice_sets"] for row in group),
        }
        result.update({metric: weighted_mean(group, metric) for metric in METRICS})
        summary.append(result)
    return summary


def paired_contrasts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute model contrasts within the identical fold, risk set, and scope."""
    indexed = {(row["variant"], row["fold"], row["scope"], row["model"]): row for row in rows}
    contrasts: list[dict[str, Any]] = []
    keys = sorted({key[:3] for key in indexed})
    for variant, fold, scope in keys:
        dyadic = indexed.get((variant, fold, scope, "DYADIC_HISTORY"))
        group = indexed.get((variant, fold, scope, "GROUP_AUGMENTED"))
        if dyadic is None or group is None:
            raise SystemExit("STOP: sensitivity result lacks a paired model contrast.")
        if dyadic["choice_sets"] != group["choice_sets"]:
            raise SystemExit("STOP: model contrast has unequal choice-set counts.")
        contrasts.append(
            {
                "variant": variant,
                "sensitivity_dimension": group["sensitivity_dimension"],
                "fold": fold,
                "scope": scope,
                "choice_sets": group["choice_sets"],
                "delta_mean_log_score": group["mean_log_score"] - dyadic["mean_log_score"],
                "delta_top1_tie_adjusted": group["top1_tie_adjusted"] - dyadic["top1_tie_adjusted"],
                "delta_mrr_tie_adjusted": group["mrr_tie_adjusted"] - dyadic["mrr_tie_adjusted"],
                "delta_mean_rank": group["mean_rank"] - dyadic["mean_rank"],
            }
        )
    return contrasts


def summarize_contrasts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pool paired contrasts across the fixed chronological folds by sensitivity variant."""
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row["variant"], row["sensitivity_dimension"], row["scope"]), []).append(
            row
        )
    output: list[dict[str, Any]] = []
    fields = (
        "delta_mean_log_score",
        "delta_top1_tie_adjusted",
        "delta_mrr_tie_adjusted",
        "delta_mean_rank",
    )
    for key in sorted(groups):
        group = groups[key]
        result = {
            "variant": key[0],
            "sensitivity_dimension": key[1],
            "scope": key[2],
            "folds": len(group),
            "choice_sets": sum(row["choice_sets"] for row in group),
        }
        result.update({field: weighted_mean(group, field) for field in fields})
        output.append(result)
    return output


def render_summary(
    variant_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    manifests: dict[str, dict[str, Any]],
) -> str:
    """Render a concise aggregate-only result record with interpretation limits."""
    lines = [
        "# Enron conditional-RHEM sampled-risk-set sensitivities",
        "",
        "## Design",
        "",
        "The primary task is receiver-set choice conditional on the observed sender and observed receiver-set size. It is evaluated in four expanding 2001 quarters on a 50-actor universe selected from pre-2001 participation only. Every displayed metric is calculated within Eventnet's same-size sampled candidate sets; it is not a probability of an email event, sender, timing, or set size.",
        "",
        "The sensitivity runs include a second sampled-control seed, a reverse deterministic order within identical timestamps, and a source-record representation sensitivity that collapses identical timestamp/sender/receiver-set footprints. Each requests 100 non-events per observed event, while an event with a singleton receiver may have fewer than 100 eligible alternatives in the 50-actor universe.",
        "",
        "## Pooled discrimination by sensitivity variant",
        "",
        "| Variant | Model | Scope | Choice sets | Mean log score | Top-1 | MRR | Mean rank |",
        "|:---|:---|:---|---:|---:|---:|---:|---:|",
    ]
    for row in variant_rows:
        lines.append(
            "| {variant} | {model} | {scope} | {choice_sets:,} | {mean_log_score:.4f} | {top1_tie_adjusted:.4f} | {mrr_tie_adjusted:.4f} | {mean_rank:.3f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Group-augmented minus dyadic-history contrast",
            "",
            "| Variant | Scope | Choice sets | Δ log score | Δ Top-1 | Δ MRR | Δ mean rank |",
            "|:---|:---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in contrast_rows:
        lines.append(
            "| {variant} | {scope} | {choice_sets:,} | {delta_mean_log_score:+.4f} | {delta_top1_tie_adjusted:+.4f} | {delta_mrr_tie_adjusted:+.4f} | {delta_mean_rank:+.3f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The multi-recipient scope is small. Its results are a targeted feasibility signal, not an estimate of a stable higher-order effect. The time-order sensitivity is an Eventnet interval-order check; a batch-history analysis that prevents same-time records from entering one another's covariates remains required before final interpretation. The observed group-model contrast also depends on the declared decay half-life, candidate eligibility rule, and selected 50-actor universe.",
            "",
            "## Run provenance",
            "",
        ]
    )
    for label in sorted(manifests):
        manifest = manifests[label]
        lines.append(
            f"- `{label}`: Eventnet seed `{manifest['eventnet_random_seed']}`; "
            f"requested controls `{manifest['requested_controls_per_event']}`; "
            f"choice sets `{manifest['choice_sets']:,}`."
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    """Assemble a safe aggregate Paper 2 sensitivity bundle."""
    args = parse_args()
    specs = [
        RunSpec("primary_ascending_seed_20261030", resolve(args.primary), "primary"),
        RunSpec("sampling_seed_20261031", resolve(args.sampling_sensitivity), "control_sampling"),
        RunSpec("descending_order_seed_20261030", resolve(args.tie_sensitivity), "timestamp_order"),
    ]
    if args.footprint_collapse_sensitivity is not None:
        specs.append(
            RunSpec(
                "collapsed_timestamp_footprints_seed_20261030",
                resolve(args.footprint_collapse_sensitivity),
                "event_representation",
            )
        )
    output_dir = resolve(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        if not args.overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {output_dir}; pass --overwrite.")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict[str, Any]] = []
    manifests: dict[str, dict[str, Any]] = {}
    for spec in specs:
        rows, manifest = read_run(spec)
        all_rows.extend(rows)
        manifests[spec.label] = manifest
    key_sets = [
        {
            (row["model"], row["fold"], row["scope"])
            for row in all_rows
            if row["variant"] == spec.label
        }
        for spec in specs
    ]
    if any(keys != key_sets[0] for keys in key_sets[1:]):
        raise SystemExit("STOP: sensitivity bundles do not cover identical model-fold-scope keys.")

    variant_summary = summarize_variant(all_rows)
    contrasts = paired_contrasts(all_rows)
    contrast_summary = summarize_contrasts(contrasts)
    detailed_fields = [
        "variant",
        "sensitivity_dimension",
        "model",
        "fold",
        "scope",
        "choice_sets",
        *METRICS,
    ]
    variant_fields = [
        "variant",
        "sensitivity_dimension",
        "model",
        "scope",
        "folds",
        "choice_sets",
        *METRICS,
    ]
    contrast_fields = [
        "variant",
        "sensitivity_dimension",
        "fold",
        "scope",
        "choice_sets",
        "delta_mean_log_score",
        "delta_top1_tie_adjusted",
        "delta_mrr_tie_adjusted",
        "delta_mean_rank",
    ]
    contrast_summary_fields = [
        "variant",
        "sensitivity_dimension",
        "scope",
        "folds",
        "choice_sets",
        "delta_mean_log_score",
        "delta_top1_tie_adjusted",
        "delta_mrr_tie_adjusted",
        "delta_mean_rank",
    ]
    safe_write_csv(output_dir / "rhem_metrics_by_fold.csv", all_rows, detailed_fields)
    safe_write_csv(output_dir / "rhem_metrics_pooled.csv", variant_summary, variant_fields)
    safe_write_csv(output_dir / "rhem_group_contrasts_by_fold.csv", contrasts, contrast_fields)
    safe_write_csv(
        output_dir / "rhem_group_contrasts_pooled.csv", contrast_summary, contrast_summary_fields
    )
    provenance = {
        "status": "conditional_rhem_sampled_risk_set_pilot_completed",
        "driver": "scripts/79_summarize_enron_rhem_sensitivities.py",
        "input_runs": {spec.label: recorded(spec.path) for spec in specs},
        "input_run_manifests": manifests,
        "data_policy": {
            "actor_universe": "50 actors selected from pre-2001 participation only",
            "evaluation": "four expanding 2001 quarterly folds",
            "event_task": "receiver-set choice conditional on observed sender and receiver-set size",
            "raw_event_or_candidate_rows_published": False,
        },
        "limitations": [
            "Results are conditional on Eventnet sampled candidate sets, not full-risk-set probabilities.",
            "The group-event subset is small and must be reported separately from singleton-receiver events.",
            "The timestamp-order sensitivity does not replace a simultaneous-batch history analysis.",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "summary.md").write_text(
        render_summary(variant_summary, contrast_summary, manifests), encoding="utf-8"
    )
    print("Enron RHEM aggregate sensitivity summary complete.")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
