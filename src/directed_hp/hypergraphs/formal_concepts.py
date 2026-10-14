"""Deterministic formal-concept sections for finite directed arc relations.

For a directed relation ``R`` on nodes ``V``, a non-empty directed formal
concept is a pair ``(T, H)`` satisfying

``H = successors(T)`` and ``T = predecessors(H)``,

where ``successors(T)`` are the common successors of every member of ``T``
and ``predecessors(H)`` are the common predecessors of every member of ``H``.
Its footprint is the complete directed rectangle ``T x H``.  Consequently,
the union of all uncapped concept footprints reconstructs ``R`` (Proposition
1): every observed arc belongs to at least one such concept.

The enumerator is deliberately cap-first.  It generates only candidate tails
or heads whose arity is within the requested bound, then computes their
Galois closure; it never enumerates all concepts and filters them afterwards.
For a core-100 graph callers should set at least one small arity cap.  Formal
concept enumeration can be exponential, so this module refuses an enumeration
whose *candidate* seed count exceeds ``max_candidates`` rather than returning
a silent partial section.  A capped formal-concept section need not reconstruct
the whole relation; :func:`augmented_section` restores every observed arc by
adding its singleton tail/head pair.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Iterator
from dataclasses import dataclass
from itertools import combinations, product
from math import comb
from typing import TypeAlias

Node: TypeAlias = Hashable
Arc: TypeAlias = tuple[Node, Node]


@dataclass(frozen=True, slots=True)
class DirectedFormalConcept:
    """An immutable, canonically ordered non-empty formal concept.

    ``tail`` and ``head`` are tuples so that concepts are hashable and safe to
    use in sets or as dictionary keys.  Instances emitted by this module are
    closed under the predecessor-successor Galois connection.
    """

    tail: tuple[Node, ...]
    head: tuple[Node, ...]

    @property
    def footprint(self) -> frozenset[Arc]:
        """Return the directed Cartesian footprint ``tail x head``."""

        return frozenset(product(self.tail, self.head))


# A concise public spelling for use where the module already establishes the
# directed relation context.
FormalConcept = DirectedFormalConcept


@dataclass(frozen=True, slots=True)
class _Relation:
    """Canonical finite relation plus its predecessor/successor indexes."""

    arcs: frozenset[Arc]
    nodes: tuple[Node, ...]
    successors_by_node: dict[Node, frozenset[Node]]
    predecessors_by_node: dict[Node, frozenset[Node]]


def _node_sort_key(node: Node) -> tuple[str, str, str]:
    """Provide a reproducible fallback key when node types cannot be compared."""

    node_type = type(node)
    return (node_type.__module__, node_type.__qualname__, repr(node))


def _ordered_nodes(nodes: Iterable[Node]) -> tuple[Node, ...]:
    """Deduplicate and deterministically order hashable node labels."""

    values = set(nodes)
    try:
        return tuple(sorted(values))
    except TypeError:
        return tuple(sorted(values, key=_node_sort_key))


def _concept_sort_key(
    concept: DirectedFormalConcept,
) -> tuple[tuple[tuple[str, str, str], ...], tuple[tuple[str, str, str], ...]]:
    """Order concepts independently of input arc order and node comparability."""

    return (
        tuple(_node_sort_key(node) for node in concept.tail),
        tuple(_node_sort_key(node) for node in concept.head),
    )


def _normalise_relation(arcs: Iterable[Arc], nodes: Iterable[Node] | None = None) -> _Relation:
    """Materialize and index an arc relation once, rejecting malformed arcs."""

    relation: set[Arc] = set()
    supplied_nodes: list[Node] = [] if nodes is None else list(nodes)
    for arc in arcs:
        try:
            source, destination = arc
        except (TypeError, ValueError) as error:
            raise TypeError("Each directed arc must contain exactly two node labels.") from error
        try:
            hash(source)
            hash(destination)
        except TypeError as error:
            raise TypeError("Directed arc node labels must be hashable.") from error
        relation.add((source, destination))
        supplied_nodes.extend((source, destination))

    ordered_nodes = _ordered_nodes(supplied_nodes)
    successors = {node: set() for node in ordered_nodes}
    predecessors = {node: set() for node in ordered_nodes}
    for source, destination in relation:
        successors[source].add(destination)
        predecessors[destination].add(source)

    return _Relation(
        arcs=frozenset(relation),
        nodes=ordered_nodes,
        successors_by_node={node: frozenset(values) for node, values in successors.items()},
        predecessors_by_node={node: frozenset(values) for node, values in predecessors.items()},
    )


def _common_successors(tail: Iterable[Node], relation: _Relation) -> tuple[Node, ...]:
    """Return nodes reached by every tail node, with the FCA empty-set rule."""

    tail_nodes = tuple(tail)
    if not tail_nodes:
        return relation.nodes
    common: set[Node] | None = None
    for node in tail_nodes:
        neighbours = relation.successors_by_node.get(node, frozenset())
        common = set(neighbours) if common is None else common.intersection(neighbours)
        if not common:
            return ()
    return _ordered_nodes(common or ())


def _common_predecessors(head: Iterable[Node], relation: _Relation) -> tuple[Node, ...]:
    """Return nodes reaching every head node, with the FCA empty-set rule."""

    head_nodes = tuple(head)
    if not head_nodes:
        return relation.nodes
    common: set[Node] | None = None
    for node in head_nodes:
        neighbours = relation.predecessors_by_node.get(node, frozenset())
        common = set(neighbours) if common is None else common.intersection(neighbours)
        if not common:
            return ()
    return _ordered_nodes(common or ())


def common_successors(
    tail: Iterable[Node], arcs: Iterable[Arc], *, nodes: Iterable[Node] | None = None
) -> tuple[Node, ...]:
    """Return the successor derivation ``tail'`` in the directed Galois connection."""

    return _common_successors(tail, _normalise_relation(arcs, nodes))


