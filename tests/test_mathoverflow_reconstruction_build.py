"""Integration tests for approved MathOverflow reconstructed-event materialization."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "24_prepare_mathoverflow.py"


def write_posts(path: Path) -> None:
    """Write a compact Stack Exchange post fixture with one valid group event."""
    path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<posts>
<row Id="1" PostTypeId="1" OwnerUserId="10" CreationDate="2024-01-01T00:00:00.000" />
<row Id="2" PostTypeId="1" CreationDate="2024-01-01T00:00:00.000" />
<row Id="11" PostTypeId="2" ParentId="1" OwnerUserId="11" CreationDate="2024-01-02T00:00:00.000" />
<row Id="12" PostTypeId="2" ParentId="1" OwnerUserId="11" CreationDate="2024-01-03T00:00:00.000" />
<row Id="13" PostTypeId="2" ParentId="1" OwnerUserId="12" CreationDate="2024-01-11T00:00:00.000" />
<row Id="14" PostTypeId="2" ParentId="2" OwnerUserId="13" CreationDate="2024-01-02T00:00:00.000" />
<row Id="15" PostTypeId="2" ParentId="1" OwnerUserId="10" CreationDate="2024-01-02T00:00:00.000" />
</posts>
""",
        encoding="utf-8",
    )


def approved_policy(path: Path) -> None:
    """Write the exact policy contract required by the production builder."""
    path.write_text(
        json.dumps(
            {
                "approved": True,
                "answer_window_days": 30,
                "policies": {
                    "comments": "excluded",
                    "anonymous_user": "exclude",
                    "duplicate_answerer": "collapse_per_question",
                    "deleted_post": "retain_rows_present_in_public_dump",
                },
            }
        ),
        encoding="utf-8",
    )


def load_driver():
    """Load a fresh module so each fixture has isolated path settings."""
    spec = importlib.util.spec_from_file_location("prepare_mathoverflow_fixture", DRIVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def configure(module, tmp_path: Path) -> tuple[Path, Path, Path]:
    """Redirect all local data and outputs to the temporary fixture directory."""
    posts = tmp_path / "Posts.xml"
    gate = tmp_path / "policy.json"
    work_dir = tmp_path / "interim"
    output = tmp_path / "processed" / "native_events.parquet"
    audit_summary = tmp_path / "audit.json"
    audit_report = tmp_path / "audit.md"
    reconstruction_summary = tmp_path / "reconstruction.json"
    reconstruction_report = tmp_path / "reconstruction.md"
    write_posts(posts)
    approved_policy(gate)

    module.INPUT = posts
    module.GATE = gate
    module.WORK_DIR = work_dir
    module.QUESTION_DB = work_dir / "questions.sqlite"
    module.OUTPUT = output
    module.TEMP_OUTPUT = output.with_suffix(".parquet.tmp")
    module.AUDIT_SUMMARY = audit_summary
    module.AUDIT_REPORT = audit_report
    module.RECONSTRUCTION_SUMMARY = reconstruction_summary
    module.RECONSTRUCTION_REPORT = reconstruction_report
    return audit_summary, audit_report, reconstruction_summary


def test_approved_build_preserves_audit_and_materializes_distinct_answerers(tmp_path: Path) -> None:
    """An approved build uses its own outputs and keeps the prior audit intact."""
    module = load_driver()
    audit_summary, audit_report, reconstruction_summary = configure(module, tmp_path)

    module.audit(build_events=False, overwrite=False)
    module.audit(build_events=True, overwrite=False)

    assert audit_summary.is_file()
    assert audit_report.is_file()
    summary = json.loads(reconstruction_summary.read_text(encoding="utf-8"))
    assert summary["analysis_status"] == "reconstructed_events_built_after_approved_policy"
    assert summary["answer_window_days"] == 30
    assert summary["accepted_answers_within_window"] == 3
    assert summary["reconstructed_events"] == 1

    rows = pq.read_table(module.OUTPUT).to_pylist()
    assert rows == [
        {
            "event_id": "mathoverflow:1:window_30d",
            "question_id": "1",
            "question_created_at": "2024-01-01T00:00:00.000",
            "answer_window_days": 30,
            "tail_answerers": ["11", "12"],
            "head_asker": "10",
            "construction": "reconstructed_distinct_answerers_to_asker",
        }
    ]


def test_approved_build_requires_explicit_overwrite(tmp_path: Path) -> None:
    """A completed approved build is only replaced with a deliberate overwrite."""
    module = load_driver()
    configure(module, tmp_path)
    module.audit(build_events=True, overwrite=False)
    try:
        module.audit(build_events=True, overwrite=False)
    except SystemExit as error:
        assert "output already exists" in str(error)
    else:
        raise AssertionError("Expected a completed build to require --overwrite")
    module.audit(build_events=True, overwrite=True)
