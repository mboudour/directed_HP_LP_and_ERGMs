#!/usr/bin/env python3
"""Evaluate tail/head role assignment for held-out native event types."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, stdev
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT37 = PROJECT_ROOT / "scripts" / "37_run_native_event_heuristics.py"
spec = importlib.util.spec_from_file_location("native_heuristics", SCRIPT37)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load shared native-event utilities")
shared = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = shared
spec.loader.exec_module(shared)


def parse_args() -> argparse.Namespace:
    """Parse a fixed frozen-mask role-assignment evaluation contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def candidate_partitions(
    target: Any,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    """Enumerate every role partition of a known event node set at fixed arities."""
    nodes = tuple(sorted(set(target.tail + target.head)))
    if len(nodes) != len(target.tail) + len(target.head):
        raise ValueError("role-assignment target has overlapping roles")
    return tuple(
        (tuple(sorted(tail)), tuple(node for node in nodes if node not in tail))
        for tail in combinations(nodes, len(target.tail))
    )


def row_scores(target: Any, arcs: frozenset[tuple[str, str]]) -> list[dict[str, object]]:
    """Score every fixed-arity partition using only split-observed arcs."""
    candidates = tuple(
        shared.candidate_from_roles(
            f"{target.candidate_id}_partition_{index:03d}",
            tail,
            head,
            int((tail, head) == target.key),
        )
        for index, (tail, head) in enumerate(candidate_partitions(target), start=1)
    )
    rows = shared.candidate_rows(candidates, arcs)
    for row in rows:
        row["event_type_id"] = target.candidate_id
        row["correct_partition"] = int(row["label"])
        row["partition_count"] = len(rows)
    return rows


def expected_rank_metrics(scores: list[float], correct_index: int) -> tuple[float, float]:
    """Return tie-aware expected top-one accuracy and reciprocal rank."""
    correct = scores[correct_index]
    above = sum(score > correct for score in scores)
    tied = sum(score == correct for score in scores)
    top1 = 1.0 / tied if above == 0 else 0.0
    reciprocal_rank = mean(1.0 / rank for rank in range(above + 1, above + tied + 1))
    return top1, reciprocal_rank


def evaluate_event(target: Any, arcs: frozenset[tuple[str, str]]) -> list[dict[str, object]]:
    """Compute tie-aware role-assignment metrics for one target and every score."""
    rows = row_scores(target, arcs)
    correct_index = next(index for index, row in enumerate(rows) if int(row["label"]) == 1)
    output: list[dict[str, object]] = []
    score_columns = [
        column
        for column in rows[0]
        if column.startswith("lifted_") or column == "already_observed_footprint"
    ]
    reversal_index: int | None = None
    reversed_key = (target.head, target.tail)
    for index, row in enumerate(rows):
        if (
            tuple(json.loads(str(row["tail_nodes_json"]))) == reversed_key[0]
            and tuple(json.loads(str(row["head_nodes_json"]))) == reversed_key[1]
        ):
            reversal_index = index
    for score in score_columns:
        values = [float(row[score]) for row in rows]
        top1, reciprocal_rank = expected_rank_metrics(values, correct_index)
        output.extend(
            {
                "event_type_id": target.candidate_id,
                "tail_arity": len(target.tail),
                "head_arity": len(target.head),
                "participants": len(target.tail) + len(target.head),
                "partition_count": len(rows),
                "score": score,
                "metric": metric,
                "value": value,
            }
            for metric, value in (("top1_accuracy", top1), ("mrr", reciprocal_rank))
        )
        if reversal_index is not None:
            output.append(
                {
                    "event_type_id": target.candidate_id,
                    "tail_arity": len(target.tail),
                    "head_arity": len(target.head),
                    "participants": len(target.tail) + len(target.head),
                    "partition_count": len(rows),
                    "score": score,
                    "metric": "correct_score_exceeds_reversal",
                    "value": float(values[correct_index] > values[reversal_index]),
                }
            )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty deterministic CSV table."""
    if not rows:
        raise RuntimeError(f"cannot write empty role-assignment table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate event-level role metrics by split mechanism and arity."""
    groups: dict[tuple[str, int, int, str, str], list[float]] = defaultdict(list)
    for row in rows:
        key = (
            str(row["mechanism"]),
            int(row["tail_arity"]),
            int(row["head_arity"]),
            str(row["score"]),
            str(row["metric"]),
        )
        groups[key].append(float(row["value"]))
    return [
        {
            "mechanism": mechanism,
            "tail_arity": tail_arity,
            "head_arity": head_arity,
            "score": score,
            "metric": metric,
            "event_evaluations": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, tail_arity, head_arity, score, metric), values in sorted(groups.items())
    ]


def main() -> None:
    """Evaluate every held-out event type in all completed frozen mask splits."""
    args = parse_args()
    mask_dir = shared.resolve_path(args.mask_dir)
    nodes_path = shared.resolve_path(args.nodes)
    output = shared.resolve_path(args.output_dir)
    shared.prepare_output_dir(output, args.overwrite)
    nodes = shared.read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    all_rows: list[dict[str, object]] = []
    coverage: list[dict[str, object]] = []
    for split_dir in shared.split_directories(mask_dir):
        mechanism, replicate = shared.split_identity(split_dir)
        heldout = shared.read_type_table(split_dir / "heldout_event_types.csv", label=1)
        arcs = shared.read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        split_rows: list[dict[str, object]] = []
        for target in heldout:
            for row in evaluate_event(target, arcs):
                row.update({"mechanism": mechanism, "replicate": replicate})
                split_rows.append(row)
        split_output = output / split_dir.name
        split_output.mkdir()
        write_csv(split_output / "event_role_metrics.csv", split_rows)
        coverage.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "heldout_event_types": len(heldout),
                "event_role_evaluations": len({row["event_type_id"] for row in split_rows}),
                "mean_partition_count": mean(int(row["partition_count"]) for row in split_rows),
            }
        )
        all_rows.extend(split_rows)
    summary = summarize(all_rows)
    write_csv(output / "split_summary.csv", coverage)
    write_csv(output / "metric_summary_by_arity.csv", summary)
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/49_evaluate_native_event_role_assignment.py",
                "dataset_id": args.dataset_id,
                "target": "role_partition_of_heldout_native_event_node_set",
                "candidate_rule": "all fixed-arity tail/head partitions of the known event node set",
                "scores": "same split-observed lifted directed LP scores as native-event ranking",
                "ties": "expected top-1 and reciprocal rank under uniform tie breaking",
                "source_masks": shared.recorded_path(mask_dir),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Native-event role-assignment evaluation",
        "",
        f"- Dataset: `{args.dataset_id}`",
        "- Target: assign the known participants of each held-out event to its fixed tail/head arities.",
        "- Candidate set: every compatible partition; no random case-control prevalence is implied.",
        "- Metrics use uniform tie-breaking expectations and are reported overall through arity rows.",
        "",
        "## Split coverage",
        "",
        "| Mechanism | Replicate | Held-out types | Evaluated types | Mean partitions |",
        "|---|---:|---:|---:|---:|",
    ]
    lines.extend(
        "| {mechanism} | {replicate} | {heldout_event_types} | {event_role_evaluations} | {mean_partition_count:.2f} |".format(
            **row
        )
        for row in coverage
    )
    lines.extend(
        ["", "Full results by tail/head arity and score are in `metric_summary_by_arity.csv`.", ""]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Native-event role-assignment evaluation passed.")
    print(f"Dataset: {args.dataset_id}; splits: {len(coverage)}.")
    print(f"Output bundle: {shared.recorded_path(output)}")


if __name__ == "__main__":
    main()
