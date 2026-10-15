#!/usr/bin/env python3
"""Collect non-sensitive aggregate Phase 2 outputs for the private repository.

This collector deliberately excludes raw data, events, actor identifiers, candidate
panels, conditional prediction rows, fitted R objects, and free-form run logs. It
copies only aggregate summaries, coefficients, model statuses, and metric tables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "published" / "phase2_20261015"

PHASE2_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "caviar_full_static_formal_concepts_tail3_head3": (
        "summary.md",
        "arity_distribution.csv",
        "arc_multiplicity.csv",
    ),
    "caviar_concept_recovery": ("summary.md", "metric_summary.csv", "split_summary.csv"),
    "enron_formal_concepts_tail3_head3": (
        "summary.md",
        "arity_distribution.csv",
        "arc_multiplicity.csv",
    ),
    "enron_concept_recovery": ("summary.md", "metric_summary.csv", "split_summary.csv"),
    "enron_native_event_fidelity_tail3_head3": ("summary.md", "summary.json"),
    "enron_fidelity_rewire_null": (
        "summary.md",
        "summary.json",
        "observed_vs_rewire_null.csv",
        "rewire_metrics.csv",
    ),
    "enron_event_first_type_masks": ("summary.md", "split_summary.csv"),
    "enron_event_first_native_heuristics": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
    ),
    "enron_event_first_native_hard_panels": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
    ),
    "eu_core_formal_concepts_tail3_head3": (
        "summary.md",
        "arity_distribution.csv",
        "arc_multiplicity.csv",
    ),
    "eu_core_concept_recovery": ("summary.md", "metric_summary.csv", "split_summary.csv"),
    "mathoverflow_formal_concepts_tail3_head3": (
        "summary.md",
        "arity_distribution.csv",
        "arc_multiplicity.csv",
    ),
    "mathoverflow_concept_recovery": ("summary.md", "metric_summary.csv", "split_summary.csv"),
    "mathoverflow_native_event_fidelity_tail3_head3": ("summary.md", "summary.json"),
    "mathoverflow_event_first_type_masks": ("summary.md", "split_summary.csv"),
    "mathoverflow_event_first_native_heuristics": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
    ),
    "mathoverflow_event_first_native_hard_panels": (
        "summary.md",
        "metric_summary.csv",
        "split_summary.csv",
    ),
}

MODEL_ARTIFACTS: dict[str, tuple[str, ...]] = {
    "caviar_static_ladder_plan": ("model_status.csv", "coefficients.csv", "network_summary.csv"),
    "caviar_masked_ergm_plan": (
        "summary.md",
        "metrics.csv",
        "model_status.csv",
        "replicate_status.csv",
        "replicate_network_summary.csv",
    ),
    "enron_static_ladder_plan": ("model_status.csv", "coefficients.csv", "network_summary.csv"),
    "enron_masked_ergm_plan": (
        "summary.md",
        "metrics.csv",
        "model_status.csv",
        "replicate_status.csv",
        "replicate_network_summary.csv",
    ),
    "enron_native_event_ergm_footprints": (
        "summary.md",
        "metric_summary.csv",
        "ranking_metrics.csv",
        "model_status.csv",
        "split_status.csv",
        "network_summary.csv",
    ),
    "enron_temporal_lagged": (
        "summary.md",
        "factorized_coefficients.csv",
        "factorized_model_status.csv",
        "feature_summary.csv",
        "package_placeholder_status.csv",
    ),
    "enron_temporal_btergm_v3": (
        "summary.md",
        "model_status.csv",
        "coefficients.csv",
        "input_summary.csv",
        "panel_summary.csv",
        "lag_alignment.csv",
    ),
    "eu_core_static_ladder_plan": ("model_status.csv", "coefficients.csv", "network_summary.csv"),
    "eu_core_masked_ergm_plan": (
        "summary.md",
        "metrics.csv",
        "model_status.csv",
        "replicate_status.csv",
        "replicate_network_summary.csv",
    ),
    "eu_core_temporal_lagged": (
        "summary.md",
        "factorized_coefficients.csv",
        "factorized_model_status.csv",
        "feature_summary.csv",
        "package_placeholder_status.csv",
    ),
    "eu_core_temporal_btergm_v3": (
        "summary.md",
        "model_status.csv",
        "coefficients.csv",
        "input_summary.csv",
        "panel_summary.csv",
        "lag_alignment.csv",
    ),
    "mathoverflow_static_ladder_plan": (
        "model_status.csv",
        "coefficients.csv",
        "network_summary.csv",
    ),
    "mathoverflow_masked_ergm_plan": (
        "summary.md",
        "metrics.csv",
        "model_status.csv",
        "replicate_status.csv",
        "replicate_network_summary.csv",
    ),
    "mathoverflow_native_event_ergm_footprints": (
        "summary.md",
        "metric_summary.csv",
        "ranking_metrics.csv",
        "model_status.csv",
        "split_status.csv",
        "network_summary.csv",
    ),
}


def parse_args() -> argparse.Namespace:
    """Parse output controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def digest(path: Path) -> str:
    """Return a SHA-256 checksum of one copied aggregate artifact."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve(path: Path) -> Path:
    """Resolve project-relative paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def collect_group(
    *,
    source_root: Path,
    names: dict[str, tuple[str, ...]],
    destination_root: Path,
    manifest: list[dict[str, str]],
) -> None:
    """Copy the allowlisted aggregate files and record their digests."""
    for bundle, filenames in names.items():
        for filename in filenames:
            source = source_root / bundle / filename
            if not source.is_file():
                raise SystemExit(f"STOP: expected aggregate artifact is missing: {source}")
            destination = destination_root / bundle / filename
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


def main() -> None:
    """Build a repeatable aggregate-only Phase 2 result bundle."""
    args = parse_args()
    output_dir = resolve(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    manifest: list[dict[str, str]] = []
    collect_group(
        source_root=PROJECT_ROOT / "results" / "phase2",
        names=PHASE2_ARTIFACTS,
        destination_root=output_dir / "phase2",
        manifest=manifest,
    )
    collect_group(
        source_root=PROJECT_ROOT / "results" / "models",
        names=MODEL_ARTIFACTS,
        destination_root=output_dir / "models",
        manifest=manifest,
    )
    manifest_payload = {
        "purpose": "aggregate-only private-repository Phase 2 computational output",
        "privacy_policy": (
            "No raw data, event rows, actor identifiers, candidate panels, "
            "conditional prediction rows, fitted R objects, or free-form logs are included."
        ),
        "artifacts": manifest,
    }
    (output_dir / "MANIFEST.json").write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Aggregate Phase 2 publication bundle written: {output_dir}")
    print(f"Artifacts: {len(manifest):,}")


if __name__ == "__main__":
    main()
