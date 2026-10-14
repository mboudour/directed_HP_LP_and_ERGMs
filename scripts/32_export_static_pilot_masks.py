#!/usr/bin/env python3
"""Backfill deterministic training masks from a completed static Phase 2 pilot.

The static pilot stores its full reproducibility contract in ``run_manifest.json``. This
script reconstructs exactly those arc-first masks, verifies them against the recorded LP
candidate labels, and exports only the local files required for masked ERGM conditional
scoring. It never changes the completed pilot's scores or metrics.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pyarrow.parquet as pq

from directed_hp.masking.directed_masks import MaskingMechanism, mask_arc_first

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse the completed pilot bundle to augment with deterministic mask files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve_recorded_path(value: str) -> Path:
    """Resolve a manifest path that may be project-relative or absolute."""
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Display a repository-relative local path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_arcs(path: Path, tail_column: str, head_column: str) -> tuple[tuple[str, str], ...]:
    """Read the frozen loop-free relation under the pilot's original column contract."""
    if not path.is_file():
        raise SystemExit(f"STOP: pilot input arcs are missing: {path}")
    source = pq.ParquetFile(path)
    missing = {tail_column, head_column} - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: pilot input arcs lack columns {sorted(missing)}")
    arcs: dict[tuple[str, str], None] = {}
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            tail = str(row[tail_column])
            head = str(row[head_column])
            if tail != head:
                arcs.setdefault((tail, head), None)
    return tuple(arcs)


def write_edges(path: Path, arcs: tuple[tuple[str, str], ...]) -> None:
    """Write one simple directed edge list used by the masked R ERGM scorer."""
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["from", "to"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"from": tail, "to": head} for tail, head in arcs)


def main() -> None:
    """Recreate pilot masks and candidate panels exactly from the recorded seed contract."""
    args = parse_args()
    pilot_dir = args.pilot_dir if args.pilot_dir.is_absolute() else PROJECT_ROOT / args.pilot_dir
    manifest_path = pilot_dir / "run_manifest.json"
    prediction_path = pilot_dir / "arc_lp_predictions.parquet"
    if not manifest_path.is_file() or not prediction_path.is_file():
        raise SystemExit(
            "STOP: pilot directory must contain run_manifest.json and arc_lp_predictions.parquet: "
            f"{pilot_dir}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("pilot_type") != "static_arc_lp_and_representation_fidelity":
        raise SystemExit("STOP: supplied directory is not a static Phase 2 pilot bundle.")
    masking = manifest.get("masking")
    if not isinstance(masking, dict) or masking.get("regime") != "arc_first":
        raise SystemExit("STOP: mask export supports the recorded arc-first pilot regime only.")
    try:
        replicates = int(masking["replicates"])
        seed = int(masking["seed"])
        rate = float(masking["requested_rate"])
        mechanism = MaskingMechanism(str(masking["mechanism"]))
        arcs_path = resolve_recorded_path(str(manifest["input_arcs"]))
        tail_column = str(manifest["tail_column"])
        head_column = str(manifest["head_column"])
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(
            "STOP: static pilot manifest lacks a valid masking/input contract."
        ) from error

    masks_dir = pilot_dir / "masks"
    if masks_dir.exists() and any(masks_dir.iterdir()) and not args.overwrite:
        raise SystemExit(f"STOP: mask directory is nonempty: {masks_dir}")
    masks_dir.mkdir(parents=True, exist_ok=True)
    arcs = read_arcs(arcs_path, tail_column, head_column)
    prediction_table = pq.read_table(
        prediction_path, columns=["replicate", "candidate_tail", "candidate_head", "label"]
    )
    prediction_rows = prediction_table.to_pylist()
    exported: list[dict[str, object]] = []

    for replicate in range(1, replicates + 1):
        mask = mask_arc_first(arcs, rate=rate, mechanism=mechanism, seed=seed + replicate - 1)
        candidates = [row for row in prediction_rows if int(row["replicate"]) == replicate]
        if not candidates:
            raise SystemExit(f"STOP: pilot predictions have no rows for replicate {replicate}.")
        positive_candidates = {
            (str(row["candidate_tail"]), str(row["candidate_head"]))
            for row in candidates
            if int(row["label"]) == 1
        }
        if positive_candidates != set(mask.held_out_arcs):
            raise SystemExit(
                "STOP: reconstructed held-out arcs differ from pilot candidates for "
                f"replicate {replicate}."
            )
        prefix = f"replicate_{replicate:03d}"
        write_edges(masks_dir / f"{prefix}_train_edges.csv", mask.observed_arcs)
        write_edges(masks_dir / f"{prefix}_heldout_edges.csv", mask.held_out_arcs)
        with (masks_dir / f"{prefix}_candidates.csv").open(
            "x", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["candidate_tail", "candidate_head", "label"],
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(
                {
                    "candidate_tail": str(row["candidate_tail"]),
                    "candidate_head": str(row["candidate_head"]),
                    "label": int(row["label"]),
                }
                for row in candidates
            )
        exported.append(
            {
                "replicate": replicate,
                "train_arcs": len(mask.observed_arcs),
                "heldout_arcs": len(mask.held_out_arcs),
                "candidate_rows": len(candidates),
                "accounting": {
                    "requested_rate": mask.accounting.requested_rate,
                    "realized_rate": mask.accounting.realized_rate,
                    "masked_count": mask.accounting.masked_count,
                    "observed_count": mask.accounting.observed_count,
                },
            }
        )

    export_manifest = {
        "purpose": "masked_ergm_conditional_scoring_input",
        "source_pilot": str(pilot_dir),
        "input_arcs": str(arcs_path),
        "replicates": exported,
        "r_driver": "r/models/score_masked_ergm.R",
        "assurance": "Held-out positives were checked exactly against recorded pilot "
        "candidate labels.",
    }
    (masks_dir / "mask_export_manifest.json").write_text(
        json.dumps(export_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Static-pilot masks exported.")
    print(f"Replicates: {replicates:,}; source arcs: {len(arcs):,}")
    print(f"Mask directory: {recorded_path(masks_dir)}")


if __name__ == "__main__":
    main()
