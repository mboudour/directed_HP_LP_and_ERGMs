"""Regression coverage for the public Senate co-sponsorship Stage-A pipeline."""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ACQUIRE_DRIVER = PROJECT_ROOT / "scripts" / "63_acquire_senate_billstatus.py"
PREPARE_DRIVER = PROJECT_ROOT / "scripts" / "65_prepare_senate_118_s_bills.py"
CAP_DRIVER = PROJECT_ROOT / "scripts" / "66_profile_senate_cap_gate.py"
HARD_DRIVER = PROJECT_ROOT / "scripts" / "67_run_senate_sponsor_substitution.py"


def load_module(path: Path):  # type: ignore[no-untyped-def]
    """Import a numbered standalone script without changing its source interface."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_xml(path: Path, number: int, sponsor: str, cosponsors: list[dict[str, str]]) -> None:
    """Write a small Bill Status v3-compatible XML fixture."""
    cosponsor_xml = "\n".join(
        """<item>
<bioguideId>{bioguide}</bioguideId>
<isOriginalCosponsor>{original}</isOriginalCosponsor>
<sponsorshipDate>2023-01-03</sponsorshipDate>
{withdrawal}
</item>""".format(
            bioguide=item["bioguide"],
            original=item["original"],
            withdrawal=(
                f"<sponsorshipWithdrawnDate>{item['withdrawal']}</sponsorshipWithdrawnDate>"
                if item.get("withdrawal")
                else ""
            ),
        )
        for item in cosponsors
    )
    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<billStatus><version>3.0.0</version><bill>
<number>{number}</number><type>S</type><congress>118</congress>
<introducedDate>2023-01-03</introducedDate>
<sponsors><item><bioguideId>{sponsor}</bioguideId></item></sponsors>
<cosponsors>{cosponsor_xml}</cosponsors>
</bill></billStatus>
""",
        encoding="utf-8",
    )


def roster_person(
    identifier: str, start: str = "2023-01-03", end: str = "2025-01-03"
) -> dict[str, object]:
    """Return one Senate-term roster fixture record keyed by Bioguide ID."""
    return {"id": {"bioguide": identifier}, "terms": [{"type": "sen", "start": start, "end": end}]}


