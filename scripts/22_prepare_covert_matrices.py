#!/usr/bin/env python3
"""Audit CAVIAR or Ciel matrices and build directed inputs only after approval."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DatasetSpec:
    """Locations and scope for one audited covert-network source."""

    dataset_id: str
    matrix_paths: tuple[Path, ...]
    gate_record: Path
    output_dir: Path
    summary: Path
    report: Path
    expected_matrices: int
    phase_based: bool


def dataset_spec(dataset_id: str) -> DatasetSpec:
    """Return the fixed local layout for one supported covert dataset."""
    if dataset_id == "caviar":
        matrix_dir = PROJECT_ROOT / "data" / "raw" / "caviar" / "csv_matrices"
        return DatasetSpec(
            dataset_id="caviar",
            matrix_paths=tuple(sorted(matrix_dir.glob("CAVIAR*.csv"))),
            gate_record=PROJECT_ROOT / "data" / "metadata" / "gates" / "caviar_direction.json",
            output_dir=PROJECT_ROOT / "data" / "processed" / "caviar",
            summary=PROJECT_ROOT / "data" / "metadata" / "caviar_matrix_preparation.json",
            report=PROJECT_ROOT / "docs" / "data_audits" / "caviar_matrix_preparation.md",
            expected_matrices=12,
            phase_based=True,
        )
    if dataset_id == "ciel":
        matrix = PROJECT_ROOT / "data" / "raw" / "ciel" / "csv_matrix" / "CSV" / "CIELNET.csv"
        return DatasetSpec(
            dataset_id="ciel",
            matrix_paths=(matrix,),
            gate_record=PROJECT_ROOT / "data" / "metadata" / "gates" / "ciel_direction.json",
            output_dir=PROJECT_ROOT / "data" / "processed" / "ciel",
            summary=PROJECT_ROOT / "data" / "metadata" / "ciel_matrix_preparation.json",
            report=PROJECT_ROOT / "docs" / "data_audits" / "ciel_matrix_preparation.md",
            expected_matrices=1,
            phase_based=False,
        )
    raise ValueError(f"unsupported dataset: {dataset_id}")


def direction_approved(path: Path) -> bool:
    """Read the explicit local approval record without inferring semantics."""
    if not path.is_file():
        return False
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON gate record: {path}") from error
    return record.get("approved") is True and record.get("row_direction") == "caller_to_receiver"


def read_matrix(path: Path) -> tuple[list[str], list[list[float]], int]:
    """Read the UCINET CSV export format with labels in the first row and column."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 2:
        raise ValueError(f"matrix has fewer than two rows: {path}")

    labels = [value.strip() for value in rows[0][1:]]
    if not labels:
        raise ValueError(f"matrix has no column labels: {path}")
    duplicate_label_occurrences = sum(count - 1 for count in Counter(labels).values() if count > 1)
    if len(rows) - 1 != len(labels):
        raise ValueError(f"matrix is not square: {path}")

    values: list[list[float]] = []
    row_labels: list[str] = []
    for row in rows[1:]:
        if len(row) != len(labels) + 1:
            raise ValueError(f"matrix row width differs from header: {path}")
        row_labels.append(row[0].strip())
        try:
            values.append([float(value) for value in row[1:]])
        except ValueError as error:
            raise ValueError(f"matrix contains a non-numeric tie value: {path}") from error

    if row_labels != labels:
        raise ValueError(f"matrix row and column labels do not agree: {path}")
    return labels, values, duplicate_label_occurrences


