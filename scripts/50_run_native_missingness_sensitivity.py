#!/usr/bin/env python3
"""Run predeclared native-event masking-rate and MNAR-in sensitivity analyses."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse fully explicit dataset inputs and predeclared sensitivity controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--event-tail-column", required=True)
    parser.add_argument("--event-head-column", required=True)
    parser.add_argument("--node-column", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--rates", default="0.10,0.20,0.50")
    parser.add_argument("--mechanisms", default="mcar,mnar_out,mnar_in")
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--tail-cap", type=int, default=3)
    parser.add_argument("--head-cap", type=int, default=3)
    parser.add_argument("--max-weak-distance", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        args.rates = tuple(float(item.strip()) for item in args.rates.split(",") if item.strip())
    except ValueError as error:
        parser.error(f"--rates must contain comma-separated decimal fractions: {error}")
    if not args.rates or any(not 0.0 < rate < 1.0 for rate in args.rates):
        parser.error("--rates must be nonempty values strictly between zero and one.")
    if len(set(args.rates)) != len(args.rates) or args.replicates < 1:
        parser.error("--rates must not repeat and --replicates must be at least one.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative command-line paths."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render a project-relative path when possible, otherwise preserve its absolute form."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def run(command: list[str]) -> None:
    """Execute one source-controlled component with fail-fast behavior."""
    print("RUN:", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    """Materialize masks and both uncalibrated native-event sensitivity scorers."""
    args = parse_args()
    output_root = resolve(args.output_root)
    events, nodes = resolve(args.events), resolve(args.nodes)
    if not events.is_file() or not nodes.is_file():
        raise SystemExit("STOP: declared native-event sensitivity inputs are missing.")
    if output_root.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: sensitivity output root exists: {output_root}")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    runs: list[dict[str, object]] = []
    for rate in args.rates:
        label = f"rate{int(round(rate * 100)):02d}"
        mask_dir = output_root / f"{label}_masks"
        heuristic_dir = output_root / f"{label}_heuristics"
        hard_dir = output_root / f"{label}_hard_panels"
        common = [
            f"--dataset-id={args.dataset_id}",
            f"--nodes={nodes}",
            f"--node-column={args.node_column}",
            f"--seed={args.seed}",
        ]
        run(
            [
                sys.executable,
                "scripts/36_prepare_event_first_masks.py",
                *common,
                f"--events={events}",
                f"--event-tail-column={args.event_tail_column}",
                f"--event-head-column={args.event_head_column}",
                f"--tail-cap={args.tail_cap}",
                f"--head-cap={args.head_cap}",
                f"--mask-rate={rate}",
                f"--mechanisms={args.mechanisms}",
                f"--replicates={args.replicates}",
                f"--output-dir={mask_dir}",
                "--overwrite",
            ]
        )
        run(
            [
                sys.executable,
                "scripts/37_run_native_event_heuristics.py",
                *common,
                f"--mask-dir={mask_dir}",
                f"--max-weak-distance={args.max_weak_distance}",
                f"--output-dir={heuristic_dir}",
                "--overwrite",
            ]
        )
        run(
            [
                sys.executable,
                "scripts/38_run_native_event_hard_panels.py",
                *common,
                f"--mask-dir={mask_dir}",
                f"--max-weak-distance={args.max_weak_distance}",
                f"--output-dir={hard_dir}",
                "--overwrite",
            ]
        )
        runs.append(
            {
                "mask_rate": rate,
                "mask_dir": recorded_path(mask_dir),
                "heuristic_dir": recorded_path(heuristic_dir),
                "hard_panel_dir": recorded_path(hard_dir),
            }
        )
    (output_root / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/50_run_native_missingness_sensitivity.py",
                "dataset_id": args.dataset_id,
                "predeclared_rates": args.rates,
                "mechanisms": args.mechanisms.split(","),
                "replicates": args.replicates,
                "scope": "supplementary native-event heuristic and directed hard-panel rankings; no ERGM refitting",
                "runs": runs,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("Native-event missingness sensitivity completed.")
    print(f"Dataset: {args.dataset_id}; rates: {', '.join(str(rate) for rate in args.rates)}")
    print(f"Output root: {recorded_path(output_root)}")


if __name__ == "__main__":
    main()
