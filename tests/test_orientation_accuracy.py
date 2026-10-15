"""Regression checks for plan-defined orientation-accuracy extraction."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "57_extract_orientation_accuracy.py"


def load_module():
    """Import the standalone extraction script as a testable module."""
    specification = importlib.util.spec_from_file_location("orientation_accuracy", SCRIPT)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def test_orientation_value_uses_half_credit_for_ties() -> None:
    module = load_module()
    assert module.orientation_value(2.0, 1.0) == 1.0
    assert module.orientation_value(1.0, 2.0) == 0.0
    assert module.orientation_value(1.0, 1.0) == 0.5


def test_pair_rows_matches_reversal_by_ordered_roles_not_identifier() -> None:
    module = load_module()
    frame = pd.DataFrame(
        {
            "candidate_id": ["positive-unrelated-id", "negative-unrelated-id"],
            "label": [1, 0],
            "tail_arity": [1, 1],
            "head_arity": [1, 1],
            "tail_nodes_json": ['["alpha"]', '["beta"]'],
            "head_nodes_json": ['["beta"]', '["alpha"]'],
        }
    )
    pairs = module.paired_rows(frame, Path("synthetic.csv"))
    assert len(pairs) == 1
    positive, negative = pairs[0]
    assert positive["candidate_id"] == "positive-unrelated-id"
    assert negative["candidate_id"] == "negative-unrelated-id"
