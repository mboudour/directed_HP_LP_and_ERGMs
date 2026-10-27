#!/usr/bin/env python3
"""Build auditable temporal constraints for Senate random native-event negatives.

The event-first masks are frozen and are not modified.  This Senate-specific
sidecar reconstructs their canonical cap-specific event-type IDs from the
processed Bill Status event table, attaches every distinct associated bill
introduction date to each type, and validates its identity against every
frozen mask.  The companion random-negative driver uses the sidecar with the
public congress-legislators roster to require service coverage at every
associated introduction date.

Only actor-free sidecars and aggregate audit records are written.  The
sidecars remain ignored with processed data; the metadata and audit report are
safe for repository publication.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class CapAccounting:
    """Aggregate accounting for one cap-specific canonical type reconstruction."""

    head_cap: int
    event_records_read: int
    excluded_empty_tail: int
    excluded_empty_head: int
    excluded_role_overlap: int
    excluded_outside_fixed_node_universe: int
    excluded_by_arity_cap: int
    cap_eligible_event_records: int
    cap_eligible_event_types: int
    recurrent_event_types: int
    event_types_with_multiple_introduction_dates: int
    distinct_type_introduction_dates: int
    types_with_full_participant_service_coverage: int


def parse_args() -> argparse.Namespace:
    """Parse the explicit frozen-mask temporal-sidecar contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--current-roster", type=Path, required=True)
    parser.add_argument("--historical-roster", type=Path, required=True)
    parser.add_argument("--event-tail-column", default="tail_sponsor_bioguide")
    parser.add_argument("--event-head-column", default="head_original_cosponsors_bioguide")
    parser.add_argument("--introduced-date-column", default="introduced_date")
    parser.add_argument("--node-column", default="node")
    parser.add_argument("--tail-cap", type=int, default=1)
    parser.add_argument(
        "--head-caps",
        default="3,10",
        help="Comma-separated positive head caps to reconstruct and cross-check.",
    )
    parser.add_argument(
        "--mask-dirs",
        required=True,
        help="Comma-separated HEAD_CAP=FROZEN_MASK_DIRECTORY assignments.",
    )
    parser.add_argument(
        "--legacy-heuristic-dirs",
        help=(
            "Optional comma-separated HEAD_CAP=LEGACY_RANDOM_PANEL_DIRECTORY assignments. "
            "When supplied before correction, writes aggregate date-infeasibility counts."
        ),
    )
    parser.add_argument("--sidecar-dir", type=Path, required=True)
    parser.add_argument("--metadata-output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.tail_cap < 1:
        parser.error("--tail-cap must be at least one.")
    try:
        head_caps = tuple(sorted({int(value.strip()) for value in args.head_caps.split(",")}))
    except ValueError as error:
        parser.error(f"--head-caps must contain positive integers: {error}")
    if not head_caps or any(cap < 1 for cap in head_caps):
        parser.error("--head-caps must contain at least one positive integer.")
    assignments: dict[int, Path] = {}
    for value in (item.strip() for item in args.mask_dirs.split(",") if item.strip()):
        if "=" not in value:
            parser.error("--mask-dirs assignments must use HEAD_CAP=PATH.")
        raw_cap, raw_path = value.split("=", maxsplit=1)
        try:
            cap = int(raw_cap)
        except ValueError as error:
            parser.error(f"invalid --mask-dirs cap {raw_cap!r}: {error}")
        if cap in assignments or cap not in head_caps or not raw_path.strip():
            parser.error("--mask-dirs must assign each requested cap exactly once.")
        assignments[cap] = Path(raw_path.strip())
    if set(assignments) != set(head_caps):
        parser.error("--mask-dirs must provide exactly one directory for every --head-caps value.")
    legacy_assignments: dict[int, Path] = {}
    if args.legacy_heuristic_dirs:
        for value in (
            item.strip() for item in args.legacy_heuristic_dirs.split(",") if item.strip()
        ):
            if "=" not in value:
                parser.error("--legacy-heuristic-dirs assignments must use HEAD_CAP=PATH.")
            raw_cap, raw_path = value.split("=", maxsplit=1)
            try:
                cap = int(raw_cap)
            except ValueError as error:
                parser.error(f"invalid --legacy-heuristic-dirs cap {raw_cap!r}: {error}")
            if cap in legacy_assignments or cap not in head_caps or not raw_path.strip():
                parser.error(
                    "--legacy-heuristic-dirs must use unique requested head caps with paths."
                )
            legacy_assignments[cap] = Path(raw_path.strip())
    args.head_caps = head_caps
    args.mask_dirs = assignments
    args.legacy_heuristic_dirs = legacy_assignments
    return args


def resolve(path: Path) -> Path:
    """Resolve a project-relative input or output path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Return a project-relative provenance path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    """Hash one input or sidecar file with bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, description: str) -> None:
    """Fail with a concrete message if one declared source is unavailable."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")


def read_nodes(path: Path, column: str) -> tuple[str, ...]:
    """Read the fixed actor universe while retaining opaque identifier strings."""
    require_file(path, "node table")
    values: dict[str, None] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"STOP: node table lacks declared column {column!r}: {path}")
        for row in reader:
            value = row[column].strip()
            if not value or value in values:
                raise SystemExit("STOP: node table has an empty or duplicate actor identifier.")
            values[value] = None
    if not values:
        raise SystemExit("STOP: node table is empty.")
    return tuple(values)


def canonical_role(value: object, role: str) -> tuple[str, ...]:
    """Canonicalize a scalar or Parquet-list role with no string-list parsing."""
    raw = value if isinstance(value, list) else [value]
    members = [str(member).strip() for member in raw if member is not None]
    if not members or any(not member for member in members):
        raise ValueError(f"native-event {role} contains an empty actor ID")
    return tuple(sorted(set(members)))


def read_roster_file(path: Path) -> list[dict[str, Any]]:
    """Read one congress-legislators JSON roster snapshot with strict top-level type."""
    require_file(path, "roster JSON")
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: roster JSON is invalid: {path}") from error
    if not isinstance(values, list):
        raise SystemExit(f"STOP: roster JSON must contain a list: {path}")
    return [value for value in values if isinstance(value, dict)]


def parse_term(term: object) -> tuple[date, date] | None:
    """Return one valid Senate half-open service interval, or None for other terms."""
    if not isinstance(term, dict) or term.get("type") != "sen":
        return None
    start, end = term.get("start"), term.get("end")
    if not isinstance(start, str) or not isinstance(end, str):
        return None
    try:
        interval = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        return None
    return interval if interval[0] < interval[1] else None


def load_senate_terms(current: Path, historical: Path) -> dict[str, tuple[tuple[date, date], ...]]:
    """Load merged Senate intervals from the two declared public roster snapshots."""
    terms_by_actor: dict[str, set[tuple[date, date]]] = defaultdict(set)
    for path in (current, historical):
        for person in read_roster_file(path):
            identifier = person.get("id", {}).get("bioguide")
            if not isinstance(identifier, str) or not identifier.strip():
                continue
            terms = person.get("terms")
            if not isinstance(terms, list):
                continue
            for term in terms:
                if interval := parse_term(term):
                    terms_by_actor[identifier.strip()].add(interval)
    if not terms_by_actor:
        raise SystemExit(
            "STOP: no valid Senate service intervals were read from the roster snapshots."
        )
    return {
        identifier: tuple(sorted(intervals)) for identifier, intervals in terms_by_actor.items()
    }


def serving_on(
    actor: str, when: date, terms_by_actor: dict[str, tuple[tuple[date, date], ...]]
) -> bool:
    """Apply the Senate roster's half-open term semantics at one introduction date."""
    return any(start <= when < end for start, end in terms_by_actor.get(actor, ()))


