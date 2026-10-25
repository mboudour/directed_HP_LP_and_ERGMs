#!/usr/bin/env python3
"""Publish only non-sensitive aggregate outputs from the Senate benchmark.

Raw Bill Status XML, roster snapshots, processed events, actor identifiers,
candidate panels, conditional prediction rows, and R objects are excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "published" / "network_science_20261025"

PHASE2 = {
    "senate_118_s_bills_cap_profile": (
        "summary.md",
        "summary.json",
        "cap_profile.csv",
        "head_arity_distribution.csv",
    ),
    "senate_118_s_bills_cap_gate": ("summary.md", "summary.json", "formal_concept_feasibility.csv"),
    "senate_118_s_bills_native_event_fidelity_tail3_head10": ("summary.md", "summary.json"),
    "senate_118_s_bills_primary_masks": ("summary.md", "split_summary.csv", "manifest.json"),
    "senate_118_s_bills_primary_heuristics": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_sponsor_substitution": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_same_party_random": (
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_same_party_sponsor_substitution": (
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_sponsor_substitution_diagnostics": (
        "summary.csv",
        "recoverability_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_role_assignment": (
        "summary.md",
        "metric_summary_by_arity.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_primary_heuristic_paired_uncertainty": (
        "summary.md",
        "paired_differences.csv",
    ),
    "senate_118_s_bills_primary_competitive_contrasts": (
        "competitive_contrasts.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_static_arc_pilot": ("arc_lp_metrics.csv", "run_manifest.json"),
    "senate_118_s_bills_cap3_sensitivity_masks": (
        "summary.md",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_heuristics": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_sponsor_substitution": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_role_assignment": (
        "summary.md",
        "metric_summary_by_arity.csv",
        "split_summary.csv",
        "manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_heuristic_paired_uncertainty": (
        "summary.md",
        "paired_differences.csv",
    ),
}

MODELS = {
    "senate_118_s_bills_primary_ergm_scores": (
        "summary.md",
        "metric_summary.csv",
        "model_status.csv",
        "network_summary.csv",
        "split_status.csv",
        "run_manifest.json",
    ),
    "senate_118_s_bills_primary_ergm_paired_uncertainty": ("summary.md", "paired_differences.csv"),
    "senate_118_s_bills_primary_ergm_m5_scores": (
        "summary.md",
        "metric_summary.csv",
        "model_status.csv",
        "network_summary.csv",
        "split_status.csv",
        "run_manifest.json",
    ),
    "senate_118_s_bills_primary_m5_vs_m4c_paired_uncertainty": (
        "summary.md",
        "paired_differences.csv",
    ),
    "senate_118_s_bills_primary_ergm_role_assignment": (
        "manifest.json",
        "metric_summary.csv",
        "split_summary.csv",
    ),
    "senate_118_s_bills_primary_m5_ergm_role_assignment": (
        "manifest.json",
        "metric_summary.csv",
        "split_summary.csv",
    ),
    "senate_118_s_bills_primary_mtt_logistic": (
        "summary.md",
        "mechanism_summary.csv",
        "split_coefficients.csv",
        "run_manifest.json",
    ),
    "senate_118_s_bills_static_arc_ergm": (
        "summary.md",
        "metrics.csv",
        "model_status.csv",
        "replicate_status.csv",
        "replicate_network_summary.csv",
        "run_manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_ergm_scores": (
        "summary.md",
        "metric_summary.csv",
        "model_status.csv",
        "network_summary.csv",
        "split_status.csv",
        "run_manifest.json",
    ),
    "senate_118_s_bills_cap3_sensitivity_ergm_paired_uncertainty": (
        "summary.md",
        "paired_differences.csv",
    ),
}

RECORDS = (
    "docs/data_audits/senate_118_s_bills.md",
    "docs/SENATE_CAP_GATE_DECISION.md",
    "data/metadata/senate_118_s_bills_audit.json",
    "data/metadata/gates/senate_118_s_bills_policy.json",
    "data/metadata/gates/senate_118_s_bills_cap_selection.json",
    "data/metadata/senate_118_s_bills_political_covariates.json",
    "data/metadata/voteview_members_acquisition.json",
    "docs/data_audits/senate_118_s_bills_political_covariates.md",
)


def parse_args() -> argparse.Namespace:
    """Parse output controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve project-relative paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def digest(path: Path) -> str:
    """Return the SHA-256 digest of one published file."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_one(source: Path, destination: Path, manifest: list[dict[str, str]]) -> None:
    """Copy one allowlisted aggregate item and add it to the manifest."""
    if not source.is_file():
        raise SystemExit(f"STOP: expected allowlisted source does not exist: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if destination.suffix == ".md":
        destination.write_text(
            destination.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8"
        )
    manifest.append(
        {
            "source": str(source.relative_to(PROJECT_ROOT)),
            "published": str(destination.relative_to(PROJECT_ROOT)),
            "sha256": digest(destination),
            "bytes": str(destination.stat().st_size),
        }
    )


def copy_group(
    root: Path, names: dict[str, tuple[str, ...]], destination: Path, manifest: list[dict[str, str]]
) -> None:
    """Copy a group of allowlisted aggregate bundle files."""
    for bundle, files in names.items():
        for filename in files:
            copy_one(root / bundle / filename, destination / bundle / filename, manifest)


def main() -> None:
    """Build the aggregate-only Network Science evidence bundle."""
    args = parse_args()
    output_dir = resolve(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    manifest: list[dict[str, str]] = []
    copy_group(PROJECT_ROOT / "results" / "phase2", PHASE2, output_dir / "phase2", manifest)
    copy_group(PROJECT_ROOT / "results" / "models", MODELS, output_dir / "models", manifest)
    for record in RECORDS:
        source = PROJECT_ROOT / record
        copy_one(source, output_dir / "records" / Path(record).name, manifest)
    payload = {
        "purpose": (
            "aggregate-only Senate co-sponsorship evidence for the Network Science manuscript"
        ),
        "privacy_policy": (
            "No raw XML, roster files, processed events, actor identifiers, candidate panels, "
            "conditional prediction rows, fitted objects, or free-form logs are included."
        ),
        "artifacts": manifest,
    }
    (output_dir / "MANIFEST.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Aggregate Senate publication bundle written: {output_dir}")
    print(f"Artifacts: {len(manifest):,}")


if __name__ == "__main__":
    main()
