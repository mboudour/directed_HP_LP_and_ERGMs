#!/usr/bin/env python3
"""Collect aggregate native-event missingness sensitivity results without candidate data."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    """Parse a sensitivity-run root and its separate summary destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded_path(path: Path) -> str:
    """Render a project-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read a required aggregate CSV table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a deterministic nonempty CSV table."""
    if not rows:
        raise RuntimeError(f"cannot write empty sensitivity summary: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Collect rate-labelled mask, heuristic, and hard-panel aggregate statistics."""
    args = parse_args()
    input_root, output = resolve(args.input_root), resolve(args.output_dir)
    if not input_root.is_dir() or not (input_root / "manifest.json").is_file():
        raise SystemExit(f"STOP: native-event sensitivity input root is missing: {input_root}")
    if output.exists():
        if not args.overwrite:
            raise SystemExit(f"STOP: sensitivity summary output exists: {output}")
        for child in output.iterdir():
            child.unlink()
    else:
        output.mkdir(parents=True)
    manifest = json.loads((input_root / "manifest.json").read_text(encoding="utf-8"))
    mask_rows: list[dict[str, object]] = []
    heuristic_rows: list[dict[str, object]] = []
    hard_rows: list[dict[str, object]] = []
    for run in manifest["runs"]:
        rate = float(run["mask_rate"])
        mask_dir = resolve(Path(str(run["mask_dir"])))
        heuristic_dir = resolve(Path(str(run["heuristic_dir"])))
        hard_dir = resolve(Path(str(run["hard_panel_dir"])))
        for row in read_rows(mask_dir / "split_summary.csv"):
            safe_row = {
                key: value
                for key, value in row.items()
                if key not in {"oracle_sender_activity", "files"}
            }
            mask_rows.append({"mask_rate": rate, **safe_row})
        for row in read_rows(heuristic_dir / "metric_summary.csv"):
            heuristic_rows.append({"mask_rate": rate, **row})
        for row in read_rows(hard_dir / "metric_summary.csv"):
            hard_rows.append({"mask_rate": rate, **row})
    write_csv(output / "masking_summary.csv", mask_rows)
    write_csv(output / "heuristic_metric_summary.csv", heuristic_rows)
    write_csv(output / "hard_panel_metric_summary.csv", hard_rows)
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "driver": "scripts/51_summarize_native_missingness_sensitivity.py",
                "dataset_id": args.dataset_id,
                "source": recorded_path(input_root),
                "rates": manifest["predeclared_rates"],
                "mechanisms": manifest["mechanisms"],
                "scope": manifest["scope"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Supplementary native-event missingness sensitivity",
        "",
        f"- Dataset: `{args.dataset_id}`",
        "- Rates: " + ", ".join(f"{rate:.0%}" for rate in manifest["predeclared_rates"]),
        "- Mechanisms: " + ", ".join(manifest["mechanisms"]),
        "- Scope: native-event heuristic and directed hard-panel rankings only; ERGM fits retain the primary 30% protocol.",
        "",
        "The aggregate masking rates, heuristic metrics, and hard-panel metrics are in the three CSV files in this bundle.",
        "",
    ]
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("Native-event missingness sensitivity summary passed.")
    print(f"Dataset: {args.dataset_id}; rate rows: {len(mask_rows):,}.")
    print(f"Output bundle: {recorded_path(output)}")


if __name__ == "__main__":
    main()
