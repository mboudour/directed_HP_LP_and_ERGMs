#!/usr/bin/env python3
"""Score directed hard negatives for the event-first native-event-type target.

Two separately reported hard panels are created from each frozen event-first
split. The *reversal_orientation* panel contrasts a held-out event type with
its role reversal. The *role_exchange* panel contrasts it with a same-arity
candidate formed by exchanging one tail-role actor and one head-role actor.

A hard negative is retained only if it is not any observed or held-out native
event type, lies in the observed split's weak two-hop candidate universe, and
is unique within its panel. Positives with no valid partner are recorded as
out of panel rather than silently assigned an easier random negative.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, product
from pathlib import Path
from random import Random
from statistics import mean, stdev
from typing import Any

from directed_hp.evaluation.metrics import pr_auc, roc_auc
from directed_hp.lp.directed_scores import DirectedScoreEngine

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Candidate:
    """A canonical directed native-event candidate for a hard evaluation panel."""

    candidate_id: str
    tail: tuple[str, ...]
    head: tuple[str, ...]
    label: int
    source_event_type_id: str | None

    @property
    def key(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return the candidate identity that determines event-type equality."""
        return self.tail, self.head

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return the simple directed graph footprint of this candidate."""
        return frozenset(product(self.tail, self.head))


def parse_args() -> argparse.Namespace:
    """Parse the explicit frozen-mask hard-panel benchmark contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.max_weak_distance < 1:
        parser.error("--max-weak-distance must be at least 1.")
    if isinstance(args.seed, bool):
        parser.error("--seed must be an integer.")
    return args


def resolve_path(path: Path) -> Path:
    """Resolve a project-relative command argument at the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render a repository-relative path when the input lies in this project."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path, description: str) -> None:
    """Fail before output creation when a required frozen-mask input is absent."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read the fixed actor universe and reject empty or duplicate labels."""
    require_file(path, "node table")
    nodes: dict[str, None] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks declared column {column!r}: {path}")
        for row in reader:
            node = row[column].strip()
            if not node:
                raise SystemExit("STOP: node table contains an empty actor ID.")
            if node in nodes:
                raise SystemExit(f"STOP: node table contains duplicate actor ID {node!r}.")
            nodes[node] = None
    if not nodes:
        raise SystemExit("STOP: node table contains no actor IDs.")
    return tuple(nodes)


def parse_role_json(value: str, field: str) -> tuple[str, ...]:
    """Decode one canonical nonempty, duplicate-free stored role list."""
    try:
        raw = json.loads(value)
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: invalid {field} JSON in event mask: {value!r}") from error
    if not isinstance(raw, list) or not raw:
        raise SystemExit(f"STOP: {field} must be a nonempty JSON list in event mask.")
    values = tuple(str(item).strip() for item in raw)
    if any(not item for item in values) or len(set(values)) != len(values):
        raise SystemExit(f"STOP: {field} contains an empty or duplicate actor ID.")
    return tuple(sorted(values))


def read_type_table(path: Path, label: int) -> tuple[Candidate, ...]:
    """Load an observed or held-out native event-type table from a frozen split."""
    require_file(path, "event-type table")
    required = {"event_type_id", "tail_nodes_json", "head_nodes_json"}
    seen_ids: set[str] = set()
    seen_keys: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    result: list[Candidate] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(f"STOP: event-type table lacks required columns: {path}")
        for row in reader:
            event_type_id = row["event_type_id"].strip()
            candidate = Candidate(
                candidate_id=event_type_id,
                tail=parse_role_json(row["tail_nodes_json"], "tail_nodes_json"),
                head=parse_role_json(row["head_nodes_json"], "head_nodes_json"),
                label=label,
                source_event_type_id=event_type_id,
            )
            if set(candidate.tail).intersection(candidate.head):
                raise SystemExit("STOP: event-type table contains overlapping tail/head roles.")
            if not event_type_id or event_type_id in seen_ids or candidate.key in seen_keys:
                raise SystemExit("STOP: event-type table contains duplicate or empty identities.")
            seen_ids.add(event_type_id)
            seen_keys.add(candidate.key)
            result.append(candidate)
    if not result:
        raise SystemExit(f"STOP: event-type table is empty: {path}")
    return tuple(result)


