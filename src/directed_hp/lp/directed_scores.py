"""Deterministic local scores for simple directed link prediction.

The direction convention for a candidate arc ``source -> target`` is:

* **OI** (or two-path): ``N_out(source) ∩ N_in(target)``;
* **OO** (or shared-target): ``N_out(source) ∩ N_out(target)``;
* **II** (or shared-source): ``N_in(source) ∩ N_in(target)``.

Inputs represent a simple directed graph.  Self-loops in an input iterable are
ignored, and candidate self-loops are never emitted or scored.  The score engine
uses only its supplied arcs; in particular, the lagged functions deliberately
receive *only* a previous-window arc set.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from math import log
from types import MappingProxyType
from typing import TypeAlias

Node: TypeAlias = Hashable
Arc: TypeAlias = tuple[Node, Node]


@dataclass(frozen=True)
class CommonNeighborCounts:
    """The three directed common-neighbor components for one candidate arc."""

    oi: int
    oo: int
    ii: int

    @property
    def total(self) -> int:
        """Return the ttriple-compatible sum ``OI + OO + II``."""
        return self.oi + self.oo + self.ii


@dataclass(frozen=True)
class AdamicAdarComponents:
    """Componentwise directed Adamic--Adar scores for one candidate arc."""

    oi: float
    oo: float
    ii: float

    @property
    def total(self) -> float:
        """Return the sum of the three directed Adamic--Adar components."""
        return self.oi + self.oo + self.ii


@dataclass(frozen=True)
class DirectedScore:
    """Count and Adamic--Adar components for a directed candidate arc."""

    common_neighbors: CommonNeighborCounts
    adamic_adar: AdamicAdarComponents

    @property
    def total(self) -> int:
        """Return the unweighted common-neighbor total."""
        return self.common_neighbors.total

    @property
    def adamic_adar_total(self) -> float:
        """Return the total Adamic--Adar score."""
        return self.adamic_adar.total


def _node_sort_key(node: Node) -> tuple[str, str, str]:
    """Provide a stable ordering for heterogeneous hashable node labels."""
    node_type = type(node)
    return (node_type.__module__, node_type.__qualname__, repr(node))


def _unique_nodes(nodes: Iterable[Node]) -> tuple[Node, ...]:
    """Deduplicate nodes while retaining the caller's explicit order."""
    unique: dict[Node, None] = {}
    for node in nodes:
        unique[node] = None
    return tuple(unique)


def _normalise_arcs(arcs: Iterable[Arc]) -> frozenset[Arc]:
    """Return loop-free, unique arcs and give malformed arcs a clear error."""
    normalised: set[Arc] = set()
    for arc in arcs:
        try:
            source, target = arc
        except (TypeError, ValueError) as error:
            raise ValueError("each arc must contain exactly a source and target") from error
        if source != target:
            normalised.add((source, target))
    return frozenset(normalised)


def adamic_adar_weight(degree: int) -> float:
    """Return ``1 / log(degree)`` for degree greater than one, otherwise zero.

    A zero- or one-degree node receives a zero contribution rather than an
    undefined or infinite weight.  In a loop-free graph, a valid common
    neighbor normally has the relevant degree at least two; this rule makes
    the behavior explicit for sparse or externally supplied degree values.
    """
    if degree <= 1:
        return 0.0
    return 1.0 / log(degree)


