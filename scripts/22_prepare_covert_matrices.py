#!/usr/bin/env python3
"""Audit covert matrices and build directed inputs only under an approved scope."""

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
    """Locations and scientific scope for one auditable matrix collection."""

    dataset_id: str
    scope: str
    matrix_paths: tuple[Path, ...]
    gate_record: Path
    output_dir: Path
    summary: Path
    report: Path
    expected_matrices: int
    phase_based: bool
    permitted_directed_build: bool
    directed_scope_token: str | None


def dataset_spec(dataset_id: str, scope: str) -> DatasetSpec:
    """Return the fixed local layout for an audited dataset/scope combination."""
    if dataset_id == "caviar":
        matrix_dir = PROJECT_ROOT / "data" / "raw" / "caviar" / "csv_matrices"
        common = {
            "dataset_id": "caviar",
            "gate_record": PROJECT_ROOT / "data" / "metadata" / "gates" / "caviar_direction.json",
            "output_dir": PROJECT_ROOT / "data" / "processed" / "caviar",
        }
        if scope == "all_matrices":
            return DatasetSpec(
                scope=scope,
                matrix_paths=tuple(sorted(matrix_dir.glob("CAVIAR*.csv"))),
                summary=PROJECT_ROOT / "data" / "metadata" / "caviar_matrix_preparation.json",
                report=PROJECT_ROOT / "docs" / "data_audits" / "caviar_matrix_preparation.md",
                expected_matrices=12,
                phase_based=True,
                permitted_directed_build=False,
                directed_scope_token=None,
                **common,
            )
        if scope == "full_static":
            return DatasetSpec(
                scope=scope,
                matrix_paths=(matrix_dir / "CAVIAR_FULL.csv",),
                summary=PROJECT_ROOT / "data" / "metadata" / "caviar_full_static_preparation.json",
                report=PROJECT_ROOT / "docs" / "data_audits" / "caviar_full_static_preparation.md",
                expected_matrices=1,
                phase_based=False,
                permitted_directed_build=True,
                directed_scope_token="caviar_full_static",
                **common,
            )
        raise ValueError(f"unsupported CAVIAR scope: {scope}")
    if dataset_id == "ciel":
        if scope != "static":
            raise ValueError("Ciel supports only the static scope")
        matrix = PROJECT_ROOT / "data" / "raw" / "ciel" / "csv_matrix" / "CSV" / "CIELNET.csv"
        return DatasetSpec(
            dataset_id="ciel",
            scope=scope,
            matrix_paths=(matrix,),
            gate_record=PROJECT_ROOT / "data" / "metadata" / "gates" / "ciel_direction.json",
            output_dir=PROJECT_ROOT / "data" / "processed" / "ciel",
            summary=PROJECT_ROOT / "data" / "metadata" / "ciel_matrix_preparation.json",
            report=PROJECT_ROOT / "docs" / "data_audits" / "ciel_matrix_preparation.md",
            expected_matrices=1,
            phase_based=False,
            permitted_directed_build=True,
            directed_scope_token="ciel_static",
        )
    raise ValueError(f"unsupported dataset: {dataset_id}")


def direction_approved(path: Path, scope_token: str | None) -> bool:
    """Read an explicit evidence-backed direction approval for the requested scope."""
    if scope_token is None or not path.is_file():
        return False
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON gate record: {path}") from error
    approved_scopes = record.get("approved_scopes", [])
    return (
        record.get("approved") is True
        and record.get("row_direction") == "caller_to_receiver"
        and scope_token in approved_scopes
    )


