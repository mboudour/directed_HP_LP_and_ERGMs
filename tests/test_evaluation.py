"""Tests for deterministic evaluation metrics and leakage-safe negative panels."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from directed_hp.evaluation.metrics import (
    binary_classification_metrics,
    binary_log_loss,
    f1_score,
    matthews_corrcoef,
    pr_auc,
    precision_score,
    recall_score,
    roc_auc,
)
from directed_hp.evaluation.negative_panels import (
    build_target_aware_negative_panels,
    random_negative_panel,
)


def test_binary_metrics_are_deterministic_and_match_known_values() -> None:
    labels = [0, 0, 1, 1]
    probabilities = [0.1, 0.4, 0.35, 0.8]

    metrics = binary_classification_metrics(labels, probabilities)

    assert roc_auc(labels, probabilities) == pytest.approx(0.75)
    assert pr_auc(labels, probabilities) == pytest.approx(5 / 6)
    assert precision_score(labels, probabilities) == pytest.approx(1.0)
    assert recall_score(labels, probabilities) == pytest.approx(0.5)
    assert f1_score(labels, probabilities) == pytest.approx(2 / 3)
    assert matthews_corrcoef(labels, probabilities) == pytest.approx(1 / math.sqrt(3))
    assert metrics == binary_classification_metrics(labels, probabilities)
    assert metrics["n_positive"] == 2
    assert metrics["n_negative"] == 2
    assert metrics["log_loss"] == pytest.approx(binary_log_loss(labels, probabilities))


def test_degenerate_labels_have_explicit_metric_behavior() -> None:
    labels = [1, 1]
    probabilities = [0.1, 0.9]

    metrics = binary_classification_metrics(labels, probabilities)

    assert math.isnan(metrics["roc_auc"])
    assert math.isnan(metrics["pr_auc"])
    assert metrics["precision"] == pytest.approx(1.0)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["mcc"] == pytest.approx(0.0)
    assert metrics["log_loss"] > 0.0


def _positives() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tail": [("a",), ("b",)],
            "head": [("c",), ("d",)],
            "candidate_metadata": ["positive-a", "positive-b"],
        }
    )


def _random_pool() -> pd.DataFrame:
    return pd.DataFrame(
        {
            # The first row duplicates a positive key but deliberately has
            # different metadata; key_columns must still prevent leakage.
            "tail": [("a",), ("e",), ("f",), ("f",), ("g",)],
            "head": [("c",), ("h",), ("i",), ("i",), ("j",)],
            "candidate_metadata": ["leak", "random-e", "random-f", "duplicate-f", "random-g"],
        }
    )


def test_random_panel_is_reproducible_preserves_metadata_and_excludes_positives() -> None:
    first = random_negative_panel(
        _positives(), _random_pool(), n_negatives=2, seed=41, key_columns=["tail", "head"]
    )
    second = random_negative_panel(
        _positives(), _random_pool(), n_negatives=2, seed=41, key_columns=["tail", "head"]
    )

    pd.testing.assert_frame_equal(first, second)
    negatives = first.loc[first["label"] == 0]
    positives = first.loc[first["label"] == 1]
    assert len(negatives) == 2
    assert "candidate_metadata" in first.columns
    assert "leak" not in negatives["candidate_metadata"].tolist()
    assert set(zip(positives["tail"], positives["head"], strict=True)).isdisjoint(
        set(zip(negatives["tail"], negatives["head"], strict=True))
    )


def test_target_aware_hard_panels_are_built_only_for_supplied_candidates() -> None:
    positives = _positives()
    hard_candidate = pd.DataFrame(
        {
            "tail": [("a",), ("z",)],
            "head": [("c",), ("q",)],
            "candidate_metadata": ["overlap", "hard-candidate"],
        }
    )

    panels = build_target_aware_negative_panels(
        positives,
        reversal_candidates=hard_candidate,
        orientation_candidates=hard_candidate,
        near_complete_footprint_candidates=hard_candidate,
        non_maximal_concept_candidates=hard_candidate,
        role_corrupted_candidates=hard_candidate,
        key_columns=["tail", "head"],
    )

    assert set(panels) == {
        "reversal_orientation",
        "near_complete_footprint",
        "non_maximal_concept",
        "role_corrupted",
    }
    for kind, panel in panels.items():
        negatives = panel.loc[panel["label"] == 0]
        assert negatives["candidate_metadata"].tolist() == ["hard-candidate"]
        assert negatives["negative_kind"].tolist() == [kind]
        assert set(
            zip(
                panel.loc[panel["label"] == 1, "tail"],
                panel.loc[panel["label"] == 1, "head"],
                strict=True,
            )
        ).isdisjoint(set(zip(negatives["tail"], negatives["head"], strict=True)))