def common_predecessors(
    head: Iterable[Node], arcs: Iterable[Arc], *, nodes: Iterable[Node] | None = None
) -> tuple[Node, ...]:
    """Return the predecessor derivation ``head'`` in the directed Galois connection."""

    return _common_predecessors(head, _normalise_relation(arcs, nodes))


def tail_closure(
    tail: Iterable[Node], arcs: Iterable[Arc], *, nodes: Iterable[Node] | None = None
) -> tuple[Node, ...]:
    """Return ``tail'' = predecessors(successors(tail))``."""

    relation = _normalise_relation(arcs, nodes)
    return _common_predecessors(_common_successors(tail, relation), relation)


def head_closure(
    head: Iterable[Node], arcs: Iterable[Arc], *, nodes: Iterable[Node] | None = None
) -> tuple[Node, ...]:
    """Return ``head'' = successors(predecessors(head))``."""

    relation = _normalise_relation(arcs, nodes)
    return _common_successors(_common_predecessors(head, relation), relation)


def _validate_cap(cap: int | None, name: str) -> int | None:
    """Validate a non-negative arity cap without conflating zero and no cap."""

    if cap is None:
        return None
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 0:
        raise ValueError(f"{name} must be a non-negative integer or None.")
    return cap


def _seed_count(size: int, cap: int | None) -> int:
    """Count non-empty seed subsets, stopping only after exact arithmetic."""

    upper = size if cap is None else min(size, cap)
    return sum(comb(size, arity) for arity in range(1, upper + 1))


def _seed_subsets(nodes: tuple[Node, ...], cap: int | None) -> Iterator[tuple[Node, ...]]:
    """Yield canonical, non-empty seed subsets up to a requested arity cap."""

    upper = len(nodes) if cap is None else min(len(nodes), cap)
    for arity in range(1, upper + 1):
        yield from combinations(nodes, arity)


def _validate_formal_concepts(
    concepts: Iterable[DirectedFormalConcept], relation: _Relation
) -> None:
    """Check closure, canonical tuple order, and observed footprint for concepts."""

    for concept in concepts:
        if not isinstance(concept, DirectedFormalConcept):
            raise TypeError("Concepts must be DirectedFormalConcept instances.")
        if not concept.tail or not concept.head:
            raise ValueError("A emitted formal concept must have non-empty tail and head.")
        if concept.tail != _ordered_nodes(concept.tail) or concept.head != _ordered_nodes(
            concept.head
        ):
            raise ValueError("Concept tails and heads must be unique, canonical ordered tuples.")
        expected_head = _common_successors(concept.tail, relation)
        expected_tail = _common_predecessors(concept.head, relation)
        if concept.head != expected_head or concept.tail != expected_tail:
            raise ValueError("Concept is not closed under predecessor-successor derivation.")
        if not concept.footprint <= relation.arcs:
            raise ValueError("Concept footprint contains an unobserved directed arc.")


