#!/usr/bin/env python3
"""Evaluate lifted directed-LP heuristics on event-first native-event masks.

This driver consumes only frozen event-first splits. A held-out positive is a
native tail/head event type; a candidate is eligible only if all of its
participants are within weak distance two in the split's observed directed
projection. It creates an arity-matched random-negative panel for each split,
excluding every observed or held-out native event type from the negative pool.

The reported scores are ranking rules, not probabilities: the arithmetic mean
of component directed-LP dyad scores across a candidate footprint, plus an
already-observed-footprint baseline. Therefore only ranking metrics (ROC-AUC,
PR-AUC, precision@k, recall@k) are reported; calibration and threshold metrics
require a train-only calibration step and are deliberately not manufactured.
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
    """A canonical native-event candidate with an evaluation label."""

    candidate_id: str
    tail: tuple[str, ...]
    head: tuple[str, ...]
    label: int
    source_event_type_id: str | None
    occurrence_count: int | None

    @property
    def key(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return a canonical structural identity independent of stored metadata."""
        return self.tail, self.head

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return the candidate's directed dyadic footprint."""
        return frozenset(product(self.tail, self.head))

    @property
    def tail_arity(self) -> int:
        """Return the number of sender-role participants."""
        return len(self.tail)

    @property
    def head_arity(self) -> int:
        """Return the number of recipient-role participants."""
        return len(self.head)


def parse_args() -> argparse.Namespace:
    """Parse the explicit frozen-mask native-event heuristic run contract."""
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
    """Render a reproducible repository-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path, description: str) -> None:
    """Fail before writing output when a declared local input is absent."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read the fixed node universe and reject empty or duplicate actor IDs."""
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
    """Decode and validate canonical stored role membership from a mask split."""
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


def read_type_table(path: Path, *, label: int) -> tuple[Candidate, ...]:
    """Read one observed/held-out type table as canonical candidates."""
    require_file(path, "event-type table")
    candidates: list[Candidate] = []
    seen_ids: set[str] = set()
    seen_keys: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "event_type_id",
            "tail_nodes_json",
            "head_nodes_json",
            "tail_arity",
            "head_arity",
            "occurrence_count",
        }
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(f"STOP: event-type table is missing required columns: {path}")
        for row in reader:
            event_type_id = row["event_type_id"].strip()
            tail = parse_role_json(row["tail_nodes_json"], "tail_nodes_json")
            head = parse_role_json(row["head_nodes_json"], "head_nodes_json")
            if set(tail).intersection(head):
                raise SystemExit("STOP: event-type table contains overlapping tail/head roles.")
            if int(row["tail_arity"]) != len(tail) or int(row["head_arity"]) != len(head):
                raise SystemExit("STOP: event-type table has inconsistent role arity metadata.")
            occurrence_count = int(row["occurrence_count"])
            if occurrence_count < 1:
                raise SystemExit("STOP: event-type table has non-positive occurrence count.")
            candidate = Candidate(
                candidate_id=event_type_id,
                tail=tail,
                head=head,
                label=label,
                source_event_type_id=event_type_id,
                occurrence_count=occurrence_count,
            )
            if not event_type_id or event_type_id in seen_ids or candidate.key in seen_keys:
                raise SystemExit(
                    "STOP: event-type table has duplicate or empty candidate identities."
                )
            seen_ids.add(event_type_id)
            seen_keys.add(candidate.key)
            candidates.append(candidate)
    if not candidates:
        raise SystemExit(f"STOP: event-type table is empty: {path}")
    return tuple(candidates)


def read_observed_arcs(path: Path, nodes: set[str]) -> frozenset[tuple[str, str]]:
    """Read and validate the observed split's simple directed projection."""
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
                raise SystemExit(
                    "STOP: observed arc table contains an empty endpoint or self-loop."
                )
            if tail not in nodes or head not in nodes:
                raise SystemExit("STOP: observed arc references an actor outside the node table.")
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit(f"STOP: observed arc table is empty: {path}")
    return frozenset(arcs)


