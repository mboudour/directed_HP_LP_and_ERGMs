#!/usr/bin/env python3
"""Print and save a compact status summary for the bounded btergm temporal ladder."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse the completed btergm ladder output and frozen panel folders."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative or absolute local result path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a required artifact while retaining labels and status strings exactly."""
    if not path.is_file():
        raise SystemExit(f"STOP: expected btergm artifact is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite_number(value: str | None) -> float | None:
    """Return a finite CSV number, preserving empty diagnostic rows as missing."""
    if value is None or not value.strip():
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def main() -> None:
    """Summarize btergm MPLE/bootstrapped coefficients without forecast claims."""
    args = parse_args()
    model_dir = resolve(args.model_dir)
    panel_dir = resolve(args.panel_dir)
    manifest_path = model_dir / "run_manifest.json"
    panel_manifest_path = panel_dir / "temporal_input_manifest.json"
    if not manifest_path.is_file() or not panel_manifest_path.is_file():
        raise SystemExit("STOP: btergm or panel manifest is missing.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    panel_manifest = json.loads(panel_manifest_path.read_text(encoding="utf-8"))
    statuses = read_csv(model_dir / "model_status.csv")
    coefficients = read_csv(model_dir / "coefficients.csv")
    summary_rows = read_csv(model_dir / "input_summary.csv")
    if len(summary_rows) != 1:
        raise SystemExit("STOP: input_summary.csv must contain exactly one row.")
    input_summary = summary_rows[0]
    status_counts = Counter(row["status"] for row in statuses)
    status_count_text = ", ".join(
        f"{status}={count}" for status, count in sorted(status_counts.items())
    )

    lines = [
        "# Bounded btergm temporal-ladder summary",
        "",
        "This is the plan's bounded **btergm MPLE with temporal bootstrap** estimator. "
        "It is not a forecasting, simulation, MCMC-MLE, or STERGM result.",
        "",
        "## Frozen panel and estimator",
        "",
        f"- Dataset: `{panel_manifest['dataset']}`",
        f"- Panel labels: `{', '.join(panel_manifest['selected_panel_labels'])}`",
        f"- Nodes: {input_summary['nodes']}; response transitions: {input_summary['transitions']}; "
        f"dyad-time rows: {input_summary['response_dyad_time_rows']}",
        f"- Estimator status: `{manifest.get('status', 'unknown')}`",
        "- Interpretation: T1, T2, and T2_minus_H are MPLE conditional score estimators "
        "only; no simulated probability or forecast was computed.",
        "",
        "## Model status",
        "",
        f"- Counts: {status_count_text}",
    ]
    for row in statuses:
        message = f" — {row['message']}" if row.get("message") else ""
        lines.append(f"- `{row['model']}`: `{row['status']}`{message}")

    lines.extend(
        [
            "",
            "## MPLE coefficients and bootstrap-interval availability",
            "",
            "| Model | Term | Estimate | 95% bootstrap interval | Interval status |",
            "|---|---|---:|---:|---|",
        ]
    )
    valid_coefficients = 0
    incomplete_coefficients = 0
    for row in coefficients:
        estimate = finite_number(row.get("estimate"))
        if not row.get("model") or not row.get("term") or estimate is None:
            incomplete_coefficients += 1
            continue
        lower = finite_number(row.get("ci_lower"))
        upper = finite_number(row.get("ci_upper"))
        interval = "—" if lower is None or upper is None else f"[{lower:.4f}, {upper:.4f}]"
        lines.append(
            f"| {row['model']} | {row['term']} | {estimate:.4f} | "
            f"{interval} | {row.get('ci_status', 'unknown')} |"
        )
        valid_coefficients += 1
    if not valid_coefficients:
        lines.append("| — | — | — | — | No coefficients emitted |")
    if incomplete_coefficients:
        lines.append(
            f"\nOmitted {incomplete_coefficients} blank or nonfinite coefficient row(s); "
            "their model-level diagnostics remain in `model_status.csv`."
        )

    lines.extend(
        [
            "",
            "Inspect `model_status.csv`, `diagnostics.txt`, and `coefficients.csv` before "
            "interpreting any term. With only 20 bootstrap replicates and two response "
            "transitions, intervals are pilot diagnostics—not confirmatory uncertainty estimates.",
            "",
        ]
    )
    report = model_dir / "summary.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved summary: {report}")


if __name__ == "__main__":
    main()
