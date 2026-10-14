from __future__ import annotations

import pytest

from directed_hp.masking.directed_masks import (
    DirectedEvent,
    MaskingMechanism,
    MaskingRegime,
    mask_arc_first,
    mask_event_first,
)


def _events() -> list[DirectedEvent]:
    return [
        DirectedEvent("e1", {"a"}, {"b", "c"}),
        DirectedEvent("e2", {"a"}, {"d"}),
        DirectedEvent("e3", {"b"}, {"d"}),
        DirectedEvent("e4", {"c"}, {"a"}),
        DirectedEvent("e5", {"d"}, {"a"}),
    ]


def test_event_first_mcar_is_seeded_and_retains_native_roles() -> None:
    first = mask_event_first(_events(), rate=0.4, mechanism="mcar", seed=17)
    second = mask_event_first(_events(), rate=0.4, mechanism="mcar", seed=17)

    assert first == second
    assert first.regime is MaskingRegime.EVENT_FIRST
    assert first.mechanism is MaskingMechanism.MCAR
    assert len(first.held_out_events) == 2
    assert first.accounting.realized_rate == pytest.approx(0.4)
    assert first.accounting.has_usable_split
    assert all(event.tail and event.head and event.has_disjoint_roles for event in first.observed)
    assert all(source != target for source, target in first.observed_arcs + first.held_out_arcs)
    assert {event.event_id for event in first.observed_events}.isdisjoint(
        event.event_id for event in first.held_out_events
    )


def test_event_first_mnar_out_is_seeded_and_reports_invalid_event_exclusions() -> None:
    events = _events() + [
        DirectedEvent("loop", {"x", "y"}, {"y"}),
        DirectedEvent("empty-tail", set(), {"z"}),
    ]

    first = mask_event_first(events, rate=0.4, mechanism=MaskingMechanism.MNAR_OUT, seed=4)
    second = mask_event_first(events, rate=0.4, mechanism=MaskingMechanism.MNAR_OUT, seed=4)

    assert first == second
    assert first.mechanism is MaskingMechanism.MNAR_OUT
    assert first.accounting.input_count == 7
    assert first.accounting.eligible_count == 5
    assert first.accounting.excluded_count == 2
    assert first.accounting.excluded_self_loops == 1
    assert first.accounting.excluded_empty_roles == 1
    assert all(event.has_disjoint_roles for event in first.held_out_events)


def test_arc_first_mcar_excludes_loops_and_duplicates_and_reports_realized_rate() -> None:
    arcs = [("a", "b"), ("a", "c"), ("b", "a"), ("c", "a"), ("a", "a"), ("a", "b")]

    result = mask_arc_first(arcs, rate=0.5, mechanism="mcar", seed=8)

    assert result.regime is MaskingRegime.ARC_FIRST
    assert result.accounting.input_count == 6
    assert result.accounting.eligible_count == 4
    assert result.accounting.excluded_self_loops == 1
    assert result.accounting.excluded_duplicates == 1
    assert result.accounting.excluded_count == 2
    assert result.accounting.masked_count == 2
    assert result.accounting.realized_rate == pytest.approx(0.5)
    assert set(result.observed_arcs).isdisjoint(result.held_out_arcs)
    assert all(source != target for source, target in result.observed_arcs + result.held_out_arcs)


def test_arc_first_mnar_out_is_seeded_and_uses_public_train_test_aliases() -> None:
    arcs = [("a", "b"), ("a", "c"), ("a", "d"), ("a", "e"), ("z", "a")]

    first = mask_arc_first(arcs, rate=0.4, mechanism="mnar_out", seed=0)
    second = mask_arc_first(arcs, rate=0.4, mechanism="mnar_out", seed=0)

    assert first == second
    assert first.mechanism is MaskingMechanism.MNAR_OUT
    assert {source for source, _ in first.held_out_arcs} == {"a"}
    assert first.train_arcs == first.observed_arcs
    assert first.test_arcs == first.held_out_arcs
    assert first.observed == first.observed_arcs
    assert first.held_out == first.held_out_arcs


@pytest.mark.parametrize(
    ("callable_", "values"),
    [
        (mask_event_first, []),
        (mask_event_first, [DirectedEvent("only", {"a"}, {"b"})]),
        (mask_arc_first, []),
        (mask_arc_first, [("a", "b")]),
    ],
)
def test_empty_and_too_small_inputs_are_safe(callable_: object, values: object) -> None:
    result = callable_(values, rate=1.0, seed=3)  # type: ignore[operator]

    assert result.accounting.masked_count == 0
    assert result.accounting.realized_rate == 0.0
    assert result.accounting.observed_count == result.accounting.eligible_count
    assert not result.accounting.has_usable_split


def test_rate_mechanism_and_arc_shape_are_validated() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        mask_arc_first([("a", "b")], rate=1.1)
    with pytest.raises(ValueError, match="mechanism"):
        mask_event_first(_events(), mechanism="not-a-mechanism")
    with pytest.raises(TypeError, match="exactly two"):
        mask_arc_first([("a", "b", "c")])  # type: ignore[list-item]