def split_directories(mask_dir: Path) -> tuple[Path, ...]:
    """Find frozen mask directories only when their complete core inputs exist."""
    required = {"observed_event_types.csv", "heldout_event_types.csv", "observed_arcs.csv"}
    splits = tuple(
        path
        for path in sorted(mask_dir.iterdir())
        if path.is_dir() and required <= {child.name for child in path.iterdir()}
    )
    if not splits:
        raise SystemExit(f"STOP: no complete event-first split directories found in {mask_dir}")
    return splits


def weak_distance_two_map(
    nodes: tuple[str, ...], arcs: frozenset[tuple[str, str]], max_distance: int
) -> dict[str, frozenset[str]]:
    """Construct deterministic weak k-hop neighborhoods from observed arcs only."""
    neighbors: dict[str, set[str]] = {node: set() for node in nodes}
    for tail, head in arcs:
        neighbors[tail].add(head)
        neighbors[head].add(tail)
    reachable: dict[str, frozenset[str]] = {}
    for source in nodes:
        visited = {source}
        frontier = {source}
        for _ in range(max_distance):
            frontier = set().union(*(neighbors[node] for node in frontier)) - visited
            visited.update(frontier)
        reachable[source] = frozenset(visited)
    return reachable


def is_local_candidate(candidate: Candidate, reachable: dict[str, frozenset[str]]) -> bool:
    """Require every pair of role participants to lie within the observed k-hop universe."""
    participants = candidate.tail + candidate.head
    return all(right in reachable[left] for left, right in combinations(participants, 2))


def candidate_from_roles(
    candidate_id: str, tail: tuple[str, ...], head: tuple[str, ...], label: int
) -> Candidate:
    """Create a structurally valid synthetic evaluation candidate."""
    if not tail or not head or set(tail).intersection(head):
        raise ValueError("native-event candidates must have nonempty disjoint roles")
    return Candidate(
        candidate_id=candidate_id,
        tail=tuple(sorted(tail)),
        head=tuple(sorted(head)),
        label=label,
        source_event_type_id=None,
        occurrence_count=None,
    )


def negative_candidates_by_arity(
    *,
    positives: tuple[Candidate, ...],
    full_type_keys: set[tuple[tuple[str, ...], tuple[str, ...]]],
    nodes: tuple[str, ...],
    reachable: dict[str, frozenset[str]],
    seed: int,
) -> tuple[Candidate, ...]:
    """Sample one unique non-event negative for each positive, matched on both role arities."""
    grouped: dict[tuple[int, int], list[Candidate]] = defaultdict(list)
    for positive in positives:
        grouped[(positive.tail_arity, positive.head_arity)].append(positive)

    random = Random(seed)
    negatives: list[Candidate] = []
    used_keys: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    node_count = len(nodes)
    for (tail_size, head_size), group in sorted(grouped.items()):
        if tail_size + head_size > node_count:
            raise SystemExit("STOP: requested candidate arity exceeds the fixed node universe.")
        required = len(group)
        accepted = 0
        attempts = 0
        maximum_attempts = max(100_000, required * 5_000)
        while accepted < required and attempts < maximum_attempts:
            attempts += 1
            sampled = random.sample(nodes, tail_size + head_size)
            candidate = candidate_from_roles(
                candidate_id=f"negative_{tail_size}_{head_size}_{accepted + 1:05d}",
                tail=tuple(sampled[:tail_size]),
                head=tuple(sampled[tail_size:]),
                label=0,
            )
            if candidate.key in full_type_keys or candidate.key in used_keys:
                continue
            if not is_local_candidate(candidate, reachable):
                continue
            used_keys.add(candidate.key)
            negatives.append(candidate)
            accepted += 1
        if accepted != required:
            raise SystemExit(
                "STOP: insufficient unique local non-event negatives for arity "
                f"({tail_size}, {head_size}); generated {accepted}/{required} after "
                f"{maximum_attempts:,} attempts. Reduce the caps or revise the candidate universe."
            )
    return tuple(negatives)