def read_observed_arcs(path: Path, node_set: set[str]) -> frozenset[tuple[str, str]]:
    """Read the split-specific observed projection, forbidding loops and unknown actors."""
    require_file(path, "observed arc table")
    arcs: set[tuple[str, str]] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or {"tail", "head"} - set(reader.fieldnames):
            raise SystemExit(f"STOP: observed arc table requires tail/head columns: {path}")
        for row in reader:
            tail = row["tail"].strip()
            head = row["head"].strip()
            if not tail or not head or tail == head:
                raise SystemExit("STOP: observed arc table contains an invalid endpoint.")
            if tail not in node_set or head not in node_set:
                raise SystemExit(
                    "STOP: observed arc table references an actor outside node universe."
                )
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit(f"STOP: observed arc table is empty: {path}")
    return frozenset(arcs)


def split_directories(mask_dir: Path) -> tuple[Path, ...]:
    """Locate only complete event-first split directories."""
    required = {"observed_event_types.csv", "heldout_event_types.csv", "observed_arcs.csv"}
    paths = tuple(
        path
        for path in sorted(mask_dir.iterdir())
        if path.is_dir() and required <= {child.name for child in path.iterdir()}
    )
    if not paths:
        raise SystemExit(f"STOP: no complete event-first splits found in {mask_dir}")
    return paths