def parse_introduced_date(value: object, event_identifier: object) -> date:
    """Parse an immutable Bill Status introduction date from the processed event table."""
    if not isinstance(value, str):
        raise SystemExit(f"STOP: event {event_identifier!r} lacks a string introduction date.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise SystemExit(
            f"STOP: event {event_identifier!r} has an invalid introduction date {value!r}."
        ) from error


def read_type_dates(
    path: Path,
    *,
    tail_column: str,
    head_column: str,
    date_column: str,
    node_set: set[str],
    tail_cap: int,
    head_cap: int,
    terms_by_actor: dict[str, tuple[tuple[date, date], ...]],
) -> tuple[
    list[dict[str, object]],
    CapAccounting,
    dict[str, int],
]:
    """Reconstruct event-type IDs and all associated introduction dates at one cap."""
    require_file(path, "native-event table")
    source = pq.ParquetFile(path)
    required = {tail_column, head_column, date_column, "event_id"}
    missing = required - set(source.schema_arrow.names)
    if missing:
        raise SystemExit(f"STOP: native-event table lacks columns {sorted(missing)}: {path}")
    counters: Counter[str] = Counter()
    dates_by_key: dict[tuple[tuple[str, ...], tuple[str, ...]], set[date]] = defaultdict(set)
    records_by_key: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    full_positive_coverage: Counter[str] = Counter()
    fields = [tail_column, head_column, date_column, "event_id"]
    for batch in source.iter_batches(columns=fields, batch_size=50_000):
        for row in batch.to_pylist():
            counters["event_records_read"] += 1
            full_positive_coverage["event_records_checked"] += 1
            try:
                tail = canonical_role(row[tail_column], "tail")
            except ValueError:
                counters["excluded_empty_tail"] += 1
                continue
            try:
                head = canonical_role(row[head_column], "head")
            except ValueError:
                counters["excluded_empty_head"] += 1
                continue
            introduced = parse_introduced_date(row[date_column], row["event_id"])
            participants = tail + head
            full_positive_coverage["participant_appearances"] += len(participants)
            service_matches = sum(
                serving_on(actor, introduced, terms_by_actor) for actor in participants
            )
            full_positive_coverage["participant_appearances_service_covered"] += service_matches
            if service_matches == len(participants):
                full_positive_coverage["event_records_service_covered"] += 1
            else:
                full_positive_coverage["event_records_without_full_service_coverage"] += 1
                full_positive_coverage["participant_appearances_without_service_coverage"] += (
                    len(participants) - service_matches
                )
            if set(tail).intersection(head):
                counters["excluded_role_overlap"] += 1
                continue
            if set(participants) - node_set:
                counters["excluded_outside_fixed_node_universe"] += 1
                continue
            if len(tail) > tail_cap or len(head) > head_cap:
                counters["excluded_by_arity_cap"] += 1
                continue
            key = tail, head
            dates_by_key[key].add(introduced)
            records_by_key[key] += 1
            counters["cap_eligible_event_records"] += 1
    rows: list[dict[str, object]] = []
    full_type_service_coverage = 0
    for index, key in enumerate(sorted(records_by_key), start=1):
        tail, head = key
        dates = tuple(sorted(dates_by_key[key]))
        participants = tail + head
        all_dates_covered = all(
            serving_on(actor, introduced, terms_by_actor)
            for actor in participants
            for introduced in dates
        )
        full_type_service_coverage += int(all_dates_covered)
        rows.append(
            {
                "event_type_id": f"event_type_{index:05d}",
                "introduction_dates": [introduced.isoformat() for introduced in dates],
                "occurrence_count": records_by_key[key],
                "all_source_participants_service_covered_on_all_associated_dates": (
                    all_dates_covered
                ),
            }
        )
    if not rows:
        raise SystemExit(f"STOP: no cap-eligible event types at head cap {head_cap}.")
    accounting = CapAccounting(
        head_cap=head_cap,
        event_records_read=counters["event_records_read"],
        excluded_empty_tail=counters["excluded_empty_tail"],
        excluded_empty_head=counters["excluded_empty_head"],
        excluded_role_overlap=counters["excluded_role_overlap"],
        excluded_outside_fixed_node_universe=counters["excluded_outside_fixed_node_universe"],
        excluded_by_arity_cap=counters["excluded_by_arity_cap"],
        cap_eligible_event_records=counters["cap_eligible_event_records"],
        cap_eligible_event_types=len(rows),
        recurrent_event_types=sum(row["occurrence_count"] > 1 for row in rows),
        event_types_with_multiple_introduction_dates=sum(
            len(row["introduction_dates"]) > 1 for row in rows
        ),
        distinct_type_introduction_dates=sum(len(row["introduction_dates"]) for row in rows),
        types_with_full_participant_service_coverage=full_type_service_coverage,
    )
    return rows, accounting, dict(sorted(full_positive_coverage.items()))


