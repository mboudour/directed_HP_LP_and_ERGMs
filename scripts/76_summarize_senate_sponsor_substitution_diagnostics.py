#!/usr/bin/env python3
"""Summarize Senate sponsor-substitution recoverability and paired score preference.

The diagnostic keeps the frozen grammar-preserving pairs intact. It reports the
fraction of true bills and sponsor-substitution alternatives whose directed
dyadic footprints already survive in the split-observed graph, then evaluates
whether each score prefers the true ordered sponsor assignment within every
pair. All uncertainty is resampled over complete frozen masks, never over
candidate rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_REPS = 10_000
SCORE_MODELS = ("M4c", "M5")
NO_MUTUALITY_MODEL = "M4c_no_mutual"


def parse_args() -> argparse.Namespace:
    """Parse one fixed Senate sponsor-substitution diagnostic contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument("--hard-panel-dir", type=Path, required=True)
    parser.add_argument("--ergm-dir", type=Path, required=True)
    parser.add_argument(
        "--structural-ergm-dir",
        type=Path,
        help=(
            "Optional M4c score bundle when --ergm-dir contains M5 only. Without it, "
            "--ergm-dir must contain M4c and M5."
        ),
    )
    parser.add_argument(
        "--no-mutuality-ergm-dir",
        type=Path,
        help=(
            "Optional matched score bundle containing M4c and M4c_no_mutual for the direct "
            "within-stratum mutuality diagnostic."
        ),
    )
    parser.add_argument("--node-covariates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve project-relative paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render repository-relative provenance paths where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def split_identity(name: str) -> tuple[str, int]:
    """Decode masking mechanism and replicate from a frozen split name."""
    mechanism, replicate = name.rsplit("_replicate_", maxsplit=1)
    if not replicate.isdigit():
        raise ValueError(f"invalid split name: {name}")
    return mechanism, int(replicate)


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create or deliberately replace the aggregate-only diagnostic directory."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read one required nonempty CSV table."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"STOP: empty required CSV: {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write one nonempty deterministic aggregate table."""
    if not rows:
        raise RuntimeError(f"cannot write empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_party(path: Path) -> dict[str, str]:
    """Read complete fixed Senate party information without writing actor-level output."""
    rows = read_csv(path)
    required = {"node", "party_118_entry"}
    if required - set(rows[0]):
        raise SystemExit(f"STOP: covariate table lacks fields {sorted(required)}")
    values = {row["node"].strip(): row["party_118_entry"].strip() for row in rows}
    if len(values) != len(rows) or any(not node or not party for node, party in values.items()):
        raise SystemExit("STOP: covariate table has duplicate or empty party records.")
    return values


def read_ergm_scores(
    path: Path, required_models: tuple[str, ...]
) -> dict[tuple[str, int, str, str], float]:
    """Index geometric footprint scores by complete split, model, and candidate ID."""
    scores: dict[tuple[str, int, str, str], float] = {}
    for row in read_csv(path):
        model = row["model"]
        if model not in required_models or row["panel"] != "sponsor_substitution":
            continue
        key = (row["mechanism"], int(row["replicate"]), model, row["candidate_id"])
        if key in scores:
            raise SystemExit(f"STOP: duplicate ERGM score record: {key}")
        scores[key] = float(row["L1g"])
    for model in required_models:
        if not any(key[2] == model for key in scores):
            raise SystemExit(f"STOP: expected {model} sponsor-substitution scores are absent.")
    return scores


def party_footprint_mean(row: dict[str, str], party: dict[str, str]) -> float:
    """Calculate the transparent same-party local score for one candidate."""
    tail = tuple(str(value) for value in json.loads(row["tail_nodes_json"]))
    head = tuple(str(value) for value in json.loads(row["head_nodes_json"]))
    missing = set(tail + head) - set(party)
    if missing:
        raise SystemExit(f"STOP: party mapping lacks candidate actors: {sorted(missing)[:10]}")
    return mean(int(party[source] == party[target]) for source in tail for target in head)


def preference(positive: float, negative: float) -> float:
    """Return the tie-aware probability that a score ranks the positive above its substitute."""
    if positive > negative:
        return 1.0
    if positive < negative:
        return 0.0
    return 0.5


def stratum(positive_survives: bool, substitute_survives: bool) -> str:
    """Assign a pair to one recoverability pattern."""
    if positive_survives and substitute_survives:
        return "both footprints survive"
    if positive_survives:
        return "true bill only survives"
    if substitute_survives:
        return "substitution only survives"
    return "neither footprint survives"


def bootstrap(values: list[float], key: str) -> tuple[float, float]:
    """Generate a deterministic percentile interval over complete masks."""
    seed = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    generator = np.random.default_rng(seed)
    observed = np.asarray(values, dtype=float)
    draws = generator.choice(observed, size=(BOOTSTRAP_REPS, observed.size), replace=True).mean(
        axis=1
    )
    lower, upper = np.quantile(draws, (0.025, 0.975))
    return float(lower), float(upper)


def summarize(split_rows: list[dict[str, object]], dataset_id: str) -> list[dict[str, object]]:
    """Summarize mask-level exact fractions and pair preferences with CIs."""
    groups: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in split_rows:
        measures = (
            "positive_footprint_survival",
            "substitution_footprint_survival",
            "M4c_positive_preference",
            "M5_positive_preference",
            "same_party_positive_preference",
        )
        if "M4c_no_mutual_positive_preference" in row:
            measures += ("M4c_no_mutual_positive_preference",)
        for measure in measures:
            groups[(str(row["mechanism"]), str(row["recoverability_stratum"]), measure)].append(
                float(row[measure])
            )
    output: list[dict[str, object]] = []
    for (mechanism, recoverability, measure), values in sorted(groups.items()):
        lower, upper = bootstrap(values, f"{dataset_id}|{mechanism}|{recoverability}|{measure}")
        output.append(
            {
                "mechanism": mechanism,
                "recoverability_stratum": recoverability,
                "measure": measure,
                "completed_masks": len(values),
                "mean": mean(values),
                "sd": stdev(values) if len(values) > 1 else 0.0,
                "bootstrap_reps": BOOTSTRAP_REPS,
                "bootstrap_ci_lower": lower,
                "bootstrap_ci_upper": upper,
            }
        )
    return output


def recoverability_summary(
    split_rows: list[dict[str, object]], dataset_id: str
) -> list[dict[str, object]]:
    """Summarize the per-mask prevalence of each exact recoverability pattern."""
    by_mask: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in split_rows:
        by_mask[(str(row["mechanism"]), int(row["replicate"]))].append(row)
    values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (mechanism, _replicate), rows in by_mask.items():
        total_pairs = sum(int(row["pairs"]) for row in rows)
        if total_pairs == 0:
            raise RuntimeError("a diagnosed Senate mask has zero sponsor-substitution pairs")
        for row in rows:
            pattern = str(row["recoverability_stratum"])
            values[(mechanism, pattern)].append(int(row["pairs"]) / total_pairs)
        values[(mechanism, "true bill footprint survives")].append(
            sum(int(row["pairs"]) * float(row["positive_footprint_survival"]) for row in rows)
            / total_pairs
        )
        values[(mechanism, "substitution footprint survives")].append(
            sum(int(row["pairs"]) * float(row["substitution_footprint_survival"]) for row in rows)
            / total_pairs
        )
    output: list[dict[str, object]] = []
    for (mechanism, measure), observations in sorted(values.items()):
        lower, upper = bootstrap(observations, f"{dataset_id}|{mechanism}|recoverability|{measure}")
        output.append(
            {
                "mechanism": mechanism,
                "measure": measure,
                "completed_masks": len(observations),
                "mean": mean(observations),
                "sd": stdev(observations) if len(observations) > 1 else 0.0,
                "bootstrap_reps": BOOTSTRAP_REPS,
                "bootstrap_ci_lower": lower,
                "bootstrap_ci_upper": upper,
            }
        )
    return output


def main() -> None:
    """Create aggregate-only Senate sponsor-substitution survival diagnostics."""
    args = parse_args()
    hard_dir = resolve(args.hard_panel_dir)
    ergm_dir = resolve(args.ergm_dir)
    structural_ergm_dir = resolve(args.structural_ergm_dir) if args.structural_ergm_dir else None
    no_mutuality_dir = resolve(args.no_mutuality_ergm_dir) if args.no_mutuality_ergm_dir else None
    covariate_path = resolve(args.node_covariates)
    output_dir = resolve(args.output_dir)
    if (
        not hard_dir.is_dir()
        or not ergm_dir.is_dir()
        or not covariate_path.is_file()
        or (structural_ergm_dir is not None and not structural_ergm_dir.is_dir())
        or (no_mutuality_dir is not None and not no_mutuality_dir.is_dir())
    ):
        raise SystemExit(
            "STOP: hard-panel directory, ERGM directory, or covariate input is missing."
        )
    prepare_output(output_dir, args.overwrite)
    party = read_party(covariate_path)
    m5_scores = read_ergm_scores(ergm_dir / "event_footprint_scores.csv", ("M5",))
    m4c_scores = read_ergm_scores(
        (structural_ergm_dir or ergm_dir) / "event_footprint_scores.csv", ("M4c",)
    )
    no_mutuality_scores = (
        read_ergm_scores(
            no_mutuality_dir / "event_footprint_scores.csv", ("M4c", NO_MUTUALITY_MODEL)
        )
        if no_mutuality_dir is not None
        else None
    )
    split_rows: list[dict[str, object]] = []
    for split_dir in sorted(path for path in hard_dir.iterdir() if path.is_dir()):
        prediction_path = split_dir / "sponsor_substitution_candidate_predictions.csv"
        if not prediction_path.is_file():
            continue
        mechanism, replicate = split_identity(split_dir.name)
        pairs: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in read_csv(prediction_path):
            pairs[row["paired_source_event_type_id"]].append(row)
        grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
        for source_id, pair in pairs.items():
            if len(pair) != 2:
                raise SystemExit(
                    f"STOP: incomplete sponsor-substitution pair: {split_dir.name}:{source_id}"
                )
            positive = next((row for row in pair if int(row["label"]) == 1), None)
            negative = next((row for row in pair if int(row["label"]) == 0), None)
            if positive is None or negative is None:
                raise SystemExit(f"STOP: invalid labels in pair {split_dir.name}:{source_id}")
            positive_survives = int(positive["already_observed_footprint"]) == 1
            negative_survives = int(negative["already_observed_footprint"]) == 1
            pattern = stratum(positive_survives, negative_survives)
            record: dict[str, float] = {
                "positive_footprint_survival": float(positive_survives),
                "substitution_footprint_survival": float(negative_survives),
                "same_party_positive_preference": preference(
                    party_footprint_mean(positive, party), party_footprint_mean(negative, party)
                ),
            }
            for model, score_source in (("M4c", m4c_scores), ("M5", m5_scores)):
                positive_key = (
                    mechanism,
                    replicate,
                    model,
                    f"sponsor_substitution::{positive['candidate_id']}",
                )
                negative_key = (
                    mechanism,
                    replicate,
                    model,
                    f"sponsor_substitution::{negative['candidate_id']}",
                )
                if positive_key not in score_source or negative_key not in score_source:
                    raise SystemExit(
                        f"STOP: missing {model} ERGM score for {split_dir.name}:{source_id}"
                    )
                record[f"{model}_positive_preference"] = preference(
                    score_source[positive_key], score_source[negative_key]
                )
            if no_mutuality_scores is not None:
                positive_key = (
                    mechanism,
                    replicate,
                    NO_MUTUALITY_MODEL,
                    f"sponsor_substitution::{positive['candidate_id']}",
                )
                negative_key = (
                    mechanism,
                    replicate,
                    NO_MUTUALITY_MODEL,
                    f"sponsor_substitution::{negative['candidate_id']}",
                )
                if (
                    positive_key not in no_mutuality_scores
                    or negative_key not in no_mutuality_scores
                ):
                    raise SystemExit(
                        f"STOP: missing M4c_no_mutual score for {split_dir.name}:{source_id}"
                    )
                record["M4c_no_mutual_positive_preference"] = preference(
                    no_mutuality_scores[positive_key], no_mutuality_scores[negative_key]
                )
            grouped[pattern].append(record)
        for pattern, records in sorted(grouped.items()):
            split_rows.append(
                {
                    "mechanism": mechanism,
                    "replicate": replicate,
                    "recoverability_stratum": pattern,
                    "pairs": len(records),
                    **{key: mean(row[key] for row in records) for key in records[0]},
                }
            )
    if not split_rows:
        raise SystemExit("STOP: no sponsor-substitution panels were diagnosed.")
    summary = summarize(split_rows, args.dataset_id)
    prevalence = recoverability_summary(split_rows, args.dataset_id)
    write_csv(output_dir / "split_diagnostics.csv", split_rows)
    write_csv(output_dir / "summary.csv", summary)
    write_csv(output_dir / "recoverability_summary.csv", prevalence)
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/76_summarize_senate_sponsor_substitution_diagnostics.py",
                "dataset_id": args.dataset_id,
                "source_hard_panels": recorded(hard_dir),
                "source_m5_ergm_scores": recorded(ergm_dir),
                "source_m4c_ergm_scores": recorded(structural_ergm_dir or ergm_dir),
                "source_no_mutuality_ergm_scores": (
                    recorded(no_mutuality_dir) if no_mutuality_dir is not None else None
                ),
                "score_contract": {
                    "M4c_and_M5": (
                        "tie-aware within-pair preference using L1g conditional footprint scores"
                    ),
                    "same_party": (
                        "tie-aware within-pair preference using mean same-party footprint share"
                    ),
                    "M4c_no_mutual": (
                        "tie-aware within-pair preference using density-controlled structural "
                        "conditional footprint scores with mutuality removed"
                    ),
                },
                "survival_definition": (
                    "all candidate footprint arcs appear in the split-observed projection"
                ),
                "uncertainty": (
                    "10,000 percentile bootstrap resamples of complete frozen masks within each "
                    "mechanism and stratum"
                ),
                "privacy": "actor-level pair records are not emitted",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Senate sponsor-substitution diagnostics passed.")
    print(f"Mask-stratum summaries: {len(split_rows)}")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
