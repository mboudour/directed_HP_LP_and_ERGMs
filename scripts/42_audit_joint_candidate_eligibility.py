#!/usr/bin/env python3
"""Audit bounded joint-footprint candidate eligibility before an ERGM fit."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse input/output paths and explicit replacement permission."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def split_identity(split: str) -> tuple[str, int]:
    """Extract the frozen mechanism and replicate number from a split ID."""
    marker = "_replicate_"
    if marker not in split:
        raise ValueError(f"split does not follow '<mechanism>_replicate_<integer>': {split}")
    mechanism, replicate = split.rsplit(marker, maxsplit=1)
    if not mechanism or not replicate.isdigit() or int(replicate) < 1:
        raise ValueError(f"invalid split identity: {split}")
    return mechanism, int(replicate)


def read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    """Read a nonempty UTF-8 CSV and require its core columns."""
    if not path.is_file():
        raise ValueError(f"missing required input: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise ValueError(f"{path} must contain {sorted(required)}")
        return list(reader)


def candidate_rows(
    split: str, footprints: list[dict[str, str]], observed_keys: set[tuple[str, str]]
) -> list[dict[str, object]]:
    """Compute unknown-dyad and reciprocal-observation counts per candidate footprint."""
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in footprints:
        grouped[(row["panel"], row["candidate_id"])].append(row)
    rows: list[dict[str, object]] = []
    mechanism, replicate = split_identity(split)
    for (panel, candidate_id), group in grouped.items():
        labels = {row["label"] for row in group}
        declared_sizes = {row["footprint_size"] for row in group}
        if len(labels) != 1 or len(declared_sizes) != 1:
            raise ValueError(
                f"candidate has inconsistent label or footprint_size: {split}/{candidate_id}"
            )
        try:
            footprint_size = int(next(iter(declared_sizes)))
            label = int(next(iter(labels)))
        except ValueError as error:
            raise ValueError(
                f"candidate has non-integer label or footprint_size: {split}/{candidate_id}"
            ) from error
        if footprint_size != len(group):
            raise ValueError(
                f"candidate footprint size mismatch: {split}/{candidate_id} declares "
                f"{footprint_size} but has {len(group)} rows"
            )
        dyads = {(row["candidate_tail"], row["candidate_head"]) for row in group}
        if len(dyads) != footprint_size:
            raise ValueError(f"candidate has duplicate footprint dyads: {split}/{candidate_id}")
        unknown = sorted(dyads - observed_keys)
        reverse_observed = sum((head, tail) in observed_keys for tail, head in unknown)
        rows.append(
            {
                "split": split,
                "mechanism": mechanism,
                "replicate": replicate,
                "panel": panel,
                "label": label,
                "footprint_size": footprint_size,
                "unknown_dyads": len(unknown),
                "unknown_dyads_with_reverse_observed": reverse_observed,
                "all_unknown_dyads_reverse_observed": bool(unknown)
                and reverse_observed == len(unknown),
            }
        )
    return rows


def prepare_output(path: Path, overwrite: bool) -> None:
    """Avoid mixing a fresh audit with a previous one by accident."""
    if path.exists():
        existing = list(path.iterdir()) if path.is_dir() else [path]
        if existing and not overwrite:
            raise SystemExit(f"STOP: output already exists; pass --overwrite: {path}")
        if path.is_dir():
            for child in existing:
                if child.is_file():
                    child.unlink()
                else:
                    raise SystemExit(f"STOP: output contains an unexpected directory: {child}")
        else:
            path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Produce an aggregate, privacy-preserving eligibility audit for every frozen split."""
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    split_root = input_dir / "splits"
    if not split_root.is_dir():
        raise SystemExit(f"STOP: joint input directory has no splits/ subdirectory: {input_dir}")
    prepare_output(output_dir, args.overwrite)

    all_candidates: list[dict[str, object]] = []
    split_dirs = sorted(path for path in split_root.iterdir() if path.is_dir())
    if not split_dirs:
        raise SystemExit(f"STOP: no split directories in {split_root}")
    for split_dir in split_dirs:
        split = split_dir.name
        footprint_rows = read_csv(
            split_dir / "candidate_footprints.csv",
            {
                "panel",
                "candidate_id",
                "label",
                "footprint_size",
                "candidate_tail",
                "candidate_head",
            },
        )
        edge_rows = read_csv(split_dir / "train_edges.csv", {"from", "to"})
        observed_keys = {(row["from"], row["to"]) for row in edge_rows}
        all_candidates.extend(candidate_rows(split, footprint_rows, observed_keys))

    grouped: Counter[tuple[object, ...]] = Counter()
    for row in all_candidates:
        grouped[
            (
                row["split"],
                row["mechanism"],
                row["replicate"],
                row["panel"],
                row["label"],
                row["unknown_dyads"],
                row["all_unknown_dyads_reverse_observed"],
            )
        ] += 1
    detail_path = output_dir / "candidate_eligibility_counts.csv"
    with detail_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "split",
                "mechanism",
                "replicate",
                "panel",
                "label",
                "unknown_dyads",
                "all_unknown_dyads_reverse_observed",
                "candidates",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for key, count in sorted(grouped.items()):
            writer.writerow(
                {
                    "split": key[0],
                    "mechanism": key[1],
                    "replicate": key[2],
                    "panel": key[3],
                    "label": key[4],
                    "unknown_dyads": key[5],
                    "all_unknown_dyads_reverse_observed": key[6],
                    "candidates": count,
                }
            )

    split_summary: list[dict[str, object]] = []
    for split in sorted({str(row["split"]) for row in all_candidates}):
        rows = [row for row in all_candidates if row["split"] == split]
        mechanism, replicate = split_identity(split)
        exact_two = [row for row in rows if row["unknown_dyads"] == 2]
        strict_two = [row for row in exact_two if row["all_unknown_dyads_reverse_observed"]]
        split_summary.append(
            {
                "split": split,
                "mechanism": mechanism,
                "replicate": replicate,
                "candidates_total": len(rows),
                "candidates_exactly_two_unknown_dyads": len(exact_two),
                "candidates_exactly_two_unknown_dyads_all_reverse_observed": len(strict_two),
            }
        )
    summary_path = output_dir / "split_selection_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(split_summary[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(split_summary)

    total_exact_two = sum(row["candidates_exactly_two_unknown_dyads"] for row in split_summary)
    total_strict_two = sum(
        row["candidates_exactly_two_unknown_dyads_all_reverse_observed"] for row in split_summary
    )
    report = output_dir / "summary.md"
    report.write_text(
        "\n".join(
            [
                "# Joint-footprint candidate eligibility audit",
                "",
                f"- Dataset/input bundle: `{args.dataset_id}`",
                f"- Frozen splits audited: `{len(split_summary)}`",
                f"- Candidate footprints audited: `{len(all_candidates)}`",
                f"- Candidates with exactly two unknown footprint dyads: `{total_exact_two}`",
                "- Of those, candidates with every unknown dyad's reverse arc observed: "
                f"`{total_strict_two}`",
                "",
                "The strict condition is used only for the reciprocal two-dyad factorization "
                "smoke design. The M2 feasibility gate may use the exact-two rule without that "
                "additional reciprocal filter when the strict count is zero. This audit contains "
                "aggregate counts only; it does not disclose selected participant identities.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "dataset_id": args.dataset_id,
        "input_dir": str(input_dir),
        "splits_audited": len(split_summary),
        "candidate_footprints_audited": len(all_candidates),
        "strict_selection_rule": {
            "unknown_dyads": 2,
            "all_unknown_dyads_reverse_observed": True,
        },
        "exact_two_rule": {"unknown_dyads": 2},
        "output_files": {
            "summary": "summary.md",
            "split_selection_summary": "split_selection_summary.csv",
            "eligibility_counts": "candidate_eligibility_counts.csv",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Joint-footprint candidate eligibility audit passed.")
    print(f"Dataset/input bundle: {args.dataset_id}.")
    print(f"Frozen splits audited: {len(split_summary)}.")
    print(f"Candidate footprints audited: {len(all_candidates):,}.")
    print(f"Exactly two unknown dyads: {total_exact_two:,}.")
    print(f"Exactly two unknown dyads with all reverse arcs observed: {total_strict_two:,}.")
    print(f"Output bundle: {output_dir.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