def split_identity(path: Path) -> tuple[str, int]:
    """Parse the mechanism and replicate encoded by the frozen split name."""
    parts = path.name.rsplit("_replicate_", maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        raise SystemExit(f"STOP: invalid event-first split directory name: {path.name}")
    return parts[0], int(parts[1])


def weak_reachability(
    nodes: tuple[str, ...], arcs: frozenset[tuple[str, str]], distance: int
) -> dict[str, frozenset[str]]:
    """Compute weak, split-specific neighborhoods up to the declared path length."""
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for tail, head in arcs:
        adjacency[tail].add(head)
        adjacency[head].add(tail)
    result: dict[str, frozenset[str]] = {}
    for source in nodes:
        visited = {source}
        frontier = {source}
        for _ in range(distance):
            expanded: set[str] = set()
            for node in frontier:
                expanded.update(adjacency[node])
            frontier = expanded - visited
            visited.update(frontier)
        result[source] = frozenset(visited)
    return result


def is_local(candidate: Candidate, reachable: dict[str, frozenset[str]]) -> bool:
    """Require every cross-role and same-role participant pair to be weakly nearby."""
    participants = candidate.tail + candidate.head
    return all(right in reachable[left] for left, right in combinations(participants, 2))


def make_candidate(
    candidate_id: str, tail: tuple[str, ...], head: tuple[str, ...], label: int, source: str | None
) -> Candidate:
    """Create a canonical role-disjoint candidate after a structural transformation."""
    candidate = Candidate(
        candidate_id=candidate_id,
        tail=tuple(sorted(tail)),
        head=tuple(sorted(head)),
        label=label,
        source_event_type_id=source,
    )
    if not candidate.tail or not candidate.head or set(candidate.tail).intersection(candidate.head):
        raise ValueError("hard-panel candidates need nonempty disjoint tail/head roles")
    return candidate


def reversal_pairs(
    positives: tuple[Candidate, ...],
    full_type_keys: set[tuple[tuple[str, ...], tuple[str, ...]],],
    reachable: dict[str, frozenset[str]],
) -> tuple[tuple[Candidate, Candidate], ...]:
    """Pair a positive with its unseen role reversal whenever that is a valid negative."""
    pairs: list[tuple[Candidate, Candidate]] = []
    used_negatives: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for positive in positives:
        negative = make_candidate(
            f"reversal_of_{positive.candidate_id}",
            positive.head,
            positive.tail,
            0,
            positive.candidate_id,
        )
        if negative.key in full_type_keys or negative.key in used_negatives:
            continue
        if not is_local(negative, reachable):
            continue
        pairs.append((positive, negative))
        used_negatives.add(negative.key)
    return tuple(pairs)


def role_exchange_pairs(
    positives: tuple[Candidate, ...],
    full_type_keys: set[tuple[tuple[str, ...], tuple[str, ...]],],
    reachable: dict[str, frozenset[str]],
    seed: int,
) -> tuple[tuple[Candidate, Candidate], ...]:
    """Pair positives with one valid unseen one-tail/one-head role exchange each."""
    random = Random(seed)
    pairs: list[tuple[Candidate, Candidate]] = []
    used_negatives: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for positive in positives:
        alternatives: list[Candidate] = []
        for tail_member in positive.tail:
            for head_member in positive.head:
                tail = tuple(node for node in positive.tail if node != tail_member) + (head_member,)
                head = tuple(node for node in positive.head if node != head_member) + (tail_member,)
                negative = make_candidate(
                    f"role_exchange_of_{positive.candidate_id}_{tail_member}_{head_member}",
                    tail,
                    head,
                    0,
                    positive.candidate_id,
                )
                if negative.key in full_type_keys or negative.key in used_negatives:
                    continue
                if is_local(negative, reachable):
                    alternatives.append(negative)
        if alternatives:
            negative = random.choice(sorted(alternatives, key=lambda item: item.key))
            pairs.append((positive, negative))
            used_negatives.add(negative.key)
    return tuple(pairs)


def prediction_rows(
    candidates: tuple[Candidate, ...], arcs: frozenset[tuple[str, str]], panel: str
) -> list[dict[str, object]]:
    """Apply identical split-specific lifted directed-LP scoring to a hard panel."""
    engine = DirectedScoreEngine(arcs)
    outdegree = {node: len(neighbors) for node, neighbors in engine.out_neighbors.items()}
    indegree = {node: len(neighbors) for node, neighbors in engine.in_neighbors.items()}
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        dyad_scores = [engine.score(tail, head) for tail, head in sorted(candidate.footprint)]
        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "panel": panel,
                "tail_nodes_json": json.dumps(candidate.tail),
                "head_nodes_json": json.dumps(candidate.head),
                "tail_arity": len(candidate.tail),
                "head_arity": len(candidate.head),
                "label": candidate.label,
                "paired_source_event_type_id": candidate.source_event_type_id or "",
                "footprint_size": len(dyad_scores),
                "already_observed_footprint": int(candidate.footprint <= arcs),
                "lifted_reverse_arc_mean": mean(
                    int((head, tail) in arcs) for tail, head in candidate.footprint
                ),
                "lifted_degree_product_mean": mean(
                    outdegree.get(tail, 0) * indegree.get(head, 0)
                    for tail, head in candidate.footprint
                ),
                "lifted_oi_mean": mean(score.common_neighbors.oi for score in dyad_scores),
                "lifted_oo_mean": mean(score.common_neighbors.oo for score in dyad_scores),
                "lifted_ii_mean": mean(score.common_neighbors.ii for score in dyad_scores),
                "lifted_cn_total_mean": mean(score.common_neighbors.total for score in dyad_scores),
                "lifted_adamic_adar_oi_mean": mean(score.adamic_adar.oi for score in dyad_scores),
                "lifted_adamic_adar_oo_mean": mean(score.adamic_adar.oo for score in dyad_scores),
                "lifted_adamic_adar_ii_mean": mean(score.adamic_adar.ii for score in dyad_scores),
                "lifted_adamic_adar_total_mean": mean(
                    score.adamic_adar.total for score in dyad_scores
                ),
            }
        )
    return rows


def precision_recall_at_k(labels: list[int], scores: list[float], k: int) -> tuple[float, float]:
    """Return expected precision@k and recall@k under uniformly random tie resolution."""
    if len(labels) != len(scores) or not labels or not 0 < k <= len(labels):
        raise ValueError("precision/recall@k requires nonempty aligned scores and a valid k")
    positives = sum(labels)
    if positives < 1:
        raise ValueError("precision/recall@k requires at least one positive")
    ordered = sorted(zip(scores, labels, strict=True), reverse=True)
    selected = 0
    expected_true_positive = 0.0
    start = 0
    while start < len(ordered) and selected < k:
        score = ordered[start][0]
        stop = start + 1
        while stop < len(ordered) and ordered[stop][0] == score:
            stop += 1
        tied = ordered[start:stop]
        take = min(k - selected, len(tied))
        expected_true_positive += take * sum(label for _, label in tied) / len(tied)
        selected += take
        start = stop
    return expected_true_positive / k, expected_true_positive / positives


