#!/usr/bin/env python3
"""Evaluate directed formal-concept recovery after arc-first masking.

A positive target is a capped formal concept of the full static directed relation that
is no longer a concept after a frozen arc-first mask. Scores use only the split's
observed arcs. The driver writes random, degree-matched, and non-maximal-complete
negative panels separately; unavailable hard panels are recorded rather than replaced
with an easier panel.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations, product
from pathlib import Path
from random import Random
from statistics import mean, stdev
from typing import Any

import pyarrow.parquet as pq

from directed_hp.evaluation.metrics import pr_auc, roc_auc
from directed_hp.hypergraphs.formal_concepts import DirectedFormalConcept, enumerate_formal_concepts
from directed_hp.lp.directed_scores import DirectedScoreEngine
from directed_hp.masking.directed_masks import MaskingMechanism, mask_arc_first

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = 20_261_013
DEFAULT_REPLICATES = 3
DEFAULT_MASK_RATE = 0.30
MAX_ATTEMPTS_PER_NEGATIVE = 20_000

DATASET_DEFAULTS: dict[str, dict[str, str]] = {
    "enron": {
        "arcs": "data/processed/enron_20150507/custodian_core100_static_arcs.parquet",
        "nodes": "data/processed/enron_20150507/custodian_core100_nodes.csv",
        "tail_column": "tail_custodian",
        "head_column": "head_custodian",
        "node_column": "custodian_mailbox",
    },
    "eu_core": {
        "arcs": "data/processed/email_eu_core_temporal/core100_static_arcs.parquet",
        "nodes": "data/processed/email_eu_core_temporal/core100_nodes.csv",
        "tail_column": "tail",
        "head_column": "head",
        "node_column": "node",
    },
    "caviar": {
        "arcs": "data/processed/caviar/directed_valued_arcs.parquet",
        "nodes": "data/processed/caviar/nodes.csv",
        "tail_column": "tail",
        "head_column": "head",
        "node_column": "id",
    },
    "mathoverflow": {
        "arcs": "data/processed/mathoverflow_stackexchange_2024/core100_static_arcs.parquet",
        "nodes": "data/processed/mathoverflow_stackexchange_2024/core100_nodes.csv",
        "tail_column": "tail",
        "head_column": "head",
        "node_column": "node",
    },
}


@dataclass(frozen=True, slots=True)
class Candidate:
    """One candidate tail/head pair in a concept-recovery test panel."""

    tail: tuple[str, ...]
    head: tuple[str, ...]
    label: int
    source_concept_id: str | None

    @property
    def key(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Return a canonical candidate identity."""
        return self.tail, self.head

    @property
    def footprint(self) -> frozenset[tuple[str, str]]:
        """Return the directed dyadic footprint."""
        return frozenset(product(self.tail, self.head))

    @property
    def tail_arity(self) -> int:
        """Return tail-role arity."""
        return len(self.tail)

    @property
    def head_arity(self) -> int:
        """Return head-role arity."""
        return len(self.head)


