"""Deterministic binary-ranking and threshold-metric utilities.

The functions in this module deliberately make singleton label sets visible rather
than reporting misleading perfect discrimination.  ``roc_auc`` and ``pr_auc``
return ``math.nan`` when either the positive or negative class is absent.  The
threshold metrics use a zero-denominator value of ``0.0`` and MCC is ``0.0``
when its denominator is zero.  Log loss remains well-defined for singleton
label sets and clips exact zero/one probabilities at machine epsilon.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import sqrt
from typing import Any

import numpy as np

_DEGENERATE_RANKING_VALUE = float("nan")


def _as_one_dimensional(values: Iterable[Any], *, name: str, dtype: type) -> np.ndarray:
    """Return *values* as a non-empty, one-dimensional NumPy array."""
    if isinstance(values, np.ndarray):
        array = np.asarray(values, dtype=dtype)
    else:
        array = np.asarray(list(values), dtype=dtype)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional; got shape {array.shape}.")
    if array.size == 0:
        raise ValueError(f"{name} must not be empty.")
    return array


def _validated_labels(y_true: Iterable[Any]) -> np.ndarray:
    """Validate and return binary integer labels."""
    raw = _as_one_dimensional(y_true, name="y_true", dtype=object)
    labels = np.empty(raw.size, dtype=np.int8)
    for index, value in enumerate(raw):
        if isinstance(value, (bool, np.bool_)):
            labels[index] = int(value)
        elif value in (0, 1):
            labels[index] = int(value)
        else:
            raise ValueError("y_true must contain only binary labels 0, 1, False, or True.")
    return labels


def _validated_scores(y_score: Iterable[Any], *, n_obs: int) -> np.ndarray:
    """Validate finite scores and ensure they align with the labels."""
    scores = _as_one_dimensional(y_score, name="y_score", dtype=float)
    if scores.size != n_obs:
        raise ValueError(f"y_true has {n_obs} observations but y_score has {scores.size}.")
    if not np.all(np.isfinite(scores)):
        raise ValueError("y_score must contain only finite values.")
    return scores


def _validated_inputs(
    y_true: Iterable[Any], y_score: Iterable[Any]
) -> tuple[np.ndarray, np.ndarray]:
    labels = _validated_labels(y_true)
    return labels, _validated_scores(y_score, n_obs=labels.size)


def _require_probability_scores(scores: np.ndarray) -> None:
    if np.any((scores < 0.0) | (scores > 1.0)):
        raise ValueError("Log loss requires probability scores in the closed interval [0, 1].")


def _confusion_counts(
    labels: np.ndarray, scores: np.ndarray, *, threshold: float
) -> tuple[int, int, int, int]:
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite.")
    predicted_positive = scores >= threshold
    positive = labels == 1
    negative = ~positive
    true_positive = int(np.count_nonzero(predicted_positive & positive))
    false_positive = int(np.count_nonzero(predicted_positive & negative))
    false_negative = int(np.count_nonzero(~predicted_positive & positive))
    true_negative = int(np.count_nonzero(~predicted_positive & negative))
    return true_positive, false_positive, false_negative, true_negative


def roc_auc(y_true: Iterable[Any], y_score: Iterable[Any]) -> float:
    """Compute tie-aware ROC-AUC without random tie breaking.

    If ``y_true`` contains only one class, ROC-AUC is undefined and this
    function returns ``math.nan``.
    """
    labels, scores = _validated_inputs(y_true, y_score)
    n_positive = int(np.count_nonzero(labels))
    n_negative = labels.size - n_positive
    if n_positive == 0 or n_negative == 0:
        return _DEGENERATE_RANKING_VALUE

    # Average ranks for tied scores yield the conventional Mann--Whitney ROC-AUC.
    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(scores.size, dtype=float)
    start = 0
    while start < scores.size:
        stop = start + 1
        while stop < scores.size and sorted_scores[stop] == sorted_scores[start]:
            stop += 1
        average_rank = (start + 1 + stop) / 2.0  # One-based rank endpoints.
        ranks[order[start:stop]] = average_rank
        start = stop

    positive_rank_sum = float(ranks[labels == 1].sum())
    numerator = positive_rank_sum - (n_positive * (n_positive + 1) / 2.0)
    return numerator / (n_positive * n_negative)


def pr_auc(y_true: Iterable[Any], y_score: Iterable[Any]) -> float:
    """Compute tie-aware average precision (the project's PR-AUC convention).

    This is the step-wise area under the precision--recall curve, equivalent to
    scikit-learn's ``average_precision_score`` for non-degenerate labels.  If
    either class is absent, the score is undefined and ``math.nan`` is returned.
    """
    labels, scores = _validated_inputs(y_true, y_score)
    n_positive = int(np.count_nonzero(labels))
    n_negative = labels.size - n_positive
    if n_positive == 0 or n_negative == 0:
        return _DEGENERATE_RANKING_VALUE

    # A stable ordering makes the implementation deterministic.  Score ties are
    # evaluated as one threshold, so their input order cannot affect the result.
    order = np.argsort(-scores, kind="mergesort")
    sorted_scores = scores[order]
    sorted_labels = labels[order]
    true_positives = 0
    false_positives = 0
    previous_recall = 0.0
    average_precision = 0.0
    start = 0
    while start < labels.size:
        stop = start + 1
        while stop < labels.size and sorted_scores[stop] == sorted_scores[start]:
            stop += 1
        group_labels = sorted_labels[start:stop]
        true_positives += int(np.count_nonzero(group_labels))
        false_positives += int(group_labels.size - np.count_nonzero(group_labels))
        recall = true_positives / n_positive
        precision = true_positives / (true_positives + false_positives)
        average_precision += precision * (recall - previous_recall)
        previous_recall = recall
        start = stop
    return average_precision


def precision_score(
    y_true: Iterable[Any], y_score: Iterable[Any], *, threshold: float = 0.5
) -> float:
    """Return thresholded precision, using ``0.0`` for no predicted positives."""
    labels, scores = _validated_inputs(y_true, y_score)
    true_positive, false_positive, _, _ = _confusion_counts(labels, scores, threshold=threshold)
    denominator = true_positive + false_positive
    return true_positive / denominator if denominator else 0.0


def recall_score(y_true: Iterable[Any], y_score: Iterable[Any], *, threshold: float = 0.5) -> float:
    """Return thresholded recall, using ``0.0`` when there are no positives."""
    labels, scores = _validated_inputs(y_true, y_score)
    true_positive, _, false_negative, _ = _confusion_counts(labels, scores, threshold=threshold)
    denominator = true_positive + false_negative
    return true_positive / denominator if denominator else 0.0


def f1_score(y_true: Iterable[Any], y_score: Iterable[Any], *, threshold: float = 0.5) -> float:
    """Return thresholded F1, using ``0.0`` when precision plus recall is zero."""
    labels, scores = _validated_inputs(y_true, y_score)
    true_positive, false_positive, false_negative, _ = _confusion_counts(
        labels, scores, threshold=threshold
    )
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    precision = true_positive / precision_denominator if precision_denominator else 0.0
    recall = true_positive / recall_denominator if recall_denominator else 0.0
    return 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0


def matthews_corrcoef(
    y_true: Iterable[Any], y_score: Iterable[Any], *, threshold: float = 0.5
) -> float:
    """Return thresholded Matthews correlation, or ``0.0`` if undefined."""
    labels, scores = _validated_inputs(y_true, y_score)
    true_positive, false_positive, false_negative, true_negative = _confusion_counts(
        labels, scores, threshold=threshold
    )
    numerator = (true_positive * true_negative) - (false_positive * false_negative)
    denominator = sqrt(
        (true_positive + false_positive)
        * (true_positive + false_negative)
        * (true_negative + false_positive)
        * (true_negative + false_negative)
    )
    return numerator / denominator if denominator else 0.0


def binary_log_loss(y_true: Iterable[Any], y_probability: Iterable[Any]) -> float:
    """Return mean binary log loss for probability scores.

    Exact zero and one probabilities are clipped to machine epsilon before the
    logarithm.  Unlike ranking AUCs, this metric is defined for a singleton
    label set.
    """
    labels, probabilities = _validated_inputs(y_true, y_probability)
    _require_probability_scores(probabilities)
    epsilon = np.finfo(float).eps
    clipped = np.clip(probabilities, epsilon, 1.0 - epsilon)
    losses = -(labels * np.log(clipped) + (1 - labels) * np.log1p(-clipped))
    return float(np.mean(losses))


def binary_classification_metrics(
    y_true: Iterable[Any],
    y_score: Iterable[Any],
    *,
    threshold: float = 0.5,
) -> dict[str, float | int]:
    """Evaluate deterministic ranking, threshold, and probability metrics.

    ``y_score`` is used as a ranking score and as a threshold score.  It must
    also lie in ``[0, 1]`` because this convenience function reports log loss;
    use the individual ranking/threshold functions when evaluating uncalibrated
    scores or logits.
    """
    labels, scores = _validated_inputs(y_true, y_score)
    _require_probability_scores(scores)
    true_positive, false_positive, false_negative, true_negative = _confusion_counts(
        labels, scores, threshold=threshold
    )
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    precision = true_positive / precision_denominator if precision_denominator else 0.0
    recall = true_positive / recall_denominator if recall_denominator else 0.0
    f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
    mcc_denominator = sqrt(
        (true_positive + false_positive)
        * (true_positive + false_negative)
        * (true_negative + false_positive)
        * (true_negative + false_negative)
    )
    mcc_numerator = (true_positive * true_negative) - (false_positive * false_negative)

    return {
        "n_obs": int(labels.size),
        "n_positive": int(np.count_nonzero(labels)),
        "n_negative": int(labels.size - np.count_nonzero(labels)),
        "roc_auc": roc_auc(labels, scores),
        "pr_auc": pr_auc(labels, scores),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mcc": mcc_numerator / mcc_denominator if mcc_denominator else 0.0,
        "log_loss": binary_log_loss(labels, scores),
    }


# Concise aliases for callers that use the metric names directly in configuration.
precision = precision_score
recall = recall_score
f1 = f1_score
mcc = matthews_corrcoef
log_loss = binary_log_loss
evaluate_binary_predictions = binary_classification_metrics

__all__ = [
    "binary_classification_metrics",
    "binary_log_loss",
    "evaluate_binary_predictions",
    "f1",
    "f1_score",
    "log_loss",
    "matthews_corrcoef",
    "mcc",
    "pr_auc",
    "precision",
    "precision_score",
    "recall",
    "recall_score",
    "roc_auc",
]
