"""Focused behavioral tests for directed formal-concept sections."""

from __future__ import annotations

from directed_hp.hypergraphs.formal_concepts import (
    DirectedFormalConcept,
    augmented_section,
    common_predecessors,
    common_successors,
    enumerate_formal_concepts,
    head_closure,
    reconstruct_relation,
    tail_closure,
    validate_concepts,
)


def test_proposition_1_reconstructs_a_toy_directed_relation() -> None:
    """All uncapped formal-concept footprints recover every observed toy arc."""

    arcs = {
        ("alice", "x"),
        ("alice", "y"),
        ("bob", "x"),
        ("bob", "y"),
        ("bob", "z"),
        ("carol", "z"),
    }

    concepts = enumerate_formal_concepts(arcs)

    validate_concepts(concepts, arcs)
    assert reconstruct_relation(concepts) == frozenset(arcs)
    assert concepts == enumerate_formal_concepts(reversed(sorted(arcs)))


def test_predecessor_successor_closures_remain_directed_and_non_diagonal() -> None:
    """The two Galois derivations never reverse the observed arc direction."""

    arcs = {
        ("sender_a", "recipient_x"),
        ("sender_a", "recipient_y"),
        ("sender_b", "recipient_x"),
        ("sender_b", "recipient_y"),
    }

    assert common_successors(("sender_a", "sender_b"), arcs) == (
        "recipient_x",
        "recipient_y",
    )
    assert common_predecessors(("recipient_x", "recipient_y"), arcs) == (
        "sender_a",
        "sender_b",
    )
    assert tail_closure(("sender_a",), arcs) == ("sender_a", "sender_b")
    assert head_closure(("recipient_x",), arcs) == ("recipient_x", "recipient_y")

    concepts = enumerate_formal_concepts(arcs)
    assert (
        DirectedFormalConcept(("sender_a", "sender_b"), ("recipient_x", "recipient_y")) in concepts
    )
    assert (
        DirectedFormalConcept(("recipient_x", "recipient_y"), ("sender_a", "sender_b"))
        not in concepts
    )


def test_arity_caps_exclude_large_closed_concepts_during_enumeration() -> None:
    """A cap applies to generated candidates and emitted closed concepts."""

    arcs = {
        ("a", "x"),
        ("a", "y"),
        ("b", "x"),
        ("b", "y"),
    }
    full_rectangle = DirectedFormalConcept(("a", "b"), ("x", "y"))

    uncapped = enumerate_formal_concepts(arcs)
    capped = enumerate_formal_concepts(arcs, max_tail_arity=1, max_head_arity=2)

    assert full_rectangle in uncapped
    assert full_rectangle not in capped
    assert all(len(concept.tail) <= 1 for concept in capped)
    assert all(len(concept.head) <= 2 for concept in capped)


def test_augmented_section_includes_every_observed_arc_as_a_singleton_pair() -> None:
    """Singleton additions restore an exact arc section when caps remove concepts."""

    arcs = {
        ("a", "x"),
        ("a", "y"),
        ("b", "x"),
        ("b", "y"),
    }

    section = augmented_section(arcs, max_tail_arity=1, max_head_arity=1)

    assert reconstruct_relation(section) == frozenset(arcs)
    for source, destination in arcs:
        assert DirectedFormalConcept((source,), (destination,)) in section
