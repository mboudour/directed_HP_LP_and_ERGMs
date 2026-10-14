"""Tests for deterministic directed local link-prediction scores."""

from __future__ import annotations

from math import log

import pytest

from directed_hp.lp.directed_scores import (
    DirectedScoreEngine,
    adamic_adar_weight,
    lagged_score_candidate,
    lagged_score_candidates,
    ttriple_statistic,
    ttriple_toggle_change,
)


@pytest.fixture
def component_arcs() -> set[tuple[str, str]]:
    """Give one separate witness for each directed component of u -> v."""
    return {
        ("u", "a"),
        ("a", "v"),  # OI: u -> a -> v
        ("u", "b"),
        ("v", "b"),  # OO: u and v share target b
        ("c", "u"),
        ("c", "v"),  # II: u and v share source c
    }


def test_directed_common_neighbor_counts_and_componentwise_adamic_adar(
    component_arcs: set[tuple[str, str]],
) -> None:
    engine = DirectedScoreEngine(component_arcs, nodes=("u", "v", "a", "b", "c", "isolated"))

    assert engine.oi_neighbors("u", "v") == frozenset({"a"})
    assert engine.oo_neighbors("u", "v") == frozenset({"b"})
    assert engine.ii_neighbors("u", "v") == frozenset({"c"})
    assert engine.common_neighbor_counts("u", "v").total == 3

    aa = engine.adamic_adar_components("u", "v")
    assert aa.oi == pytest.approx(1.0 / log(2))
    assert aa.oo == pytest.approx(1.0 / log(2))
    assert aa.ii == pytest.approx(1.0 / log(2))
    assert aa.total == pytest.approx(3.0 / log(2))


def test_adamic_adar_zero_and_one_degree_have_zero_weight() -> None:
    assert adamic_adar_weight(0) == 0.0
    assert adamic_adar_weight(1) == 0.0
    assert adamic_adar_weight(2) == pytest.approx(1.0 / log(2))


def test_candidate_scoring_emits_only_non_loop_unobserved_dyads(
    component_arcs: set[tuple[str, str]],
) -> None:
    nodes = ("u", "v", "a", "b", "c", "isolated")
    engine = DirectedScoreEngine(component_arcs, nodes=nodes)
    scores = engine.score_candidates()

    assert set(scores) == set(engine.candidate_dyads())
    assert all(source != target for source, target in scores)
    assert not (set(scores) & component_arcs)
    assert scores[("u", "v")].common_neighbors.oi == 1
    assert scores[("u", "v")].common_neighbors.oo == 1
    assert scores[("u", "v")].common_neighbors.ii == 1
    assert scores[("u", "v")].total == 3

    explicit = engine.score_candidates((("u", "u"), ("u", "v"), ("u", "a")), exclude_existing=True)
    assert set(explicit) == {("u", "v")}


def test_ttriple_toggle_change_equals_oi_plus_oo_plus_ii_numerically(
    component_arcs: set[tuple[str, str]],
) -> None:
    engine = DirectedScoreEngine(component_arcs)
    before = ttriple_statistic(component_arcs)
    toggled = component_arcs | {("u", "v")}
    after = ttriple_statistic(toggled)

    assert engine.common_neighbor_counts("u", "v").total == 3
    assert before == 0
    assert after == 3
    assert after - before == 3
    assert ttriple_toggle_change(component_arcs, "u", "v") == 3
    assert ttriple_toggle_change(toggled, "u", "v") == -3


def test_lagged_helpers_are_order_independent_and_cannot_use_future_arcs() -> None:
    previous_window = (("u", "a"), ("a", "v"))
    future_only_arcs = {("u", "b"), ("v", "b"), ("c", "u"), ("c", "v")}

    previous_score = lagged_score_candidate(previous_window, "u", "v")
    reversed_score = lagged_score_candidate(tuple(reversed(previous_window)), "u", "v")
    contemporaneous_engine = DirectedScoreEngine(previous_window + tuple(future_only_arcs))
    contemporaneous_score = contemporaneous_engine.score("u", "v")

    assert previous_score == reversed_score
    assert previous_score.total == 1
    assert contemporaneous_score.total == 3

    candidates = (("u", "u"), ("u", "v"), ("v", "u"))
    forward = lagged_score_candidates(previous_window, candidates, nodes=("u", "v", "a"))
    backward = lagged_score_candidates(
        tuple(reversed(previous_window)), candidates, nodes=("u", "v", "a")
    )
    assert forward == backward
    assert set(forward) == {("u", "v"), ("v", "u")}
