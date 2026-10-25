#!/usr/bin/env python3
"""Prepare audited 118th-Congress Senate bill co-sponsorship native events.

A native record is one Senate bill: the unique sponsor is its singleton tail and
its distinct original co-sponsors form the head. The driver retains original
co-sponsors even when the Bill Status record later lists withdrawal, because the
target is the coalition recorded at introduction. It audits two person-universe
policies before selecting the all-serving-persons policy when it preserves the
full valid event population.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONGRESS_START = date(2023, 1, 3)
CONGRESS_END = date(2025, 1, 3)
DEFAULT_REFERENCE_DATE = date(2024, 1, 1)


@dataclass(frozen=True, slots=True)
class SenateEvent:
    """One validated original-co-sponsorship record before actor-policy filtering."""

    event_id: str
    congress: int
    measure_type: str
    measure_number: int
    introduced_date: str
    sponsor: str
    original_cosponsors: tuple[str, ...]
    original_cosponsor_withdrawals: int


@dataclass(frozen=True, slots=True)
class ActorPolicy:
    """One transparent Bioguide-defined fixed person universe."""

    name: str
    description: str
    nodes: frozenset[str]


def parse_args() -> argparse.Namespace:
    """Parse a strict source, roster, and output contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", default="senate_118_s_bills")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/us_senate_118_billstatus_s"))
    parser.add_argument(
        "--roster-dir", type=Path, default=Path("data/raw/us_congress_legislators_gh_pages")
    )
    parser.add_argument(
        "--processed-dir", type=Path, default=Path("data/processed/senate_118_s_bills")
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/metadata/senate_118_s_bills_audit.json"),
    )
    parser.add_argument(
        "--policy-output",
        type=Path,
        default=Path("data/metadata/gates/senate_118_s_bills_policy.json"),
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("docs/data_audits/senate_118_s_bills.md"),
    )
    parser.add_argument("--congress", type=int, default=118)
    parser.add_argument("--measure-type", default="S")
    parser.add_argument("--reference-date", default=DEFAULT_REFERENCE_DATE.isoformat())
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.congress < 1:
        parser.error("--congress must be positive.")
    if args.measure_type != "S":
        parser.error("this Senate-bill pipeline accepts only --measure-type S.")
    try:
        reference = date.fromisoformat(args.reference_date)
    except ValueError as error:
        parser.error(f"--reference-date must be ISO YYYY-MM-DD: {error}")
    if not CONGRESS_START <= reference < CONGRESS_END:
        parser.error("--reference-date must lie within the 118th Congress term interval.")
    return args