def metric_rows(
    predictions: list[dict[str, object]], panel: str, mechanism: str, replicate: int
) -> list[dict[str, object]]:
    """Calculate only valid rank metrics for uncalibrated hard-panel heuristic scores."""
    labels = [int(row["label"]) for row in predictions]
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives < 1 or negatives < 1:
        raise RuntimeError("hard panel must contain at least one positive and one negative")
    score_columns = [
        column
        for column in predictions[0]
        if column.startswith("lifted_") or column == "already_observed_footprint"
    ]
    result: list[dict[str, object]] = []
    for score_name in score_columns:
        values = [float(row[score_name]) for row in predictions]
        precision, recall = precision_recall_at_k(labels, values, positives)
        for metric, value in (
            ("roc_auc", roc_auc(labels, values)),
            ("pr_auc", pr_auc(labels, values)),
            ("precision_at_k", precision),
            ("recall_at_k", recall),
        ):
            result.append(
                {
                    "panel": panel,
                    "mechanism": mechanism,
                    "replicate": replicate,
                    "score": score_name,
                    "metric": metric,
                    "value": value,
                    "candidates": len(predictions),
                    "positives": positives,
                    "negatives": negatives,
                    "k": positives,
                }
            )
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty deterministic CSV result table."""
    if not rows:
        raise RuntimeError(f"cannot write an empty required result table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Prevent accidental blending of hard-panel result bundles."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: native-event hard-panel output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def aggregate_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate replicate metrics separately by panel and mechanism."""
    groups: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        key = (str(row["panel"]), str(row["mechanism"]), str(row["score"]), str(row["metric"]))
        groups[key].append(float(row["value"]))
    return [
        {
            "panel": panel,
            "mechanism": mechanism,
            "score": score,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (panel, mechanism, score, metric), values in sorted(groups.items())
    ]


def write_summary_markdown(
    path: Path,
    dataset_id: str,
    coverage: list[dict[str, object]],
    metrics: list[dict[str, object]],
) -> None:
    """Write readable coverage and ranking summaries without hiding panel availability."""
    lines = [
        "# Native-event directed hard-negative benchmark",
        "",
        f"- Dataset: `{dataset_id}`",
        "- Each panel is balanced with a held-out native-event type and one structurally "
        "constructed, unseen hard negative. Scores are uncalibrated ranking rules.",
        "- Reversal/orientation changes tail and head roles. Role exchange preserves both "
        "tail and head arities while swapping one actor across roles.",
        "",
        "## Panel coverage",
        "",
        "| Mechanism | Replicate | Candidate-eligible positives | Reversal pairs | "
        "Role-exchange pairs |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in coverage:
        lines.append(
            "| {mechanism} | {replicate} | {eligible} | {reversal} | {role_exchange} |".format(
                mechanism=row["mechanism"],
                replicate=row["replicate"],
                eligible=row["candidate_eligible_positive_types"],
                reversal=row["reversal_orientation_pairs"],
                role_exchange=row["role_exchange_pairs"],
            )
        )
    lines.extend(
        [
            "",
            "## Ranking metrics across completed replicates",
            "",
            "| Panel | Mechanism | Score | Metric | Replicates | Mean | SD |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in metrics:
        lines.append(
            "| {panel} | {mechanism} | {score} | {metric} | {replicates} | {mean:.4f} | "
            "{sd:.4f} |".format(
                panel=row["panel"],
                mechanism=row["mechanism"],
                score=row["score"],
                metric=row["metric"],
                replicates=row["completed_replicates"],
                mean=float(row["mean"]),
                sd=float(row["sd"]),
            )
        )
    lines.extend(
        [
            "",
            "The `already_observed_footprint` column is a diagnostic baseline, not a prediction "
            "model. A valid hard negative must not be any known native event type, so an "
            "unavailable reversal or role exchange is recorded as a coverage limitation rather "
            "than relabelled.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Score all valid directed hard pairs from the frozen primary Enron masks."""
    args = parse_args()
    mask_dir = resolve_path(args.mask_dir)
    nodes_path = resolve_path(args.nodes)
    output_dir = resolve_path(args.output_dir)
    if not mask_dir.is_dir():
        raise SystemExit(f"STOP: event-first mask directory is missing: {mask_dir}")
    prepare_output_dir(output_dir, args.overwrite)
    nodes = read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    all_metrics: list[dict[str, object]] = []
    coverage_rows: list[dict[str, object]] = []

    for split_dir in split_directories(mask_dir):
        mechanism, replicate = split_identity(split_dir)
        observed = read_type_table(split_dir / "observed_event_types.csv", label=0)
        heldout = read_type_table(split_dir / "heldout_event_types.csv", label=1)
        if {candidate.key for candidate in observed}.intersection(
            candidate.key for candidate in heldout
        ):
            raise SystemExit("STOP: frozen split leaks held-out types into observed event types.")
        for candidate in observed + heldout:
            if any(node not in node_set for node in candidate.tail + candidate.head):
                raise SystemExit(
                    "STOP: event type references an actor outside the fixed node universe."
                )
        arcs = read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        reachable = weak_reachability(nodes, arcs, args.max_weak_distance)
        positives = tuple(candidate for candidate in heldout if is_local(candidate, reachable))
        if not positives:
            raise SystemExit(f"STOP: no candidate-eligible held-out types in {split_dir.name}")
        full_type_keys = {candidate.key for candidate in observed + heldout}
        reversal = reversal_pairs(positives, full_type_keys, reachable)
        split_seed = args.seed + 20_011 * replicate + (0 if mechanism == "mcar" else 10_009)
        exchanged = role_exchange_pairs(positives, full_type_keys, reachable, split_seed)
        panels = {
            "reversal_orientation": reversal,
            "role_exchange": exchanged,
        }
        split_output = output_dir / split_dir.name
        split_output.mkdir()
        panel_availability: dict[str, int] = {}
        for panel, pairs in panels.items():
            panel_availability[panel] = len(pairs)
            if not pairs:
                continue
            candidates = tuple(candidate for pair in pairs for candidate in pair)
            predictions = prediction_rows(candidates, arcs, panel)
            metrics = metric_rows(predictions, panel, mechanism, replicate)
            write_csv(split_output / f"{panel}_candidate_predictions.csv", predictions)
            write_csv(split_output / f"{panel}_metrics.csv", metrics)
            all_metrics.extend(metrics)
        split_manifest = {
            "source_mask_split": recorded_path(split_dir),
            "mechanism": mechanism,
            "replicate": replicate,
            "candidate_universe": "all participants pairwise within weak distance two in "
            "observed projection",
            "candidate_eligible_positive_types": len(positives),
            "full_heldout_positive_types": len(heldout),
            "panels": {
                "reversal_orientation": {
                    "pairs": len(reversal),
                    "negative_rule": "reverse_tail_and_head_roles; "
                    "exclude_all_known_native_event_types",
                },
                "role_exchange": {
                    "pairs": len(exchanged),
                    "negative_rule": "exchange_one_tail_and_one_head_actor; preserve_role_arities; "
                    "exclude_all_known_native_event_types",
                },
            },
            "metric_contract": "ranking only; raw heuristic scores are not calibrated "
            "probabilities",
        }
        (split_output / "manifest.json").write_text(
            json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        coverage_rows.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "heldout_positive_types": len(heldout),
                "candidate_eligible_positive_types": len(positives),
                "positive_eligibility_rate": len(positives) / len(heldout),
                "reversal_orientation_pairs": panel_availability["reversal_orientation"],
                "role_exchange_pairs": panel_availability["role_exchange"],
            }
        )

    if not all_metrics:
        raise SystemExit("STOP: no valid reversal or role-exchange hard panels were available.")
    summary_metrics = aggregate_metrics(all_metrics)
    write_csv(output_dir / "split_summary.csv", coverage_rows)
    write_csv(output_dir / "metric_summary.csv", summary_metrics)
    manifest: dict[str, Any] = {
        "driver": "scripts/38_run_native_event_hard_panels.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "target": "native_event_type",
        "source_masks": recorded_path(mask_dir),
        "hard_panels": ["reversal_orientation", "role_exchange"],
        "candidate_universe": "weak distance two in each split's observed projection",
        "negative_exclusion": "all observed and held-out native event types",
        "splits_completed": len(coverage_rows),
        "outputs": {
            "split_summary": "split_summary.csv",
            "metric_summary": "metric_summary.csv",
            "summary_markdown": "summary.md",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary_markdown(
        output_dir / "summary.md", args.dataset_id, coverage_rows, summary_metrics
    )
    print("Native-event directed hard-negative benchmark passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Frozen splits completed: {len(coverage_rows):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
