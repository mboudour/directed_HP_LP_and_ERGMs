"""Integration tests for the no-event MathOverflow reconstruction profile."""

# ruff: noqa: E501

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "scripts" / "43_profile_mathoverflow_reconstruction.py"


def write_posts(path: Path) -> None:
    """Create questions, a duplicate answerer, a late answer, and excluded records."""
    path.write_text(
        """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<posts>
<row Id=\"1\" PostTypeId=\"1\" OwnerUserId=\"10\" CreationDate=\"2024-01-01T00:00:00.000\" />
<row Id=\"2\" PostTypeId=\"1\" CreationDate=\"2024-01-01T00:00:00.000\" />
<row Id=\"3\" PostTypeId=\"1\" OwnerUserId=\"20\" CreationDate=\"2024-01-01T00:00:00.000\" />
<row Id=\"11\" PostTypeId=\"2\" ParentId=\"1\" OwnerUserId=\"11\" CreationDate=\"2024-01-02T00:00:00.000\" />
<row Id=\"12\" PostTypeId=\"2\" ParentId=\"1\" OwnerUserId=\"11\" CreationDate=\"2024-01-03T00:00:00.000\" />
<row Id=\"13\" PostTypeId=\"2\" ParentId=\"1\" OwnerUserId=\"12\" CreationDate=\"2024-01-11T00:00:00.000\" />
<row Id=\"14\" PostTypeId=\"2\" ParentId=\"2\" OwnerUserId=\"13\" CreationDate=\"2024-01-02T00:00:00.000\" />
<row Id=\"15\" PostTypeId=\"2\" ParentId=\"3\" OwnerUserId=\"20\" CreationDate=\"2024-01-02T00:00:00.000\" />
<row Id=\"16\" PostTypeId=\"2\" ParentId=\"1\" CreationDate=\"2024-01-02T00:00:00.000\" />
<row Id=\"17\" PostTypeId=\"2\" OwnerUserId=\"14\" CreationDate=\"2024-01-02T00:00:00.000\" />
</posts>
""",
        encoding="utf-8",
    )


def command(posts: Path, summary: Path, report: Path, *extra: str) -> list[str]:
    """Build an explicit temporary-fixture profiling command."""
    return [
        sys.executable,
        str(DRIVER),
        "--input",
        str(posts),
        "--summary",
        str(summary),
        "--report",
        str(report),
        "--windows-days",
        "1,7,30",
        *extra,
    ]


def test_profile_reports_window_and_duplicate_answerer_evidence(tmp_path: Path) -> None:
    """The no-event profiler reports deterministic eligible-pair window profiles."""
    posts = tmp_path / "Posts.xml"
    summary_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"
    write_posts(posts)

    completed = subprocess.run(
        command(posts, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "MathOverflow reconstruction profile passed." in completed.stdout

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert (
        summary["reconstruction_status"] == "profile_only_policy_unapproved_no_events_materialized"
    )
    assert summary["questions"]["eligible_with_owner_and_valid_timestamp"] == 2
    assert summary["questions"]["missing_owner"] == 1
    assert summary["answers"]["total"] == 7
    assert summary["answers"]["missing_owner"] == 1
    assert summary["answers"]["missing_parent"] == 1
    assert summary["answers"]["parent_not_eligible_question"] == 1
    assert summary["answers"]["answerer_is_asker"] == 1
    assert summary["answers"]["duplicate_eligible_answer_records"] == 1
    assert summary["answers"]["distinct_question_answerer_pairs"] == 2

    profiles = {row["answer_window_days"]: row for row in summary["window_profiles"]}
    assert profiles[1]["distinct_question_answerer_pairs"] == 1
    assert profiles[1]["questions_with_two_or_more_answerers"] == 0
    assert profiles[30]["distinct_question_answerer_pairs"] == 2
    assert profiles[30]["questions_with_two_or_more_answerers"] == 1
    assert "does not approve an" in report_path.read_text(encoding="utf-8")


def test_profile_requires_explicit_overwrite(tmp_path: Path) -> None:
    """Existing descriptive output cannot silently mix parameter choices."""
    posts = tmp_path / "Posts.xml"
    summary_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"
    write_posts(posts)
    first = subprocess.run(
        command(posts, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert first.returncode == 0, first.stderr
    blocked = subprocess.run(
        command(posts, summary_path, report_path),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert blocked.returncode != 0
    assert "reconstruction-profile output already exists" in blocked.stderr
    rerun = subprocess.run(
        command(posts, summary_path, report_path, "--overwrite"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert rerun.returncode == 0, rerun.stderr
