"""Source-level contract for the bounded btergm driver; modeling packages not needed."""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DRIVER = PROJECT_ROOT / "r" / "models" / "temporal_btergm_ladder.R"
R_TEST = PROJECT_ROOT / "r" / "tests" / "test_temporal_btergm_ladder.R"


def test_temporal_btergm_source_contract() -> None:
    """Pin the named models, fixed directed terms, defaults, and no-forecast engine."""
    source = DRIVER.read_text(encoding="utf-8")
    assert 'c("T_tt", "T0", "T1", "T2", "T2_minus_H")' in source
    for term in (
        "edges + edgecov(lag_total_CN)",
        "memory(type='autoregression', lag=1)",
        "delrecip(lag=1)",
        "edgecov(lag_oi)",
        "edgecov(lag_oo)",
        "edgecov(lag_ii)",
        "edgecov(lag_outdegree_source)",
        "edgecov(lag_indegree_target)",
        "gwodegree(",
        "gwidegree(",
        "fixed=TRUE",
        'c("OTP", "OSP", "ISP")',
    ):
        assert term in source
    for default in (
        '"bootstrap-reps" = "20"',
        '"degree-decay" = "0.5"',
        '"esp-decay" = "0.5"',
        'models = "all"',
        'parallel = "no"',
        'ncpus = "1"',
    ):
        assert default in source
    assert 'colClasses = "character"' in source
    assert "any(diff(positions) != 1)" in source
    assert "lag <- panels[[time - 1L]]" in source
    assert "oi <- lag %*% lag" in source
    assert "oo <- lag %*% t(lag)" in source
    assert "ii <- t(lag) %*% lag" in source
    assert "btergm::btergm(formula, R = config" in source
    assert "ncpus = config$ncpus, verbose = FALSE" in source
    assert "fit@boot$t" in source
    assert 'methods::slot(fit, "boot")$t' not in source
    assert 'stats::confint(fit, level = 0.95, type = "perc", invlogit = FALSE)' in source
    assert 'c("btergm", "network", "jsonlite")' in source
    assert "failure_missing_packages" in source
    assert "never forecasts; no simulated probabilities" in source
    assert "temporal bootstrap is an estimator, not a competitor" in source
    assert not re.search(r"\b(?:predict|simulate|gof|mtergm|tbergm)\s*\(", source)
    assert not re.search(r"(?<![\w])(?:ergm|tergm|mtergm|tbergm)::", source)
    for artifact in (
        "model_specs.csv",
        "model_status.csv",
        "coefficients.csv",
        "input_summary.csv",
        "lag_alignment.csv",
        "run_manifest.json",
    ):
        assert artifact in source


def test_temporal_btergm_base_r_contract() -> None:
    """Exercise all pure helpers without installing btergm/network/jsonlite."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        pytest.skip("Rscript not installed; source contract remains available")
    completed = subprocess.run(
        [rscript, str(R_TEST)], cwd=PROJECT_ROOT, capture_output=True, text=True, check=False
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "base R only" in completed.stdout


def test_temporal_btergm_validation_failure_manifest(tmp_path: Path) -> None:
    """A missing consecutive period must fail before modeling, without packages."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        pytest.skip("Rscript not installed")
    nodes = tmp_path / "nodes.csv"
    panel = tmp_path / "panel.csv"
    output = tmp_path / "out"
    nodes.write_text("id\n001\n002\n", encoding="utf-8")
    panel.write_text("time,from,to\n001,001,002\n003,002,001\n", encoding="utf-8")
    completed = subprocess.run(
        [rscript, str(DRIVER), f"--input={panel}", f"--nodes={nodes}", f"--output-dir={output}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failure_validation_or_runtime"
    assert "exact consecutive periods" in manifest["message"]
    assert manifest["forecasts"] is False
    assert manifest["simulated_probabilities"] is False
    assert "failure_validation_or_runtime" in (output / "model_status.csv").read_text(
        encoding="utf-8"
    )


def test_temporal_btergm_missing_package_manifest(tmp_path: Path) -> None:
    """Missing dependencies must never be disguised as fitted coefficients."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        pytest.skip("Rscript not installed")
    probe = subprocess.run(
        [
            rscript,
            "-e",
            'p <- c("btergm","network","jsonlite"); '
            'cat(p[!vapply(p, requireNamespace, logical(1), quietly=TRUE)], sep=",")',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    package_names = ("btergm", "network", "jsonlite")
    # renv may emit a status notice before the comma-delimited probe result.
    # Retain only the requested package names, in the probe's declared order.
    missing = [package for package in package_names if package in probe.stdout]
    if not missing:
        pytest.skip("All modeling packages are installed; this is the missing-package test")
    nodes = tmp_path / "nodes.csv"
    panel = tmp_path / "panel.csv"
    output = tmp_path / "out"
    nodes.write_text("id\n001\n002\n003\n", encoding="utf-8")
    panel.write_text("time,from,to\n001,001,002\n002,002,001\n", encoding="utf-8")
    completed = subprocess.run(
        [rscript, str(DRIVER), f"--input={panel}", f"--nodes={nodes}", f"--output-dir={output}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failure_missing_packages"
    assert manifest["missing_packages"] == missing
    assert manifest["forecasts"] is False
    with (output / "coefficients.csv").open(encoding="utf-8", newline="") as handle:
        assert list(csv.DictReader(handle)) == []
    with (output / "model_status.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["model"] for row in rows] == ["T_tt", "T0", "T1", "T2", "T2_minus_H"]
    assert all(row["status"] == "failure_missing_packages" for row in rows)
    with (output / "input_summary.csv").open(encoding="utf-8", newline="") as handle:
        summary = next(csv.DictReader(handle))
    assert summary["nodes"] == "3"
    assert summary["panels"] == "2"
    assert summary["first_time"] == "001"


def test_temporal_btergm_output_protection(tmp_path: Path) -> None:
    """An invalid rerun without overwrite cannot replace a previous manifest."""
    rscript = shutil.which("Rscript")
    if rscript is None:
        pytest.skip("Rscript not installed")
    output = tmp_path / "out"
    output.mkdir()
    manifest_path = output / "run_manifest.json"
    original = '{"status":"previous_run"}\n'
    manifest_path.write_text(original, encoding="utf-8")
    completed = subprocess.run(
        [rscript, str(DRIVER), "--input=missing", "--nodes=missing", f"--output-dir={output}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "Output directory is non-empty" in completed.stderr
    assert manifest_path.read_text(encoding="utf-8") == original