def candidate_rows(
    candidates: tuple[Candidate, ...], observed_arcs: frozenset[tuple[str, str]]
) -> list[dict[str, object]]:
    """Score candidates using only their split-specific observed directed graph."""
    engine = DirectedScoreEngine(observed_arcs)
    outdegree = {node: len(neighbors) for node, neighbors in engine.out_neighbors.items()}
    indegree = {node: len(neighbors) for node, neighbors in engine.in_neighbors.items()}
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        scores = [engine.score(tail, head) for tail, head in sorted(candidate.footprint)]
        footprint_size = len(scores)
        reverse_fraction = mean(
            int((head, tail) in observed_arcs) for tail, head in candidate.footprint
        )
        degree_product_mean = mean(
            outdegree.get(tail, 0) * indegree.get(head, 0) for tail, head in candidate.footprint
        )
        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "tail_nodes_json": json.dumps(candidate.tail),
                "head_nodes_json": json.dumps(candidate.head),
                "tail_arity": candidate.tail_arity,
                "head_arity": candidate.head_arity,
                "label": candidate.label,
                "source_event_type_id": candidate.source_event_type_id or "",
                "occurrence_count": candidate.occurrence_count or "",
                "footprint_size": footprint_size,
                "already_observed_footprint": int(candidate.footprint <= observed_arcs),
                "lifted_reverse_arc_mean": reverse_fraction,
                "lifted_degree_product_mean": degree_product_mean,
                "lifted_oi_mean": mean(score.common_neighbors.oi for score in scores),
                "lifted_oo_mean": mean(score.common_neighbors.oo for score in scores),
                "lifted_ii_mean": mean(score.common_neighbors.ii for score in scores),
                "lifted_cn_total_mean": mean(score.common_neighbors.total for score in scores),
                "lifted_adamic_adar_oi_mean": mean(score.adamic_adar.oi for score in scores),
                "lifted_adamic_adar_oo_mean": mean(score.adamic_adar.oo for score in scores),
                "lifted_adamic_adar_ii_mean": mean(score.adamic_adar.ii for score in scores),
                "lifted_adamic_adar_total_mean": mean(score.adamic_adar.total for score in scores),
            }
        )
    return rows


def precision_recall_at_k(labels: list[int], scores: list[float], k: int) -> tuple[float, float]:
    """Return tie-invariant expected precision@k and recall@k under random tie breaks."""
    if not labels or len(labels) != len(scores) or k < 1 or k > len(labels):
        raise ValueError("precision/recall@k requires equally sized nonempty scores and a valid k")
    positives = sum(labels)
    if positives < 1:
        raise ValueError("precision/recall@k requires at least one positive")
    ordered = sorted(zip(scores, labels, strict=True), reverse=True)
    selected = 0
    expected_true_positive = 0.0
    position = 0
    while position < len(ordered) and selected < k:
        score = ordered[position][0]
        stop = position + 1
        while stop < len(ordered) and ordered[stop][0] == score:
            stop += 1
        group = ordered[position:stop]
        take = min(k - selected, len(group))
        expected_true_positive += take * sum(label for _, label in group) / len(group)
        selected += take
        position = stop
    return expected_true_positive / k, expected_true_positive / positives