def validate_concepts(
    concepts: Iterable[DirectedFormalConcept],
    arcs: Iterable[Arc],
    *,
    nodes: Iterable[Node] | None = None,
) -> None:
    """Raise if a formal concept is not closed or its footprint is not observed.

    This validation is applied to every concept emitted by
    :func:`enumerate_formal_concepts`.  Singleton pairs added by
    :func:`augmented_section` are observed hyperarcs, not necessarily formal
    concepts: an observed arc need not itself be Galois-closed.
    """

    _validate_formal_concepts(concepts, _normalise_relation(arcs, nodes))


def _validate_observed_pairs(pairs: Iterable[DirectedFormalConcept], relation: _Relation) -> None:
    """Verify that general non-empty tail/head pairs have observed footprints."""

    for pair in pairs:
        if not pair.tail or not pair.head:
            raise ValueError("A section pair must have non-empty tail and head.")
        if pair.tail != _ordered_nodes(pair.tail) or pair.head != _ordered_nodes(pair.head):
            raise ValueError("Section tails and heads must be unique, canonical ordered tuples.")
        if not pair.footprint <= relation.arcs:
            raise ValueError("Section pair footprint contains an unobserved directed arc.")


def _closed_concept_from_tail(
    tail: tuple[Node, ...], relation: _Relation
) -> DirectedFormalConcept | None:
    """Close a candidate tail, excluding empty-footprint concepts."""

    head = _common_successors(tail, relation)
    if not head:
        return None
    closed_tail = _common_predecessors(head, relation)
    if not closed_tail:
        return None
    return DirectedFormalConcept(closed_tail, head)


def _closed_concept_from_head(
    head: tuple[Node, ...], relation: _Relation
) -> DirectedFormalConcept | None:
    """Close a candidate head, excluding empty-footprint concepts."""

    tail = _common_predecessors(head, relation)
    if not tail:
        return None
    closed_head = _common_successors(tail, relation)
    if not closed_head:
        return None
    return DirectedFormalConcept(tail, closed_head)