def parse_args() -> argparse.Namespace:
    """Parse an explicit leakage-safe concept-recovery evaluation contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, choices=sorted(DATASET_DEFAULTS))
    parser.add_argument(
        "--arcs", type=Path, help="Prepared Parquet arcs; overrides dataset default."
    )
    parser.add_argument("--nodes", type=Path, help="Prepared node CSV; overrides dataset default.")
    parser.add_argument("--tail-column", help="Arc source column; overrides dataset default.")
    parser.add_argument("--head-column", help="Arc target column; overrides dataset default.")
    parser.add_argument("--node-column", help="Node ID column; overrides dataset default.")
    parser.add_argument("--tail-cap", type=int, default=3)
    parser.add_argument("--head-cap", type=int, default=3)
    parser.add_argument("--max-concept-candidates", type=int, default=1_000_000)
    parser.add_argument("--mask-rate", type=float, default=DEFAULT_MASK_RATE)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument(
        "--mechanisms",
        nargs="+",
        choices=[item.value for item in MaskingMechanism],
        default=["mcar", "mnar_out"],
    )
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.tail_cap < 1 or args.head_cap < 1:
        parser.error("--tail-cap and --head-cap must be positive.")
    if args.max_concept_candidates < 1:
        parser.error("--max-concept-candidates must be positive.")
    if not 0.0 < args.mask_rate < 1.0:
        parser.error("--mask-rate must be strictly between zero and one.")
    if args.replicates < 1:
        parser.error("--replicates must be positive.")
    if args.max_weak_distance < 1:
        parser.error("--max-weak-distance must be positive.")
    if args.seed < 0:
        parser.error("--seed must be non-negative.")
    return args


def resolve_path(value: Path | None, fallback: str) -> Path:
    """Resolve a project-relative declared source path."""
    raw = value if value is not None else Path(fallback)
    return raw if raw.is_absolute() else PROJECT_ROOT / raw


def display_path(path: Path) -> str:
    """Render a stable project-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    """Return a streaming source-file checksum."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read a declared fixed node universe with deterministic ordering."""
    if not path.is_file():
        raise SystemExit(f"STOP: node table is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table has no {column!r} column: {path}")
        values = [str(row[column]).strip() for row in reader]
    if not values or any(not value for value in values):
        raise SystemExit("STOP: node table must contain only non-empty IDs.")
    if len(values) != len(set(values)):
        raise SystemExit("STOP: node table contains duplicate IDs.")
    return tuple(sorted(values))


def read_arcs(
    path: Path, tail_column: str, head_column: str, nodes: set[str]
) -> tuple[tuple[str, str], ...]:
    """Read and canonically order a loop-free binary directed relation."""
    if not path.is_file():
        raise SystemExit(f"STOP: prepared arc table is missing: {path}")
    source = pq.ParquetFile(path)
    required = {tail_column, head_column}
    if missing := required - set(source.schema_arrow.names):
        raise SystemExit(f"STOP: arc table lacks required columns: {sorted(missing)}")
    arcs: set[tuple[str, str]] = set()
    for batch in source.iter_batches(columns=[tail_column, head_column], batch_size=50_000):
        for row in batch.to_pylist():
            tail = str(row[tail_column]).strip()
            head = str(row[head_column]).strip()
            if not tail or not head or tail == head:
                raise SystemExit(
                    "STOP: prepared arc table contains an empty endpoint or self-loop."
                )
            if tail not in nodes or head not in nodes:
                raise SystemExit("STOP: prepared arc endpoint is absent from the node table.")
            arcs.add((tail, head))
    if not arcs:
        raise SystemExit("STOP: prepared arc table contains no usable directed arcs.")
    return tuple(sorted(arcs))


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    """Create a clean owned output directory only on explicit replacement."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def concepts_for(
    arcs: tuple[tuple[str, str], ...],
    nodes: tuple[str, ...],
    tail_cap: int,
    head_cap: int,
    max_candidates: int,
) -> tuple[DirectedFormalConcept, ...]:
    """Enumerate only the declared capped formal-concept target section."""
    return enumerate_formal_concepts(
        arcs,
        nodes=nodes,
        max_tail_arity=tail_cap,
        max_head_arity=head_cap,
        max_candidates=max_candidates,
    )


def concept_key(concept: DirectedFormalConcept) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return a string-normalized formal-concept identity."""
    return tuple(map(str, concept.tail)), tuple(map(str, concept.head))


def candidate_from_key(
    key: tuple[tuple[str, ...], tuple[str, ...]], label: int, source_id: str | None
) -> Candidate:
    """Construct a canonical candidate from separately ordered role tuples."""
    tail, head = tuple(sorted(key[0])), tuple(sorted(key[1]))
    if not tail or not head or set(tail).intersection(head):
        raise ValueError("concept candidate roles must be non-empty and disjoint")
    return Candidate(tail=tail, head=head, label=label, source_concept_id=source_id)