def parse_role_json(value: str, field: str) -> tuple[str, ...]:
    """Decode one frozen mask role list for canonical type-identity checking."""
    try:
        items = json.loads(value)
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: invalid {field} JSON in frozen mask: {value!r}") from error
    if not isinstance(items, list) or not items:
        raise SystemExit(f"STOP: frozen mask {field} must be a nonempty JSON list.")
    result = tuple(sorted(str(item).strip() for item in items))
    if any(not item for item in result) or len(set(result)) != len(result):
        raise SystemExit(f"STOP: frozen mask {field} has an empty or duplicate actor.")
    return result


def validate_mask_identity(
    mask_dir: Path,
    type_rows: list[dict[str, object]],
) -> dict[str, int]:
    """Prove that the sidecar ID order exactly matches every frozen type table."""
    if not mask_dir.is_dir():
        raise SystemExit(f"STOP: frozen mask directory is missing: {mask_dir}")
    expected_ids = {str(row["event_type_id"]) for row in type_rows}
    split_dirs = sorted(path for path in mask_dir.iterdir() if path.is_dir())
    checked_tables = 0
    checked_rows = 0
    for split_dir in split_dirs:
        observed_ids: set[str] = set()
        for filename in ("observed_event_types.csv", "heldout_event_types.csv"):
            path = split_dir / filename
            require_file(path, "frozen event-type table")
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                required = {"event_type_id", "tail_nodes_json", "head_nodes_json"}
                if reader.fieldnames is None or required - set(reader.fieldnames):
                    raise SystemExit(f"STOP: frozen type table lacks required fields: {path}")
                for row in reader:
                    event_type_id = row["event_type_id"].strip()
                    tail = parse_role_json(row["tail_nodes_json"], "tail_nodes_json")
                    head = parse_role_json(row["head_nodes_json"], "head_nodes_json")
                    if set(tail).intersection(head) or not event_type_id:
                        raise SystemExit(f"STOP: frozen type table has invalid event roles: {path}")
                    observed_ids.add(event_type_id)
                    checked_rows += 1
            checked_tables += 1
        if observed_ids != expected_ids:
            raise SystemExit(
                "STOP: reconstructed temporal-sidecar IDs do not reconcile with frozen mask "
                f"{split_dir.name}; missing={len(expected_ids - observed_ids)}, "
                f"extra={len(observed_ids - expected_ids)}."
            )
    if not split_dirs:
        raise SystemExit(f"STOP: frozen mask directory contains no split directories: {mask_dir}")
    return {
        "splits_checked": len(split_dirs),
        "type_tables_checked": checked_tables,
        "rows_checked": checked_rows,
    }