def resolve(path: Path) -> Path:
    """Resolve project-relative paths against the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def recorded(path: Path) -> str:
    """Render a reproducible repository-relative path when possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    """Return a bounded-memory content hash for an input or prepared artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path, description: str) -> Any:
    """Read a required JSON source with a helpful failure message."""
    if not path.is_file():
        raise SystemExit(f"STOP: {description} is missing: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"STOP: {description} is not valid JSON: {path}") from error


def child_text(parent: ET.Element, path: str) -> str:
    """Read a trimmed optional text child from an XML element."""
    item = parent.find(path)
    return (item.text or "").strip() if item is not None and item.text else ""


def bioguide_id(item: ET.Element) -> str:
    """Read current direct or older nested Bill Status Bioguide identifiers."""
    return child_text(item, "bioguideId") or child_text(item, "identifiers/bioguideId")


def is_true(value: str) -> bool:
    """Recognise the canonical Bill Status XML Boolean literal."""
    return value.strip().casefold() == "true"


def parse_date(value: str, field: str, source: Path) -> date:
    """Validate a date-only source field before it enters a network policy."""
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field} is invalid in {source.name}: {value!r}") from error


def parse_bill_xml(
    path: Path,
    congress: int,
    measure_type: str,
    accounting: Counter[str],
) -> SenateEvent | None:
    """Parse one official Bill Status record under the declared event semantics."""
    accounting["xml_records_read"] += 1
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        accounting["excluded_xml_parse_error"] += 1
        return None
    bill = root.find("bill")
    if bill is None:
        accounting["excluded_missing_bill_element"] += 1
        return None
    observed_congress = child_text(bill, "congress")
    observed_type = child_text(bill, "type")
    number = child_text(bill, "number")
    if observed_congress != str(congress) or observed_type != measure_type:
        accounting["excluded_scope_mismatch"] += 1
        return None
    if not number.isdigit() or int(number) < 1:
        accounting["excluded_invalid_measure_number"] += 1
        return None
    introduced = child_text(bill, "introducedDate")
    try:
        parse_date(introduced, "introducedDate", path)
    except ValueError:
        accounting["excluded_invalid_introduced_date"] += 1
        return None

    sponsor_items = bill.findall("sponsors/item")
    sponsor_ids = [bioguide_id(item) for item in sponsor_items]
    if len(sponsor_items) != 1:
        accounting["excluded_not_exactly_one_sponsor_item"] += 1
        return None
    if len(sponsor_ids) != 1 or not sponsor_ids[0]:
        accounting["excluded_missing_sponsor_bioguide"] += 1
        return None
    sponsor = sponsor_ids[0]

    original_ids: list[str] = []
    withdrawals = 0
    for item in bill.findall("cosponsors/item"):
        accounting["cosponsor_rows_read"] += 1
        original_flag = child_text(item, "isOriginalCosponsor")
        if not original_flag:
            accounting["cosponsor_rows_missing_original_flag"] += 1
            continue
        if not is_true(original_flag):
            accounting["nonoriginal_cosponsor_rows"] += 1
            continue
        accounting["original_cosponsor_rows"] += 1
        identifier = bioguide_id(item)
        if not identifier:
            accounting["excluded_missing_original_cosponsor_bioguide"] += 1
            return None
        original_ids.append(identifier)
        if child_text(item, "sponsorshipWithdrawnDate"):
            withdrawals += 1

    if not original_ids:
        accounting["zero_original_cosponsor_measures"] += 1
        return None
    original_set = frozenset(original_ids)
    duplicate_count = len(original_ids) - len(original_set)
    accounting["duplicate_original_cosponsor_rows"] += duplicate_count
    if sponsor in original_set:
        accounting["excluded_sponsor_in_original_head"] += 1
        return None
    head = tuple(sorted(original_set))
    event = SenateEvent(
        event_id=f"{congress}-{measure_type}-{int(number)}",
        congress=congress,
        measure_type=measure_type,
        measure_number=int(number),
        introduced_date=introduced,
        sponsor=sponsor,
        original_cosponsors=head,
        original_cosponsor_withdrawals=withdrawals,
    )
    accounting["valid_nonempty_head_event_records"] += 1
    accounting["original_cosponsor_withdrawals_retained"] += withdrawals
    return event


def load_events(
    raw_dir: Path, congress: int, measure_type: str
) -> tuple[tuple[SenateEvent, ...], dict[str, int]]:
    """Parse and reconcile every acquired XML file in the declared official snapshot."""
    manifest = read_json(raw_dir / "SOURCE_MANIFEST.json", "Bill Status source manifest")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("records"), list):
        raise SystemExit("STOP: Bill Status source manifest lacks the acquisition record list.")
    expected_names = {str(row.get("filename", "")) for row in manifest["records"]}
    xml_paths = tuple(sorted(raw_dir.glob("BILLSTATUS-*.xml")))
    observed_names = {path.name for path in xml_paths}
    if not xml_paths or expected_names != observed_names:
        raise SystemExit(
            "STOP: acquired XML files do not exactly reconcile with SOURCE_MANIFEST.json."
        )
    accounting: Counter[str] = Counter()
    events: list[SenateEvent] = []
    event_ids: set[str] = set()
    for path in xml_paths:
        event = parse_bill_xml(path, congress, measure_type, accounting)
        if event is None:
            continue
        if event.event_id in event_ids:
            raise SystemExit(f"STOP: duplicate stable bill event ID: {event.event_id}")
        event_ids.add(event.event_id)
        events.append(event)
    if not events:
        raise SystemExit("STOP: no valid nonempty-head Senate bill events were constructed.")
    if accounting["xml_records_read"] != len(xml_paths):
        raise RuntimeError("XML record accounting did not reconcile.")
    return tuple(sorted(events, key=lambda event: event.measure_number)), dict(
        sorted(accounting.items())
    )


def term_dates(term: dict[str, Any]) -> tuple[date, date] | None:
    """Read a Senate term date interval, rejecting incomplete or malformed entries."""
    if term.get("type") != "sen":
        return None
    start, end = term.get("start"), term.get("end")
    if not isinstance(start, str) or not isinstance(end, str):
        return None
    try:
        return date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        return None


def load_roster(roster_dir: Path) -> tuple[dict[str, list[tuple[date, date]]], dict[str, int]]:
    """Load all current/historical Senate terms keyed solely by Bioguide ID."""
    records: dict[str, list[tuple[date, date]]] = {}
    accounting: Counter[str] = Counter()
    for filename in ("legislators-current.json", "legislators-historical.json"):
        values = read_json(roster_dir / filename, f"roster source {filename}")
        if not isinstance(values, list):
            raise SystemExit(f"STOP: roster source is not a list: {filename}")
        for person in values:
            accounting["roster_people_read"] += 1
            if not isinstance(person, dict) or not isinstance(person.get("id"), dict):
                accounting["roster_people_invalid"] += 1
                continue
            identifier = person["id"].get("bioguide")
            if not isinstance(identifier, str) or not identifier.strip():
                accounting["roster_people_missing_bioguide"] += 1
                continue
            terms = person.get("terms")
            if not isinstance(terms, list):
                accounting["roster_people_missing_terms"] += 1
                continue
            sen_terms = [
                dates for term in terms if isinstance(term, dict) if (dates := term_dates(term))
            ]
            if not sen_terms:
                continue
            records.setdefault(identifier.strip(), []).extend(sen_terms)
    if not records:
        raise SystemExit("STOP: no Bioguide-keyed Senate terms were loaded from roster files.")
    for identifier, terms in records.items():
        records[identifier] = sorted(set(terms))
    accounting["roster_people_with_senate_terms"] = len(records)
    return records, dict(sorted(accounting.items()))


def actor_policies(
    roster: dict[str, list[tuple[date, date]]], reference_date: date
) -> tuple[ActorPolicy, ...]:
    """Create the planned reference-date and all-serving-person actor policies."""
    reference_nodes = frozenset(
        identifier
        for identifier, terms in roster.items()
        if any(start <= reference_date < end for start, end in terms)
    )
    all_serving = frozenset(
        identifier
        for identifier, terms in roster.items()
        if any(start < CONGRESS_END and end > CONGRESS_START for start, end in terms)
    )
    if not reference_nodes or not all_serving:
        raise SystemExit("STOP: roster policies produced an empty actor universe.")
    return (
        ActorPolicy(
            name=f"reference_date_{reference_date.isoformat().replace('-', '_')}",
            description=(
                "Persons with a Senate term covering the declared 118th-Congress reference date "
                f"{reference_date.isoformat()}."
            ),
            nodes=reference_nodes,
        ),
        ActorPolicy(
            name="all_serving_persons_during_118th_congress",
            description=(
                "Persons with a Senate term overlapping 2023-01-03 through 2025-01-03; "
                "people are never merged by seat."
            ),
            nodes=all_serving,
        ),
    )


def filter_events(
    events: tuple[SenateEvent, ...], nodes: frozenset[str]
) -> tuple[SenateEvent, ...]:
    """Retain only events whose entire ordered group lies in one fixed actor universe."""
    return tuple(
        event
        for event in events
        if event.sponsor in nodes and set(event.original_cosponsors) <= nodes
    )


def event_rows(events: tuple[SenateEvent, ...]) -> list[dict[str, object]]:
    """Convert native bill events to a typed, role-explicit Parquet table."""
    return [
        {
            "event_id": event.event_id,
            "congress": event.congress,
            "measure_type": event.measure_type,
            "measure_number": event.measure_number,
            "introduced_date": event.introduced_date,
            "tail_sponsor_bioguide": event.sponsor,
            "head_original_cosponsors_bioguide": list(event.original_cosponsors),
            "original_head_size": len(event.original_cosponsors),
            "original_cosponsor_withdrawals": event.original_cosponsor_withdrawals,
        }
        for event in events
    ]


def node_rows(events: tuple[SenateEvent, ...], nodes: frozenset[str]) -> list[dict[str, object]]:
    """Create actor-free activity counts for every fixed-universe Bioguide node."""
    sponsor = Counter(event.sponsor for event in events)
    cosponsor = Counter(member for event in events for member in event.original_cosponsors)
    return [
        {
            "node": node,
            "sponsor_event_records": sponsor[node],
            "original_cosponsor_event_records": cosponsor[node],
            "total_event_participations": sponsor[node] + cosponsor[node],
        }
        for node in sorted(nodes)
    ]


def arc_rows(events: tuple[SenateEvent, ...]) -> list[dict[str, object]]:
    """Construct the simple sponsor-to-original-co-sponsor projection with counts."""
    counts = Counter(
        (event.sponsor, cosponsor) for event in events for cosponsor in event.original_cosponsors
    )
    return [
        {"tail": tail, "head": head, "interaction_count": count}
        for (tail, head), count in sorted(counts.items())
    ]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty deterministic CSV table with POSIX line endings."""
    if not rows:
        raise RuntimeError(f"cannot write an empty required CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_parquet(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty typed Parquet output without pandas conversion ambiguity."""
    if not rows:
        raise RuntimeError(f"cannot write an empty required Parquet table: {path}")
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def prepare_output(path: Path, overwrite: bool) -> None:
    """Create or explicitly replace only the Senate processed-data directory."""
    if path.exists() and not path.is_dir():
        raise SystemExit(f"STOP: processed output path is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not overwrite:
            raise SystemExit(f"STOP: processed output is nonempty: {path}; pass --overwrite.")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_markdown_audit(path: Path, audit: dict[str, Any]) -> None:
    """Write a concise inspectable event and actor-policy audit."""
    events = audit["event_construction"]
    policies = audit["actor_policies"]
    zero_head = events.get("zero_original_cosponsor_measures", 0)
    sponsor_exclusions = events.get("excluded_not_exactly_one_sponsor_item", 0) + events.get(
        "excluded_missing_sponsor_bioguide", 0
    )
    invalid_dates = events.get("excluded_invalid_introduced_date", 0)
    retained_withdrawals = events.get("original_cosponsor_withdrawals_retained", 0)
    lines = [
        "# U.S. Senate 118th Congress S. bill co-sponsorship audit",
        "",
        "## Event definition",
        "",
        "One source record is a Senate bill (`S.`) from the 118th Congress. Its singleton "
        "tail is the Bill Status sponsor Bioguide ID; its head is the set of co-sponsors whose "
        "`isOriginalCosponsor` field is `True`. The target retains an original co-sponsor even "
        "if the official record later lists a withdrawal date, because it represents the "
        "coalition recorded at introduction.",
        "",
        "## Source accounting",
        "",
        f"- Official XML files read: `{events['xml_records_read']:,}`",
        f"- Valid records with a nonempty original-co-sponsor head: "
        f"`{events['valid_nonempty_head_event_records']:,}`",
        f"- Measures with zero original co-sponsors: `{zero_head:,}`",
        f"- Records excluded for non-single/missing sponsors: `{sponsor_exclusions:,}`",
        f"- Records excluded for an invalid introduction date: `{invalid_dates:,}`",
        f"- Original-cosponsor withdrawal entries retained as introduction-time members: "
        f"`{retained_withdrawals:,}`",
        "",
        "## Actor-universe comparison",
        "",
        "| Policy | Nodes | Valid events retained | Event retention | Static arcs |",
        "|---|---:|---:|---:|---:|",
    ]
    total = events["valid_nonempty_head_event_records"]
    for policy in policies:
        lines.append(
            "| {name} | {nodes:,} | {events:,} | {share:.3%} | {arcs:,} |".format(
                name=policy["name"],
                nodes=policy["nodes"],
                events=policy["retained_event_records"],
                share=policy["retained_event_records"] / total,
                arcs=policy["static_arcs"],
            )
        )
    primary = audit["primary_policy"]
    lines.extend(
        [
            "",
            "## Frozen Stage-A policy",
            "",
            f"- Primary actor universe: `{primary['name']}` (`{primary['nodes']:,}` persons).",
            f"- Reason: {primary['selection_reason']}",
            "- The cap has deliberately **not** been selected in this audit. A separate cap-first "
            "audit reports retention, formal-concept feasibility, and candidate viability before "
            "any primary masking or model run.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Build the event table, projection, actor-policy audit, and frozen Stage-A policy."""
    args = parse_args()
    raw_dir = resolve(args.raw_dir)
    roster_dir = resolve(args.roster_dir)
    processed_dir = resolve(args.processed_dir)
    metadata_output = resolve(args.metadata_output)
    policy_output = resolve(args.policy_output)
    audit_output = resolve(args.audit_output)
    reference_date = date.fromisoformat(args.reference_date)

    events, event_accounting = load_events(raw_dir, args.congress, args.measure_type)
    roster, roster_accounting = load_roster(roster_dir)
    policies = actor_policies(roster, reference_date)
    policy_rows: list[dict[str, Any]] = []
    selected_events: tuple[SenateEvent, ...] | None = None
    primary_name = "all_serving_persons_during_118th_congress"
    for policy in policies:
        retained = filter_events(events, policy.nodes)
        arcs = arc_rows(retained)
        row = {
            "name": policy.name,
            "description": policy.description,
            "nodes": len(policy.nodes),
            "retained_event_records": len(retained),
            "excluded_outside_actor_universe": len(events) - len(retained),
            "static_arcs": len(arcs),
        }
        policy_rows.append(row)
        if policy.name == primary_name:
            selected_events = retained
            selected_policy = policy
            selected_row = row
    if selected_events is None or "selected_policy" not in locals():
        raise RuntimeError("all-serving-persons actor policy was not constructed")
    if not selected_events:
        raise SystemExit("STOP: all-serving-persons policy retained no valid native events.")
    if len(selected_events) != len(events):
        raise SystemExit(
            "STOP: all-serving-persons policy did not preserve every valid bill event; "
            "inspect roster coverage before continuing."
        )

    prepare_output(processed_dir, args.overwrite)
    native_event_path = processed_dir / "native_events.parquet"
    node_path = processed_dir / "nodes.csv"
    arc_path = processed_dir / "static_arcs.parquet"
    write_parquet(native_event_path, event_rows(selected_events))
    write_csv(node_path, node_rows(selected_events, selected_policy.nodes))
    write_parquet(arc_path, arc_rows(selected_events))

    audit: dict[str, Any] = {
        "dataset_id": args.dataset_id,
        "status": "stage_a_event_and_actor_policy_audited",
        "driver": "scripts/65_prepare_senate_118_s_bills.py",
        "event_definition": {
            "source_scope": f"{args.congress}th Congress, {args.measure_type}. bills only",
            "event_record": "one stable bill identifier",
            "tail": "unique Bill Status sponsor Bioguide ID",
            "head": "distinct Bill Status original-co-sponsor Bioguide IDs",
            "original_member_policy": "isOriginalCosponsor == True; later withdrawal retained",
            "empty_head_policy": "reported and excluded from nonempty-head native-event target",
            "identity_policy": "opaque Bioguide IDs only; no person-name matching or seat merging",
        },
        "inputs": {
            "billstatus_raw_directory": {
                "path": recorded(raw_dir),
                "source_manifest_sha256": sha256_file(raw_dir / "SOURCE_MANIFEST.json"),
            },
            "roster_raw_directory": {
                "path": recorded(roster_dir),
                "current_sha256": sha256_file(roster_dir / "legislators-current.json"),
                "historical_sha256": sha256_file(roster_dir / "legislators-historical.json"),
            },
        },
        "event_construction": event_accounting,
        "roster_accounting": roster_accounting,
        "actor_policies": policy_rows,
        "primary_policy": {
            "name": selected_policy.name,
            "description": selected_policy.description,
            "nodes": len(selected_policy.nodes),
            "selection_reason": (
                "It preserves every valid nonempty-head event while retaining distinct persons "
                "throughout the completed Congress; no people are merged by Senate seat."
            ),
        },
        "processed_outputs": {
            "native_events": {
                "path": recorded(native_event_path),
                "sha256": sha256_file(native_event_path),
            },
            "nodes": {"path": recorded(node_path), "sha256": sha256_file(node_path)},
            "static_arcs": {"path": recorded(arc_path), "sha256": sha256_file(arc_path)},
        },
        "next_gate": (
            "Run cap-first retention, formal-concept feasibility, and candidate-panel audit before "
            "selecting the Senate head cap or creating primary masks."
        ),
    }
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    policy = {
        "dataset_id": args.dataset_id,
        "status": "approved_for_cap_gate_only",
        "event_definition": audit["event_definition"],
        "actor_universe": audit["primary_policy"],
        "processed_paths": audit["processed_outputs"],
        "cap_policy": "pending_cap_first_audit; no masking or model fit permitted",
    }
    policy_output.parent.mkdir(parents=True, exist_ok=True)
    policy_output.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_audit(audit_output, audit)
    print("Senate bill co-sponsorship event and actor-policy audit passed.")
    print(f"Dataset: {args.dataset_id}.")
    print(f"Valid nonempty-head bill records: {len(events):,}.")
    print(f"Primary fixed person universe: {len(selected_policy.nodes):,}.")
    print(f"Static directed arcs: {len(arc_rows(selected_events)):,}.")
    print(f"Audit: {recorded(audit_output)}")


if __name__ == "__main__":
    main()