class DirectedScoreEngine:
    """Precompute directed neighborhoods for deterministic local scoring.

    Parameters
    ----------
    arcs:
        Directed arcs from the graph snapshot being scored.  Duplicate arcs and
        loops are discarded.
    nodes:
        Optional nodes, including isolates.  Nodes not listed here but found in
        ``arcs`` are retained.  Explicit node order is preserved for candidate
        enumeration; inferred nodes are sorted by type and representation.
    """

    def __init__(self, arcs: Iterable[Arc], *, nodes: Iterable[Node] | None = None) -> None:
        self.arcs = _normalise_arcs(arcs)
        arc_nodes = {node for arc in self.arcs for node in arc}

        supplied_nodes = _unique_nodes(nodes) if nodes is not None else ()
        supplied_set = set(supplied_nodes)
        inferred_nodes = sorted(arc_nodes - supplied_set, key=_node_sort_key)
        self.nodes = supplied_nodes + tuple(inferred_nodes)

        out_neighbors: dict[Node, set[Node]] = {node: set() for node in self.nodes}
        in_neighbors: dict[Node, set[Node]] = {node: set() for node in self.nodes}
        for source, target in self.arcs:
            out_neighbors[source].add(target)
            in_neighbors[target].add(source)

        self.out_neighbors: Mapping[Node, frozenset[Node]] = MappingProxyType(
            {node: frozenset(neighbors) for node, neighbors in out_neighbors.items()}
        )
        self.in_neighbors: Mapping[Node, frozenset[Node]] = MappingProxyType(
            {node: frozenset(neighbors) for node, neighbors in in_neighbors.items()}
        )

    def _require_nonloop_candidate(self, source: Node, target: Node) -> None:
        if source == target:
            raise ValueError("self-loops are not valid directed LP candidates")

    def _out(self, node: Node) -> frozenset[Node]:
        return self.out_neighbors.get(node, frozenset())

    def _in(self, node: Node) -> frozenset[Node]:
        return self.in_neighbors.get(node, frozenset())

    def oi_neighbors(self, source: Node, target: Node) -> frozenset[Node]:
        """Return OI/two-path intermediates for ``source -> target``."""
        self._require_nonloop_candidate(source, target)
        return self._out(source) & self._in(target)

    two_path_neighbors = oi_neighbors

    def oo_neighbors(self, source: Node, target: Node) -> frozenset[Node]:
        """Return OO/shared-target neighbors for ``source -> target``."""
        self._require_nonloop_candidate(source, target)
        return self._out(source) & self._out(target)

    shared_target_neighbors = oo_neighbors

    def ii_neighbors(self, source: Node, target: Node) -> frozenset[Node]:
        """Return II/shared-source neighbors for ``source -> target``."""
        self._require_nonloop_candidate(source, target)
        return self._in(source) & self._in(target)

    shared_source_neighbors = ii_neighbors

    def oi_count(self, source: Node, target: Node) -> int:
        """Return the OI/two-path common-neighbor count."""
        return len(self.oi_neighbors(source, target))

    two_path_count = oi_count

    def oo_count(self, source: Node, target: Node) -> int:
        """Return the OO/shared-target common-neighbor count."""
        return len(self.oo_neighbors(source, target))

    shared_target_count = oo_count

    def ii_count(self, source: Node, target: Node) -> int:
        """Return the II/shared-source common-neighbor count."""
        return len(self.ii_neighbors(source, target))

    shared_source_count = ii_count

    def common_neighbor_counts(self, source: Node, target: Node) -> CommonNeighborCounts:
        """Return the OI, OO, and II counts for a candidate arc."""
        return CommonNeighborCounts(
            oi=self.oi_count(source, target),
            oo=self.oo_count(source, target),
            ii=self.ii_count(source, target),
        )

    def common_neighbor_total(self, source: Node, target: Node) -> int:
        """Return ``OI + OO + II`` for a candidate arc."""
        return self.common_neighbor_counts(source, target).total

    def oi_adamic_adar(self, source: Node, target: Node) -> float:
        """Weight two-path intermediates by their total directed degree."""
        return sum(
            adamic_adar_weight(len(self._in(node)) + len(self._out(node)))
            for node in self.oi_neighbors(source, target)
        )

    adamic_adar_oi = oi_adamic_adar
    two_path_adamic_adar = oi_adamic_adar

    def oo_adamic_adar(self, source: Node, target: Node) -> float:
        """Weight shared targets by their in-degree (target popularity)."""
        return sum(
            adamic_adar_weight(len(self._in(node))) for node in self.oo_neighbors(source, target)
        )

    adamic_adar_oo = oo_adamic_adar
    shared_target_adamic_adar = oo_adamic_adar

    def ii_adamic_adar(self, source: Node, target: Node) -> float:
        """Weight shared sources by their out-degree (source broadcast degree)."""
        return sum(
            adamic_adar_weight(len(self._out(node))) for node in self.ii_neighbors(source, target)
        )

    adamic_adar_ii = ii_adamic_adar
    shared_source_adamic_adar = ii_adamic_adar

    def adamic_adar_components(self, source: Node, target: Node) -> AdamicAdarComponents:
        """Return componentwise directed Adamic--Adar scores."""
        return AdamicAdarComponents(
            oi=self.oi_adamic_adar(source, target),
            oo=self.oo_adamic_adar(source, target),
            ii=self.ii_adamic_adar(source, target),
        )

    def adamic_adar_total(self, source: Node, target: Node) -> float:
        """Return the sum of the three directed Adamic--Adar components."""
        return self.adamic_adar_components(source, target).total

    def score(self, source: Node, target: Node) -> DirectedScore:
        """Return all count and Adamic--Adar components for one candidate arc."""
        return DirectedScore(
            common_neighbors=self.common_neighbor_counts(source, target),
            adamic_adar=self.adamic_adar_components(source, target),
        )

    def _candidate_nodes(self, nodes: Iterable[Node] | None) -> tuple[Node, ...]:
        if nodes is None:
            return self.nodes
        supplied_nodes = _unique_nodes(nodes)
        supplied_set = set(supplied_nodes)
        missing_graph_nodes = sorted(set(self.nodes) - supplied_set, key=_node_sort_key)
        return supplied_nodes + tuple(missing_graph_nodes)

    def candidate_dyads(
        self,
        *,
        nodes: Iterable[Node] | None = None,
        exclude_existing: bool = True,
    ) -> tuple[Arc, ...]:
        """Enumerate non-loop dyads, excluding observed arcs by default."""
        candidate_nodes = self._candidate_nodes(nodes)
        return tuple(
            (source, target)
            for source in candidate_nodes
            for target in candidate_nodes
            if source != target and (not exclude_existing or (source, target) not in self.arcs)
        )

    def score_candidates(
        self,
        candidates: Iterable[Arc] | None = None,
        *,
        nodes: Iterable[Node] | None = None,
        exclude_existing: bool = True,
    ) -> dict[Arc, DirectedScore]:
        """Score non-loop candidate dyads using this engine's graph snapshot.

        With ``candidates=None`` every eligible ordered dyad among ``nodes`` is
        scored.  Explicit self-loop candidates are skipped, which ensures the
        returned mapping contains only non-loop dyads.
        """
        if candidates is None:
            candidate_arcs: Iterable[Arc] = self.candidate_dyads(
                nodes=nodes, exclude_existing=exclude_existing
            )
        else:
            candidate_arcs = candidates

        scores: dict[Arc, DirectedScore] = {}
        for candidate in candidate_arcs:
            try:
                source, target = candidate
            except (TypeError, ValueError) as error:
                message = "each candidate must contain exactly a source and target"
                raise ValueError(message) from error
            if source == target:
                continue
            if exclude_existing and (source, target) in self.arcs:
                continue
            scores[(source, target)] = self.score(source, target)
        return scores