def weak_reachability(
    nodes: tuple[str, ...], arcs: tuple[tuple[str, str], ...], distance: int
) -> dict[str, frozenset[str]]:
    """Calculate observed-graph weak neighborhoods without future/full-graph edges."""
    neighbors: dict[str, set[str]] = {node: set() for node in nodes}
    for tail, head in arcs:
        neighbors[tail].add(head)
        neighbors[head].add(tail)
    reached: dict[str, frozenset[str]] = {}
    for source in nodes:
        visited = {source}
        frontier = {source}
        for _ in range(distance):
            next_frontier: set[str] = set()
            for item in frontier:
                next_frontier.update(neighbors[item])
            frontier = next_frontier - visited
            visited.update(frontier)
        reached[source] = frozenset(visited)
    return reached


def is_local(candidate: Candidate, reached: dict[str, frozenset[str]]) -> bool:
    """Require every candidate participant pair to be close in the observed graph."""
    participants = candidate.tail + candidate.head
    return all(right in reached[left] for left, right in combinations(participants, 2))


def observed_degrees(
    nodes: tuple[str, ...], arcs: tuple[tuple[str, str], ...]
) -> tuple[dict[str, int], dict[str, int]]:
    """Return observed out- and in-degree maps including isolates."""
    outdegree = {node: 0 for node in nodes}
    indegree = {node: 0 for node in nodes}
    for tail, head in arcs:
        outdegree[tail] += 1
        indegree[head] += 1
    return outdegree, indegree


