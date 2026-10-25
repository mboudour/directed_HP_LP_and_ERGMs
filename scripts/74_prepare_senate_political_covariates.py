#!/usr/bin/env python3
"""Build audited 118th-Senate political covariates keyed by Bioguide ID.

The benchmark aggregates bill events over the 118th Congress. This driver
creates a fixed actor table for static ERGM scoring: party at the Congress
start (2023-01-03), serving state, Voteview first-dimension DW-NOMINATE,
majority-caucus membership, and prior Senate-service tenure. It preserves a
separate audit of affiliation changes rather than silently assuming that party
was constant over each senator's full term.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONGRESS_START = date(2023, 1, 3)
CONGRESS_END = date(2025, 1, 3)
DEFAULT_NODES = PROJECT_ROOT / "data" / "processed" / "senate_118_s_bills" / "nodes.csv"
DEFAULT_CURRENT = (
    PROJECT_ROOT / "data" / "raw" / "us_congress_legislators_gh_pages" / "legislators-current.json"
)
DEFAULT_HISTORICAL = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "us_congress_legislators_gh_pages"
    / "legislators-historical.json"
)
DEFAULT_VOTEVIEW = PROJECT_ROOT / "data" / "raw" / "voteview_members" / "HSall_members.csv"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "processed" / "senate_118_s_bills" / "node_political_covariates.csv"
)
DEFAULT_METADATA = (
    PROJECT_ROOT / "data" / "metadata" / "senate_118_s_bills_political_covariates.json"
)
DEFAULT_AUDIT = PROJECT_ROOT / "docs" / "data_audits" / "senate_118_s_bills_political_covariates.md"


def parse_args() -> argparse.Namespace:
    """Parse the explicit preparation contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=Path, default=DEFAULT_NODES)
    parser.add_argument("--current-roster", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--historical-roster", type=Path, default=DEFAULT_HISTORICAL)
    parser.add_argument("--voteview-members", type=Path, default=DEFAULT_VOTEVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve one path relative to the repository root."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def relative(path: Path) -> str:
    """Render a repository-relative path where possible."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str:
    """Calculate one local source file checksum."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare_output(path: Path, overwrite: bool) -> None:
    """Reject accidental replacement of a derived covariate file."""
    if path.exists() and not overwrite:
        raise SystemExit(f"STOP: output already exists; pass --overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def read_nodes(path: Path) -> dict[str, int]:
    """Read the unique Senate actor universe and its participation counts."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"node", "total_event_participations"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"STOP: node file lacks required fields {sorted(required)}: {path}")
    nodes = [row["node"].strip() for row in rows]
    if any(not node for node in nodes) or len(nodes) != len(set(nodes)):
        raise SystemExit("STOP: node universe has blank or duplicate identifiers.")
    try:
        counts = {
            node: int(row["total_event_participations"])
            for node, row in zip(nodes, rows, strict=True)
        }
    except ValueError as error:
        raise SystemExit("STOP: total_event_participations must be integer-valued.") from error
    if any(count < 0 for count in counts.values()):
        raise SystemExit("STOP: total_event_participations may not be negative.")
    return dict(sorted(counts.items()))


def read_roster(path: Path) -> list[dict[str, Any]]:
    """Read one congress-legislators JSON snapshot."""
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise SystemExit(f"STOP: roster JSON is not an array: {path}")
    return records


def overlaps_118(term: dict[str, Any]) -> bool:
    """Return whether a Senate service term overlaps the 118th Congress."""
    if term.get("type") != "sen":
        return False
    try:
        start = date.fromisoformat(str(term["start"]))
        end = date.fromisoformat(str(term["end"]))
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"STOP: malformed Senate term dates: {term}") from error
    return start < CONGRESS_END and end > CONGRESS_START


def party_at_reference_date(term: dict[str, Any], reference: date) -> tuple[str, bool]:
    """Return party at a service-reference date and any later term-local change."""
    affiliations = term.get("party_affiliations")
    if affiliations:
        current: str | None = None
        changed = False
        for affiliation in affiliations:
            try:
                start = date.fromisoformat(str(affiliation["start"]))
                end = date.fromisoformat(str(affiliation["end"]))
            except (KeyError, TypeError, ValueError) as error:
                raise SystemExit(
                    f"STOP: malformed party affiliation dates: {affiliation}"
                ) from error
            if start <= reference < end:
                current = str(affiliation["party"])
            if reference < end and start < CONGRESS_END:
                changed = changed or start > reference
        if current is None:
            raise SystemExit(
                f"STOP: party affiliations do not cover the declared reference date: {affiliations}"
            )
        return current, changed
    party = str(term.get("party", "")).strip()
    if not party:
        raise SystemExit(f"STOP: Senate term has no party field: {term}")
    return party, False


def senate_service_days_before(record: dict[str, Any], reference: date) -> int:
    """Return cumulative completed Senate service days before an actor's reference date."""
    service_days = 0
    for term in record.get("terms", []):
        if term.get("type") != "sen":
            continue
        try:
            start = date.fromisoformat(str(term["start"]))
            end = date.fromisoformat(str(term["end"]))
        except (KeyError, TypeError, ValueError) as error:
            raise SystemExit(f"STOP: malformed Senate term dates: {term}") from error
        completed_end = min(end, reference)
        if start < completed_end:
            service_days += (completed_end - start).days
    return service_days


def roster_lookup(records: list[dict[str, Any]], node_set: set[str]) -> dict[str, dict[str, str]]:
    """Select exactly one 118th Senate service record per benchmark actor."""
    selected: dict[str, dict[str, str]] = {}
    for record in records:
        identifiers = record.get("id", {})
        bioguide = str(identifiers.get("bioguide", "")).strip()
        if bioguide not in node_set:
            continue
        candidates = [term for term in record.get("terms", []) if overlaps_118(term)]
        if not candidates:
            continue
        candidates.sort(key=lambda term: str(term["start"]))
        states = {str(term.get("state", "")).strip() for term in candidates}
        if len(states) != 1 or "" in states:
            raise SystemExit(f"STOP: inconsistent serving-state records for {bioguide}.")
        term = candidates[0]
        term_start = date.fromisoformat(str(term["start"]))
        reference = max(CONGRESS_START, term_start)
        party, changed = party_at_reference_date(term, reference)
        for later_term in candidates[1:]:
            later_party, later_changed = party_at_reference_date(
                later_term, date.fromisoformat(str(later_term["start"]))
            )
            changed = changed or later_changed or later_party != party
        icpsr = str(identifiers.get("icpsr", "")).strip()
        state = next(iter(states))
        if not state:
            raise SystemExit(f"STOP: incomplete serving-state field for {bioguide}.")
        candidate = {
            "node": bioguide,
            "party_118_entry": party,
            "majority_caucus_entry": str(int(party != "Republican")),
            "state": state,
            "icpsr": icpsr,
            "senate_service_years_at_118_entry": (
                f"{senate_service_days_before(record, reference) / 365.25:.12g}"
            ),
            "term_start": str(candidates[0]["start"]),
            "term_end": str(candidates[-1]["end"]),
            "party_changed_during_118": str(changed).lower(),
        }
        if bioguide in selected and selected[bioguide] != candidate:
            raise SystemExit(f"STOP: conflicting roster records for {bioguide}.")
        selected[bioguide] = candidate
    missing = sorted(node_set - set(selected))
    if missing:
        raise SystemExit(
            f"STOP: roster records missing for {len(missing)} actor(s): {missing[:10]}"
        )
    return selected


def read_voteview(
    path: Path, roster: dict[str, dict[str, str]], participation: dict[str, int]
) -> tuple[dict[str, float], list[dict[str, str]]]:
    """Select one first-dimension Voteview score per roster actor.

    The stable resolution rule is exact matching on the congress-legislators
    ICPSR identifier. It resolves the duplicate Bioguide record in the current
    118th-Senate Voteview file without selecting a score by its value.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    needed = {"congress", "chamber", "bioguide_id", "icpsr", "nominate_dim1"}
    if not rows or not needed.issubset(rows[0]):
        raise SystemExit(f"STOP: Voteview file lacks required columns: {path}")
    by_bioguide: dict[str, list[dict[str, str]]] = {}
    historical_by_bioguide: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        bioguide = row["bioguide_id"].strip()
        if bioguide not in roster or row["chamber"] != "Senate":
            continue
        if row["congress"] == "118":
            by_bioguide.setdefault(bioguide, []).append(row)
        else:
            try:
                congress = int(row["congress"])
            except ValueError as error:
                raise SystemExit(
                    f"STOP: invalid Voteview Congress field: {row['congress']!r}"
                ) from error
            if congress < 118:
                historical_by_bioguide.setdefault(bioguide, []).append(row)
    scores: dict[str, float] = {}
    resolutions: list[dict[str, str]] = []
    for node, details in sorted(roster.items()):
        candidates = by_bioguide.get(node, [])
        matches = [row for row in candidates if row["icpsr"].strip() == details["icpsr"]]
        if len(candidates) == 1:
            selected = candidates[0]
            rule = "unique 118th-Senate Voteview record by Bioguide ID"
        elif len(matches) == 1:
            selected = matches[0]
            rule = "exact ICPSR match to congress-legislators roster"
        elif not candidates and participation[node] == 0:
            historical = historical_by_bioguide.get(node, [])
            if not historical:
                raise SystemExit(
                    "STOP: event-isolated actor has neither a 118th nor prior Senate "
                    f"Voteview record: {node}."
                )
            last_congress = max(int(row["congress"]) for row in historical)
            last_rows = [row for row in historical if int(row["congress"]) == last_congress]
            if len(last_rows) != 1:
                raise SystemExit(
                    "STOP: event-isolated actor has ambiguous latest prior Senate Voteview "
                    f"record: {node}; Congress={last_congress}; rows={len(last_rows)}."
                )
            selected = last_rows[0]
            rule = "latest prior Senate Voteview record for event-isolated actor"
        else:
            raise SystemExit(
                "STOP: Voteview has no unambiguous Bioguide/ICPSR match for "
                f"{node}; candidates={len(candidates)}, ICPSR matches={len(matches)}."
            )
        try:
            score = float(selected["nominate_dim1"])
        except (TypeError, ValueError) as error:
            raise SystemExit(f"STOP: invalid Voteview nominate_dim1 for {node}.") from error
        scores[node] = score
        if len(candidates) > 1 or not candidates:
            resolutions.append(
                {
                    "node": node,
                    "voteview_records": str(len(candidates)),
                    "selection_rule": rule,
                    "selected_icpsr": selected["icpsr"],
                }
            )
    return scores, resolutions


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a deterministic nonempty table."""
    if not rows:
        raise SystemExit(f"STOP: cannot write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_audit(summary: dict[str, object], resolutions: list[dict[str, str]]) -> str:
    """Render an actor-free audit report for repository tracking."""
    resolution_line = (
        "No duplicated Voteview Bioguide records were encountered."
        if not resolutions
        else (
            f"{len(resolutions)} exceptional Voteview join(s) used a documented key rule; "
            "no score-value-based selection was used."
        )
    )
    return "\n".join(
        [
            "# 118th Senate political covariate preparation",
            "",
            "## Fixed actor policy",
            "",
            "The static benchmark uses the complete 118th-Senate actor universe from the "
            "audited bill-event construction. Party is affiliation at the beginning of the "
            "actor's 118th service (2023-01-03 for incumbents), state is the serving state, "
            "and ideology is Voteview's "
            "first-dimension DW-NOMINATE estimate. This is a static covariate policy; "
            "it does not treat party or ideology as a time-varying event covariate.",
            "Majority-caucus entry is coded one for Democratic and Independent actors and "
            "zero for Republican actors, reflecting the 118th Senate's Democratic/Independent "
            "majority caucus. Senate seniority is cumulative completed Senate service before "
            "the actor's own 118th-service entry date, expressed in years.",
            "",
            "## Join checks",
            "",
            f"- Senate actors: `{summary['actors']}`",
            f"- Roster matches: `{summary['roster_matches']}`",
            f"- Voteview matches: `{summary['voteview_matches']}`",
            f"- States represented: `{summary['states_represented']}`",
            f"- Party-at-entry categories: `{summary['party_categories']}`",
            f"- Majority-caucus entrants: `{summary['majority_caucus_actors']}`",
            f"- Senate seniority years at service entry (median): "
            f"`{summary['seniority_years_median']:.2f}`",
            f"- Actors with a recorded affiliation change during the Congress: "
            f"`{summary['party_change_actors']}`",
            f"- {resolution_line}",
            "",
            "The generated node-level table remains excluded from version control. The tracked "
            "metadata file records only aggregate counts, source paths, and checksums.",
            "",
        ]
    )


def main() -> None:
    """Build the fixed political covariate table and actor-free audit."""
    args = parse_args()
    nodes_path = resolve(args.nodes)
    current_path = resolve(args.current_roster)
    historical_path = resolve(args.historical_roster)
    voteview_path = resolve(args.voteview_members)
    output_path = resolve(args.output)
    metadata_path = resolve(args.metadata)
    audit_path = resolve(args.audit)
    for path in (nodes_path, current_path, historical_path, voteview_path):
        if not path.exists():
            raise SystemExit(f"STOP: required input missing: {path}")
    prepare_output(output_path, args.overwrite)
    prepare_output(metadata_path, args.overwrite)
    prepare_output(audit_path, args.overwrite)

    nodes = read_nodes(nodes_path)
    node_set = set(nodes)
    records = read_roster(current_path) + read_roster(historical_path)
    roster = roster_lookup(records, node_set)
    scores, resolutions = read_voteview(voteview_path, roster, nodes)
    rows = [
        {
            "node": node,
            "party_118_entry": roster[node]["party_118_entry"],
            "majority_caucus_entry": roster[node]["majority_caucus_entry"],
            "state": roster[node]["state"],
            "dw_nominate_dim1": f"{scores[node]:.12g}",
            "senate_service_years_at_118_entry": roster[node]["senate_service_years_at_118_entry"],
        }
        for node in nodes
    ]
    write_csv(output_path, rows)
    party_counts = Counter(row["party_118_entry"] for row in rows)
    summary: dict[str, object] = {
        "actors": len(nodes),
        "roster_matches": len(roster),
        "voteview_matches": len(scores),
        "states_represented": len({row["state"] for row in rows}),
        "party_categories": dict(sorted(party_counts.items())),
        "party_change_actors": sum(
            details["party_changed_during_118"] == "true" for details in roster.values()
        ),
        "majority_caucus_actors": sum(
            details["majority_caucus_entry"] == "1" for details in roster.values()
        ),
        "seniority_years_median": sorted(
            float(details["senate_service_years_at_118_entry"]) for details in roster.values()
        )[len(roster) // 2],
        "voteview_duplicate_resolutions": len(resolutions),
    }
    metadata_path.write_text(
        json.dumps(
            {
                "dataset_id": "senate_118_s_bills",
                "covariate_policy": {
                    "congress_interval": [str(CONGRESS_START), str(CONGRESS_END)],
                    "party": "party at 118th-service entry (Congress start for incumbents)",
                    "majority_caucus": (
                        "Democratic/Independent majority-caucus indicator at 118th-service entry"
                    ),
                    "state": "serving state in selected Senate term",
                    "ideology": "Voteview first-dimension DW-NOMINATE",
                    "seniority": (
                        "cumulative completed Senate-service years before 118th-service entry"
                    ),
                    "voteview_duplicate_resolution": (
                        "unique 118th-Senate Bioguide record where available; exact ICPSR "
                        "match for duplicated Bioguide records; latest prior-Senate record only "
                        "for event-isolated actors; never score-value selection"
                    ),
                },
                "inputs": {
                    relative(nodes_path): sha256(nodes_path),
                    relative(current_path): sha256(current_path),
                    relative(historical_path): sha256(historical_path),
                    relative(voteview_path): sha256(voteview_path),
                },
                "outputs": {"node_covariates": relative(output_path)},
                "summary": summary,
                "duplicate_resolutions": resolutions,
                "privacy": "Actor-level covariate table is excluded from version control.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    audit_path.write_text(build_audit(summary, resolutions), encoding="utf-8")
    print("Senate political covariate preparation passed.")
    print(
        f"Actors: {summary['actors']}; roster/Voteview matches: "
        f"{summary['roster_matches']}/{summary['voteview_matches']}"
    )
    print(f"Output: {relative(output_path)}")
    print(f"Metadata: {relative(metadata_path)}")
    print(f"Audit: {relative(audit_path)}")


if __name__ == "__main__":
    main()
