"""Deterministic missingness regimes for directed events and directed arcs.

The event-first regime samples complete native directed events, retaining their tail
and head roles for hyperlink evaluation.  The arc-first regime samples unique
loop-free directed arcs.  Both regimes support uniform MCAR sampling and an
outgoing-activity-biased ``mnar_out`` mechanism.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from math import floor, isfinite
from numbers import Integral, Real
from random import Random
from typing import TypeAlias

DEFAULT_MASK_RATE = 0.30
DEFAULT_MASK_SEED = 20261013

Node: TypeAlias = Hashable
DirectedArc: TypeAlias = tuple[Node, Node]


class MaskingMechanism(StrEnum):
    """Mechanisms used to select eligible units for masking."""

    MCAR = "mcar"
    MNAR_OUT = "mnar_out"


class MaskingRegime(StrEnum):
    """Units on which a missingness mechanism operates."""

    EVENT_FIRST = "event_first"
    ARC_FIRST = "arc_first"


@dataclass(frozen=True, slots=True)
class DirectedEvent:
    """A native directed event with explicitly separate tail and head roles.

    Invalid events can be constructed so that :func:`mask_event_first` can report
    them in its exclusion accounting.  Invalid events are never returned in a
    masking result: both roles must be non-empty and they must be disjoint.
    """

    event_id: Hashable
    tail: frozenset[Node]
    head: frozenset[Node]

    def __post_init__(self) -> None:
        object.__setattr__(self, "tail", frozenset(self.tail))
        object.__setattr__(self, "head", frozenset(self.head))

    @property
    def has_disjoint_roles(self) -> bool:
        """Whether no node occurs in both the tail and head of this event."""

        return self.tail.isdisjoint(self.head)

    @property
    def is_mask_eligible(self) -> bool:
        """Whether the event can be emitted without an empty role or self-loop."""

        return bool(self.tail) and bool(self.head) and self.has_disjoint_roles

    def projected_arcs(self) -> tuple[DirectedArc, ...]:
        """Return the loop-free tail-to-head dyadic projection of this event."""

        if not self.is_mask_eligible:
            return ()
        return tuple(
            (source, target)
            for source in sorted(self.tail, key=_stable_node_key)
            for target in sorted(self.head, key=_stable_node_key)
        )


@dataclass(frozen=True, slots=True)
class MaskAccounting:
    """Auditable requested, realized, and excluded-unit counts for one mask.

    ``requested_mask_count`` is the floor of ``requested_rate * eligible_count``.
    To keep a non-empty observed partition for downstream evaluation, at least one
    eligible unit is retained.  ``limited_by_minimum_observed`` records any
    requested units that could not be masked for that reason.
    """

    input_count: int
    eligible_count: int
    excluded_count: int
    excluded_self_loops: int
    excluded_empty_roles: int
    excluded_duplicates: int
    requested_rate: float
    requested_mask_count: int
    masked_count: int
    observed_count: int
    limited_by_minimum_observed: int
    realized_rate: float

    @property
    def has_usable_split(self) -> bool:
        """Whether both observed and held-out units are available."""

        return self.masked_count > 0 and self.observed_count > 0


@dataclass(frozen=True, slots=True)
class MaskResult:
    """Result of a directed missingness regime, ready for later evaluation.

    Exactly one pair of unit fields is populated by each regime: event-first
    populates ``observed_events`` and ``held_out_events``; arc-first populates
    ``observed_arcs`` and ``held_out_arcs``.  Event-first additionally supplies
    loop-free dyadic projections for consumers that evaluate directed arcs.
    """

    regime: MaskingRegime
    mechanism: MaskingMechanism
    seed: int
    accounting: MaskAccounting
    observed_events: tuple[DirectedEvent, ...] = ()
    held_out_events: tuple[DirectedEvent, ...] = ()
    observed_arcs: tuple[DirectedArc, ...] = ()
    held_out_arcs: tuple[DirectedArc, ...] = ()

    @property
    def train_events(self) -> tuple[DirectedEvent, ...]:
        """Alias for observed native events used as a model-training input."""

        return self.observed_events

    @property
    def test_events(self) -> tuple[DirectedEvent, ...]:
        """Alias for held-out native events used as an evaluation target."""

        return self.held_out_events

    @property
    def train_arcs(self) -> tuple[DirectedArc, ...]:
        """Alias for observed arcs used as a model-training input."""

        return self.observed_arcs

    @property
    def test_arcs(self) -> tuple[DirectedArc, ...]:
        """Alias for held-out arcs used as an evaluation target."""

        return self.held_out_arcs

    @property
    def observed(self) -> tuple[DirectedEvent, ...] | tuple[DirectedArc, ...]:
        """Return the native unit type for the observed partition."""

        if self.regime is MaskingRegime.EVENT_FIRST:
            return self.observed_events
        return self.observed_arcs

    @property
    def held_out(self) -> tuple[DirectedEvent, ...] | tuple[DirectedArc, ...]:
        """Return the native unit type for the held-out partition."""

        if self.regime is MaskingRegime.EVENT_FIRST:
            return self.held_out_events
        return self.held_out_arcs


# The longer name is retained as a public alias for consumers that prefer it.
MaskingResult: TypeAlias = MaskResult


def mask_event_first(
    events: Iterable[DirectedEvent],
    *,
    rate: float = DEFAULT_MASK_RATE,
    mechanism: MaskingMechanism | str = MaskingMechanism.MCAR,
    seed: int = DEFAULT_MASK_SEED,
) -> MaskResult:
    """Mask whole native directed events using a deterministic seeded draw.

    MCAR samples eligible events uniformly without replacement.  ``mnar_out``
    samples without replacement with weights equal to the summed outgoing
    projected-arc degree of an event's tail nodes.  The returned event roles are
    unchanged and disjoint; events with an empty role or overlapping tail/head
    roles are accounted for and excluded before sampling.
    """

    normalized_rate = _validate_rate(rate)
    normalized_mechanism = _validate_mechanism(mechanism)
    normalized_seed = _validate_seed(seed)

    input_events = tuple(events)
    eligible_events: list[DirectedEvent] = []
    excluded_self_loops = 0
    excluded_empty_roles = 0

    for event in input_events:
        if not isinstance(event, DirectedEvent):
            raise TypeError("event-first masking requires DirectedEvent instances")
        if not event.tail or not event.head:
            excluded_empty_roles += 1
        elif not event.has_disjoint_roles:
            excluded_self_loops += 1
        else:
            eligible_events.append(event)

    selected_indices = _select_indices(
        item_count=len(eligible_events),
        mask_count=_mask_count(len(eligible_events), normalized_rate),
        mechanism=normalized_mechanism,
        weights=_event_outgoing_weights(eligible_events),
        seed=normalized_seed,
    )
    observed_events = tuple(
        event for index, event in enumerate(eligible_events) if index not in selected_indices
    )
    held_out_events = tuple(
        event for index, event in enumerate(eligible_events) if index in selected_indices
    )
    accounting = _build_accounting(
        input_count=len(input_events),
        eligible_count=len(eligible_events),
        excluded_self_loops=excluded_self_loops,
        excluded_empty_roles=excluded_empty_roles,
        excluded_duplicates=0,
        requested_rate=normalized_rate,
        masked_count=len(held_out_events),
    )

    return MaskResult(
        regime=MaskingRegime.EVENT_FIRST,
        mechanism=normalized_mechanism,
        seed=normalized_seed,
        accounting=accounting,
        observed_events=observed_events,
        held_out_events=held_out_events,
        observed_arcs=_unique_projected_arcs(observed_events),
        held_out_arcs=_unique_projected_arcs(held_out_events),
    )


def mask_arc_first(
    arcs: Iterable[DirectedArc],
    *,
    rate: float = DEFAULT_MASK_RATE,
    mechanism: MaskingMechanism | str = MaskingMechanism.MCAR,
    seed: int = DEFAULT_MASK_SEED,
) -> MaskResult:
    """Mask unique directed arcs using a deterministic seeded draw.

    Input self-loops are excluded and duplicate arcs are collapsed in first-seen
    order before sampling.  For ``mnar_out``, an arc's sampling weight is the
    outgoing degree of its source among the eligible unique arcs.
    """

    normalized_rate = _validate_rate(rate)
    normalized_mechanism = _validate_mechanism(mechanism)
    normalized_seed = _validate_seed(seed)

    input_arcs = tuple(arcs)
    eligible_arcs: list[DirectedArc] = []
    seen: set[DirectedArc] = set()
    excluded_self_loops = 0
    excluded_duplicates = 0

    for raw_arc in input_arcs:
        source, target = _coerce_arc(raw_arc)
        if source == target:
            excluded_self_loops += 1
            continue
        arc = (source, target)
        if arc in seen:
            excluded_duplicates += 1
            continue
        seen.add(arc)
        eligible_arcs.append(arc)

    selected_indices = _select_indices(
        item_count=len(eligible_arcs),
        mask_count=_mask_count(len(eligible_arcs), normalized_rate),
        mechanism=normalized_mechanism,
        weights=_arc_outgoing_weights(eligible_arcs),
        seed=normalized_seed,
    )
    observed_arcs = tuple(
        arc for index, arc in enumerate(eligible_arcs) if index not in selected_indices
    )
    held_out_arcs = tuple(
        arc for index, arc in enumerate(eligible_arcs) if index in selected_indices
    )
    accounting = _build_accounting(
        input_count=len(input_arcs),
        eligible_count=len(eligible_arcs),
        excluded_self_loops=excluded_self_loops,
        excluded_empty_roles=0,
        excluded_duplicates=excluded_duplicates,
        requested_rate=normalized_rate,
        masked_count=len(held_out_arcs),
    )

    return MaskResult(
        regime=MaskingRegime.ARC_FIRST,
        mechanism=normalized_mechanism,
        seed=normalized_seed,
        accounting=accounting,
        observed_arcs=observed_arcs,
        held_out_arcs=held_out_arcs,
    )


# Readable aliases for the vocabulary used in experimental configurations.
event_first_mask = mask_event_first
arc_first_mask = mask_arc_first
mask_native_events = mask_event_first
mask_directed_arcs = mask_arc_first


def _validate_rate(rate: float) -> float:
    if isinstance(rate, bool) or not isinstance(rate, Real):
        raise TypeError("rate must be a real number between 0 and 1")
    normalized_rate = float(rate)
    if not isfinite(normalized_rate) or not 0.0 <= normalized_rate <= 1.0:
        raise ValueError("rate must be finite and between 0 and 1 inclusive")
    return normalized_rate


def _validate_mechanism(mechanism: MaskingMechanism | str) -> MaskingMechanism:
    try:
        return MaskingMechanism(mechanism)
    except ValueError as error:
        allowed = ", ".join(item.value for item in MaskingMechanism)
        raise ValueError(f"mechanism must be one of: {allowed}") from error


def _validate_seed(seed: int) -> int:
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise TypeError("seed must be an integer")
    return int(seed)


def _coerce_arc(raw_arc: DirectedArc) -> DirectedArc:
    if isinstance(raw_arc, (str, bytes)):
        raise TypeError("each directed arc must contain exactly two hashable nodes")
    try:
        source, target = raw_arc
    except (TypeError, ValueError) as error:
        raise TypeError("each directed arc must contain exactly two hashable nodes") from error
    try:
        hash(source)
        hash(target)
    except TypeError as error:
        raise TypeError("directed arc nodes must be hashable") from error
    return source, target


def _mask_count(eligible_count: int, rate: float) -> int:
    """Return a floor-rate holdout size while retaining one observed unit."""

    requested_mask_count = floor(rate * eligible_count)
    return min(requested_mask_count, max(eligible_count - 1, 0))


def _select_indices(
    *,
    item_count: int,
    mask_count: int,
    mechanism: MaskingMechanism,
    weights: Sequence[int],
    seed: int,
) -> frozenset[int]:
    if item_count == 0 or mask_count == 0:
        return frozenset()

    random = Random(seed)
    if mechanism is MaskingMechanism.MCAR:
        return frozenset(random.sample(range(item_count), mask_count))
    return frozenset(_weighted_sample_without_replacement(weights, mask_count, random))


def _weighted_sample_without_replacement(
    weights: Sequence[int], count: int, random: Random
) -> list[int]:
    """Draw weighted indices without replacement with a local deterministic RNG."""

    available = list(range(len(weights)))
    selected: list[int] = []
    for _ in range(count):
        total_weight = sum(weights[index] for index in available)
        if total_weight <= 0:
            selected.extend(random.sample(available, count - len(selected)))
            break
        threshold = random.random() * total_weight
        cumulative_weight = 0.0
        for position, index in enumerate(available):
            cumulative_weight += weights[index]
            if threshold < cumulative_weight:
                selected.append(index)
                del available[position]
                break
    return selected


def _event_outgoing_weights(events: Sequence[DirectedEvent]) -> list[int]:
    outgoing_degree: dict[Node, int] = {}
    for event in events:
        for source in event.tail:
            outgoing_degree[source] = outgoing_degree.get(source, 0) + len(event.head)
    return [sum(outgoing_degree[source] for source in event.tail) for event in events]


def _arc_outgoing_weights(arcs: Sequence[DirectedArc]) -> list[int]:
    outgoing_degree: dict[Node, int] = {}
    for source, _ in arcs:
        outgoing_degree[source] = outgoing_degree.get(source, 0) + 1
    return [outgoing_degree[source] for source, _ in arcs]


def _build_accounting(
    *,
    input_count: int,
    eligible_count: int,
    excluded_self_loops: int,
    excluded_empty_roles: int,
    excluded_duplicates: int,
    requested_rate: float,
    masked_count: int,
) -> MaskAccounting:
    requested_mask_count = floor(requested_rate * eligible_count)
    excluded_count = excluded_self_loops + excluded_empty_roles + excluded_duplicates
    return MaskAccounting(
        input_count=input_count,
        eligible_count=eligible_count,
        excluded_count=excluded_count,
        excluded_self_loops=excluded_self_loops,
        excluded_empty_roles=excluded_empty_roles,
        excluded_duplicates=excluded_duplicates,
        requested_rate=requested_rate,
        requested_mask_count=requested_mask_count,
        masked_count=masked_count,
        observed_count=eligible_count - masked_count,
        limited_by_minimum_observed=requested_mask_count - masked_count,
        realized_rate=(masked_count / eligible_count) if eligible_count else 0.0,
    )


def _unique_projected_arcs(events: Iterable[DirectedEvent]) -> tuple[DirectedArc, ...]:
    unique_arcs: dict[DirectedArc, None] = {}
    for event in events:
        for arc in event.projected_arcs():
            unique_arcs.setdefault(arc, None)
    return tuple(unique_arcs)


def _stable_node_key(node: Node) -> tuple[str, str]:
    """Sort heterogeneous hashable nodes without imposing a numeric-only API."""

    return type(node).__qualname__, repr(node)
