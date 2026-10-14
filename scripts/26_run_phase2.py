#!/usr/bin/env python3
"""Run eligible Phase 2 preparation tasks once, skipping completed or gated work."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@dataclass(frozen=True)
class Task:
    """One independently rerunnable local Phase 2 preparation task."""

    name: str
    command: tuple[str, ...]
    summary: Path
    required_inputs: tuple[Path, ...]
    gated: bool = False


def tasks() -> tuple[Task, ...]:
    """List the all-dataset preparation tasks in plan order."""
    return (
        Task(
            "EU-core",
            (PYTHON, "scripts/21_prepare_eu_core.py"),
            PROJECT_ROOT / "data/metadata/email_eu_core_temporal_preparation.json",
            (PROJECT_ROOT / "data/raw/email_eu_core_temporal/email-Eu-core-temporal.txt",),
        ),
        Task(
            "CAVIAR matrix audit",
            (PYTHON, "scripts/22_prepare_covert_matrices.py", "caviar"),
            PROJECT_ROOT / "data/metadata/caviar_matrix_preparation.json",
            (PROJECT_ROOT / "data/raw/caviar/csv_matrices",),
        ),
        Task(
            "Ciel matrix audit",
            (PYTHON, "scripts/22_prepare_covert_matrices.py", "ciel"),
            PROJECT_ROOT / "data/metadata/ciel_matrix_preparation.json",
            (PROJECT_ROOT / "data/raw/ciel/csv_matrix/CSV/CIELNET.csv",),
        ),
        Task(
            "Jmail v1 audit",
            (PYTHON, "scripts/23_prepare_jmail_v1.py"),
            PROJECT_ROOT / "data/metadata/jmail_v1_2026_02_audit.json",
            (PROJECT_ROOT / "data/raw/jmail_v1_2026_02/emails-slim.parquet",),
        ),
        Task(
            "MathOverflow audit",
            (PYTHON, "scripts/24_prepare_mathoverflow.py"),
            PROJECT_ROOT / "data/metadata/mathoverflow_stackexchange_2024_audit.json",
            (PROJECT_ROOT / "data/raw/mathoverflow_stackexchange_2024/Posts.xml",),
        ),
        Task(
            "Enron custodian projection",
            (PYTHON, "scripts/25_build_enron_custodian_projection.py"),
            PROJECT_ROOT / "data/metadata/enron_20150507_custodian_projection.json",
            (
                PROJECT_ROOT / "data/interim/enron_20150507/native_events_address_level.parquet",
                PROJECT_ROOT / "data/processed/enron_20150507/custodian_address_map.csv",
                PROJECT_ROOT / "data/metadata/gates/enron_custodian_projection.json",
            ),
            gated=True,
        ),
    )


def main() -> None:
    """Run pending, locally available task scripts and leave all gated work visible."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("Phase 2 batch runner")
    print("=" * 20)
    completed = 0
    skipped = 0
    run = 0

    for task in tasks():
        if task.summary.exists():
            print(f"SKIP complete: {task.name}")
            skipped += 1
            continue
        missing = [path for path in task.required_inputs if not path.exists()]
        if missing:
            label = "GATE" if task.gated else "SKIP missing input"
            print(f"{label}: {task.name}")
            for path in missing:
                print(f"  {path.relative_to(PROJECT_ROOT)}")
            skipped += 1
            continue
        print(f"RUN: {task.name}")
        if not args.dry_run:
            subprocess.run(task.command, cwd=PROJECT_ROOT, check=True)
        run += 1
        completed += not args.dry_run

    print()
    print(f"Tasks run: {run:,}")
    print(f"Tasks completed in this invocation: {completed:,}")
    print(f"Tasks skipped: {skipped:,}")
    print("Run `make phase2-status` to inspect remaining scientific gates.")


if __name__ == "__main__":
    main()
