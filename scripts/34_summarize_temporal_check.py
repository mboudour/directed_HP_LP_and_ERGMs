#!/usr/bin/env python3
"""Print and save a compact summary of the bounded lagged temporal check."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse completed temporal-model and panel-export output folders."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative or absolute local output path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a required CSV as strings to preserve labels exactly."""
    if not path.is_file():
        raise SystemExit(f"STOP: expected temporal-check output is missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    """Summarize bounded-lagged results without calling them forecasts or TERGMs."""
    args = parse_args()
    model_dir = resolve(args.model_dir)
    panel_dir = resolve(args.panel_dir)
    feature = read_rows(model_dir / "feature_summary.csv")
    statuses = read_rows(model_dir / "factorized_model_status.csv")
    coefficients = read_rows(model_dir / "factorized_coefficients.csv")
    identity = read_rows(model_dir / "proposition6_identity.csv")
    package_status = read_rows(model_dir / "package_placeholder_status.csv")
    panel_manifest_path = panel_dir / "temporal_input_manifest.json"
    if not panel_manifest_path.is_file():
        raise SystemExit(f"STOP: temporal panel manifest is missing: {panel_manifest_path}")
    panel_manifest = json.loads(panel_manifest_path.read_text(encoding="utf-8"))
    if len(feature) != 1:
        raise SystemExit(
            "STOP: feature_summary.csv must contain exactly one bounded temporal design."
        )
    design = feature[0]
    identity_pass = bool(identity) and all(
        str(row.get("proposition6_pass", "")).lower() in {"true", "1"} for row in identity
    )
    design_size = (
        f"- Nodes: {design['nodes']}; transitions: {design['transitions']}; "
        f"factorized dyad-time rows: {design['factorized_dyad_rows']}"
    )
    outcome_summary = (
        f"- Outcome ties: {design['positive_outcomes']}; "
        f"outcome rate: {float(design['outcome_rate']):.6f}"
    )

    lines = [
        "# Bounded chronological check summary",
        "",
        "This result is a factorized lagged conditional check. It is not a full TERGM, "
        "STERGM, relational hyperevent model, or forecasting result.",
        "",
        "## Frozen chronological panel",
        "",
        f"- Dataset: `{panel_manifest['dataset']}`",
        f"- Selected panel labels: `{', '.join(panel_manifest['selected_panel_labels'])}`",
        design_size,
        outcome_summary,
        "",
        "## Factorized model status",
        "",
    ]
    for row in statuses:
        message = f" — {row['message']}" if row.get("message") else ""
        lines.append(f"- `{row['model']}`: `{row['status']}`{message}")

    lines.extend(
        [
            "",
            "## Lagged coefficients",
            "",
            "| Model | Term | Estimate | Odds ratio |",
            "|---|---|---:|---:|",
        ]
    )
    for row in coefficients:
        estimate = float(row["estimate"])
        lines.append(
            f"| {row['model']} | {row['term']} | {estimate:.6f} | {math.exp(estimate):.6f} |"
        )
    if not coefficients:
        lines.append("| — | — | — | — |")

    lines.extend(["", "## Proposition 6 numerical identity", ""])
    lines.append(f"- Status: `{'passed' if identity_pass else 'failed'}`")
    lines.append(
        "- Interpretation: with a positive coefficient on lagged shared outgoing neighbours, "
        "the fitted logistic score and that count have the same strict ranking."
    )
    lines.extend(["", "## Package guardrails", ""])
    for row in package_status:
        lines.append(
            f"- `{row['engine']}` requested as `{row['requested_mode']}`: `{row['status']}`"
        )
    lines.extend(
        [
            "",
            "The package statuses above are availability/guardrail checks only. No full temporal "
            "ERGM or STERGM has been fitted or claimed by this bounded analysis.",
            "",
        ]
    )
    report = model_dir / "summary.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved summary: {report}")


if __name__ == "__main__":
    main()