def legacy_random_negative_audit(
    heuristic_dir: Path,
    type_rows: list[dict[str, object]],
    terms_by_actor: dict[str, tuple[tuple[date, date], ...]],
) -> list[dict[str, object]]:
    """Audit old arity-group random negatives before the date-feasible replacement.

    The superseded driver numbered synthetic negatives within each arity group.
    Its deterministic group order permits reconstruction of the associated
    positive type without retaining any candidate-level audit rows.
    """
    if not heuristic_dir.is_dir():
        raise SystemExit(f"STOP: legacy heuristic directory is missing: {heuristic_dir}")
    dates_by_type = {
        str(row["event_type_id"]): tuple(
            date.fromisoformat(value) for value in row["introduction_dates"]
        )
        for row in type_rows
    }
    per_mechanism: dict[str, Counter[str]] = defaultdict(Counter)
    pattern = re.compile(r"^negative_(?P<tail>\d+)_(?P<head>\d+)_(?P<index>\d+)$")
    split_count = 0
    for split_dir in sorted(path for path in heuristic_dir.iterdir() if path.is_dir()):
        candidate_path = split_dir / "candidate_predictions.csv"
        if not candidate_path.is_file():
            continue
        mechanism = split_dir.name.rsplit("_replicate_", maxsplit=1)[0]
        with candidate_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        positives: dict[tuple[int, int], list[str]] = defaultdict(list)
        negatives: list[dict[str, str]] = []
        for row in rows:
            label = row.get("label", "").strip()
            tail_arity = int(row.get("tail_arity", ""))
            head_arity = int(row.get("head_arity", ""))
            if label == "1":
                event_type_id = row.get("source_event_type_id", "").strip()
                if event_type_id not in dates_by_type:
                    raise SystemExit(
                        "STOP: legacy positive lacks a temporal-sidecar type record: "
                        f"{split_dir.name}:{event_type_id}"
                    )
                positives[(tail_arity, head_arity)].append(event_type_id)
            elif label == "0":
                negatives.append(row)
            else:
                raise SystemExit(f"STOP: legacy panel has non-binary label: {candidate_path}")
        for row in negatives:
            match = pattern.fullmatch(row.get("candidate_id", ""))
            if match is None:
                raise SystemExit(
                    "STOP: legacy candidate ID cannot reconstruct arity-group pairing: "
                    f"{row.get('candidate_id', '')!r}"
                )
            group = int(match["tail"]), int(match["head"])
            position = int(match["index"]) - 1
            if position < 0 or position >= len(positives[group]):
                raise SystemExit(
                    "STOP: legacy negative index does not map to an eligible positive: "
                    f"{split_dir.name}:{row['candidate_id']}"
                )
            source_type = positives[group][position]
            participants = parse_role_json(row["tail_nodes_json"], "legacy tail") + parse_role_json(
                row["head_nodes_json"], "legacy head"
            )
            feasible = all(
                any(start <= introduced < end for start, end in terms_by_actor.get(actor, ()))
                for actor in participants
                for introduced in dates_by_type[source_type]
            )
            counts = per_mechanism[mechanism]
            counts["synthetic_random_negatives"] += 1
            counts["date_infeasible_random_negatives"] += int(not feasible)
        split_count += 1
    if not per_mechanism:
        raise SystemExit(f"STOP: no legacy random panels found in {heuristic_dir}")
    output: list[dict[str, object]] = []
    for mechanism, counts in sorted(per_mechanism.items()):
        total = counts["synthetic_random_negatives"]
        output.append(
            {
                "mechanism": mechanism,
                "splits_checked": sum(
                    1
                    for path in heuristic_dir.iterdir()
                    if path.is_dir() and path.name.startswith(f"{mechanism}_replicate_")
                ),
                "synthetic_random_negatives": total,
                "date_infeasible_random_negatives": counts["date_infeasible_random_negatives"],
                "date_infeasible_share": counts["date_infeasible_random_negatives"] / total,
            }
        )
    if sum(row["splits_checked"] for row in output) != split_count:
        raise RuntimeError("legacy temporal audit split accounting did not reconcile")
    return output


