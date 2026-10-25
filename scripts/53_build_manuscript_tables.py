#!/usr/bin/env python3
"""Build aggregate-only manuscript tables from the published Phase 2 bundle.

The script intentionally reads only Git-tracked metadata and aggregate result
outputs. It never reads raw data, address maps, per-event predictions, or
candidate-level panels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = PROJECT_ROOT / "results" / "published" / "phase2_20261015"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "manuscript" / "tables"

DATASET_LABELS = {
    "enron_20150507": "Enron strict custodian core",
    "email_eu_core_temporal": "EU-core",
    "caviar": "CAVIAR full matrix",
    "ciel": "Ciel",
    "jmail_v1_2026_02": "Jmail v1",
    "mathoverflow_stackexchange_2024": "MathOverflow reconstructed core",
    "senate_118_s_bills": "U.S. Senate 118th Congress",
}

MECHANISM_LABELS = {"mcar": "MCAR", "mnar_out": "MNAR-out"}
PANEL_LABELS = {
    "random": "Random arity-matched",
    "reversal_orientation": "Reversal/orientation",
    "role_exchange": "Role exchange",
}
SCORE_LABELS = {
    "already_observed_footprint": "Already-observed footprint",
    "lifted_adamic_adar_total_mean": "Directed Adamic-Adar total",
    "lifted_reverse_arc_mean": "Reverse-arc mean",
    "lifted_degree_product_mean": "Degree-product mean",
}

GATE_ROWS = [
    {
        "gate": "Data provenance and target eligibility",
        "status": "Passed with scope restrictions",
        "consequence": (
            "Enron and MathOverflow support native-event targets; EU-core is temporal "
            "dyadic; CAVIAR is static full-matrix only."
        ),
    },
    {
        "gate": "Target representation",
        "status": "Passed as diagnostic",
        "consequence": "Formal concepts remain a derived target distinct from recorded events.",
    },
    {
        "gate": "Higher-order ERGM MCMC feasibility",
        "status": "Not passed for primary claim",
        "consequence": (
            "No Enron MCMC-derived L3 result; M4 MPLE joint score is supplementary only."
        ),
    },
    {
        "gate": "NHP-D neural reproduction",
        "status": "Not passed",
        "consequence": "No neural benchmark result is admitted.",
    },
    {
        "gate": "Chronological analysis",
        "status": "Bounded diagnostic only",
        "consequence": "No forecasting, STERGM, or RHEM claim belongs to Paper 1.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help="Published Phase 2 aggregate-output bundle.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination for manuscript-safe CSV, Markdown, and manifest outputs.",
    )
    return parser.parse_args()


def relative_to_project(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"required aggregate source is missing: {path}")
    return path


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(require_file(path))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_value(value: Any) -> str:
    if pd.isna(value):
        return "—"
    if isinstance(value, float):
        if 0 < abs(value) < 0.0001:
            return f"{value:.2e}"
        return f"{value:.4f}"
    return str(value)


def markdown_table(frame: pd.DataFrame) -> str:
    display = frame.map(format_value)
    headers = [str(column).replace("_", " ") for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in display.itertuples(index=False, name=None):
        values = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def write_table(output_dir: Path, stem: str, frame: pd.DataFrame, note: str) -> list[Path]:
    csv_path = output_dir / f"{stem}.csv"
    markdown_path = output_dir / f"{stem}.md"
    frame.to_csv(csv_path, index=False)
    markdown_path.write_text(
        f"# {stem.replace('_', ' ').title()}\n\n{note}\n\n{markdown_table(frame)}"
    )
    return [csv_path, markdown_path]


def dataset_eligibility_table(registry_path: Path) -> pd.DataFrame:
    registry = yaml.safe_load(require_file(registry_path).read_text())
    rows: list[dict[str, str]] = []
    for dataset_id, payload in registry["datasets"].items():
        status = payload["status"].replace("_", " ")
        targets = ", ".join(payload["static_targets"])
        native = payload.get("native_event_policy", "not stated").replace("_", " ")
        temporal = payload.get("temporal_panels", payload.get("temporal_phase_policy", "none"))
        if isinstance(temporal, dict):
            temporal = ", ".join(f"{key}={value}" for key, value in temporal.items())
        rows.append(
            {
                "dataset": DATASET_LABELS[dataset_id],
                "phase_2_status": status,
                "admissible_targets": targets,
                "native_event_policy": native,
                "temporal_role": str(temporal).replace("_", " "),
                "gate": str(payload.get("hard_gate", "none")).replace("_", " "),
            }
        )
    return pd.DataFrame(rows)


def fidelity_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    paths = sorted(
        (source_root / "phase2").glob("*_native_event_fidelity_tail3_head3/summary.json")
    )
    if len(paths) != 2:
        raise ValueError(f"expected two native-event fidelity summaries, found {len(paths)}")
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(require_file(path).read_text())
        equality = payload["exact_tail_head_equality"]
        footprint = payload["footprint_agreement"]
        rows.append(
            {
                "dataset": DATASET_LABELS[payload["dataset_id"]],
                "nodes": payload["fixed_node_universe"],
                "static_arcs": payload["static_arcs"],
                "native_event_types": payload["native_events"]["cap_eligible_event_types"],
                "formal_concepts": payload["formal_concepts"]["count"],
                "exact_tail_head_matches": equality["matching_pairs"],
                "concept_precision": equality["concept_precision"],
                "native_type_recall": equality["native_event_type_recall"],
                "footprint_jaccard": footprint["jaccard"],
                "native_footprint_covered_by_concepts": footprint[
                    "native_event_footprint_covered_by_concepts"
                ],
                "concept_footprint_covered_by_native_events": footprint[
                    "formal_concept_footprint_covered_by_native_events"
                ],
            }
        )
    return pd.DataFrame(rows), paths


def primary_random_panel_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[pd.DataFrame] = []
    sources: list[Path] = []
    for key, dataset_id in (
        ("enron", "enron_20150507"),
        ("mathoverflow", "mathoverflow_stackexchange_2024"),
    ):
        heuristic_path = (
            source_root / "phase2" / f"{key}_event_first_native_heuristics" / "metric_summary.csv"
        )
        ergm_path = (
            source_root / "models" / f"{key}_native_event_ergm_footprints" / "metric_summary.csv"
        )
        heuristic = read_csv(heuristic_path)
        ergm = read_csv(ergm_path)
        sources.extend([heuristic_path, ergm_path])
        heuristic = heuristic[
            (heuristic["metric"] == "pr_auc")
            & heuristic["score"].isin(
                [
                    "already_observed_footprint",
                    "lifted_adamic_adar_total_mean",
                    "lifted_reverse_arc_mean",
                ]
            )
        ].copy()
        heuristic["dataset"] = DATASET_LABELS[dataset_id]
        heuristic["panel"] = PANEL_LABELS["random"]
        heuristic["score_family"] = "Directed heuristic"
        heuristic["method"] = heuristic["score"].map(SCORE_LABELS)
        ergm = ergm[
            (ergm["panel"] == "random")
            & (ergm["metric"] == "pr_auc")
            & (ergm["model"].isin(["M0", "M4c"]))
            & (ergm["score"].isin(["L1", "L1g"]))
        ].copy()
        ergm = ergm[
            ((ergm["model"] == "M0") & (ergm["score"] == "L1"))
            | ((ergm["model"] == "M4c") & (ergm["score"] == "L1g"))
        ]
        ergm["dataset"] = DATASET_LABELS[dataset_id]
        ergm["panel"] = PANEL_LABELS["random"]
        ergm["score_family"] = "ERGM conditional footprint"
        ergm["method"] = ergm["model"] + "::" + ergm["score"]
        rows.extend(
            [
                heuristic[
                    [
                        "dataset",
                        "mechanism",
                        "panel",
                        "score_family",
                        "method",
                        "completed_replicates",
                        "mean",
                        "sd",
                    ]
                ],
                ergm[
                    [
                        "dataset",
                        "mechanism",
                        "panel",
                        "score_family",
                        "method",
                        "completed_replicates",
                        "mean",
                        "sd",
                    ]
                ],
            ]
        )
    table = pd.concat(rows, ignore_index=True)
    table["mechanism"] = table["mechanism"].map(MECHANISM_LABELS)
    table = table.rename(columns={"mean": "pr_auc_mean", "sd": "mask_sd"})
    return table.sort_values(["dataset", "mechanism", "score_family", "method"]).reset_index(
        drop=True
    ), sources


def hard_panel_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[pd.DataFrame] = []
    sources: list[Path] = []
    selected_heuristics = ["lifted_adamic_adar_total_mean", "lifted_reverse_arc_mean"]
    for key, dataset_id in (
        ("enron", "enron_20150507"),
        ("mathoverflow", "mathoverflow_stackexchange_2024"),
    ):
        heuristic_path = (
            source_root / "phase2" / f"{key}_event_first_native_hard_panels" / "metric_summary.csv"
        )
        ergm_path = (
            source_root / "models" / f"{key}_native_event_ergm_footprints" / "metric_summary.csv"
        )
        heuristic = read_csv(heuristic_path)
        ergm = read_csv(ergm_path)
        sources.extend([heuristic_path, ergm_path])
        heuristic = heuristic[
            (heuristic["metric"] == "pr_auc") & heuristic["score"].isin(selected_heuristics)
        ].copy()
        heuristic["dataset"] = DATASET_LABELS[dataset_id]
        heuristic["score_family"] = "Directed heuristic"
        heuristic["method"] = heuristic["score"].map(SCORE_LABELS)
        ergm = ergm[
            (ergm["panel"].isin(["reversal_orientation", "role_exchange"]))
            & (ergm["metric"] == "pr_auc")
            & (
                ((ergm["model"] == "M0") & (ergm["score"] == "L1"))
                | ((ergm["model"] == "M4c") & (ergm["score"] == "L1g"))
            )
        ].copy()
        ergm["dataset"] = DATASET_LABELS[dataset_id]
        ergm["score_family"] = "ERGM conditional footprint"
        ergm["method"] = ergm["model"] + "::" + ergm["score"]
        rows.extend(
            [
                heuristic[
                    [
                        "dataset",
                        "panel",
                        "mechanism",
                        "score_family",
                        "method",
                        "completed_replicates",
                        "mean",
                        "sd",
                    ]
                ],
                ergm[
                    [
                        "dataset",
                        "panel",
                        "mechanism",
                        "score_family",
                        "method",
                        "completed_replicates",
                        "mean",
                        "sd",
                    ]
                ],
            ]
        )
    table = pd.concat(rows, ignore_index=True)
    table["panel"] = table["panel"].map(PANEL_LABELS)
    table["mechanism"] = table["mechanism"].map(MECHANISM_LABELS)
    table = table.rename(columns={"mean": "pr_auc_mean", "sd": "mask_sd"})
    return table.sort_values(
        ["dataset", "panel", "mechanism", "score_family", "method"]
    ).reset_index(drop=True), sources


def role_assignment_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[pd.DataFrame] = []
    sources: list[Path] = []
    selected_scores = [
        "already_observed_footprint",
        "lifted_adamic_adar_total_mean",
        "lifted_reverse_arc_mean",
        "lifted_degree_product_mean",
    ]
    for key, dataset_id in (
        ("enron", "enron_20150507"),
        ("mathoverflow", "mathoverflow_stackexchange_2024"),
    ):
        path = (
            source_root
            / "phase2"
            / f"{key}_native_event_role_assignment"
            / "metric_summary_by_arity.csv"
        )
        frame = read_csv(path)
        sources.append(path)
        frame = frame[
            (frame["metric"] == "top1_accuracy") & frame["score"].isin(selected_scores)
        ].copy()
        frame["weighted_total"] = frame["mean"] * frame["event_evaluations"]
        grouped = (
            frame.groupby(["mechanism", "score"], as_index=False)
            .agg(
                event_evaluations=("event_evaluations", "sum"),
                weighted_total=("weighted_total", "sum"),
            )
            .assign(top1_accuracy=lambda data: data["weighted_total"] / data["event_evaluations"])
        )
        grouped["dataset"] = DATASET_LABELS[dataset_id]
        grouped["method"] = grouped["score"].map(SCORE_LABELS)
        rows.append(
            grouped[["dataset", "mechanism", "method", "event_evaluations", "top1_accuracy"]]
        )
    table = pd.concat(rows, ignore_index=True)
    table["mechanism"] = table["mechanism"].map(MECHANISM_LABELS)
    return table.sort_values(["dataset", "mechanism", "method"]).reset_index(drop=True), sources


def paired_ergm_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[pd.DataFrame] = []
    sources: list[Path] = []
    for key in ("enron", "mathoverflow"):
        path = (
            source_root
            / "models"
            / f"{key}_native_ergm_paired_uncertainty"
            / "paired_differences.csv"
        )
        frame = read_csv(path)
        sources.append(path)
        selected = frame[
            (frame["comparison_method"] == "M4c::L1g")
            & (frame["reference_method"] == "M0::L1")
            & (frame["panel"] == "random")
            & (frame["metric"] == "pr_auc")
        ].copy()
        if len(selected) != 2:
            raise ValueError(f"expected MCAR and MNAR-out paired contrasts in {path}")
        rows.append(selected)
    table = pd.concat(rows, ignore_index=True)
    table["dataset"] = table["dataset_id"].map(DATASET_LABELS)
    table["mechanism"] = table["mechanism"].map(MECHANISM_LABELS)
    table["contrast"] = table["comparison_method"] + " − " + table["reference_method"]
    table["p_value_resolution"] = "1 / 20,001"
    table = table[
        [
            "dataset",
            "mechanism",
            "contrast",
            "paired_masks",
            "mean_difference",
            "bootstrap_ci_low",
            "bootstrap_ci_high",
            "paired_sign_flip_p_value",
            "bootstrap_reps",
            "permutation_reps",
            "p_value_resolution",
        ]
    ]
    return table.sort_values(["dataset", "mechanism"]).reset_index(drop=True), sources


def temporal_diagnostic_table(source_root: Path) -> tuple[pd.DataFrame, list[Path]]:
    rows: list[dict[str, Any]] = []
    sources: list[Path] = []
    for key, dataset_label in (
        ("enron", DATASET_LABELS["enron_20150507"]),
        ("eu_core", DATASET_LABELS["email_eu_core_temporal"]),
    ):
        lagged_status_path = (
            source_root / "models" / f"{key}_temporal_lagged" / "factorized_model_status.csv"
        )
        feature_path = source_root / "models" / f"{key}_temporal_lagged" / "feature_summary.csv"
        btergm_path = source_root / "models" / f"{key}_temporal_btergm_v3" / "model_status.csv"
        panel_path = source_root / "models" / f"{key}_temporal_btergm_v3" / "panel_summary.csv"
        lagged_status = read_csv(lagged_status_path)
        features = read_csv(feature_path)
        btergm_status = read_csv(btergm_path)
        panels = read_csv(panel_path)
        sources.extend([lagged_status_path, feature_path, btergm_path, panel_path])
        successful_lagged_models = (lagged_status["status"] == "fit_succeeded").sum()
        rows.append(
            {
                "dataset": dataset_label,
                "nodes": int(features.loc[0, "nodes"]),
                "panels": int(features.loc[0, "panels"]),
                "transitions": int(features.loc[0, "transitions"]),
                "factorized_lagged_models": (
                    f"{successful_lagged_models}/{len(lagged_status)} succeeded"
                ),
                "btergm_models": "; ".join(
                    f"{row.model}: {row.status}" for row in btergm_status.itertuples(index=False)
                ),
                "response_panels": int(btergm_status["response_panels"].max()),
                "bootstrap_reps": int(btergm_status["bootstrap_reps"].max()),
                "temporal_interpretation": (
                    "Bounded MPLE conditional-score diagnostic; never forecasting"
                ),
                "panel_time_labels": ", ".join(str(value) for value in panels["time"]),
            }
        )
    return pd.DataFrame(rows), sources


def write_readme(output_dir: Path, generated_files: list[Path]) -> Path:
    readme_path = output_dir / "README.md"
    filenames = "\n".join(f"- `{path.name}`" for path in sorted(generated_files))
    readme_path.write_text(
        "# Manuscript-safe aggregate tables\n\n"
        "These files are generated by `scripts/53_build_manuscript_tables.py` from "
        "the published aggregate Phase 2 bundle. They contain no raw records, actor "
        "identifiers, address maps, candidate-level predictions, or message contents.\n\n"
        "The Markdown versions are review aids; the CSV versions retain the numerical "
        "inputs for later journal-specific formatting. Generated files:\n\n"
        f"{filenames}\n"
    )
    return readme_path


def main() -> None:
    args = parse_args()
    source_root = args.source_root.resolve()
    output_dir = args.output_dir.resolve()
    registry_path = PROJECT_ROOT / "configs" / "datasets.yaml"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    tables_and_sources: list[tuple[str, pd.DataFrame, str, list[Path]]] = []
    tables_and_sources.append(
        (
            "table_01_dataset_target_eligibility",
            dataset_eligibility_table(registry_path),
            (
                "Dataset registry used to define paper scope. Statuses are eligibility "
                "labels, not performance rankings."
            ),
            [registry_path],
        )
    )
    fidelity, fidelity_sources = fidelity_table(source_root)
    tables_and_sources.append(
        (
            "table_02_concept_event_fidelity",
            fidelity,
            (
                "Cap-first concept/native-event fidelity audit. Footprint overlap is not "
                "event recovery."
            ),
            fidelity_sources,
        )
    )
    random_panel, random_sources = primary_random_panel_table(source_root)
    tables_and_sources.append(
        (
            "table_03a_primary_native_random_panel_pr_auc",
            random_panel,
            (
                "Primary 30-mask random arity-matched native-event panels. PR-AUC is a "
                "ranking metric for the stated balanced candidate panel."
            ),
            random_sources,
        )
    )
    hard_panels, hard_sources = hard_panel_table(source_root)
    tables_and_sources.append(
        (
            "table_03b_primary_native_hard_panel_pr_auc",
            hard_panels,
            (
                "Primary 30-mask directed hard panels. These selected predeclared score "
                "rows must not be treated as a post-hoc overall winner table."
            ),
            hard_sources,
        )
    )
    role_assignment, role_sources = role_assignment_table(source_root)
    tables_and_sources.append(
        (
            "table_03c_primary_native_role_assignment",
            role_assignment,
            (
                "Weighted top-1 role-assignment accuracy across the fixed arity strata. "
                "Candidate partitions preserve each event's known actor set and role arities."
            ),
            role_sources,
        )
    )
    paired, paired_sources = paired_ergm_table(source_root)
    tables_and_sources.append(
        (
            "table_04_paired_ergm_random_panel_pr_auc",
            paired,
            (
                "Predeclared paired random-panel contrast. Bootstrap and sign-flip "
                "calculations resample whole frozen masks within dataset only."
            ),
            paired_sources,
        )
    )
    temporal, temporal_sources = temporal_diagnostic_table(source_root)
    tables_and_sources.append(
        (
            "table_05_bounded_temporal_diagnostic",
            temporal,
            (
                "Bounded chronological diagnostic. The status table does not supply a "
                "forecast comparison or a joint temporal ERGM probability."
            ),
            temporal_sources,
        )
    )
    tables_and_sources.append(
        (
            "table_06_pilot_gates_and_exclusions",
            pd.DataFrame(GATE_ROWS),
            (
                "Compact transcription of the Phase 2 completion review. It preserves "
                "negative gates as explicit methodological evidence."
            ),
            [
                PROJECT_ROOT / "docs" / "PHASE2_COMPLETION_REVIEW.md",
                PROJECT_ROOT / "docs" / "NHPD_REPRODUCTION_GATE.md",
            ],
        )
    )

    generated: list[Path] = []
    source_paths: set[Path] = set()
    for stem, frame, note, paths in tables_and_sources:
        generated.extend(write_table(output_dir, stem, frame, note))
        source_paths.update(paths)

    generated.append(write_readme(output_dir, generated))
    manifest = {
        "generator": relative_to_project(Path(__file__).resolve()),
        "source_root": relative_to_project(source_root),
        "privacy": "Aggregate-only manuscript inputs; no raw or candidate-level data.",
        "generated_files": [path.name for path in sorted(generated)],
        "sources": [
            {"path": relative_to_project(path), "sha256": sha256(require_file(path))}
            for path in sorted(source_paths)
        ],
    }
    manifest_path = output_dir / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Manuscript tables written: {output_dir}")
    print(f"Tables: {len(tables_and_sources)}; generated files: {len(generated) + 1}")


if __name__ == "__main__":
    main()