def oi_count(arcs: Iterable[Arc], source: Node, target: Node) -> int:
    """Return the OI/two-path count for ``source -> target``."""
    return DirectedScoreEngine(arcs).oi_count(source, target)


def oo_count(arcs: Iterable[Arc], source: Node, target: Node) -> int:
    """Return the OO/shared-target count for ``source -> target``."""
    return DirectedScoreEngine(arcs).oo_count(source, target)


def ii_count(arcs: Iterable[Arc], source: Node, target: Node) -> int:
    """Return the II/shared-source count for ``source -> target``."""
    return DirectedScoreEngine(arcs).ii_count(source, target)


def common_neighbor_counts(arcs: Iterable[Arc], source: Node, target: Node) -> CommonNeighborCounts:
    """Return all directed common-neighbor count components."""
    return DirectedScoreEngine(arcs).common_neighbor_counts(source, target)


def common_neighbor_total(arcs: Iterable[Arc], source: Node, target: Node) -> int:
    """Return the ttriple-compatible common-neighbor sum."""
    return DirectedScoreEngine(arcs).common_neighbor_total(source, target)


def adamic_adar_components(arcs: Iterable[Arc], source: Node, target: Node) -> AdamicAdarComponents:
    """Return all componentwise directed Adamic--Adar scores."""
    return DirectedScoreEngine(arcs).adamic_adar_components(source, target)


