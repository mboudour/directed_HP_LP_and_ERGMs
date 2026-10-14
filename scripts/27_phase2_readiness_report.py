#!/usr/bin/env python3
"""Write one local, non-sensitive Phase 2 readiness report from audit metadata."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "results" / "phase2" / "readiness_report.md"

SOURCES = (
    (
        "Enron",
        "data/metadata/enron_20150507_custodian_projection.json",
        "Primary custodian projection awaits an approved map and policy record if absent.",
    ),
    (
        "EU-core",
        "data/metadata/email_eu_core_temporal_preparation.json",
        "Prepared dyadic temporal source; native-event target remains unsupported by design.",
    ),
    (
        "CAVIAR",
        "data/metadata/caviar_matrix_preparation.json",
        "Requires direction evidence and resolution of any duplicate actor labels.",
    ),
    (
        "Ciel",
        "data/metadata/ciel_matrix_preparation.json",
        "Requires authoritative relation-semantics and direction evidence.",
    ),
    (
        "Jmail v1",
        "data/metadata/jmail_v1_2026_02_audit.json",
        "Requires provenance/entity/licensing and event-policy approval before restricted events.",
    ),
    (
        "MathOverflow",
        "data/metadata/mathoverflow_stackexchange_2024_audit.json",
        "Requires a recorded reconstruction window and post/user-treatment policy.",
    ),
)


def compact_status(payload: dict[str, object]) -> str:
    """Extract the standardized status field without assuming one metadata schema."""
    for key in ("analysis_status", "status"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    if "core_static_directed_arcs" in payload and "window_width_days" in payload:
        return "prepared_static_and_temporal"
    if payload.get("matrix_label_integrity_passed") is False:
        return "blocked_pending_label_integrity"
    return "audit_present_status_not_standardized"


def main() -> None:
    """Create a compact local report and leave scientific gates visibly unresolved."""
    rows: list[tuple[str, str, str, str]] = []
    for name, relative_path, note in SOURCES:
        path = PROJECT_ROOT / relative_path
        if not path.is_file():
            rows.append((name, "not_run_or_not_built", relative_path, note))
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows.append((name, "invalid_metadata_json", relative_path, note))
            continue
        rows.append((name, compact_status(payload), relative_path, note))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    table = "\n".join(
        f"| {name} | `{status}` | `{metadata}` | {note} |" for name, status, metadata, note in rows
    )
    OUTPUT.write_text(
        "# Phase 2 local readiness report\n\n"
        "This report is generated from local aggregate audit metadata. A pending or blocked "
        "status is a recorded scientific gate, not a failure that code may override.\n\n"
        "| Dataset | Current status | Metadata | Gate note |\n"
        "|---|---|---|---|\n"
        f"{table}\n",
        encoding="utf-8",
    )
    print(f"Phase 2 readiness report: {OUTPUT.relative_to(PROJECT_ROOT)}")
    for name, status, _, _ in rows:
        print(f"{name}: {status}")


if __name__ == "__main__":
    main()
