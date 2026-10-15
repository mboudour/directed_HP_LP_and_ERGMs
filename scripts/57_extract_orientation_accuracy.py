#!/usr/bin/env python3
"""Extract plan-defined orientation accuracy from retained paired score outputs.

This script reads ignored candidate-level prediction files locally and writes only
aggregate-safe score summaries.  It never copies actor labels, event identifiers,
role lists, or candidate-level scores into the output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "manuscript" / "snam" / "tables" / "orientation_accuracy.csv"

HEURISTIC_SCORES = {
    "already_observed_footprint": "Observed-footprint baseline",
    "lifted_adamic_adar_total_mean": "Directed AA total",
    "lifted_degree_product_mean": "Degree-product mean",
    "lifted_reverse_arc_mean": "Reverse-arc mean",
}
ERGM_SCORES = {
    "M0::L1": ("M0", "L1"),
    "M4c::L1g": ("M4c", "L1g"),
}
DATASETS = ("enron", "mathoverflow")


@dataclass(frozen=True)
class PairScore:
    """One score comparison between a held-out type and its reversal."""

    split: str
    dataset: str
    mechanism: str
    method: str
    balanced: bool
    value: float


def parse_args() -> argparse.Namespace:
    """Parse local inputs and aggregate-only output location."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase2-root",
        type=Path,
        default=PROJECT_ROOT / "results" / "phase2",
        help="Ignored local Phase 2 result root containing hard-panel predictions.",
    )
    parser.add_argument(
        "--models-root",
        type=Path,
        default=PROJECT_ROOT / "results" / "models",
        help="Ignored local model-result root containing ERGM footprint scores.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Aggregate-only CSV destination.",
    )
    return parser.parse_args()


def parse_split(split: str) -> tuple[str, int]:
    """Validate the frozen mask identifier and return its mechanism and replicate."""
    mechanism, separator, replicate_text = split.rpartition("_replicate_")
    if not separator or not mechanism or not replicate_text.isdigit():
        raise ValueError(f"invalid frozen split label: {split!r}")
    return mechanism, int(replicate_text)


def orientation_value(positive: float, negative: float) -> float:
    """Return the planned half-credit orientation comparison for one pair."""
    if positive > negative:
        return 1.0
    if positive < negative:
        return 0.0
    return 0.5


def paired_rows(frame: pd.DataFrame, path: Path) -> list[tuple[pd.Series, pd.Series]]:
    """Return each positive and its unique reversal, matched by ordered role sets."""
    required = {
        "candidate_id",
        "label",
        "tail_arity",
        "head_arity",
        "tail_nodes_json",
        "head_nodes_json",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"hard-panel file lacks required columns {sorted(missing)}: {path}")
    if set(frame["label"].unique()) != {0, 1}:
        raise ValueError(f"hard-panel labels must be exactly 0/1: {path}")
    positives = frame.loc[frame["label"] == 1]
    negatives = frame.loc[frame["label"] == 0]
    negative_by_roles = {
        (row.tail_nodes_json, row.head_nodes_json): row for row in negatives.itertuples(index=False)
    }
    if len(negative_by_roles) != len(negatives):
        raise ValueError(f"duplicate reversal-role identities in {path}")
    pairs: list[tuple[pd.Series, pd.Series]] = []
    for _, positive in positives.iterrows():
        reversal_key = (positive["head_nodes_json"], positive["tail_nodes_json"])
        negative = negative_by_roles.get(reversal_key)
        if negative is None:
            raise ValueError(f"reversal candidate pairing failed in {path}")
        pairs.append((positive, pd.Series(negative._asdict())))
    if len(pairs) != len(negatives):
        raise ValueError(f"reversal candidate pairing failed in {path}")
    return pairs


def heuristic_pair_scores(phase2_root: Path, dataset: str) -> list[PairScore]:
    """Compute heuristic orientation values from one candidate pair per held-out type."""
    root = phase2_root / f"{dataset}_event_first_native_hard_panels"
    paths = sorted(root.glob("*/reversal_orientation_candidate_predictions.csv"))
    if len(paths) != 60:
        raise ValueError(f"expected 60 hard-panel files for {dataset}, found {len(paths)}")
    result: list[PairScore] = []
    for path in paths:
        split = path.parent.name
        mechanism, _ = parse_split(split)
        frame = pd.read_csv(path)
        pairs = paired_rows(frame, path)
        for method, label in HEURISTIC_SCORES.items():
            if method not in frame.columns:
                raise ValueError(f"missing score {method!r} in {path}")
            for positive, negative in pairs:
                result.append(
                    PairScore(
                        split=split,
                        dataset=dataset,
                        mechanism=mechanism,
                        method=label,
                        balanced=bool(int(positive["tail_arity"]) == int(positive["head_arity"])),
                        value=orientation_value(float(positive[method]), float(negative[method])),
                    )
                )
    return result