def adamic_adar_total(arcs: Iterable[Arc], source: Node, target: Node) -> float:
    """Return the summed directed Adamic--Adar score."""
    return DirectedScoreEngine(arcs).adamic_adar_total(source, target)


def score_candidates(
    arcs: Iterable[Arc],
    candidates: Iterable[Arc] | None = None,
    *,
    nodes: Iterable[Node] | None = None,
    exclude_existing: bool = True,
) -> dict[Arc, DirectedScore]:
    """Build an engine from ``arcs`` and score its non-loop candidate dyads."""
    return DirectedScoreEngine(arcs, nodes=nodes).score_candidates(
        candidates, exclude_existing=exclude_existing
    )


def ttriple_statistic(arcs: Iterable[Arc]) -> int:
    """Return ``sum_ijk y_ij * y_ik * y_kj`` for the loop-free digraph.

    Equivalently, this sums OI/two-path closures over every observed arc.  It is
    the directed transitive-triple statistic whose single-arc change statistic
    decomposes into OI, OO, and II components.
    """
    engine = DirectedScoreEngine(arcs)
    return sum(engine.oi_count(source, target) for source, target in engine.arcs)


def ttriple_toggle_change(arcs: Iterable[Arc], source: Node, target: Node) -> int:
    """Return the ttriple change from toggling the non-loop arc ``source -> target``.

    For an absent arc this equals its current ``OI + OO + II`` total.  For a
    present arc it is the negative total evaluated after removing that arc.
    """
    engine = DirectedScoreEngine(arcs)
    engine._require_nonloop_candidate(source, target)
    candidate = (source, target)
    if candidate not in engine.arcs:
        return engine.common_neighbor_total(source, target)

    reduced_arcs = engine.arcs - {candidate}
    reduced_engine = DirectedScoreEngine(reduced_arcs, nodes=engine.nodes)
    return -reduced_engine.common_neighbor_total(source, target)


ttriple_change_statistic = ttriple_toggle_change


def lagged_score_candidate(
    previous_window_arcs: Iterable[Arc],
    source: Node,
    target: Node,
    *,
    nodes: Iterable[Node] | None = None,
) -> DirectedScore:
    """Score one dyad strictly from a previous-window directed arc set.

    This function accepts no current- or future-window arcs, preventing temporal
    leakage by construction.
    """
    return DirectedScoreEngine(previous_window_arcs, nodes=nodes).score(source, target)


def lagged_score_candidates(
    previous_window_arcs: Iterable[Arc],
    candidates: Iterable[Arc] | None = None,
    *,
    nodes: Iterable[Node] | None = None,
    exclude_existing: bool = True,
) -> dict[Arc, DirectedScore]:
    """Deterministically score candidate dyads from previous-window arcs only."""
    return score_candidates(
        previous_window_arcs,
        candidates,
        nodes=nodes,
        exclude_existing=exclude_existing,
    )


lagged_candidate_scores = lagged_score_candidates
two_path_count = oi_count
shared_target_count = oo_count
shared_source_count = ii_count
