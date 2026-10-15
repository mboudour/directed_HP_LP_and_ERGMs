#!/usr/bin/env python3
"""Write one local, non-sensitive Phase 2 readiness report from approved registry and audits."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "results" / "phase2" / "readiness_report.md"
REGISTRY_PATH = PROJECT_ROOT / "configs" / "datasets.yaml"

SOURCES = (
    (
        "Enron",
        "enron_20150507",
        "data/metadata/enron_20150507_custodian_projection.json",
        "Primary native-event and bounded chronological source after strict custodian projection.",
    ),
    (
        "EU-core",
        "email_eu_core_temporal",
        "data/metadata/email_eu_core_temporal_preparation.json",
        "Prepared dyadic temporal source; native-event target remains unsupported by design.",
    ),
    (
        "CAVIAR",
        "caviar",
        "data/metadata/caviar_full_static_preparation.json",
        "Approved only for the unique-labelled full static matrix; phase series remains excluded.",
    ),
    (
        "Ciel",
        "ciel",
        "data/metadata/ciel_matrix_preparation.json",
        "Requires authoritative relation-semantics and direction evidence.",
    ),
    (
        "Jmail v1",
        "jmail_v1_2026_02",
        "data/metadata/jmail_v1_2026_02_audit.json",
        "Requires provenance/entity/licensing and event-policy approval before restricted events.",
    ),
    (
        "MathOverflow",
        "mathoverflow_stackexchange_2024",
        "data/metadata/mathoverflow_stackexchange_2024_audit.json",
        "Prepared reconstructed native/static core under the approved 30-day window policy.",
    ),
)


def compact_audit_status(payload: dict[str, object]) -> str:
    """Extract an audit status for context without overriding approved registry scope."""
    for key in ("analysis_status", "status"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    if "core_static_directed_arcs" in payload and "window_width_days" in payload:
        return "prepared_static_and_temporal"
    if payload.get("matrix_label_integrity_passed") is False:
        return "blocked_pending_label_integrity"
    return "audit_present_status_not_standardized"


def compact_status(payload: dict[str, object]) -> str:
    """Retain the original helper name for downstream audit-status checks."""
    return compact_audit_status(payload)


def load_registry() -> dict[str, dict[str, object]]:
    """Load approved dataset eligibility states from the committed registry."""
    payload = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    datasets = payload.get("datasets") if isinstance(payload, dict) else None
    if not isinstance(datasets, dict):
        raise SystemExit(f"STOP: invalid dataset registry: {REGISTRY_PATH}")
    return datasets


def main() -> None:
    """Create a compact report without letting stale audit wording override registry policy."""
    registry = load_registry()
    rows: list[tuple[str, str, str, str, str]] = []
    for name, dataset_id, relative_path, note in SOURCES:
        registry_entry = registry.get(dataset_id)
        if not isinstance(registry_entry, dict) or "status" not in registry_entry:
            raise SystemExit(f"STOP: dataset registry lacks approved status for {dataset_id!r}")
        approved_status = str(registry_entry["status"])
        path = PROJECT_ROOT / relative_path
        if not path.is_file():
            rows.append((name, approved_status, "audit_not_found", relative_path, note))
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rows.append((name, approved_status, "invalid_metadata_json", relative_path, note))
            continue
        rows.append((name, approved_status, compact_audit_status(payload), relative_path, note))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    table = "\n".join(
        f"| {name} | `{approved}` | `{audit}` | `{metadata}` | {note} |"
        for name, approved, audit, metadata, note in rows
    )
    OUTPUT.write_text(
        "# Phase 2 local readiness report\n\n"
        "The **approved registry status** is authoritative for target eligibility. Audit status "
        "is retained for provenance context because older audit files may predate an approved "
        "reconstruction or projection policy.\n\n"
        "| Dataset | Approved status | Audit status | Metadata | Gate note |\n"
        "|---|---|---|---|---|\n"
        f"{table}\n",
        encoding="utf-8",
    )
    print(f"Phase 2 readiness report: {OUTPUT.relative_to(PROJECT_ROOT)}")
    for name, approved, _, _, _ in rows:
        print(f"{name}: {approved}")


if __name__ == "__main__":
    main()
