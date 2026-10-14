"""Integration test for the aggregate-only Enron timestamp policy audit."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "14_profile_enron_event_timestamps.py"


def load_driver():
    """Load the standalone driver so local test paths can be injected."""
    spec = importlib.util.spec_from_file_location("enron_timestamp_profile", DRIVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_timestamp_profile_reports_aggregate_year_and_month_counts(
    tmp_path: Path, monkeypatch
) -> None:
    """The audit must report an unfiltered temporal distribution without identifiers."""
    module = load_driver()
    event_table = tmp_path / "native_events.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {"sent_at_utc": datetime(2000, 1, 2, tzinfo=UTC)},
                {"sent_at_utc": datetime(2000, 1, 31, tzinfo=UTC)},
                {"sent_at_utc": datetime(2001, 2, 1, tzinfo=UTC)},
            ]
        ),
        event_table,
    )
    summary = tmp_path / "metadata" / "summary.json"
    years = tmp_path / "metadata" / "years.csv"
    months = tmp_path / "metadata" / "months.csv"
    report = tmp_path / "audit.md"
    monkeypatch.setattr(module, "INPUT", event_table)
    monkeypatch.setattr(module, "SUMMARY", summary)
    monkeypatch.setattr(module, "YEAR_COUNTS", years)
    monkeypatch.setattr(module, "MONTH_COUNTS", months)
    monkeypatch.setattr(module, "REPORT", report)
    monkeypatch.setattr(module, "OUTPUTS", (summary, years, months, report))
    monkeypatch.setattr(module, "EXPECTED_EVENTS", 3)
    monkeypatch.setattr(sys, "argv", [str(DRIVER), "--overwrite"])

    module.main()

    payload = json.loads(summary.read_text(encoding="utf-8"))
    assert payload["address_level_events_profiled"] == 3
    assert payload["calendar_year_counts"] == {"2000": 2, "2001": 1}
    assert payload["calendar_month_count"] == 2
    assert "No timestamp range has been selected" in payload["policy_status"]
    assert "2000,2" in years.read_text(encoding="utf-8")
    assert "2001-02,1" in months.read_text(encoding="utf-8")
    assert "select a study period" in report.read_text(encoding="utf-8")
