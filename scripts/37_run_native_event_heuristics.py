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
import hashlib
import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
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


@dataclass(frozen=True, slots=True)
class TemporalConstraints:
    """Senate-specific all-associated-date service eligibility for random negatives."""

    dates_by_event_type: dict[str, tuple[date, ...]]
    terms_by_actor: dict[str, tuple[tuple[date, date], ...]]
    sidecar_path: Path
    sidecar_sha256: str
    current_roster_path: Path
    current_roster_sha256: str
    historical_roster_path: Path
    historical_roster_sha256: str

    @property
    def service_rule(self) -> str:
        """Describe the complete half-open eligibility rule used for synthetic negatives."""
        return "term_start <= introduction_date < term_end for every associated introduction date"

    def dates_for(self, event_type_id: str) -> tuple[date, ...]:
        """Return all distinct paired-positive dates or stop on an invalid sidecar join."""
        try:
            return self.dates_by_event_type[event_type_id]
        except KeyError as error:
            raise SystemExit(
                f"STOP: temporal sidecar lacks dates for held-out event type {event_type_id!r}."
            ) from error

    def participants_serve_for_all_dates(
        self, participants: tuple[str, ...], event_type_id: str
    ) -> bool:
        """Require every candidate participant to cover every date of the paired positive type."""
        dates = self.dates_for(event_type_id)
        return all(
            any(start <= introduced < end for start, end in self.terms_by_actor.get(actor, ()))
            for actor in participants
            for introduced in dates
        )


def parse_args() -> argparse.Namespace:
    """Parse the explicit frozen-mask native-event heuristic run contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--mask-dir", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument(
        "--temporal-constraint-sidecar",
        type=Path,
        help=(
            "Optional Senate type-date sidecar. With both roster files, requires every synthetic "
            "random-negative participant to serve on every associated positive introduction date."
        ),
    )
    parser.add_argument(
        "--senate-current-roster",
        type=Path,
        help=(
            "Optional congress-legislators current JSON required with "
            "--temporal-constraint-sidecar."
        ),
    )
    parser.add_argument(
        "--senate-historical-roster",
        type=Path,
        help=(
            "Optional congress-legislators historical JSON required with "
            "--temporal-constraint-sidecar."
        ),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.max_weak_distance < 1:
        parser.error("--max-weak-distance must be at least 1.")
    if isinstance(args.seed, bool):
        parser.error("--seed must be an integer.")
    temporal_paths = (
        args.temporal_constraint_sidecar,
        args.senate_current_roster,
        args.senate_historical_roster,
    )
    if any(temporal_paths) and not all(temporal_paths):
        parser.error(
            "--temporal-constraint-sidecar, --senate-current-roster, and "
            "--senate-historical-roster must be supplied together."
        )
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


def sha256_file(path: Path) -> str:
    """Return a bounded-memory content hash for declared temporal inputs."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


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


def parse_date(value: object, description: str) -> date:
    """Parse one ISO date required by the temporal eligibility contract."""
    if not isinstance(value, str):
        raise SystemExit(f"STOP: {description} must be an ISO date string.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise SystemExit(f"STOP: invalid {description}: {value!r}") from error


def read_senate_terms(path: Path) -> dict[str, set[tuple[date, date]]]:
    """Read valid Senate intervals from one public congress-legislators JSON snapshot."""
    require_file(path, "Senate roster JSON")
    try:
        people = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: Senate roster JSON is invalid: {path}") from error
    if not isinstance(people, list):
        raise SystemExit(f"STOP: Senate roster JSON must contain a list: {path}")
    terms: dict[str, set[tuple[date, date]]] = defaultdict(set)
    for person in people:
        if not isinstance(person, dict):
            continue
        ids = person.get("id")
        identifier = ids.get("bioguide") if isinstance(ids, dict) else None
        raw_terms = person.get("terms")
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or not isinstance(raw_terms, list)
        ):
            continue
        for raw_term in raw_terms:
            if not isinstance(raw_term, dict) or raw_term.get("type") != "sen":
                continue
            start, end = raw_term.get("start"), raw_term.get("end")
            if not isinstance(start, str) or not isinstance(end, str):
                continue
            try:
                interval = date.fromisoformat(start), date.fromisoformat(end)
            except ValueError:
                continue
            if interval[0] < interval[1]:
                terms[identifier.strip()].add(interval)
    return terms