def read_matrix(path: Path) -> tuple[list[str], list[list[float]], int]:
    """Read a UCINET CSV export with labels in the first row and column."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    if len(rows) < 2:
        raise ValueError(f"matrix has fewer than two rows: {path}")
    labels = [value.strip() for value in rows[0][1:]]
    if not labels or any(not label for label in labels):
        raise ValueError(f"matrix has missing column labels: {path}")
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


def prepare_outputs(outputs: list[Path]) -> None:
    """Avoid silently mixing a new directed build with a previous build."""
    existing = [path for path in outputs if path.exists()]
    if existing:
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in existing)
        raise SystemExit(
            "STOP: matrix-preparation output already exists. This script will not overwrite it:\n"
            f"  {rendered}"
        )


def write_nodes(path: Path, labels: list[str]) -> None:
    """Write the exact, unique static node universe used by the directed build."""
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"id": label} for label in labels)


def main() -> None:
    """Audit matrices and conditionally materialize a direction-approved static graph."""
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", choices=("caviar", "ciel"))
    parser.add_argument(
        "--scope",
        help="CAVIAR: all_matrices or full_static; Ciel: static. Defaults to the complete audit.",
    )
    parser.add_argument(
        "--build-directed",
        action="store_true",
        help="Build oriented arcs only after a valid scope-specific direction gate exists.",
    )
    args = parser.parse_args()
    default_scope = "all_matrices" if args.dataset == "caviar" else "static"
    spec = dataset_spec(args.dataset, args.scope or default_scope)

    if len(spec.matrix_paths) != spec.expected_matrices or not all(
        path.is_file() for path in spec.matrix_paths
    ):
        rendered = "\n  ".join(str(path.relative_to(PROJECT_ROOT)) for path in spec.matrix_paths)
        raise SystemExit(
            "STOP: expected covert-network CSV matrices are missing or incomplete.\n"
            f"Found {len(spec.matrix_paths):,}; expected {spec.expected_matrices:,}.\n"
            f"  {rendered}"
        )
    approved = direction_approved(spec.gate_record, spec.directed_scope_token)
    if args.build_directed and not spec.permitted_directed_build:
        raise SystemExit(
            "STOP: this scope is audit-only because it contains the unresolved CAVIAR phase "
            "series. "
            "Use CAVIAR --scope=full_static for the approved static full-network build."
        )
    if args.build_directed and not approved:
        raise SystemExit(
            "STOP: directed build is blocked pending an explicit scope-specific direction gate.\n"
            f"Required gate record: {spec.gate_record.relative_to(PROJECT_ROOT)}\n"
            'It must contain approved=true, row_direction="caller_to_receiver", and the '
            "required scope token."
        )

    directed_output = spec.output_dir / "directed_valued_arcs.parquet"
    nodes_output = spec.output_dir / "nodes.csv"
    outputs = [spec.summary, spec.report]
    if args.build_directed:
        outputs.extend([directed_output, nodes_output])
    prepare_outputs(outputs)

    matrix_rows: list[dict[str, object]] = []
    total_positive_cells = 0
    total_nonzero_weight = 0.0
    matrix_summaries: list[dict[str, object]] = []
    build_labels: list[str] | None = None

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
                        matrix_rows.append(
                            {
                                "matrix_id": path.stem,
                                "tail": tail,
                                "head": head,
                                "communication_count": value,
                            }
                        )
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
        build_labels = labels

    if spec.phase_based:
        phases = sorted(item["phase"] for item in matrix_summaries if item["phase"] is not None)
        if phases != list(range(1, 12)):
            raise SystemExit(f"STOP: CAVIAR phases are not exactly 1–11: {phases}")
    labels_unique = all(item["duplicate_label_occurrences"] == 0 for item in matrix_summaries)
    if args.build_directed and not labels_unique:
        raise SystemExit(
            "STOP: directed build is blocked because at least one source matrix has duplicate "
            "actor labels."
        )

    spec.summary.parent.mkdir(parents=True, exist_ok=True)
    spec.report.parent.mkdir(parents=True, exist_ok=True)
    analysis_status = (
        "eligible_static_full_directed_processing"
        if args.build_directed and approved and labels_unique
        else "audit_only_phase_series_contains_label_integrity_failure"
        if spec.dataset_id == "caviar" and spec.scope == "all_matrices" and not labels_unique
        else "eligible_for_directed_processing"
        if approved and labels_unique
        else "blocked_pending_direction_audit"
    )
    summary = {
        "dataset_id": spec.dataset_id,
        "scope": spec.scope,
        "matrix_files_read": len(spec.matrix_paths),
        "direction_gate_approved": approved,
        "directed_output_built": args.build_directed,
        "matrix_summaries": matrix_summaries,
        "matrix_label_integrity_passed": labels_unique,
        "positive_off_diagonal_cells_total": total_positive_cells,
        "positive_tie_weight_total": total_nonzero_weight,
        "dichotomization_rule": "value_greater_than_zero",
        "analysis_status": analysis_status,
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
    scope_note = (
        "This full-network static build excludes the phase series because the CAVIAR7 source "
        "matrix duplicates actor label `9`."
        if spec.dataset_id == "caviar" and spec.scope == "full_static"
        else "The phase series is retained for audit only; it has no directed derived output."
        if spec.dataset_id == "caviar" and spec.scope == "all_matrices"
        else ""
    )
    spec.report.write_text(
        f"""# {spec.dataset_id.upper()} matrix-preparation audit

## Direction gate

Status: **{status}**.

Rows are treated as callers/senders and columns as receivers only under the recorded,
scope-specific approval. Duplicate actor labels are an integrity failure and are never
merged.

## Scope

`{spec.scope}`. {scope_note}

## Matrix integrity

| Matrix | Nodes | Positive off-diagonal cells | Nonzero diagonal cells | Duplicate labels |
|---|---:|---:|---:|---:|
{table}

Values greater than zero define the documented binary sensitivity graph; original values
are retained for the planned valued-ERGM sensitivity analysis. This script does not infer
unverified orientation or manufacture native events.
""",
        encoding="utf-8",
    )

    if args.build_directed:
        if build_labels is None:
            raise RuntimeError("directed build has no matrix labels")
        spec.output_dir.mkdir(parents=True, exist_ok=True)
        schema = pa.schema(
            [
                pa.field("matrix_id", pa.string()),
                pa.field("tail", pa.string()),
                pa.field("head", pa.string()),
                pa.field("communication_count", pa.float64()),
            ]
        )
        pq.write_table(
            pa.Table.from_pylist(matrix_rows, schema=schema), directed_output, compression="zstd"
        )
        write_nodes(nodes_output, build_labels)

    print(f"{spec.dataset_id} matrix preparation passed.")
    print(f"Scope: {spec.scope}.")
    print(f"Matrices read: {len(spec.matrix_paths):,}.")
    print(f"Direction gate approved: {approved}.")
    print(f"Directed output built: {args.build_directed}.")
    print(f"Summary: {spec.summary.relative_to(PROJECT_ROOT)}")
    print(f"Audit report: {spec.report.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