def ergm_pair_scores(models_root: Path, dataset: str) -> list[PairScore]:
    """Compute selected ERGM orientation values from matching footprint-score rows."""
    path = models_root / f"{dataset}_native_event_ergm_footprints" / "event_footprint_scores.csv"
    if not path.is_file():
        raise FileNotFoundError(f"missing ERGM candidate-score file: {path}")
    frame = pd.read_csv(path)
    required = {
        "split",
        "mechanism",
        "model",
        "panel",
        "candidate_id",
        "label",
        "tail_arity",
        "head_arity",
        "L1",
        "L1g",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"ERGM file lacks required columns {sorted(missing)}: {path}")
    frame = frame.loc[frame["panel"] == "reversal_orientation"].copy()
    result: list[PairScore] = []
    for method, (model, score) in ERGM_SCORES.items():
        subset = frame.loc[frame["model"] == model].copy()
        if subset.empty:
            raise ValueError(f"missing model {model!r} in {path}")
        for split, split_frame in subset.groupby("split", sort=True):
            mechanism, _ = parse_split(split)
            if set(split_frame["mechanism"].unique()) != {mechanism}:
                raise ValueError(f"mechanism does not match split name in {path}: {split}")
            pairs = paired_rows(split_frame, path)
            for positive, negative in pairs:
                result.append(
                    PairScore(
                        split=split,
                        dataset=dataset,
                        mechanism=mechanism,
                        method=method,
                        balanced=bool(int(positive["tail_arity"]) == int(positive["head_arity"])),
                        value=orientation_value(float(positive[score]), float(negative[score])),
                    )
                )
    return result


def summarize(scores: list[PairScore]) -> pd.DataFrame:
    """Summarize plan-defined orientation accuracy by frozen mask and subset."""
    records = pd.DataFrame(
        [
            {
                "dataset": score.dataset,
                "mechanism": score.mechanism,
                "split": score.split,
                "method": score.method,
                "subset": "balanced arity" if score.balanced else "all arities",
                "value": score.value,
            }
            for score in scores
        ]
    )
    all_records = records.copy()
    all_records["subset"] = "all arities"
    records = pd.concat([all_records, records.loc[records["subset"] == "balanced arity"]])
    per_mask = (
        records.groupby(["dataset", "mechanism", "split", "method", "subset"], as_index=False)
        .agg(orientation_accuracy=("value", "mean"), paired_types=("value", "size"))
        .sort_values(["dataset", "mechanism", "method", "subset", "split"])
    )
    rows: list[dict[str, object]] = []
    for keys, group in per_mask.groupby(["dataset", "mechanism", "method", "subset"], sort=True):
        values = group["orientation_accuracy"].tolist()
        masks = len(values)
        rows.append(
            {
                "dataset": keys[0],
                "mechanism": keys[1],
                "method": keys[2],
                "subset": keys[3],
                "completed_masks": masks,
                "orientation_accuracy_mean": mean(values),
                "orientation_accuracy_mask_sd": stdev(values) if masks > 1 else 0.0,
                "paired_types_total": int(group["paired_types"].sum()),
                "paired_types_per_mask_mean": mean(group["paired_types"].tolist()),
            }
        )
    output = pd.DataFrame(rows).sort_values(["dataset", "mechanism", "method", "subset"])
    expected = len(DATASETS) * 2 * (len(HEURISTIC_SCORES) + len(ERGM_SCORES)) * 2
    if len(output) != expected:
        raise ValueError(f"expected {expected} aggregate rows, found {len(output)}")
    if not (output["completed_masks"] == 30).all():
        raise ValueError("each orientation summary must contain 30 completed masks")
    return output.reset_index(drop=True)


def main() -> None:
    """Write aggregate-safe plan-defined orientation accuracy results."""
    args = parse_args()
    phase2_root = args.phase2_root.resolve()
    models_root = args.models_root.resolve()
    scores: list[PairScore] = []
    for dataset in DATASETS:
        scores.extend(heuristic_pair_scores(phase2_root, dataset))
        scores.extend(ergm_pair_scores(models_root, dataset))
    output = summarize(scores)
    destination = args.output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(destination, index=False)
    print(f"Orientation summaries written: {destination}")
    print(f"Aggregate rows: {len(output)}; candidate-level rows retained only in source inputs.")


if __name__ == "__main__":
    main()