def equal_count_deciles(nodes: tuple[str, ...], values: dict[str, int]) -> dict[str, int]:
    """Assign deterministic degree-rank deciles, preserving tied-node order by ID."""
    ordered = sorted(nodes, key=lambda node: (values[node], node))
    return {node: min(9, (position * 10) // len(ordered)) for position, node in enumerate(ordered)}


def random_candidate(
    nodes: tuple[str, ...], tail_size: int, head_size: int, random: Random
) -> Candidate:
    """Sample one role-disjoint candidate with declared arities."""
    sample = random.sample(nodes, tail_size + head_size)
    return candidate_from_key((tuple(sample[:tail_size]), tuple(sample[tail_size:])), 0, None)


def is_valid_negative(
    candidate: Candidate,
    full_concepts: set[tuple[tuple[str, ...], tuple[str, ...]]],
    used: set[tuple[tuple[str, ...], tuple[str, ...]]],
    reached: dict[str, frozenset[str]],
) -> bool:
    """Reject positives, duplicated candidates, and candidates outside U_k."""
    return (
        candidate.key not in full_concepts
        and candidate.key not in used
        and is_local(candidate, reached)
    )


def random_negative_panel(
    positives: tuple[Candidate, ...],
    nodes: tuple[str, ...],
    full_concepts: set[tuple[tuple[str, ...], tuple[str, ...]]],
    reached: dict[str, frozenset[str]],
    seed: int,
) -> tuple[tuple[Candidate, ...], tuple[Candidate, ...]]:
    """Draw available true non-concepts, matching positives on both role arities."""
    random = Random(seed)
    retained: list[Candidate] = []
    negatives: list[Candidate] = []
    used: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for positive in positives:
        for _ in range(MAX_ATTEMPTS_PER_NEGATIVE):
            candidate = random_candidate(nodes, positive.tail_arity, positive.head_arity, random)
            if is_valid_negative(candidate, full_concepts, used, reached):
                retained.append(positive)
                negatives.append(candidate)
                used.add(candidate.key)
                break
    return tuple(retained), tuple(negatives)


def draw_matched_roles(
    positive: Candidate,
    nodes: tuple[str, ...],
    out_decile: dict[str, int],
    in_decile: dict[str, int],
    random: Random,
) -> Candidate | None:
    """Sample role-disjoint substitutes that match each positive role's degree decile."""
    tail: list[str] = []
    for source in positive.tail:
        pool = [
            node for node in nodes if out_decile[node] == out_decile[source] and node not in tail
        ]
        if not pool:
            return None
        tail.append(random.choice(pool))
    head: list[str] = []
    for target in positive.head:
        pool = [
            node
            for node in nodes
            if in_decile[node] == in_decile[target] and node not in tail and node not in head
        ]
        if not pool:
            return None
        head.append(random.choice(pool))
    return candidate_from_key((tuple(tail), tuple(head)), 0, None)


def degree_matched_negative_panel(
    positives: tuple[Candidate, ...],
    nodes: tuple[str, ...],
    full_concepts: set[tuple[tuple[str, ...], tuple[str, ...]]],
    reached: dict[str, frozenset[str]],
    outdegree: dict[str, int],
    indegree: dict[str, int],
    seed: int,
) -> tuple[tuple[Candidate, ...], tuple[Candidate, ...]]:
    """Draw available arity- and observed-degree-decile-matched true non-concepts."""
    out_decile = equal_count_deciles(nodes, outdegree)
    in_decile = equal_count_deciles(nodes, indegree)
    random = Random(seed)
    retained: list[Candidate] = []
    negatives: list[Candidate] = []
    used: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    for positive in positives:
        for _ in range(MAX_ATTEMPTS_PER_NEGATIVE):
            candidate = draw_matched_roles(positive, nodes, out_decile, in_decile, random)
            if candidate is not None and is_valid_negative(candidate, full_concepts, used, reached):
                retained.append(positive)
                negatives.append(candidate)
                used.add(candidate.key)
                break
    return tuple(retained), tuple(negatives)


def common_successors(tail: tuple[str, ...], successors: dict[str, set[str]]) -> set[str]:
    """Return the observed common successors of a non-empty candidate tail."""
    shared: set[str] | None = None
    for node in tail:
        shared = set(successors[node]) if shared is None else shared.intersection(successors[node])
    return shared or set()


def common_predecessors(head: tuple[str, ...], predecessors: dict[str, set[str]]) -> set[str]:
    """Return the observed common predecessors of a non-empty candidate head."""
    shared: set[str] | None = None
    for node in head:
        shared = (
            set(predecessors[node]) if shared is None else shared.intersection(predecessors[node])
        )
    return shared or set()


def nonmaximal_candidate(
    positive: Candidate,
    nodes: tuple[str, ...],
    observed_arcs: tuple[tuple[str, str], ...],
    full_concepts: set[tuple[tuple[str, ...], tuple[str, ...]]],
    used: set[tuple[tuple[str, ...], tuple[str, ...]]],
    reached: dict[str, frozenset[str]],
    random: Random,
) -> Candidate | None:
    """Find a same-arity complete observed footprint that is non-maximal in the full graph."""
    successors = {node: set() for node in nodes}
    predecessors = {node: set() for node in nodes}
    for tail, head in observed_arcs:
        successors[tail].add(head)
        predecessors[head].add(tail)
    for _ in range(MAX_ATTEMPTS_PER_NEGATIVE):
        if random.random() < 0.5:
            tail = tuple(sorted(random.sample(nodes, positive.tail_arity)))
            choices = sorted(common_successors(tail, successors))
            if len(choices) <= positive.head_arity:
                continue
            head = tuple(sorted(random.sample(choices, positive.head_arity)))
        else:
            head = tuple(sorted(random.sample(nodes, positive.head_arity)))
            choices = sorted(common_predecessors(head, predecessors))
            if len(choices) <= positive.tail_arity:
                continue
            tail = tuple(sorted(random.sample(choices, positive.tail_arity)))
        if set(tail).intersection(head):
            continue
        candidate = candidate_from_key((tail, head), 0, None)
        if is_valid_negative(candidate, full_concepts, used, reached):
            return candidate
    return None


def nonmaximal_complete_panel(
    positives: tuple[Candidate, ...],
    nodes: tuple[str, ...],
    observed_arcs: tuple[tuple[str, str], ...],
    full_concepts: set[tuple[tuple[str, ...], tuple[str, ...]]],
    reached: dict[str, frozenset[str]],
    seed: int,
) -> tuple[tuple[Candidate, ...], tuple[Candidate, ...]]:
    """Create an available-subset non-maximal panel without easier substitution."""
    random = Random(seed)
    used: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    retained: list[Candidate] = []
    negatives: list[Candidate] = []
    for positive in positives:
        candidate = nonmaximal_candidate(
            positive, nodes, observed_arcs, full_concepts, used, reached, random
        )
        if candidate is not None:
            retained.append(positive)
            negatives.append(candidate)
            used.add(candidate.key)
    return tuple(retained), tuple(negatives)


def score_candidates(
    candidates: tuple[Candidate, ...], observed_arcs: tuple[tuple[str, str], ...]
) -> list[dict[str, object]]:
    """Compute split-specific lifted directed-LP scores for concept candidates."""
    engine = DirectedScoreEngine(observed_arcs)
    rows: list[dict[str, object]] = []
    observed = frozenset(observed_arcs)
    for index, candidate in enumerate(candidates, start=1):
        dyad_scores = [engine.score(tail, head) for tail, head in sorted(candidate.footprint)]
        rows.append(
            {
                "candidate_id": f"candidate_{index:05d}",
                "tail_nodes_json": json.dumps(candidate.tail),
                "head_nodes_json": json.dumps(candidate.head),
                "tail_arity": candidate.tail_arity,
                "head_arity": candidate.head_arity,
                "label": candidate.label,
                "source_concept_id": candidate.source_concept_id or "",
                "footprint_size": len(candidate.footprint),
                "already_observed_footprint": int(candidate.footprint <= observed),
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
    """Compute tie-invariant expected precision and recall at the positive count."""
    ordered = sorted(zip(scores, labels, strict=True), reverse=True)
    selected = 0
    true_positive = 0.0
    position = 0
    positives = sum(labels)
    while position < len(ordered) and selected < k:
        score = ordered[position][0]
        stop = position + 1
        while stop < len(ordered) and ordered[stop][0] == score:
            stop += 1
        group = ordered[position:stop]
        take = min(k - selected, len(group))
        true_positive += take * sum(label for _, label in group) / len(group)
        selected += take
        position = stop
    return true_positive / k, true_positive / positives


def metric_rows(
    rows: list[dict[str, object]], mechanism: str, replicate: int, panel: str
) -> list[dict[str, object]]:
    """Calculate ranking metrics for one balanced concept-recovery panel."""
    labels = [int(row["label"]) for row in rows]
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("concept panel requires at least one positive and one negative")
    output: list[dict[str, object]] = []
    score_columns = [
        name
        for name in rows[0]
        if name.startswith("lifted_") or name == "already_observed_footprint"
    ]
    for score_name in score_columns:
        scores = [float(row[score_name]) for row in rows]
        precision, recall = precision_recall_at_k(labels, scores, positives)
        for metric, value in (
            ("roc_auc", roc_auc(labels, scores)),
            ("pr_auc", pr_auc(labels, scores)),
            ("precision_at_k", precision),
            ("recall_at_k", recall),
        ):
            output.append(
                {
                    "mechanism": mechanism,
                    "replicate": replicate,
                    "panel": panel,
                    "score": score_name,
                    "metric": metric,
                    "value": value,
                    "positives": positives,
                    "negatives": negatives,
                    "candidates": len(rows),
                }
            )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty stable CSV with Unix line endings."""
    if not rows:
        raise ValueError(f"cannot write an empty required table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_empty_csv(path: Path, fieldnames: list[str]) -> None:
    """Write an explicit header-only table when a hard panel has no eligible candidates."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n").writeheader()


def summarise_metrics(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate only completed replicate/panel metric rows."""
    grouped: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        grouped[
            (str(row["mechanism"]), str(row["panel"]), str(row["score"]), str(row["metric"]))
        ].append(float(row["value"]))
    return [
        {
            "mechanism": mechanism,
            "panel": panel,
            "score": score,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, panel, score, metric), values in sorted(grouped.items())
    ]


def write_summary(
    path: Path,
    dataset: str,
    full_concept_count: int,
    split_rows: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
) -> None:
    """Write an interpretation-safe concept-recovery summary."""
    lines = [
        "# Arc-first directed formal-concept recovery",
        "",
        f"- Dataset: `{dataset}`",
        f"- Full capped formal-concept target count: `{full_concept_count:,}`",
        "- Positive target: a full-graph formal concept lost from the observed graph after an "
        "arc-first mask.",
        "- Candidate universe: all candidate participants are pairwise within weak distance two "
        "in that split's observed projection.",
        "- Every negative is a true non-concept of the full graph. No test negative is an observed "
        "training concept.",
        "- Scores are uncalibrated lifted directed-LP rankings; metrics are ranking-only.",
        "",
        "## Split and panel availability",
        "",
        "| Mechanism | Replicate | Full concepts lost | Eligible positives | Random negatives | "
        "Degree-matched negatives | Non-maximal complete negatives |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in split_rows:
        lines.append(
            "| {mechanism} | {replicate} | {lost} | {eligible} | {random_count} | "
            "{degree_count} | {nonmaximal_count} |".format(
                mechanism=row["mechanism"],
                replicate=row["replicate"],
                lost=row["lost_full_concepts"],
                eligible=row["eligible_positive_concepts"],
                random_count=row["random_negative_concepts"],
                degree_count=row["degree_matched_negative_concepts"],
                nonmaximal_count=row["nonmaximal_complete_negative_concepts"],
            )
        )
    lines.extend(
        [
            "",
            "## Ranking metrics across completed replicates",
            "",
            "| Mechanism | Panel | Score | Metric | Completed replicates | Mean | SD |",
            "|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in summary_rows:
        lines.append(
            "| {mechanism} | {panel} | {score} | {metric} | {completed_replicates} | "
            "{mean:.4f} | {sd:.4f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "The non-maximal-complete panel is reported only where sufficient same-arity negatives "
            "exist. An unavailable hard panel is not substituted with a random panel.",
            "Every completed panel is balanced, but its positive count can be below the count of "
            "eligible lost concepts when the matching negative panel is sparse.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run all frozen arc-first concept-recovery splits for one eligible static graph."""
    args = parse_args()
    defaults = DATASET_DEFAULTS[args.dataset]
    arc_path = resolve_path(args.arcs, defaults["arcs"])
    node_path = resolve_path(args.nodes, defaults["nodes"])
    tail_column = args.tail_column or defaults["tail_column"]
    head_column = args.head_column or defaults["head_column"]
    node_column = args.node_column or defaults["node_column"]
    output_dir = (
        args.output_dir or PROJECT_ROOT / "results" / "phase2" / f"{args.dataset}_concept_recovery"
    )
    output_dir = output_dir if output_dir.is_absolute() else PROJECT_ROOT / output_dir
    prepare_output_dir(output_dir, args.overwrite)

    nodes = read_nodes(node_path, node_column)
    arcs = read_arcs(arc_path, tail_column, head_column, set(nodes))
    full_concepts = concepts_for(
        arcs, nodes, args.tail_cap, args.head_cap, args.max_concept_candidates
    )
    full_keys = {concept_key(concept) for concept in full_concepts}
    if not full_keys:
        raise SystemExit(
            "STOP: no capped full-graph concepts are available for recovery evaluation."
        )

    all_metrics: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    full_arc_set = frozenset(arcs)
    for mechanism_index, mechanism_name in enumerate(args.mechanisms):
        mechanism = MaskingMechanism(mechanism_name)
        for replicate in range(1, args.replicates + 1):
            split_seed = args.seed + mechanism_index * 1_000_000 + replicate - 1
            mask = mask_arc_first(arcs, rate=args.mask_rate, mechanism=mechanism, seed=split_seed)
            observed_arcs = tuple(sorted(mask.observed_arcs))
            observed_keys = {
                concept_key(concept)
                for concept in concepts_for(
                    observed_arcs,
                    nodes,
                    args.tail_cap,
                    args.head_cap,
                    args.max_concept_candidates,
                )
            }
            reached = weak_reachability(nodes, observed_arcs, args.max_weak_distance)
            lost_keys = tuple(sorted(full_keys - observed_keys))
            positives = tuple(
                candidate_from_key(key, 1, f"full_concept_{index:05d}")
                for index, key in enumerate(lost_keys, start=1)
                if is_local(candidate_from_key(key, 1, None), reached)
            )
            if not positives:
                raise SystemExit(
                    "STOP: no lost formal concepts remain in the observed candidate universe for "
                    f"{mechanism_name} replicate {replicate}."
                )
            outdegree, indegree = observed_degrees(nodes, observed_arcs)
            random_positives, random_negatives = random_negative_panel(
                positives, nodes, full_keys, reached, split_seed + 10_000
            )
            degree_positives, degree_negatives = degree_matched_negative_panel(
                positives,
                nodes,
                full_keys,
                reached,
                outdegree,
                indegree,
                split_seed + 20_000,
            )
            nonmaximal_positives, nonmaximal_negatives = nonmaximal_complete_panel(
                positives,
                nodes,
                observed_arcs,
                full_keys,
                reached,
                split_seed + 30_000,
            )
            split_dir = output_dir / f"{mechanism_name}_replicate_{replicate:03d}"
            split_dir.mkdir()
            write_csv(
                split_dir / "lost_positive_concepts.csv",
                [
                    {
                        "source_concept_id": item.source_concept_id,
                        "tail_nodes_json": json.dumps(item.tail),
                        "head_nodes_json": json.dumps(item.head),
                        "tail_arity": item.tail_arity,
                        "head_arity": item.head_arity,
                        "footprint_size": len(item.footprint),
                    }
                    for item in positives
                ],
            )
            panel_outputs: dict[str, dict[str, int]] = {}
            for panel_name, panel_positives, negatives in (
                ("random", random_positives, random_negatives),
                ("degree_matched", degree_positives, degree_negatives),
                ("nonmaximal_complete", nonmaximal_positives, nonmaximal_negatives),
            ):
                panel_outputs[panel_name] = {
                    "positives": len(panel_positives),
                    "negatives": len(negatives),
                }
                if not negatives:
                    continue
                rows = score_candidates(panel_positives + negatives, observed_arcs)
                for row in rows:
                    row["mechanism"] = mechanism_name
                    row["replicate"] = replicate
                    row["panel"] = panel_name
                write_csv(split_dir / f"{panel_name}_predictions.csv", rows)
                metrics = metric_rows(rows, mechanism_name, replicate, panel_name)
                write_csv(split_dir / f"{panel_name}_metrics.csv", metrics)
                all_metrics.extend(metrics)
            split_manifest: dict[str, Any] = {
                "dataset": args.dataset,
                "mechanism": mechanism_name,
                "replicate": replicate,
                "mask_accounting": asdict(mask.accounting),
                "heldout_arcs": len(mask.held_out_arcs),
                "observed_arcs": len(observed_arcs),
                "full_capped_concepts": len(full_keys),
                "observed_capped_concepts": len(observed_keys),
                "lost_full_concepts": len(lost_keys),
                "eligible_positive_concepts": len(positives),
                "candidate_universe": "weak_distance_two_observed_projection",
                "negative_panels": {
                    "random": "true non-concepts exactly matched on tail/head arity",
                    "degree_matched": "true non-concepts matched on observed role-degree deciles",
                    "nonmaximal_complete": "complete observed-footprint true non-concepts",
                },
                "negative_counts": panel_outputs,
                "scores": [
                    "already_observed_footprint",
                    "lifted_oi_mean",
                    "lifted_oo_mean",
                    "lifted_ii_mean",
                    "lifted_cn_total_mean",
                    "lifted_adamic_adar_oi_mean",
                    "lifted_adamic_adar_oo_mean",
                    "lifted_adamic_adar_ii_mean",
                    "lifted_adamic_adar_total_mean",
                ],
            }
            (split_dir / "manifest.json").write_text(
                json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            split_rows.append(
                {
                    "mechanism": mechanism_name,
                    "replicate": replicate,
                    "heldout_arcs": len(mask.held_out_arcs),
                    "observed_arcs": len(observed_arcs),
                    "lost_full_concepts": len(lost_keys),
                    "eligible_positive_concepts": len(positives),
                    "random_positive_concepts": len(random_positives),
                    "random_negative_concepts": len(random_negatives),
                    "degree_matched_positive_concepts": len(degree_positives),
                    "degree_matched_negative_concepts": len(degree_negatives),
                    "nonmaximal_complete_positive_concepts": len(nonmaximal_positives),
                    "nonmaximal_complete_negative_concepts": len(nonmaximal_negatives),
                }
            )

    summary_rows = summarise_metrics(all_metrics)
    write_csv(output_dir / "split_summary.csv", split_rows)
    if summary_rows:
        write_csv(output_dir / "metric_summary.csv", summary_rows)
    else:
        write_empty_csv(
            output_dir / "metric_summary.csv",
            [
                "mechanism",
                "panel",
                "score",
                "metric",
                "completed_replicates",
                "mean",
                "sd",
            ],
        )
    manifest = {
        "driver": "scripts/46_run_arcfirst_concept_recovery.py",
        "dataset": args.dataset,
        "target": "full_graph_formal_concepts_lost_after_arc_first_masking",
        "inputs": {
            "arcs": display_path(arc_path),
            "arcs_sha256": sha256(arc_path),
            "nodes": display_path(node_path),
            "nodes_sha256": sha256(node_path),
            "tail_column": tail_column,
            "head_column": head_column,
            "node_column": node_column,
        },
        "caps": {"tail": args.tail_cap, "head": args.head_cap},
        "masking": {
            "regime": "arc_first",
            "mechanisms": args.mechanisms,
            "requested_rate": args.mask_rate,
            "replicates_per_mechanism": args.replicates,
            "seed": args.seed,
        },
        "full_graph": {
            "nodes": len(nodes),
            "arcs": len(full_arc_set),
            "capped_concepts": len(full_keys),
        },
        "completed_splits": len(split_rows),
        "outputs": {
            "split_summary": "split_summary.csv",
            "metric_summary": "metric_summary.csv",
            "summary": "summary.md",
        },
        "interpretation": (
            "This evaluates lost formal-concept recovery with uncalibrated lifted LP scores. "
            "It does not estimate L3-C; simulation-based joint ERGM concept probabilities are a "
            "separate planned computation."
        ),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary(output_dir / "summary.md", args.dataset, len(full_keys), split_rows, summary_rows)
    print("Arc-first formal-concept recovery benchmark passed.")
    print(f"Dataset: {args.dataset}.")
    print(f"Full capped concepts: {len(full_keys):,}; completed splits: {len(split_rows):,}.")
    print(f"Output bundle: {display_path(output_dir)}")


if __name__ == "__main__":
    main()
