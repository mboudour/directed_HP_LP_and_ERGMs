#!/usr/bin/env python3
"""Report local inputs and scientific eligibility gates for the Phase 2 pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = PROJECT_ROOT / "configs" / "datasets.yaml"


def input_exists(project_root: Path, dataset: dict[str, object]) -> bool:
    """Check either the declared exact input path or a declared glob."""
    if "raw_input" in dataset:
        return (project_root / str(dataset["raw_input"])).is_file()
    if "raw_input_glob" in dataset:
        return any(project_root.glob(str(dataset["raw_input_glob"])))
    raise ValueError("dataset registry entry has no raw_input or raw_input_glob")


def gate_status(project_root: Path, dataset: dict[str, object]) -> str:
    """Return approved, pending, or not_required from a JSON gate record."""
    gate_record = dataset.get("gate_record")
    if not gate_record:
        return "not_required"

    path = project_root / str(gate_record)
    if not path.is_file():
        return "pending"

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "invalid_record"

    return "approved" if record.get("approved") is True else "pending"


def main() -> None:
    """Print a one-screen local readiness summary without changing any files."""
    if not REGISTRY.is_file():
        raise SystemExit(f"STOP: dataset registry not found: {REGISTRY}")

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    datasets = registry.get("datasets", {})
    if not isinstance(datasets, dict) or not datasets:
        raise SystemExit("STOP: dataset registry has no dataset entries")

    print("Phase 2 local readiness")
    print("=" * 23)
    print("dataset\traw_input\tgate\tstatus")

    for dataset_id, dataset in datasets.items():
        if not isinstance(dataset, dict):
            raise SystemExit(f"STOP: invalid registry entry for {dataset_id}")

        raw = input_exists(PROJECT_ROOT, dataset)
        gate = gate_status(PROJECT_ROOT, dataset)
        required_map = dataset.get("required_identity_map")
        map_ready = (PROJECT_ROOT / str(required_map)).is_file() if required_map else True

        if not raw:
            status = "missing_raw_input"
        elif not map_ready:
            status = "awaiting_identity_map"
        elif gate not in {"not_required", "approved"}:
            status = "audit_ready_but_analysis_blocked"
        else:
            status = "ready_for_declared_pipeline"

        print(f"{dataset_id}\t{str(raw).lower()}\t{gate}\t{status}")

    print()
    print("Raw files and record-level outputs stay local and are excluded from Git.")
    print("A pending gate is a planned result, not an error and not implicit approval.")


if __name__ == "__main__":
    main()