def rows(path: Path) -> list[dict[str, str]]:
    """Read a generated CSV table."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_govinfo_json_listing_parser_rejects_nonmatching_entries() -> None:
    """Only exact official Senate Bill Status XML links enter the source contract."""
    module = load_module(ACQUIRE_DRIVER)
    payload = {
        "files": [
            {"link": "https://www.govinfo.gov/bulkdata/BILLSTATUS/118/s/BILLSTATUS-118s1.xml"},
            {"link": "https://www.govinfo.gov/bulkdata/BILLSTATUS/118/hr/BILLSTATUS-118hr1.xml"},
            {"link": "https://example.org/BILLSTATUS-118s2.xml"},
        ]
    }
    parsed = module.parse_listing(json.dumps(payload).encode("utf-8"), 118, "s")
    assert parsed == ("/bulkdata/BILLSTATUS/118/s/BILLSTATUS-118s1.xml",)


def test_senate_preparation_and_cap_profile_enforce_event_policy(tmp_path: Path) -> None:
    """The Stage-A adapter preserves original heads and reports policy exclusions."""
    raw = tmp_path / "raw"
    roster = tmp_path / "roster"
    processed = tmp_path / "processed"
    metadata = tmp_path / "metadata.json"
    policy = tmp_path / "policy.json"
    audit = tmp_path / "audit.md"
    raw.mkdir()
    roster.mkdir()
    write_xml(
        raw / "BILLSTATUS-118s1.xml",
        1,
        "A000001",
        [
            {"bioguide": "B000001", "original": "True", "withdrawal": "2024-01-03"},
            {"bioguide": "C000001", "original": "True"},
            {"bioguide": "D000001", "original": "False"},
        ],
    )
    write_xml(raw / "BILLSTATUS-118s2.xml", 2, "A000001", [])
    write_xml(
        raw / "BILLSTATUS-118s3.xml",
        3,
        "A000001",
        [{"bioguide": "A000001", "original": "True"}],
    )
    source_manifest = {
        "records": [
            {"filename": "BILLSTATUS-118s1.xml"},
            {"filename": "BILLSTATUS-118s2.xml"},
            {"filename": "BILLSTATUS-118s3.xml"},
        ]
    }
    (raw / "SOURCE_MANIFEST.json").write_text(json.dumps(source_manifest), encoding="utf-8")
    roster_rows = [
        roster_person(identifier) for identifier in ("A000001", "B000001", "C000001", "D000001")
    ]
    for filename, values in (
        ("legislators-current.json", roster_rows),
        ("legislators-historical.json", []),
    ):
        (roster / filename).write_text(json.dumps(values), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(PREPARE_DRIVER),
            "--raw-dir",
            str(raw),
            "--roster-dir",
            str(roster),
            "--processed-dir",
            str(processed),
            "--metadata-output",
            str(metadata),
            "--policy-output",
            str(policy),
            "--audit-output",
            str(audit),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    prepared = json.loads(metadata.read_text(encoding="utf-8"))
    accounting = prepared["event_construction"]
    assert accounting["valid_nonempty_head_event_records"] == 1
    assert accounting["zero_original_cosponsor_measures"] == 1
    assert accounting["excluded_sponsor_in_original_head"] == 1
    assert accounting["original_cosponsor_withdrawals_retained"] == 1
    assert prepared["primary_policy"]["nodes"] == 4
    events = pq.read_table(processed / "native_events.parquet").to_pylist()
    assert events[0]["tail_sponsor_bioguide"] == "A000001"
    assert events[0]["head_original_cosponsors_bioguide"] == ["B000001", "C000001"]
    assert len(rows(processed / "nodes.csv")) == 4
    assert len(pq.read_table(processed / "static_arcs.parquet").to_pylist()) == 2

    cap_output = tmp_path / "cap_gate"
    profile = subprocess.run(
        [
            sys.executable,
            str(CAP_DRIVER),
            "--events",
            str(processed / "native_events.parquet"),
            "--nodes",
            str(processed / "nodes.csv"),
            "--arcs",
            str(processed / "static_arcs.parquet"),
            "--caps",
            "1,2",
            "--output-dir",
            str(cap_output),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert profile.returncode == 0, profile.stderr
    cap_rows = rows(cap_output / "cap_profile.csv")
    assert [row["head_cap"] for row in cap_rows] == ["1", "2"]
    assert cap_rows[0]["retained_event_records"] == "0"
    assert cap_rows[1]["retained_event_records"] == "1"
    assert cap_rows[1]["sponsor_substitution_eligible_event_types"] == "1"


def test_sponsor_substitution_preserves_singleton_sponsor_grammar(tmp_path: Path) -> None:
    """The Senate hard panel emits no reversal and never creates multi-sponsor negatives."""
    nodes = tmp_path / "nodes.csv"
    with nodes.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["node"], lineterminator="\n")
        writer.writeheader()
        writer.writerows({"node": node} for node in ("A", "B", "C", "D"))
    split = tmp_path / "masks" / "mcar_replicate_1"
    split.mkdir(parents=True)
    event_fields = ["event_type_id", "tail_nodes_json", "head_nodes_json"]
    for filename, records in (
        (
            "observed_event_types.csv",
            [
                {"event_type_id": "e1", "tail_nodes_json": '["A"]', "head_nodes_json": '["B"]'},
                {"event_type_id": "e2", "tail_nodes_json": '["A"]', "head_nodes_json": '["C"]'},
            ],
        ),
        (
            "heldout_event_types.csv",
            [{"event_type_id": "e3", "tail_nodes_json": '["A"]', "head_nodes_json": '["B", "C"]'}],
        ),
    ):
        with (split / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=event_fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
    with (split / "observed_arcs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tail", "head"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(({"tail": "A", "head": "B"}, {"tail": "A", "head": "C"}))

    output = tmp_path / "hard"
    completed = subprocess.run(
        [
            sys.executable,
            str(HARD_DRIVER),
            "--mask-dir",
            str(tmp_path / "masks"),
            "--nodes",
            str(nodes),
            "--output-dir",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["hard_panel"] == "sponsor_substitution"
    assert "not evaluated" in manifest["reversal_orientation"]
    predictions = rows(
        output / "mcar_replicate_1" / "sponsor_substitution_candidate_predictions.csv"
    )
    assert {row["panel"] for row in predictions} == {"sponsor_substitution"}
    assert {row["tail_arity"] for row in predictions} == {"1"}