def prepare_sidecar_dir(path: Path, overwrite: bool) -> None:
    """Avoid blending a new deterministic sidecar with an older policy version."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: sidecar path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: temporal sidecar directory is nonempty: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_audit(path: Path, metadata: dict[str, Any]) -> None:
    """Write a concise public aggregate audit with no actor or candidate identifiers."""
    coverage = metadata["source_positive_service_coverage"]
    lines = [
        "# Senate temporal-feasibility constraints for random negative coalitions",
        "",
        "The event-first masks, observed training projections, and source-positive records are "
        "frozen. "
        "This audit applies a corrected rule only to synthetic random negative coalitions: every "
        "candidate must have a half-open Senate roster interval satisfying ``term_start "
        "<= "
        "introduction_date < term_end`` for every distinct introduction date associated with its "
        "paired positive ordered event type.",
        "",
        "## Source-positive roster coverage QA",
        "",
        f"- Native event records checked: `{coverage['event_records_checked']:,}`",
        f"- Records whose every participant is service-covered at their introduction date: "
        f"`{coverage['event_records_service_covered']:,}`",
        f"- Records with one or more roster-date exceptions: "
        f"`{coverage['event_records_without_full_service_coverage']:,}`",
        f"- Participant appearances checked: `{coverage['participant_appearances_checked']:,}`",
        f"- Service-covered participant appearances: "
        f"`{coverage['participant_appearances_service_covered']:,}`",
        f"- Participant appearances outside recorded roster coverage: "
        f"`{coverage['participant_appearances_without_service_coverage']:,}`",
        "",
        "The source-positive exception is retained and documented; it is not silently removed from "
        "the source-defined target. The co-service rule instead prevents synthetic negatives from "
        "combining actors who cannot jointly occupy the Senate at every date associated with the "
        "positive event type.",
        "",
        "## Cap-specific sidecars",
        "",
        "| Head cap | Eligible records | Ordered types | Recurrent types | Types with >1 date | "
        "Distinct type-date pairs | Type IDs checked against frozen masks |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in metadata["cap_summaries"]:
        accounting = summary["accounting"]
        mask_check = summary["frozen_mask_identity_check"]
        lines.append(
            "| {cap} | {records:,} | {types:,} | {recurrent:,} | {multiple_dates:,} | "
            "{type_dates:,} | {checked:,} |".format(
                cap=accounting["head_cap"],
                records=accounting["cap_eligible_event_records"],
                types=accounting["cap_eligible_event_types"],
                recurrent=accounting["recurrent_event_types"],
                multiple_dates=accounting["event_types_with_multiple_introduction_dates"],
                type_dates=accounting["distinct_type_introduction_dates"],
                checked=mask_check["rows_checked"],
            )
        )
    legacy = [
        summary for summary in metadata["cap_summaries"] if summary["legacy_random_negative_audit"]
    ]
    if legacy:
        lines.extend(
            [
                "",
                "## Superseded random-panel audit before correction",
                "",
                "| Head cap | Mask | Synthetic negatives | Date-infeasible | Share |",
                "|---:|---|---:|---:|---:|",
            ]
        )
        for summary in legacy:
            for row in summary["legacy_random_negative_audit"]:
                lines.append(
                    "| {cap} | {mechanism} | {total:,} | {infeasible:,} | {share:.2%} |".format(
                        cap=summary["accounting"]["head_cap"],
                        mechanism=row["mechanism"],
                        total=row["synthetic_random_negatives"],
                        infeasible=row["date_infeasible_random_negatives"],
                        share=row["date_infeasible_share"],
                    )
                )
    lines.extend(
        [
            "",
            "The sidecars do not contain participant identities. They map only frozen canonical "
            "event-type identifiers to all associated introduction dates and preserve a hash-based "
            "provenance record for the public source snapshots.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Write cap-specific temporal sidecars and one safe aggregate policy audit."""
    args = parse_args()
    events = resolve(args.events)
    nodes_path = resolve(args.nodes)
    current_roster = resolve(args.current_roster)
    historical_roster = resolve(args.historical_roster)
    mask_dirs = {cap: resolve(path) for cap, path in args.mask_dirs.items()}
    sidecar_dir = resolve(args.sidecar_dir)
    metadata_path = resolve(args.metadata_output)
    audit_path = resolve(args.audit_output)
    for path, name in (
        (events, "native-event table"),
        (nodes_path, "node table"),
        (current_roster, "current roster"),
        (historical_roster, "historical roster"),
    ):
        require_file(path, name)
    nodes = read_nodes(nodes_path, args.node_column)
    terms_by_actor = load_senate_terms(current_roster, historical_roster)
    prepare_sidecar_dir(sidecar_dir, args.overwrite)
    cap_summaries: list[dict[str, Any]] = []
    source_coverage: dict[str, int] | None = None
    for head_cap in args.head_caps:
        type_rows, accounting, raw_coverage = read_type_dates(
            events,
            tail_column=args.event_tail_column,
            head_column=args.event_head_column,
            date_column=args.introduced_date_column,
            node_set=set(nodes),
            tail_cap=args.tail_cap,
            head_cap=head_cap,
            terms_by_actor=terms_by_actor,
        )
        if source_coverage is None:
            source_coverage = raw_coverage
        elif source_coverage != raw_coverage:
            raise RuntimeError("full source-positive service coverage changed across caps")
        sidecar_path = (
            sidecar_dir / f"event_type_introduction_dates_tail{args.tail_cap}_head{head_cap}.json"
        )
        sidecar_payload = {
            "schema_version": 1,
            "dataset_id": args.dataset_id,
            "service_rule": "term_start <= introduction_date < term_end for every associated date",
            "tail_cap": args.tail_cap,
            "head_cap": head_cap,
            "event_types": type_rows,
        }
        sidecar_path.write_text(
            json.dumps(sidecar_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        identity_check = validate_mask_identity(mask_dirs[head_cap], type_rows)
        legacy_audit = (
            legacy_random_negative_audit(
                resolve(args.legacy_heuristic_dirs[head_cap]), type_rows, terms_by_actor
            )
            if head_cap in args.legacy_heuristic_dirs
            else []
        )
        cap_summaries.append(
            {
                "accounting": asdict(accounting),
                "frozen_mask_directory": recorded(mask_dirs[head_cap]),
                "frozen_mask_identity_check": identity_check,
                "legacy_random_negative_audit": legacy_audit,
                "sidecar": {"path": recorded(sidecar_path), "sha256": sha256_file(sidecar_path)},
            }
        )
    if source_coverage is None:
        raise RuntimeError("source-positive service coverage was not computed")
    source_positive_service_coverage = {
        "event_records_checked": source_coverage["event_records_checked"],
        "event_records_service_covered": source_coverage["event_records_service_covered"],
        "event_records_without_full_service_coverage": source_coverage.get(
            "event_records_without_full_service_coverage", 0
        ),
        "participant_appearances_checked": source_coverage["participant_appearances"],
        "participant_appearances_service_covered": source_coverage[
            "participant_appearances_service_covered"
        ],
        "participant_appearances_without_service_coverage": source_coverage.get(
            "participant_appearances_without_service_coverage", 0
        ),
    }
    metadata: dict[str, Any] = {
        "dataset_id": args.dataset_id,
        "driver": "scripts/77_prepare_senate_temporal_constraints.py",
        "status": "temporal_random_negative_policy_ready",
        "policy": {
            "scope": (
                "Senate random native-event negatives only; frozen masks and positives unchanged"
            ),
            "date_reference": (
                "every distinct Bill Status introduction date associated with the paired positive "
                "event type"
            ),
            "service_interval": "half-open: term_start <= introduction_date < term_end",
            "negative_eligibility": (
                "every synthetic candidate participant covers every associated date"
            ),
            "positive_exception_policy": (
                "source-positive roster-date exceptions are retained and reported"
            ),
        },
        "inputs": {
            "native_events": {"path": recorded(events), "sha256": sha256_file(events)},
            "nodes": {"path": recorded(nodes_path), "sha256": sha256_file(nodes_path)},
            "current_roster": {
                "path": recorded(current_roster),
                "sha256": sha256_file(current_roster),
            },
            "historical_roster": {
                "path": recorded(historical_roster),
                "sha256": sha256_file(historical_roster),
            },
        },
        "fixed_actor_universe": len(nodes),
        "source_positive_service_coverage": source_positive_service_coverage,
        "cap_summaries": cap_summaries,
        "privacy": "No actor IDs, event rows, candidate panels, or roster intervals are published.",
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_audit(audit_path, metadata)
    print("Senate temporal candidate-constraint sidecars passed.")
    print(
        "Source-positive records checked: "
        f"{source_positive_service_coverage['event_records_checked']:,}"
    )
    print(f"Cap sidecars written: {len(cap_summaries):,}")
    print(f"Aggregate audit: {recorded(audit_path)}")


if __name__ == "__main__":
    main()