def enumerate_formal_concepts(
    arcs: Iterable[Arc],
    *,
    nodes: Iterable[Node] | None = None,
    max_tail_arity: int | None = None,
    max_head_arity: int | None = None,
    max_candidates: int = 1_000_000,
) -> tuple[DirectedFormalConcept, ...]:
    """Enumerate deterministic non-empty directed formal concepts.

    Both arity caps constrain concepts included in the returned section.  The
    chosen cap is also applied *before closure* to candidate tail/head seeds.
    If both are set, the smaller candidate family is used, which retains every
    concept satisfying both caps.  ``max_candidates`` guards the exponential
    search and raises :class:`ValueError` before work starts rather than
    returning a partial result.

    Args:
        arcs: Iterable of ``(source, destination)`` pairs. Duplicate arcs are
            ignored; direction and self-loops are preserved.
        nodes: Optional additional nodes defining the FCA universe. They only
            affect empty-set derivations; emitted concepts have both sides
            non-empty.
        max_tail_arity: Largest emitted tail cardinality, or ``None``.
        max_head_arity: Largest emitted head cardinality, or ``None``.
        max_candidates: Maximum candidate subsets to generate. For core-100,
            use small arity caps (for example 2 or 3) or a larger explicit
            budget after profiling; unbounded enumeration is exponential.
    """

    tail_cap = _validate_cap(max_tail_arity, "max_tail_arity")
    head_cap = _validate_cap(max_head_arity, "max_head_arity")
    if (
        isinstance(max_candidates, bool)
        or not isinstance(max_candidates, int)
        or max_candidates < 1
    ):
        raise ValueError("max_candidates must be a positive integer.")

    relation = _normalise_relation(arcs, nodes)
    if not relation.arcs or tail_cap == 0 or head_cap == 0:
        return ()

    tail_seeds = tuple(node for node in relation.nodes if relation.successors_by_node[node])
    head_seeds = tuple(node for node in relation.nodes if relation.predecessors_by_node[node])
    tail_seed_count = _seed_count(len(tail_seeds), tail_cap)
    head_seed_count = _seed_count(len(head_seeds), head_cap)

    # A bounded side is sufficient to generate every admissible closed pair.
    # Choosing the smaller family reduces work without changing the result.
    enumerate_tails = tail_seed_count <= head_seed_count
    seed_count = tail_seed_count if enumerate_tails else head_seed_count
    if seed_count > max_candidates:
        side = "tail" if enumerate_tails else "head"
        raise ValueError(
            f"{side} candidate count {seed_count:,} exceeds max_candidates={max_candidates:,}; "
            "use a smaller arity cap or an explicit larger budget."
        )

    concepts: set[DirectedFormalConcept] = set()
    if enumerate_tails:
        for tail in _seed_subsets(tail_seeds, tail_cap):
            concept = _closed_concept_from_tail(tail, relation)
            if concept is None:
                continue
            if head_cap is not None and len(concept.head) > head_cap:
                continue
            if tail_cap is not None and len(concept.tail) > tail_cap:
                continue
            concepts.add(concept)
    else:
        for head in _seed_subsets(head_seeds, head_cap):
            concept = _closed_concept_from_head(head, relation)
            if concept is None:
                continue
            if tail_cap is not None and len(concept.tail) > tail_cap:
                continue
            if head_cap is not None and len(concept.head) > head_cap:
                continue
            concepts.add(concept)

    ordered_concepts = tuple(sorted(concepts, key=_concept_sort_key))
    _validate_formal_concepts(ordered_concepts, relation)
    return ordered_concepts


def formal_concept_section(
    arcs: Iterable[Arc],
    **kwargs: object,
) -> tuple[DirectedFormalConcept, ...]:
    """Return the formal-concept section; a named alias for the enumerator."""

    return enumerate_formal_concepts(arcs, **kwargs)  # type: ignore[arg-type]


def reconstruct_relation(concepts: Iterable[DirectedFormalConcept]) -> frozenset[Arc]:
    """Return the union of the supplied tail/head footprints."""

    return frozenset(arc for concept in concepts for arc in concept.footprint)


def augmented_section(
    arcs: Iterable[Arc],
    *,
    nodes: Iterable[Node] | None = None,
    max_tail_arity: int | None = None,
    max_head_arity: int | None = None,
    max_candidates: int = 1_000_000,
) -> tuple[DirectedFormalConcept, ...]:
    """Return capped formal concepts plus every observed singleton directed arc.

    The formal-concept portion is first validated as closed.  Each added
    singleton pair has an observed footprint and guarantees reconstruction
    even when caps exclude a larger formal concept.  Such added singleton
    pairs are deliberately not claimed to be formal concepts: e.g., in a
    nontrivial rectangle, a singleton observed arc is usually not closed.
    """

    relation = _normalise_relation(arcs, nodes)
    concepts = enumerate_formal_concepts(
        relation.arcs,
        nodes=relation.nodes,
        max_tail_arity=max_tail_arity,
        max_head_arity=max_head_arity,
        max_candidates=max_candidates,
    )
    singleton_pairs = {
        DirectedFormalConcept((source,), (destination,)) for source, destination in relation.arcs
    }
    section = tuple(sorted(set(concepts).union(singleton_pairs), key=_concept_sort_key))
    _validate_observed_pairs(section, relation)
    return section


# Explicit aliases retain readable call sites while making direction clear.
enumerate_directed_formal_concepts = enumerate_formal_concepts
build_augmented_section = augmented_section

__all__ = [
    "Arc",
    "DirectedFormalConcept",
    "FormalConcept",
    "Node",
    "augmented_section",
    "build_augmented_section",
    "common_predecessors",
    "common_successors",
    "enumerate_directed_formal_concepts",
    "enumerate_formal_concepts",
    "formal_concept_section",
    "head_closure",
    "reconstruct_relation",
    "tail_closure",
    "validate_concepts",
]
