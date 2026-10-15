#!/usr/bin/env python3
"""Build aggregate-only static-arc and formal-concept tables for the SNAM draft."""

from __future__ import annotations

import argparse
import json
import re
from hashlib import sha256
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "results" / "published" / "phase2_20261015"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "manuscript" / "snam" / "tables"

DATASETS = {
    "caviar": "CAVIAR full static",
    "enron": "Enron strict core",
    "eu_core": "EU-core",
    "mathoverflow": "MathOverflow core",
}
CONCEPT_AUDIT_DIRECTORIES = {
    "caviar": "caviar_full_static_formal_concepts_tail3_head3",
    "enron": "enron_formal_concepts_tail3_head3",
    "eu_core": "eu_core_formal_concepts_tail3_head3",
    "mathoverflow": "mathoverflow_formal_concepts_tail3_head3",
}
MODELS = ("M0", "M1", "M3", "M4c")
STATIC_HEURISTICS = {
    "common_neighbor_total": "Directed CN total",
    "adamic_adar_total": "Directed AA total",
}
CONCEPT_SCORES = {
    "lifted_cn_total_mean": "Directed CN total",
    "lifted_adamic_adar_total_mean": "Directed AA total",
}


def parse_args() -> argparse.Namespace:
    """Parse published aggregate inputs and a safe output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def require_file(path: Path) -> Path:
    """Return an existing file or stop before writing partial tables."""
    if not path.is_file():
        raise FileNotFoundError(f"missing aggregate input: {path}")
    return path


def file_digest(path: Path) -> str:
    """Return a SHA-256 digest for a declared aggregate input."""
    return sha256(path.read_bytes()).hexdigest()


def static_arc_scores(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    """Summarize the three-mask static conditional-score pilots without pooling."""
    rows: list[dict[str, object]] = []
    sources: list[Path] = []
    for dataset, label in DATASETS.items():
        heuristic_path = require_file(
            source_root / "phase2" / f"{dataset}_static_pilot" / "arc_lp_metrics.csv"
        )
        ergm_path = require_file(
            source_root / "models" / f"{dataset}_masked_ergm_plan" / "metrics.csv"
        )
        sources.extend([heuristic_path, ergm_path])
        heuristic = pd.read_csv(heuristic_path)
        for method, method_label in STATIC_HEURISTICS.items():
            selected = heuristic.loc[heuristic["method"] == method]
            if len(selected) != 3:
                raise ValueError(f"expected three static scores for {dataset}/{method}")
            rows.append(
                {
                    "dataset": label,
                    "method_family": "Directed local score",
                    "method": method_label,
                    "completed_masks": 3,
                    "pr_auc_mean": selected["pr_auc"].mean(),
                    "pr_auc_mask_sd": selected["pr_auc"].std(),
                    "roc_auc_mean": selected["roc_auc"].mean(),
                    "roc_auc_mask_sd": selected["roc_auc"].std(),
                }
            )
        frame = pd.read_csv(ergm_path)
        selected = frame.loc[
            frame["model"].isin(MODELS)
            & frame["metric"].isin(["pr_auc", "roc_auc"])
            & (frame["status"] == "calculated")
        ]
        for model in MODELS:
            model_rows = selected.loc[selected["model"] == model]
            if len(model_rows) != 6:
                raise ValueError(
                    f"expected three PR-AUC and three ROC-AUC values for {dataset}/{model}"
                )
            summary = model_rows.groupby("metric")["value"].agg(["mean", "std", "size"])
            if set(summary.index) != {"pr_auc", "roc_auc"} or set(summary["size"]) != {3}:
                raise ValueError(f"incomplete static score summaries for {dataset}/{model}")
            rows.append(
                {
                    "dataset": label,
                    "method_family": "ERGM conditional score",
                    "method": model,
                    "completed_masks": 3,
                    "pr_auc_mean": summary.loc["pr_auc", "mean"],
                    "pr_auc_mask_sd": summary.loc["pr_auc", "std"],
                    "roc_auc_mean": summary.loc["roc_auc", "mean"],
                    "roc_auc_mask_sd": summary.loc["roc_auc", "std"],
                }
            )
    return pd.DataFrame(rows), sources


def concept_scope(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    """Extract cap-first concept-section sizes from published audit summaries."""
    rows: list[dict[str, object]] = []
    sources: list[Path] = []
    patterns = {
        "nodes": r"Fixed node universe: `([0-9,]+)`",
        "arcs": r"Observed binary directed arcs: `([0-9,]+)`",
        "concepts": r"Concepts emitted: `([0-9,]+)`",
        "covered": r"Observed arcs covered by capped concept footprints: `([0-9,]+)/([0-9,]+)`",
    }
    for dataset, label in DATASETS.items():
        directory = CONCEPT_AUDIT_DIRECTORIES[dataset]
        path = require_file(source_root / "phase2" / directory / "summary.md")
        sources.append(path)
        text = path.read_text(encoding="utf-8")
        values: dict[str, tuple[str, ...] | str] = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match is None:
                raise ValueError(f"missing {key} in concept summary: {path}")
            values[key] = match.groups() if len(match.groups()) > 1 else match.group(1)
        covered, total = values["covered"]
        rows.append(
            {
                "dataset": label,
                "nodes": int(str(values["nodes"]).replace(",", "")),
                "directed_arcs": int(str(values["arcs"]).replace(",", "")),
                "tail_cap": 3,
                "head_cap": 3,
                "formal_concepts": int(str(values["concepts"]).replace(",", "")),
                "footprint_covered_arcs": int(covered.replace(",", "")),
                "footprint_coverage": int(covered.replace(",", "")) / int(total.replace(",", "")),
            }
        )
    return pd.DataFrame(rows), sources


def concept_recovery(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    """Summarize fixed-score, random-panel concept recovery pilot evidence."""
    rows: list[dict[str, object]] = []
    sources: list[Path] = []
    for dataset, label in DATASETS.items():
        path = require_file(
            source_root / "phase2" / f"{dataset}_concept_recovery" / "metric_summary.csv"
        )
        sources.append(path)
        frame = pd.read_csv(path)
        selected = frame.loc[
            (frame["panel"] == "random")
            & frame["score"].isin(CONCEPT_SCORES)
            & frame["metric"].isin(["pr_auc", "roc_auc"])
        ]
        for mechanism in ("mcar", "mnar_out"):
            for score, score_label in CONCEPT_SCORES.items():
                rows_for_score = selected.loc[
                    (selected["mechanism"] == mechanism) & (selected["score"] == score)
                ]
                if len(rows_for_score) != 2 or set(rows_for_score["metric"]) != {
                    "pr_auc",
                    "roc_auc",
                }:
                    raise ValueError(
                        f"incomplete concept score summary for {dataset}/{mechanism}/{score}"
                    )
                metrics = rows_for_score.set_index("metric")
                if set(metrics["completed_replicates"]) != {3}:
                    raise ValueError(
                        f"unexpected replicate count for {dataset}/{mechanism}/{score}"
                    )
                rows.append(
                    {
                        "dataset": label,
                        "mechanism": "MCAR" if mechanism == "mcar" else "MNAR-out",
                        "score": score_label,
                        "completed_masks": 3,
                        "pr_auc_mean": metrics.loc["pr_auc", "mean"],
                        "pr_auc_mask_sd": metrics.loc["pr_auc", "sd"],
                        "roc_auc_mean": metrics.loc["roc_auc", "mean"],
                        "roc_auc_mask_sd": metrics.loc["roc_auc", "sd"],
                    }
                )
    return pd.DataFrame(rows), sources


def write_table(path: Path, table: pd.DataFrame) -> None:
    """Write one CSV with consistent line endings and no index column."""
    table.to_csv(path, index=False, lineterminator="\n")


def main() -> None:
    """Build all plan-aligned aggregate-safe manuscript table inputs."""
    args = parse_args()
    source_root = args.source_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    builders = {
        "static_arc_score_pilot.csv": static_arc_scores,
        "formal_concept_scope.csv": concept_scope,
        "formal_concept_recovery.csv": concept_recovery,
    }
    source_paths: set[Path] = set()
    for filename, builder in builders.items():
        table, sources = builder(source_root)
        write_table(output_dir / filename, table)
        source_paths.update(sources)

    manifest_path = output_dir / "plan_aligned_tables_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "generator": "scripts/58_build_plan_aligned_tables.py",
                "privacy": (
                    "Aggregate-only manuscript inputs; no raw records or candidate-level "
                    "predictions."
                ),
                "outputs": sorted(builders),
                "sources": [
                    {"path": str(path.relative_to(PROJECT_ROOT)), "sha256": file_digest(path)}
                    for path in sorted(source_paths)
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Plan-aligned aggregate tables written: {output_dir}")
    print(f"Tables: {len(builders)}; source files: {len(source_paths)}")


if __name__ == "__main__":
    main()