def load_temporal_constraints(
    sidecar_path: Path | None,
    current_roster_path: Path | None,
    historical_roster_path: Path | None,
    nodes: tuple[str, ...],
) -> TemporalConstraints | None:
    """Load optional Senate date and term inputs without changing generic-driver behavior."""
    if sidecar_path is None:
        return None
    if current_roster_path is None or historical_roster_path is None:
        raise RuntimeError("temporal parser validation should require both Senate roster inputs")
    for path, description in (
        (sidecar_path, "temporal-constraint sidecar"),
        (current_roster_path, "current Senate roster"),
        (historical_roster_path, "historical Senate roster"),
    ):
        require_file(path, description)
    try:
        payload = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"STOP: temporal-constraint sidecar is invalid JSON: {sidecar_path}"
        ) from error
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise SystemExit("STOP: temporal-constraint sidecar has an unsupported schema version.")
    if payload.get("service_rule") != (
        "term_start <= introduction_date < term_end for every associated date"
    ):
        raise SystemExit("STOP: temporal-constraint sidecar has an unexpected service rule.")
    rows = payload.get("event_types")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("STOP: temporal-constraint sidecar has no event-type date records.")
    dates_by_event_type: dict[str, tuple[date, ...]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit(
                "STOP: temporal-constraint sidecar contains a non-object event-type row."
            )
        event_type_id = row.get("event_type_id")
        raw_dates = row.get("introduction_dates")
        if (
            not isinstance(event_type_id, str)
            or not event_type_id
            or not isinstance(raw_dates, list)
        ):
            raise SystemExit("STOP: temporal sidecar event-type row lacks an ID or date list.")
        dates = tuple(
            sorted({parse_date(value, "sidecar introduction date") for value in raw_dates})
        )
        if not dates or event_type_id in dates_by_event_type:
            raise SystemExit(
                "STOP: temporal sidecar has an empty-date or duplicate event-type record."
            )
        dates_by_event_type[event_type_id] = dates
    terms: dict[str, set[tuple[date, date]]] = defaultdict(set)
    for source in (current_roster_path, historical_roster_path):
        for actor, intervals in read_senate_terms(source).items():
            terms[actor].update(intervals)
    missing_nodes = set(nodes) - set(terms)
    if missing_nodes:
        raise SystemExit(
            "STOP: Senate roster snapshots lack a service interval for fixed actor IDs: "
            f"{sorted(missing_nodes)[:10]}"
        )
    return TemporalConstraints(
        dates_by_event_type=dates_by_event_type,
        terms_by_actor={actor: tuple(sorted(intervals)) for actor, intervals in terms.items()},
        sidecar_path=sidecar_path,
        sidecar_sha256=sha256_file(sidecar_path),
        current_roster_path=current_roster_path,
        current_roster_sha256=sha256_file(current_roster_path),
        historical_roster_path=historical_roster_path,
        historical_roster_sha256=sha256_file(historical_roster_path),
    )


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
    candidate_id: str,
    tail: tuple[str, ...],
    head: tuple[str, ...],
    label: int,
    source_event_type_id: str | None = None,
    occurrence_count: int | None = None,
) -> Candidate:
    """Create a structurally valid synthetic evaluation candidate."""
    if not tail or not head or set(tail).intersection(head):
        raise ValueError("native-event candidates must have nonempty disjoint roles")
    return Candidate(
        candidate_id=candidate_id,
        tail=tuple(sorted(tail)),
        head=tuple(sorted(head)),
        label=label,
        source_event_type_id=source_event_type_id,
        occurrence_count=occurrence_count,
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


def temporal_negative_candidates_by_positive(
    *,
    positives: tuple[Candidate, ...],
    full_type_keys: set[tuple[tuple[str, ...], tuple[str, ...]]],
    nodes: tuple[str, ...],
    reachable: dict[str, frozenset[str]],
    seed: int,
    constraints: TemporalConstraints,
) -> tuple[tuple[Candidate, ...], dict[str, int]]:
    """Sample one date-feasible non-event per positive while retaining its identity pairing.

    This Senate-only path deliberately iterates over positives rather than arity
    groups. Each accepted negative therefore has a deterministic source type ID
    and inherits every distinct introduction date associated with that type.
    """
    random = Random(seed)
    negatives: list[Candidate] = []
    used_keys: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    audit: defaultdict[str, int] = defaultdict(int)
    node_count = len(nodes)
    for positive in positives:
        if positive.source_event_type_id is None:
            raise RuntimeError("held-out positives must carry their frozen event-type IDs")
        tail_size, head_size = positive.tail_arity, positive.head_arity
        if tail_size + head_size > node_count:
            raise SystemExit("STOP: requested candidate arity exceeds the fixed node universe.")
        constraints.dates_for(positive.source_event_type_id)
        maximum_attempts = max(100_000, 5_000)
        accepted = False
        for _attempt in range(maximum_attempts):
            audit["attempts"] += 1
            sampled = random.sample(nodes, tail_size + head_size)
            candidate = candidate_from_roles(
                candidate_id=f"negative_for_{positive.source_event_type_id}",
                tail=tuple(sampled[:tail_size]),
                head=tuple(sampled[tail_size:]),
                label=0,
                source_event_type_id=positive.source_event_type_id,
                occurrence_count=positive.occurrence_count,
            )
            if candidate.key in full_type_keys:
                audit["rejected_known_event_type"] += 1
                continue
            if candidate.key in used_keys:
                audit["rejected_duplicate_negative"] += 1
                continue
            if not is_local_candidate(candidate, reachable):
                audit["rejected_nonlocal"] += 1
                continue
            if not constraints.participants_serve_for_all_dates(
                candidate.tail + candidate.head, positive.source_event_type_id
            ):
                audit["rejected_temporal_service"] += 1
                continue
            used_keys.add(candidate.key)
            negatives.append(candidate)
            audit["accepted"] += 1
            accepted = True
            break
        if not accepted:
            raise SystemExit(
                "STOP: insufficient unique local all-date service-feasible random negatives for "
                f"positive {positive.source_event_type_id} after {maximum_attempts:,} attempts."
            )
    audit["positive_types_paired"] = len(positives)
    return tuple(negatives), dict(sorted(audit.items()))


def candidate_rows(
    candidates: tuple[Candidate, ...],
    observed_arcs: frozenset[tuple[str, str]],
    party_by_node: dict[str, str] | None = None,
    temporal_constraints: TemporalConstraints | None = None,
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
        row: dict[str, object] = {
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
        if party_by_node is not None:
            if set(candidate.tail + candidate.head) - set(party_by_node):
                raise ValueError("party baseline is missing a candidate participant")
            row["lifted_same_party_mean"] = mean(
                int(party_by_node[tail] == party_by_node[head])
                for tail, head in candidate.footprint
            )
        if temporal_constraints is not None:
            if candidate.source_event_type_id is None:
                raise RuntimeError("temporal candidate rows require a paired source event-type ID")
            dates = temporal_constraints.dates_for(candidate.source_event_type_id)
            row.update(
                {
                    "paired_source_event_type_id": candidate.source_event_type_id,
                    "paired_introduction_dates_json": json.dumps(
                        [introduced.isoformat() for introduced in dates]
                    ),
                    "temporal_service_rule": temporal_constraints.service_rule,
                    "temporal_rule_applies_to_synthetic_negative": int(candidate.label == 0),
                    "all_date_service_eligible": int(
                        temporal_constraints.participants_serve_for_all_dates(
                            candidate.tail + candidate.head, candidate.source_event_type_id
                        )
                    ),
                }
            )
        rows.append(row)
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
    temporal_constraints: TemporalConstraints | None,
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
    if temporal_constraints is not None:
        type_rows[7:7] = [
            "- Senate temporal rule: each synthetic negative is paired with one held-out positive "
            "event type and every participant must serve on every distinct associated Bill Status "
            "introduction date under half-open roster intervals.",
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
    nodes = read_nodes(nodes_path, args.node_column)
    temporal_constraints = load_temporal_constraints(
        (
            resolve_path(args.temporal_constraint_sidecar)
            if args.temporal_constraint_sidecar
            else None
        ),
        resolve_path(args.senate_current_roster) if args.senate_current_roster else None,
        resolve_path(args.senate_historical_roster) if args.senate_historical_roster else None,
        nodes,
    )
    prepare_output_dir(output_dir, args.overwrite)
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
        if temporal_constraints is None:
            negatives = negative_candidates_by_arity(
                positives=eligible_positives,
                full_type_keys={candidate.key for candidate in observed_types + heldout_types},
                nodes=nodes,
                reachable=reachable,
                seed=split_seed,
            )
            temporal_audit: dict[str, int] | None = None
        else:
            negatives, temporal_audit = temporal_negative_candidates_by_positive(
                positives=eligible_positives,
                full_type_keys={candidate.key for candidate in observed_types + heldout_types},
                nodes=nodes,
                reachable=reachable,
                seed=split_seed,
                constraints=temporal_constraints,
            )
        predictions = candidate_rows(
            eligible_positives + negatives,
            observed_arcs,
            temporal_constraints=temporal_constraints,
        )
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
        if temporal_constraints is not None and temporal_audit is not None:
            split_manifest["temporal_random_negative_eligibility"] = {
                "paired_positive": "one held-out event type per synthetic negative",
                "service_rule": temporal_constraints.service_rule,
                "all_associated_introduction_dates": True,
                **temporal_audit,
            }
        (split_output / "manifest.json").write_text(
            json.dumps(split_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        all_split_metrics.extend(metrics)
        summary_row: dict[str, object] = {
            "mechanism": mechanism,
            "replicate": replicate,
            "heldout_event_types": len(heldout_types),
            "eligible_positive_types": len(eligible_positives),
            "positive_eligibility_rate": len(eligible_positives) / len(heldout_types),
            "random_negative_types": len(negatives),
            "candidate_panel_size": len(predictions),
            "observed_projection_arcs": len(observed_arcs),
        }
        if temporal_audit is not None:
            summary_row.update(
                {
                    "temporal_sampling_attempts": temporal_audit["attempts"],
                    "temporal_service_rejections": temporal_audit.get(
                        "rejected_temporal_service", 0
                    ),
                    "temporal_service_accepted": temporal_audit["accepted"],
                }
            )
        split_summary_rows.append(summary_row)

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
    if temporal_constraints is not None:
        manifest["temporal_random_negative_eligibility"] = {
            "status": "enabled",
            "scope": (
                "synthetic random negative candidates only; frozen positives and masks unchanged"
            ),
            "paired_positive": "one deterministic paired_source_event_type_id per negative",
            "service_rule": temporal_constraints.service_rule,
            "all_associated_introduction_dates": True,
            "inputs": {
                "sidecar": {
                    "path": recorded_path(temporal_constraints.sidecar_path),
                    "sha256": temporal_constraints.sidecar_sha256,
                },
                "current_roster": {
                    "path": recorded_path(temporal_constraints.current_roster_path),
                    "sha256": temporal_constraints.current_roster_sha256,
                },
                "historical_roster": {
                    "path": recorded_path(temporal_constraints.historical_roster_path),
                    "sha256": temporal_constraints.historical_roster_sha256,
                },
            },
        }
    else:
        manifest["temporal_random_negative_eligibility"] = {"status": "not_requested"}
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary_markdown(
        output_dir / "summary.md",
        args.dataset_id,
        split_summary_rows,
        summary_rows,
        temporal_constraints,
    )
    print("Event-first native-event heuristic benchmark passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Frozen splits completed: {len(split_summary_rows):,}.")
    print(f"Output bundle: {recorded_path(output_dir)}")


if __name__ == "__main__":
    main()