def metric_rows(
    predictions: list[dict[str, object]], mechanism: str, replicate: int
) -> list[dict[str, object]]:
    """Evaluate uncalibrated ranking scores on one balanced target-specific panel."""
    labels = [int(row["label"]) for row in predictions]
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise RuntimeError("native-event panel must contain at least one positive and negative")
    score_columns = [
        key
        for key in predictions[0]
        if key.startswith("lifted_") or key == "already_observed_footprint"
    ]
    rows: list[dict[str, object]] = []
    for score_name in score_columns:
        scores = [float(row[score_name]) for row in predictions]
        precision_at_k, recall_at_k = precision_recall_at_k(labels, scores, positives)
        for metric, value in (
            ("roc_auc", roc_auc(labels, scores)),
            ("pr_auc", pr_auc(labels, scores)),
            ("precision_at_k", precision_at_k),
            ("recall_at_k", recall_at_k),
        ):
            rows.append(
                {
                    "mechanism": mechanism,
                    "replicate": replicate,
                    "score": score_name,
                    "metric": metric,
                    "value": value,
                    "candidates": len(labels),
                    "positives": positives,
                    "negatives": negatives,
                    "k": positives,
                    "metric_status": "calculated",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a required nonempty stable CSV table with Unix line endings."""
    if not rows:
        raise RuntimeError(f"cannot write a required empty table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Protect a complete output bundle unless deterministic replacement is explicit."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: native-event heuristic output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def split_identity(path: Path) -> tuple[str, int]:
    """Parse a masking split directory produced by script 36."""
    parts = path.name.rsplit("_replicate_", maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        raise SystemExit(f"STOP: invalid event-first split directory name: {path.name}")
    return parts[0], int(parts[1])


def summarise_metrics(metric_values: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate replicate-level metric values without concealing replicate counts."""
    grouped: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in metric_values:
        grouped[(str(row["mechanism"]), str(row["score"]), str(row["metric"]))].append(
            float(row["value"])
        )
    return [
        {
            "mechanism": mechanism,
            "score": score,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, score, metric), values in sorted(grouped.items())
    ]


def write_summary_markdown(
    path: Path,
    dataset_id: str,
    split_rows: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
) -> None:
    """Write a concise scoring summary that preserves the target and metric boundaries."""
    type_rows = [
        "# Event-first native-event heuristic benchmark",
        "",
        f"- Dataset: `{dataset_id}`",
        "- Target: held-out native tail/head **event types**; duplicate records of a selected "
        "type were removed together before scoring.",
        "- Candidate universe: participants are pairwise within weak distance two in the split's "
        "observed projection. Random negatives are matched exactly on tail/head arity and are "
        "not observed or held-out native event types.",
        "- Scores are uncalibrated ranking rules. ROC-AUC, PR-AUC, precision@k, and recall@k are "
        "valid here; accuracy, F1, MCC, and log loss are intentionally omitted.",
        "",
        "## Candidate-panel coverage",
        "",
        "| Mechanism | Replicate | Held-out types | Positive types eligible for the "
        "candidate universe | Random negatives |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in split_rows:
        type_rows.append(
            "| {mechanism} | {replicate} | {heldout} | {eligible} | {negatives} |".format(
                mechanism=row["mechanism"],
                replicate=row["replicate"],
                heldout=row["heldout_event_types"],
                eligible=row["eligible_positive_types"],
                negatives=row["random_negative_types"],
            )
        )
    type_rows.extend(
        [
            "",
            "## Ranking metrics across completed replicates",
            "",
            "| Mechanism | Score | Metric | Completed replicates | Mean | SD |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in summary_rows:
        type_rows.append(
            "| {mechanism} | {score} | {metric} | {completed} | {mean:.4f} | {sd:.4f} |".format(
                mechanism=row["mechanism"],
                score=row["score"],
                metric=row["metric"],
                completed=row["completed_replicates"],
                mean=float(row["mean"]),
                sd=float(row["sd"]),
            )
        )
    type_rows.extend(
        [
            "",
            "The `already_observed_footprint` score is a baseline, not a predictor: it indicates "
            "that an observed event type already induces every arc of the held-out candidate's "
            "footprint. A high value demonstrates event non-identifiability from the observed "
            "dyads.",
            "",
        ]
    )
    path.write_text("\n".join(type_rows), encoding="utf-8")


def main() -> None:
    """Score every frozen event-first split on its own leakage-safe random panel."""
    args = parse_args()
    mask_dir = resolve_path(args.mask_dir)
    nodes_path = resolve_path(args.nodes)
    output_dir = resolve_path(args.output_dir)
    if not mask_dir.is_dir():
        raise SystemExit(f"STOP: event-first mask directory is missing: {mask_dir}")
    prepare_output_dir(output_dir, args.overwrite)
    nodes = read_nodes(nodes_path, args.node_column)
    node_set = set(nodes)
    all_split_metrics: list[dict[str, object]] = []
    split_summary_rows: list[dict[str, object]] = []

    for split_dir in split_directories(mask_dir):
        mechanism, replicate = split_identity(split_dir)
        observed_types = read_type_table(split_dir / "observed_event_types.csv", label=0)
        heldout_types = read_type_table(split_dir / "heldout_event_types.csv", label=1)
        if {candidate.key for candidate in observed_types}.intersection(
            candidate.key for candidate in heldout_types
        ):
            raise SystemExit(
                "STOP: frozen mask split leaks a held-out event type into observed types."
            )
        for candidate in observed_types + heldout_types:
            if any(node not in node_set for node in candidate.tail + candidate.head):
                raise SystemExit(
                    "STOP: event split references an actor outside the declared node universe."
                )
        observed_arcs = read_observed_arcs(split_dir / "observed_arcs.csv", node_set)
        reachable = weak_distance_two_map(nodes, observed_arcs, args.max_weak_distance)
        eligible_positives = tuple(
            candidate for candidate in heldout_types if is_local_candidate(candidate, reachable)
        )
        if not eligible_positives:
            raise SystemExit(
                f"STOP: no held-out event types lie in the candidate universe for {split_dir.name}."
            )
        split_seed = args.seed + 10_007 * replicate + (0 if mechanism == "mcar" else 5_003)
        negatives = negative_candidates_by_arity(
            positives=eligible_positives,
            full_type_keys={candidate.key for candidate in observed_types + heldout_types},
            nodes=nodes,
            reachable=reachable,
            seed=split_seed,
        )
        predictions = candidate_rows(eligible_positives + negatives, observed_arcs)
        metrics = metric_rows(predictions, mechanism, replicate)
        split_output = output_dir / split_dir.name
        split_output.mkdir()
        write_csv(split_output / "candidate_predictions.csv", predictions)
        write_csv(split_output / "metrics.csv", metrics)
        split_manifest = {
            "source_mask_split": recorded_path(split_dir),
            "mechanism": mechanism,
            "replicate": replicate,
            "candidate_universe": {
                "max_weak_distance": args.max_weak_distance,
                "positive_types_held_out": len(heldout_types),
                "positive_types_eligible": len(eligible_positives),
                "positive_eligibility_rate": len(eligible_positives) / len(heldout_types),
                "random_negative_types": len(negatives),
                "negative_matching": "exact_tail_arity_and_head_arity",
                "negative_exclusions": "all_observed_and_heldout_native_event_types",
            },
            "scores": [
                key
                for key in predictions[0]
                if key.startswith("lifted_") or key == "already_observed_footprint"
            ],
            "metrics": ["roc_auc", "pr_auc", "precision_at_k", "recall_at_k"],
            "calibration": "not_applicable_to_uncalibrated_heuristic_scores",
            "files": {"predictions": "candidate_predictions.csv", "metrics": "metrics.csv"},
        }
        (split_output / "manifest.json").write_text(
            json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        all_split_metrics.extend(metrics)
        split_summary_rows.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "heldout_event_types": len(heldout_types),
                "eligible_positive_types": len(eligible_positives),
                "positive_eligibility_rate": len(eligible_positives) / len(heldout_types),
                "random_negative_types": len(negatives),
                "candidate_panel_size": len(predictions),
                "observed_projection_arcs": len(observed_arcs),
            }
        )

    summary_rows = summarise_metrics(all_split_metrics)
    write_csv(output_dir / "split_summary.csv", split_summary_rows)
    write_csv(output_dir / "metric_summary.csv", summary_rows)
    manifest: dict[str, Any] = {
        "driver": "scripts/37_run_native_event_heuristics.py",
        "dataset_id": args.dataset_id,
        "status": "completed",
        "target": "native_event_type",
        "source_masks": recorded_path(mask_dir),
        "candidate_universe": "all participants pairwise within weak distance two in "
        "observed projection",
        "negative_panel": "random true non-event types, exactly matched on tail and head arity",
        "score_interpretation": "uncalibrated lifted directed-LP ranking rules",
        "metrics": "ranking only; no calibration or threshold metrics",
        "splits_completed": len(split_summary_rows),
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
        output_dir / "summary.md", args.dataset_id, split_summary_rows, summary_rows
    )
    print("Event-first native-event heuristic benchmark passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Frozen splits completed: {len(split_summary_rows):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
