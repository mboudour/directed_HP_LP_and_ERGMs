"""Target-aware, leakage-safe negative evaluation panels.

A panel is a labelled :class:`pandas.DataFrame` containing the supplied positive
candidates followed by sampled or supplied negative candidates.  Candidate rows
are copied intact: this module only appends the requested label and panel
columns.  Before a negative row can enter a panel, its canonical candidate key
is checked against every positive key and duplicate negative keys are removed.

Pass ``key_columns`` whenever a candidate has metadata that is not part of its
identity (for example, a source dataset, an explanation, or a score).  A small
set of common directed-edge and hyperarc field names is inferred otherwise.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from numbers import Integral
from typing import Any, TypeAlias
from zlib import crc32

import numpy as np
import pandas as pd

CandidateInput: TypeAlias = pd.DataFrame | Mapping[str, Any] | Iterable[Mapping[str, Any]]
CandidateKey: TypeAlias = Callable[[dict[str, Any]], Any]

_DEFAULT_LABEL_COLUMN = "label"
_DEFAULT_PANEL_COLUMN = "negative_panel"
_DEFAULT_KIND_COLUMN = "negative_kind"

# These fields are not candidate identity in the all-column fallback.  Explicit
# key_columns remain the recommended option for nonstandard candidate schemas.
_BOOKKEEPING_COLUMNS = frozenset(
    {
        "label",
        "y",
        "y_true",
        "score",
        "probability",
        "logit",
        "prediction",
        "fold",
        "split",
        "panel",
        "negative_panel",
        "negative_kind",
    }
)
_STRUCTURAL_KEY_COLUMNS = (
    ("tail", "head", "target_type"),
    ("tail", "head", "prediction_target"),
    ("tail", "head"),
    ("tails", "heads"),
    ("source", "target"),
    ("sender", "recipient"),
    ("candidate",),
    ("hyperarc",),
    ("footprint",),
    ("concept",),
    ("role_assignment",),
    ("roles",),
)
_HARD_KIND_ALIASES = {
    "reversal": "reversal_orientation",
    "orientation": "reversal_orientation",
    "reversal_orientation": "reversal_orientation",
    "near_complete_footprint": "near_complete_footprint",
    "non_maximal_concept": "non_maximal_concept",
    "role_corrupted": "role_corrupted",
}


def _as_frame(candidates: CandidateInput, *, name: str) -> pd.DataFrame:
    """Copy candidate input into a row-oriented DataFrame."""
    if isinstance(candidates, pd.DataFrame):
        return candidates.copy(deep=True).reset_index(drop=True)
    if isinstance(candidates, Mapping):
        return pd.DataFrame([dict(candidates)])
    try:
        records = list(candidates)
    except TypeError as error:
        raise TypeError(f"{name} must be a DataFrame, mapping, or iterable of mappings.") from error
    if any(not isinstance(record, Mapping) for record in records):
        raise TypeError(f"{name} iterable must contain mapping records.")
    return pd.DataFrame.from_records(records)


def _normalise_key_columns(frame: pd.DataFrame, key_columns: Sequence[str] | None) -> list[str]:
    """Use explicit, structural, or all-non-bookkeeping candidate fields."""
    if key_columns is not None:
        if isinstance(key_columns, str):
            raise TypeError("key_columns must be a sequence of column names, not a string.")
        columns = list(key_columns)
        if not columns:
            raise ValueError("key_columns must contain at least one column name.")
        missing = [column for column in columns if column not in frame.columns]
        if missing:
            raise ValueError(f"key_columns are absent from candidates: {missing}.")
        return columns

    if "candidate_id" in frame.columns:
        return ["candidate_id"]
    for columns in _STRUCTURAL_KEY_COLUMNS:
        if all(column in frame.columns for column in columns):
            return list(columns)
    columns = [column for column in frame.columns if column not in _BOOKKEEPING_COLUMNS]
    if not columns:
        raise ValueError(
            "Could not infer candidate identity from an empty or bookkeeping-only schema; "
            "pass key_columns or candidate_key."
        )
    return columns


def _freeze(value: Any) -> Any:
    """Create a hashable, deterministic representation of nested candidate data."""
    if isinstance(value, np.generic):
        value = value.item()
    if value is None:
        return ("none",)
    if isinstance(value, Mapping):
        items = ((_freeze(key), _freeze(item)) for key, item in value.items())
        return ("mapping", tuple(sorted(items, key=repr)))
    if isinstance(value, (list, tuple, np.ndarray, pd.Series, pd.Index)):
        return ("sequence", tuple(_freeze(item) for item in value))
    if isinstance(value, (set, frozenset)):
        return ("set", tuple(sorted((_freeze(item) for item in value), key=repr)))
    try:
        missing = pd.isna(value)
    except TypeError:
        missing = False
    if isinstance(missing, (bool, np.bool_)) and missing:
        return ("missing",)
    try:
        hash(value)
    except TypeError:
        return ("repr", repr(value))
    return ("scalar", type(value).__qualname__, value)


def _candidate_keys(
    frame: pd.DataFrame,
    *,
    key_columns: Sequence[str] | None,
    candidate_key: CandidateKey | None,
) -> list[Any]:
    """Calculate canonical keys without changing candidate values or metadata."""
    if candidate_key is not None and key_columns is not None:
        raise ValueError("Pass either key_columns or candidate_key, not both.")
    if candidate_key is not None:
        return [_freeze(candidate_key(row)) for row in frame.to_dict(orient="records")]
    columns = _normalise_key_columns(frame, key_columns)
    return [_freeze(values) for values in frame.loc[:, columns].itertuples(index=False, name=None)]


def _validate_count(value: int | None, *, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer or None.")
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")
    return int(value)


def _rng(seed: int | None, *, stream: str) -> np.random.Generator:
    """Create an independent deterministic RNG stream for a panel kind."""
    if seed is None:
        return np.random.default_rng()
    if isinstance(seed, bool) or not isinstance(seed, Integral):
        raise TypeError("seed must be an integer or None.")
    if seed < 0:
        raise ValueError("seed must be non-negative.")
    # crc32 is stable across Python processes unlike hash(stream).
    sequence = np.random.SeedSequence([int(seed), crc32(stream.encode("utf-8"))])
    return np.random.default_rng(sequence)


def _eligible_negative_rows(
    positives: pd.DataFrame,
    candidates: pd.DataFrame,
    *,
    key_columns: Sequence[str] | None,
    candidate_key: CandidateKey | None,
) -> pd.DataFrame:
    """Filter positives and duplicate candidate keys out of a negative pool."""
    positive_keys = set(
        _candidate_keys(positives, key_columns=key_columns, candidate_key=candidate_key)
    )
    candidate_keys = _candidate_keys(
        candidates, key_columns=key_columns, candidate_key=candidate_key
    )
    retained_positions: list[int] = []
    retained_keys: set[Any] = set()
    for position, key in enumerate(candidate_keys):
        if key in positive_keys or key in retained_keys:
            continue
        retained_positions.append(position)
        retained_keys.add(key)
    return candidates.iloc[retained_positions].copy(deep=True).reset_index(drop=True)


def _take_negatives(
    eligible: pd.DataFrame,
    *,
    n_negatives: int | None,
    default_count: int | None,
    seed: int | None,
    stream: str,
) -> pd.DataFrame:
    """Return all eligible rows or a reproducible, without-replacement sample."""
    requested = (
        default_count if n_negatives is None else _validate_count(n_negatives, name="n_negatives")
    )
    if requested is None:
        return eligible.reset_index(drop=True)
    if requested > len(eligible):
        raise ValueError(
            f"Requested {requested} negatives but only {len(eligible)} eligible, non-overlapping "
            "candidates are available."
        )
    if requested == len(eligible):
        return eligible.reset_index(drop=True)
    positions = _rng(seed, stream=stream).choice(len(eligible), size=requested, replace=False)
    return eligible.iloc[positions].copy(deep=True).reset_index(drop=True)


def _set_label(frame: pd.DataFrame, *, label_column: str, label: int) -> pd.DataFrame:
    """Add a label while rejecting a contradictory pre-existing label field."""
    result = frame.copy(deep=True)
    if label_column in result.columns:
        existing = result[label_column]
        valid = existing.isin([label])
        if not bool(valid.all()):
            raise ValueError(
                f"{label_column!r} already exists and contains values inconsistent "
                f"with label={label}."
            )
    else:
        result[label_column] = label
    return result


def _assemble_panel(
    positives: pd.DataFrame,
    negatives: pd.DataFrame,
    *,
    kind: str,
    label_column: str,
    panel_column: str,
    kind_column: str,
) -> pd.DataFrame:
    """Label and concatenate rows without overwriting any candidate metadata."""
    for frame_name, frame in (("positives", positives), ("negatives", negatives)):
        conflicts = {panel_column, kind_column}.intersection(frame.columns)
        if conflicts:
            raise ValueError(
                f"{frame_name} already contains generated panel columns {sorted(conflicts)}; "
                "choose different panel_column or kind_column names."
            )
    labelled_positives = _set_label(positives, label_column=label_column, label=1)
    labelled_negatives = _set_label(negatives, label_column=label_column, label=0)
    labelled_positives[panel_column] = kind
    labelled_negatives[panel_column] = kind
    labelled_positives[kind_column] = pd.NA
    labelled_negatives[kind_column] = kind
    return pd.concat([labelled_positives, labelled_negatives], ignore_index=True, sort=False)


def _panel_from_candidates(
    positives: CandidateInput,
    negative_candidates: CandidateInput,
    *,
    kind: str,
    n_negatives: int | None,
    default_count: int | None,
    seed: int | None,
    key_columns: Sequence[str] | None,
    candidate_key: CandidateKey | None,
    label_column: str,
    panel_column: str,
    kind_column: str,
) -> pd.DataFrame:
    positive_frame = _as_frame(positives, name="positives")
    negative_frame = _as_frame(negative_candidates, name="negative_candidates")
    eligible = _eligible_negative_rows(
        positive_frame,
        negative_frame,
        key_columns=key_columns,
        candidate_key=candidate_key,
    )
    negatives = _take_negatives(
        eligible,
        n_negatives=n_negatives,
        default_count=default_count,
        seed=seed,
        stream=kind,
    )
    return _assemble_panel(
        positive_frame,
        negatives,
        kind=kind,
        label_column=label_column,
        panel_column=panel_column,
        kind_column=kind_column,
    )


def random_negative_panel(
    positives: CandidateInput,
    candidate_pool: CandidateInput,
    *,
    n_negatives: int | None = None,
    seed: int | None = 0,
    key_columns: Sequence[str] | None = None,
    candidate_key: CandidateKey | None = None,
    label_column: str = _DEFAULT_LABEL_COLUMN,
    panel_column: str = _DEFAULT_PANEL_COLUMN,
    kind_column: str = _DEFAULT_KIND_COLUMN,
) -> pd.DataFrame:
    """Build a reproducible 1:1 random-negative panel by default.

    Random negatives are sampled without replacement.  With the default
    ``n_negatives=None``, the panel uses one negative for every *unique*
    positive candidate.  The default seed of zero makes the result reproducible;
    use ``seed=None`` only when non-reproducible sampling is intentional.
    """
    positive_frame = _as_frame(positives, name="positives")
    positive_count = len(
        set(_candidate_keys(positive_frame, key_columns=key_columns, candidate_key=candidate_key))
    )
    return _panel_from_candidates(
        positive_frame,
        candidate_pool,
        kind="random",
        n_negatives=n_negatives,
        default_count=positive_count,
        seed=seed,
        key_columns=key_columns,
        candidate_key=candidate_key,
        label_column=label_column,
        panel_column=panel_column,
        kind_column=kind_column,
    )


def hard_negative_panel(
    positives: CandidateInput,
    candidate_pool: CandidateInput,
    *,
    kind: str,
    n_negatives: int | None = None,
    seed: int | None = 0,
    key_columns: Sequence[str] | None = None,
    candidate_key: CandidateKey | None = None,
    label_column: str = _DEFAULT_LABEL_COLUMN,
    panel_column: str = _DEFAULT_PANEL_COLUMN,
    kind_column: str = _DEFAULT_KIND_COLUMN,
) -> pd.DataFrame:
    """Build one hard-negative panel from supplied target-specific candidates.

    Hard panels retain every eligible candidate by default.  Set
    ``n_negatives`` to subsample reproducibly.  Accepted kinds are
    ``reversal_orientation``, ``near_complete_footprint``,
    ``non_maximal_concept``, and ``role_corrupted``; ``reversal`` and
    ``orientation`` are accepted aliases for the first kind.
    """
    try:
        normalised_kind = _HARD_KIND_ALIASES[kind]
    except KeyError as error:
        allowed = ", ".join(sorted(_HARD_KIND_ALIASES))
        raise ValueError(
            f"Unsupported hard-negative kind {kind!r}; expected one of {allowed}."
        ) from error
    return _panel_from_candidates(
        positives,
        candidate_pool,
        kind=normalised_kind,
        n_negatives=n_negatives,
        default_count=None,
        seed=seed,
        key_columns=key_columns,
        candidate_key=candidate_key,
        label_column=label_column,
        panel_column=panel_column,
        kind_column=kind_column,
    )


def reversal_orientation_negative_panel(
    positives: CandidateInput, candidate_pool: CandidateInput, **kwargs: Any
) -> pd.DataFrame:
    """Build a reversal/orientation hard-negative panel from supplied candidates."""
    return hard_negative_panel(positives, candidate_pool, kind="reversal_orientation", **kwargs)


def near_complete_footprint_negative_panel(
    positives: CandidateInput, candidate_pool: CandidateInput, **kwargs: Any
) -> pd.DataFrame:
    """Build a near-complete-footprint hard-negative panel from supplied candidates."""
    return hard_negative_panel(positives, candidate_pool, kind="near_complete_footprint", **kwargs)


def non_maximal_concept_negative_panel(
    positives: CandidateInput, candidate_pool: CandidateInput, **kwargs: Any
) -> pd.DataFrame:
    """Build a non-maximal-concept hard-negative panel from supplied candidates."""
    return hard_negative_panel(positives, candidate_pool, kind="non_maximal_concept", **kwargs)


def role_corrupted_negative_panel(
    positives: CandidateInput, candidate_pool: CandidateInput, **kwargs: Any
) -> pd.DataFrame:
    """Build a role-corrupted hard-negative panel from supplied candidates."""
    return hard_negative_panel(positives, candidate_pool, kind="role_corrupted", **kwargs)


def _hard_count_for(
    n_hard_negatives: int | Mapping[str, int | None] | None, kind: str
) -> int | None:
    if n_hard_negatives is None:
        return None
    if isinstance(n_hard_negatives, Mapping):
        return n_hard_negatives.get(kind)
    return _validate_count(n_hard_negatives, name="n_hard_negatives")


def build_target_aware_negative_panels(
    positives: CandidateInput,
    *,
    random_candidates: CandidateInput | None = None,
    reversal_candidates: CandidateInput | None = None,
    orientation_candidates: CandidateInput | None = None,
    near_complete_footprint_candidates: CandidateInput | None = None,
    non_maximal_concept_candidates: CandidateInput | None = None,
    role_corrupted_candidates: CandidateInput | None = None,
    n_random_negatives: int | None = None,
    n_hard_negatives: int | Mapping[str, int | None] | None = None,
    seed: int | None = 0,
    key_columns: Sequence[str] | None = None,
    candidate_key: CandidateKey | None = None,
    label_column: str = _DEFAULT_LABEL_COLUMN,
    panel_column: str = _DEFAULT_PANEL_COLUMN,
    kind_column: str = _DEFAULT_KIND_COLUMN,
) -> dict[str, pd.DataFrame]:
    """Build every requested random and target-aware hard-negative panel.

    Inputs are optional so callers can evaluate only the targets that their
    data construction supports.  Reversal and orientation candidates are merged
    into a single ``"reversal_orientation"`` panel.  Every output includes the
    same positive candidates and excludes positive-negative key overlap.
    """
    panels: dict[str, pd.DataFrame] = {}
    common = {
        "seed": seed,
        "key_columns": key_columns,
        "candidate_key": candidate_key,
        "label_column": label_column,
        "panel_column": panel_column,
        "kind_column": kind_column,
    }
    if random_candidates is not None:
        panels["random"] = random_negative_panel(
            positives,
            random_candidates,
            n_negatives=n_random_negatives,
            **common,
        )

    reversal_sources = [
        source for source in (reversal_candidates, orientation_candidates) if source is not None
    ]
    if reversal_sources:
        reversal_pool = pd.concat(
            [
                _as_frame(source, name="reversal/orientation candidates")
                for source in reversal_sources
            ],
            ignore_index=True,
            sort=False,
        )
        kind = "reversal_orientation"
        panels[kind] = hard_negative_panel(
            positives,
            reversal_pool,
            kind=kind,
            n_negatives=_hard_count_for(n_hard_negatives, kind),
            **common,
        )

    hard_sources: tuple[tuple[str, CandidateInput | None], ...] = (
        ("near_complete_footprint", near_complete_footprint_candidates),
        ("non_maximal_concept", non_maximal_concept_candidates),
        ("role_corrupted", role_corrupted_candidates),
    )
    for kind, candidates in hard_sources:
        if candidates is None:
            continue
        panels[kind] = hard_negative_panel(
            positives,
            candidates,
            kind=kind,
            n_negatives=_hard_count_for(n_hard_negatives, kind),
            **common,
        )
    return panels


# Alternate descriptive name for a call site that prefers an "evaluation" prefix.
build_evaluation_panels = build_target_aware_negative_panels

__all__ = [
    "CandidateInput",
    "build_evaluation_panels",
    "build_target_aware_negative_panels",
    "hard_negative_panel",
    "near_complete_footprint_negative_panel",
    "non_maximal_concept_negative_panel",
    "random_negative_panel",
    "reversal_orientation_negative_panel",
    "role_corrupted_negative_panel",
]
