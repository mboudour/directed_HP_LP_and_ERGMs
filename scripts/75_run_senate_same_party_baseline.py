#!/usr/bin/env python3
"""Evaluate the Senate same-party local footprint baseline on frozen panels.

For each candidate directed footprint, the score is the arithmetic mean of
I{party(tail) = party(head)} over its dyads. It is a transparent local
covariate baseline, not an estimated probability or a fitted ERGM term.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HEURISTIC_DRIVER = PROJECT_ROOT / "scripts" / "37_run_native_event_heuristics.py"
SCORE = "lifted_same_party_mean"


def load_shared() -> Any:
    """Load the tested ranking-metric primitives from the heuristic driver."""
    spec = importlib.util.spec_from_file_location("native_heuristics_same_party", HEURISTIC_DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import native heuristic driver: {HEURISTIC_DRIVER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    """Parse one frozen-panel same-party benchmark contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument(
        "--candidate-file",
        required=True,
        help="Candidate CSV filename inside every mechanism_replicate_NNN directory.",
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


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create or deliberately replace the baseline output bundle."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: output directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def read_party(path: Path) -> dict[str, str]:
    """Read a complete fixed Senate party mapping without exposing it in outputs."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"node", "party_118_entry"}
        if reader.fieldnames is None or required - set(reader.fieldnames):
            raise SystemExit(
                f"STOP: covariate table lacks required fields {sorted(required)}: {path}"
            )
        mapping = {row["node"].strip(): row["party_118_entry"].strip() for row in reader}
    if not mapping or any(not node or not party for node, party in mapping.items()):
        raise SystemExit("STOP: covariate table has empty node or party values.")
    if len(mapping) != len(set(mapping)):
        raise SystemExit("STOP: covariate table has duplicate node values.")
    return mapping


def read_rows(path: Path, party: dict[str, str]) -> list[dict[str, object]]:
    """Read panel candidates and add the party-match footprint score."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"candidate_id", "tail_nodes_json", "head_nodes_json", "label"}
    if not rows or required - set(rows[0]):
        raise SystemExit(f"STOP: candidate panel lacks required columns: {path}")
    output: list[dict[str, object]] = []
    for row in rows:
        try:
            tail = tuple(str(value) for value in json.loads(row["tail_nodes_json"]))
            head = tuple(str(value) for value in json.loads(row["head_nodes_json"]))
            label = int(row["label"])
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise SystemExit(f"STOP: malformed candidate row in {path}") from error
        if not tail or not head or label not in {0, 1} or set(tail).intersection(head):
            raise SystemExit(f"STOP: invalid candidate roles or label in {path}")
        missing = set(tail + head) - set(party)
        if missing:
            raise SystemExit(
                f"STOP: candidate references party-unmapped actors: {sorted(missing)[:10]}"
            )
        score = mean(int(party[source] == party[target]) for source in tail for target in head)
        output.append(
            {
                "candidate_id": row["candidate_id"],
                "tail_nodes_json": row["tail_nodes_json"],
                "head_nodes_json": row["head_nodes_json"],
                "tail_arity": int(row.get("tail_arity") or len(tail)),
                "head_arity": int(row.get("head_arity") or len(head)),
                "label": label,
                SCORE: score,
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a required nonempty deterministic output table."""
    if not rows:
        raise RuntimeError(f"cannot write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize(metrics: list[dict[str, object]]) -> list[dict[str, object]]:
    """Aggregate replicate-level ranking metrics by masking mechanism."""
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in metrics:
        groups[(str(row["mechanism"]), str(row["metric"]))].append(float(row["value"]))
    return [
        {
            "mechanism": mechanism,
            "score": SCORE,
            "metric": metric,
            "completed_replicates": len(values),
            "mean": mean(values),
            "sd": stdev(values) if len(values) > 1 else 0.0,
        }
        for (mechanism, metric), values in sorted(groups.items())
    ]


def main() -> None:
    """Score the same-party baseline on every complete frozen candidate panel."""
    args = parse_args()
    shared = load_shared()
    panel_dir = resolve(args.panel_dir)
    covariate_path = resolve(args.node_covariates)
    output_dir = resolve(args.output_dir)
    if not panel_dir.is_dir() or not covariate_path.is_file():
        raise SystemExit("STOP: panel directory or political covariate table is missing.")
    prepare_output(output_dir, args.overwrite)
    party = read_party(covariate_path)
    all_metrics: list[dict[str, object]] = []
    split_summary: list[dict[str, object]] = []
    for split_dir in sorted(path for path in panel_dir.iterdir() if path.is_dir()):
        candidate_path = split_dir / args.candidate_file
        if not candidate_path.is_file():
            continue
        mechanism, replicate = shared.split_identity(split_dir)
        predictions = read_rows(candidate_path, party)
        metrics = shared.metric_rows(predictions, mechanism, replicate)
        metrics = [row for row in metrics if row["score"] == SCORE]
        if not metrics:
            raise RuntimeError(f"same-party metric generation failed for {split_dir.name}")
        split_output = output_dir / split_dir.name
        split_output.mkdir()
        write_csv(split_output / "same_party_predictions.csv", predictions)
        write_csv(split_output / "same_party_metrics.csv", metrics)
        all_metrics.extend(metrics)
        split_summary.append(
            {
                "mechanism": mechanism,
                "replicate": replicate,
                "candidates": len(predictions),
                "positives": sum(int(row["label"]) for row in predictions),
                "negatives": sum(not int(row["label"]) for row in predictions),
            }
        )
    if not split_summary:
        raise SystemExit("STOP: no complete candidate panels found.")
    summary = summarize(all_metrics)
    write_csv(output_dir / "split_summary.csv", split_summary)
    write_csv(output_dir / "metric_summary.csv", summary)
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/75_run_senate_same_party_baseline.py",
                "dataset_id": args.dataset_id,
                "source_panels": recorded(panel_dir),
                "candidate_file": args.candidate_file,
                "node_covariates": recorded(covariate_path),
                "score": "mean I(party(tail)=party(head)) across candidate footprint dyads",
                "interpretation": "Fixed covariate ranking baseline; not a fitted probability.",
                "splits_completed": len(split_summary),
                "privacy": "Only aggregate score summaries are intended for publication.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Senate same-party baseline passed.")
    print(f"Dataset: {args.dataset_id}; frozen panels: {len(split_summary)}")
    print(f"Output bundle: {recorded(output_dir)}")


if __name__ == "__main__":
    main()
