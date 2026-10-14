#!/usr/bin/env python3
"""Print and save a compact, non-inferential summary of masked ERGM score outputs."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse a completed masked-ERGM output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a required CSV with its headers preserved as strings."""
    if not path.is_file():
        raise SystemExit(f"STOP: expected masked-ERGM output is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def render_metric(value: float) -> str:
    """Render a bounded discrimination metric compactly."""
    return f"{value:.4f}"


def main() -> None:
    """Aggregate complete masked-ERGM score outputs without inferential claims."""
    args = parse_args()
    input_dir = args.input_dir if args.input_dir.is_absolute() else PROJECT_ROOT / args.input_dir
    model_rows = read_rows(input_dir / "model_status.csv")
    replicate_rows = read_rows(input_dir / "replicate_status.csv")
    metric_rows = read_rows(input_dir / "metrics.csv")

    model_status = Counter(row["status"] for row in model_rows)
    replicate_status = Counter(row["status"] for row in replicate_rows)
    calculated: dict[tuple[str, str], list[float]] = defaultdict(list)
    metric_failures: Counter[tuple[str, str, str]] = Counter()
    for row in metric_rows:
        key = (row["model"], row["metric"])
        if row["status"] == "calculated" and row["value"].strip():
            calculated[key].append(float(row["value"]))
        else:
            metric_failures[(row["model"], row["metric"], row["status"])] += 1

    replicate_status_text = ", ".join(
        f"{key}={value}" for key, value in sorted(replicate_status.items())
    )
    model_status_text = ", ".join(f"{key}={value}" for key, value in sorted(model_status.items()))

    lines = [
        "# Masked ERGM conditional-score summary",
        "",
        "This is a score-discrimination summary for exact conditional ERGM probabilities "
        "fitted to masked training networks. It is not an inferential ERGM table and not a "
        "forecasting result.",
        "",
        "## Completion status",
        "",
        f"- Replicates: {len(replicate_rows)} ({replicate_status_text})",
        f"- Model-replicate outcomes: {len(model_rows)} ({model_status_text})",
        "",
        "## Discrimination metrics across completed replicates",
        "",
        "| Model | Metric | Completed replicates | Mean | SD |",
        "|---|---|---:|---:|---:|",
    ]
    for model, metric in sorted(calculated):
        values = calculated[(model, metric)]
        standard_deviation = stdev(values) if len(values) > 1 else 0.0
        lines.append(
            f"| {model} | {metric} | {len(values)} | {render_metric(mean(values))} | "
            f"{render_metric(standard_deviation)} |"
        )
    if not calculated:
        lines.append("| — | — | 0 | — | — |")

    if metric_failures:
        lines.extend(["", "## Metric statuses requiring inspection", ""])
        for (model, metric, status), count in sorted(metric_failures.items()):
            lines.append(f"- `{model}` / `{metric}`: `{status}` in {count} replicate(s).")
    lines.extend(
        [
            "",
            "Inspect `model_status.csv` for any fit or prediction failure and `metrics.csv` for "
            "replicate-level values before interpreting score differences.",
            "",
        ]
    )
    report = input_dir / "summary.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved summary: {report}")


if __name__ == "__main__":
    main()