def phase_number(path: Path) -> int | None:
    """Extract a CAVIAR phase number from the documented filename convention."""
    stem = path.stem.casefold()
    if stem == "caviar_full":
        return None
    suffix = stem.removeprefix("caviar")
    return int(suffix) if suffix.isdigit() else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=("caviar", "ciel"))
    parser.add_argument(
        "--build-directed",
        action="store_true",
        help="Build oriented arcs only after a valid caller-to-receiver gate record exists.",
    )
    args = parser.parse_args()

    spec = dataset_spec(args.dataset)
    if len(spec.matrix_paths) != spec.expected_matrices or not all(
        path.is_file() for path in spec.matrix_paths
    ):
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in spec.matrix_paths)
        raise SystemExit(
            "STOP: expected covert-network CSV matrices are missing or incomplete.\n"
            f"Found {len(spec.matrix_paths):,}; expected {spec.expected_matrices:,}.\n"
            f"  {rendered}"
        )

    approved = direction_approved(spec.gate_record)
    if args.build_directed and not approved:
        raise SystemExit(
            "STOP: directed build is blocked pending an explicit authoritative direction audit.\n"
            f"Required gate record: {spec.gate_record.relative_to(PROJECT_ROOT)}\n"
            'It must contain {"approved": true, "row_direction": "caller_to_receiver", ...}.'
        )

    directed_output = spec.output_dir / "directed_valued_arcs.parquet"
    outputs = [spec.summary, spec.report]
    if args.build_directed:
        outputs.append(directed_output)
    existing = [path for path in outputs if path.exists()]
    if existing:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing)
        raise SystemExit(
            "STOP: matrix-preparation output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )

    matrix_rows: list[dict[str, object]] = []
    total_positive_cells = 0
    total_nonzero_weight = 0.0
    matrix_summaries: list[dict[str, object]] = []

    for path in spec.matrix_paths:
        labels, values, duplicate_label_occurrences = read_matrix(path)
        nonzero = 0
        loops = 0
        weight_sum = 0.0
        current_phase = phase_number(path) if spec.phase_based else None

        for row_index, tail in enumerate(labels):
            for column_index, head in enumerate(labels):
                value = values[row_index][column_index]
                if value < 0:
                    raise SystemExit(f"STOP: negative tie value in {path}")
                if row_index == column_index and value != 0:
                    loops += 1
                if value > 0 and row_index != column_index:
                    nonzero += 1
                    weight_sum += value
                    if args.build_directed:
                        row: dict[str, object] = {
                            "matrix_id": path.stem,
                            "tail": tail,
                            "head": head,
                            "communication_count": value,
                        }
                        if current_phase is not None:
                            row["phase"] = current_phase
                        matrix_rows.append(row)

        total_positive_cells += nonzero
        total_nonzero_weight += weight_sum
        matrix_summaries.append(
            {
                "matrix_id": path.stem,
                "nodes": len(labels),
                "positive_off_diagonal_cells": nonzero,
                "positive_tie_weight_sum": weight_sum,
                "nonzero_diagonal_cells": loops,
                "duplicate_label_occurrences": duplicate_label_occurrences,
                "phase": current_phase,
            }
        )

    if spec.phase_based:
        phases = sorted(item["phase"] for item in matrix_summaries if item["phase"] is not None)
        if phases != list(range(1, 12)):
            raise SystemExit(f"STOP: CAVIAR phases are not exactly 1–11: {phases}")

    labels_unique = all(item["duplicate_label_occurrences"] == 0 for item in matrix_summaries)
    if args.build_directed and not labels_unique:
        raise SystemExit(
            "STOP: directed build is blocked because at least one source matrix has "
            "duplicate actor labels. Run the audit-only command and resolve the source "
            "label-integrity issue before constructing directed arcs."
        )

    spec.summary.parent.mkdir(parents=True, exist_ok=True)
    spec.report.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "dataset_id": spec.dataset_id,
        "matrix_files_read": len(spec.matrix_paths),
        "direction_gate_approved": approved,
        "directed_output_built": args.build_directed,
        "matrix_summaries": matrix_summaries,
        "matrix_label_integrity_passed": labels_unique,
        "positive_off_diagonal_cells_total": total_positive_cells,
        "positive_tie_weight_total": total_nonzero_weight,
        "dichotomization_rule": "value_greater_than_zero",
        "analysis_status": (
            "blocked_pending_label_integrity"
            if not labels_unique
            else "eligible_for_directed_processing"
            if approved
            else "blocked_pending_direction_audit"
        ),
    }
    spec.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    table = "\n".join(
        f"| `{item['matrix_id']}` | {item['nodes']:,} | "
        f"{item['positive_off_diagonal_cells']:,} | {item['nonzero_diagonal_cells']:,} | "
        f"{item['duplicate_label_occurrences']:,} |"
        for item in matrix_summaries
    )
    status = (
        "approved" if approved and labels_unique else "pending; no directed output has been created"
    )
    spec.report.write_text(
        f"""# {spec.dataset_id.upper()} matrix-preparation audit

## Direction gate

Status: **{status}**.

The source matrices are directed and valued, but row-to-column semantics are not inferred
from matrix shape. The local approval record must document authoritative evidence that rows
mean caller/sender and columns mean receiver before a directed analysis is eligible.
Duplicate actor labels are also an integrity failure: they are reported, never merged.

## Matrix integrity

| Matrix | Nodes | Positive off-diagonal cells | Nonzero diagonal cells | Duplicate labels |
|---|---:|---:|---:|---:|
{table}

Values greater than zero define the documented binary sensitivity graph; original values are
retained for the planned valued-ERGM supplement. This script does not fit an ERGM or use an
unverified orientation in prediction.
""",
        encoding="utf-8",
    )

    if args.build_directed:
        spec.output_dir.mkdir(parents=True, exist_ok=True)
        fields = [
            pa.field("matrix_id", pa.string()),
            pa.field("phase", pa.int16()),
            pa.field("tail", pa.string()),
            pa.field("head", pa.string()),
            pa.field("communication_count", pa.float64()),
        ]
        schema = pa.schema(fields)
        normalized_rows = [
            {"phase": None, **row} if "phase" not in row else row for row in matrix_rows
        ]
        pq.write_table(
            pa.Table.from_pylist(normalized_rows, schema=schema),
            directed_output,
            compression="zstd",
        )

    print(f"{spec.dataset_id} matrix preparation passed.")
    print(f"Matrices read: {len(spec.matrix_paths):,}.")
    print(f"Direction gate approved: {approved}.")
    print(f"Directed output built: {args.build_directed}.")
    print(f"Summary: {spec.summary.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {spec.report.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
