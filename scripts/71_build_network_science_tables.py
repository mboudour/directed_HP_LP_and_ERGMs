#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate Network Science LaTeX tables from aggregate-only benchmark outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "manuscript" / "network_science" / "tables"


def parse_args() -> argparse.Namespace:
    """Parse table-output controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def fmt(value: float, digits: int = 3) -> str:
    """Format a finite numeric value consistently for a manuscript table."""
    return f"{float(value):.{digits}f}"


def metric(
    frame: pd.DataFrame, panel: str, mechanism: str, model: str, score: str, name: str
) -> float:
    """Extract a uniquely identified ERGM aggregate metric."""
    result = frame.loc[
        (frame["panel"] == panel)
        & (frame["mechanism"] == mechanism)
        & (frame["model"] == model)
        & (frame["score"] == score)
        & (frame["metric"] == name),
        "mean",
    ]
    if len(result) != 1:
        raise ValueError(f"Expected one ERGM {panel}/{mechanism}/{model}/{score}/{name} row")
    return float(result.iloc[0])


def local_metric(frame: pd.DataFrame, mechanism: str, score: str, name: str) -> float:
    """Extract a uniquely identified local-score aggregate metric."""
    result = frame.loc[
        (frame["mechanism"] == mechanism) & (frame["score"] == score) & (frame["metric"] == name),
        "mean",
    ]
    if len(result) != 1:
        raise ValueError(f"Expected one local {mechanism}/{score}/{name} row")
    return float(result.iloc[0])


def weighted_role(frame: pd.DataFrame, mechanism: str, score: str, name: str) -> float:
    """Compute an event-weighted role-assignment mean across observed arities."""
    subset = frame.loc[
        (frame["mechanism"] == mechanism) & (frame["score"] == score) & (frame["metric"] == name)
    ]
    if subset.empty:
        raise ValueError(f"No role rows for {mechanism}/{score}/{name}")
    return float(
        (subset["mean"] * subset["event_evaluations"]).sum() / subset["event_evaluations"].sum()
    )


def tex_table(
    caption: str, label: str, column_spec: str, header: str, rows: list[str], note: str
) -> str:
    """Return one self-contained, booktabs LaTeX table environment."""
    row_text = "\n".join(rows)
    return (
        "\\begin{table}[tbp]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        f"\\begin{{tabular}}{{{column_spec}}}\n"
        "\\toprule\n"
        f"{header} " + r"\\" + "\n"
        "\\midrule\n"
        f"{row_text}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        f"\\par\\vspace{{2pt}}\\footnotesize {note}\n"
        "\\end{table}\n"
    )


def main() -> None:
    """Build all table fragments used by the anonymized Network Science manuscript."""
    args = parse_args()
    output_dir = resolve(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise SystemExit(f"STOP: table directory is nonempty; pass --overwrite: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    audit = json.loads((PROJECT_ROOT / "data/metadata/senate_118_s_bills_audit.json").read_text())
    event = audit["event_construction"]
    primary_heuristic = pd.read_csv(
        PROJECT_ROOT / "results/phase2/senate_118_s_bills_primary_heuristics/metric_summary.csv"
    )
    primary_hard = pd.read_csv(
        PROJECT_ROOT
        / "results/phase2/senate_118_s_bills_primary_sponsor_substitution/metric_summary.csv"
    )
    primary_ergm = pd.read_csv(
        PROJECT_ROOT / "results/models/senate_118_s_bills_primary_ergm_scores/metric_summary.csv"
    )
    competitive = pd.read_csv(
        PROJECT_ROOT
        / "results/phase2/senate_118_s_bills_primary_competitive_contrasts"
        / "competitive_contrasts.csv"
    )
    primary_role = pd.read_csv(
        PROJECT_ROOT
        / "results/phase2/senate_118_s_bills_primary_role_assignment/metric_summary_by_arity.csv"
    )
    ergm_role = pd.read_csv(
        PROJECT_ROOT
        / "results/models/senate_118_s_bills_primary_ergm_role_assignment/metric_summary.csv"
    )
    fidelity = json.loads(
        (
            PROJECT_ROOT
            / "results/phase2/senate_118_s_bills_native_event_fidelity_tail3_head10/summary.json"
        ).read_text()
    )
    static_metrics = pd.read_csv(
        PROJECT_ROOT / "results/models/senate_118_s_bills_static_arc_ergm/metrics.csv"
    )
    mtt = pd.read_csv(
        PROJECT_ROOT
        / "results/models/senate_118_s_bills_primary_mtt_logistic/mechanism_summary.csv"
    )
    sensitivity = pd.read_csv(
        PROJECT_ROOT
        / "results/models/senate_118_s_bills_cap3_sensitivity_ergm_paired_uncertainty"
        / "paired_differences.csv"
    )
    original_scope = pd.read_csv(
        PROJECT_ROOT / "manuscript/tables/table_03a_primary_native_random_panel_pr_auc.csv"
    )

    table1 = tex_table(
        "Senate co-sponsorship record construction and fixed actor universe.",
        "tab:senate-data",
        "lr",
        "Quantity & Value",
        [
            "Bill Status XML records (118th Congress, S. bills) & "
            f"{event['xml_records_read']:,} \\\\",
            "Measures with nonempty original-co-sponsor head & "
            f"{event['valid_nonempty_head_event_records']:,} \\\\",
            "Measures with zero original co-sponsors & "
            f"{event['zero_original_cosponsor_measures']:,} \\\\",
            f"Distinct Senate persons in primary universe & {audit['primary_policy']['nodes']:,} \\\\",
            f"Directed sponsor-to-co-sponsor arcs & {audit['actor_policies'][1]['static_arcs']:,} \\\\",
            "Primary event target & one sponsor $\\to$ up to ten original co-sponsors \\\\",
            "Missingness grid & 30 MCAR + 30 activity-biased MNAR-out masks " + r"\\",
        ],
        "A record is an S. bill with its sole recorded sponsor as tail and its original co-sponsors as head."
        " Later withdrawals remain in the introduction-time membership target.",
    )

    performance_rows: list[str] = []
    for mechanism, display in (("mcar", "MCAR"), ("mnar_out", "MNAR-out")):
        random_local_pr = local_metric(
            primary_heuristic, mechanism, "lifted_adamic_adar_total_mean", "pr_auc"
        )
        random_local_roc = local_metric(
            primary_heuristic, mechanism, "lifted_adamic_adar_total_mean", "roc_auc"
        )
        random_ergm_pr = metric(primary_ergm, "random", mechanism, "M4c", "L1g", "pr_auc")
        random_ergm_roc = metric(primary_ergm, "random", mechanism, "M4c", "L1g", "roc_auc")
        hard_local_pr = local_metric(
            primary_hard, mechanism, "lifted_degree_product_mean", "pr_auc"
        )
        hard_local_roc = local_metric(
            primary_hard, mechanism, "lifted_degree_product_mean", "roc_auc"
        )
        hard_ergm_pr = metric(
            primary_ergm, "sponsor_substitution", mechanism, "M4c", "L1g", "pr_auc"
        )
        hard_ergm_roc = metric(
            primary_ergm, "sponsor_substitution", mechanism, "M4c", "L1g", "roc_auc"
        )
        performance_rows.extend(
            [
                f"{display} & random & AA-total & {fmt(random_local_pr)} & {fmt(random_local_roc)} \\\\",
                f"{display} & random & M4c conditional & {fmt(random_ergm_pr)} & {fmt(random_ergm_roc)} \\\\",
                f"{display} & sponsor substitution & degree product & {fmt(hard_local_pr)} & {fmt(hard_local_roc)} \\\\",
                f"{display} & sponsor substitution & M4c conditional & {fmt(hard_ergm_pr)} & {fmt(hard_ergm_roc)} \\\\",
            ]
        )
    table2 = tex_table(
        "Primary Senate native-event footprint recovery across matched masks.",
        "tab:senate-performance",
        "llllrr",
        "Mask & panel & score & score class & PR-AUC & ROC-AUC",
        performance_rows,
        "Entries are means over 30 matched masks. M4c uses split-specific MPLE estimates and the"
        " factorized conditional footprint score $L_{1g}$; it is not a joint coalition probability.",
    )

    contrast_rows: list[str] = []
    for _, row in competitive.iterrows():
        panel = "random" if row["panel"] == "random" else "sponsor substitution"
        interval = f"[{fmt(row['bootstrap_ci_low'])}, {fmt(row['bootstrap_ci_high'])}]"
        metric_label = "PR-AUC" if row["metric"] == "pr_auc" else "ROC-AUC"
        mechanism_label = "MCAR" if row["mechanism"] == "mcar" else "MNAR-out"
        contrast_rows.append(
            f"{mechanism_label} & {panel} & {metric_label} & {fmt(row['mean_difference'])} & {interval} & {row['paired_sign_flip_p_value']:.5f} \\\\"
        )
    table3 = tex_table(
        "Matched-mask difference between M4c $L_{1g}$ and the declared local reference.",
        "tab:senate-contrasts",
        "lllrrr",
        "Mask & panel & metric & difference & 95\\% CI & sign-flip $p$",
        contrast_rows,
        "Difference = M4c $L_{1g}$ minus AA-total on random panels and minus degree product on"
        " sponsor-substitution panels. Intervals resample whole masks within the fixed Senate network.",
    )

    role_rows: list[str] = []
    for mechanism in ("mcar", "mnar_out"):
        local_top1 = weighted_role(
            primary_role, mechanism, "lifted_adamic_adar_oi_mean", "top1_accuracy"
        )
        local_mrr = weighted_role(primary_role, mechanism, "lifted_adamic_adar_oi_mean", "mrr")
        model_row = ergm_role.loc[ergm_role["mechanism"] == mechanism].iloc[0]
        mechanism_label = "MCAR" if mechanism == "mcar" else "MNAR-out"
        role_rows.append(f"{mechanism_label} & AA-OI & {fmt(local_top1)} & {fmt(local_mrr)} \\\\")
        role_rows.append(
            f"{mechanism_label} & M4c conditional & {fmt(model_row['weighted_top1_accuracy'])} & {fmt(model_row['weighted_mrr'])} \\\\"
        )
    table4 = tex_table(
        "Sponsor identification with participants and arities held fixed.",
        "tab:senate-role",
        "lrrr",
        "Mask & score & top-1 accuracy & MRR",
        role_rows,
        "Each held-out bill is evaluated against every compatible sponsor/co-sponsor partition."
        " Local rows are event-weighted over observed arities; ERGM rows use M4c $L_{1g}$.",
    )

    sensitivity_rows: list[str] = []
    for mechanism in ("mcar", "mnar_out"):
        subset = sensitivity.loc[
            (sensitivity["mechanism"] == mechanism)
            & (sensitivity["panel"] == "random")
            & (sensitivity["metric"] == "pr_auc")
            & (sensitivity["comparison_method"] == "M4c::L1g")
            & (sensitivity["reference_method"] == "M0::L1")
        ]
        row = subset.iloc[0]
        mechanism_label = "MCAR" if mechanism == "mcar" else "MNAR-out"
        sensitivity_rows.append(
            f"$|H|\\leq3$ & {mechanism_label} & {fmt(row['mean_difference'])} & "
            f"[{fmt(row['bootstrap_ci_low'])}, {fmt(row['bootstrap_ci_high'])}] \\\\"
        )
    table5 = tex_table(
        "Cap-three sensitivity: paired M4c $L_{1g}$ versus density-only random-panel PR-AUC.",
        "tab:senate-cap-sensitivity",
        "llrr",
        "Cap & mask & difference & 95\\% CI",
        sensitivity_rows,
        "The primary cap is $|H|\\leq10$; this independent cap-three rerun preserves the fixed Senate"
        " actor universe, event-first masking design, and 30 masks per mechanism.",
    )

    fidelity_rows = [
        f"formal concepts & {fidelity['formal_concepts']['count']:,} \\\\",
        f"cap-eligible bill types & {fidelity['native_events']['cap_eligible_event_types']:,} \\\\",
        f"exact tail/head matches & {fidelity['exact_tail_head_equality']['matching_pairs']:,} \\\\",
        f"footprint Jaccard & {fmt(fidelity['footprint_agreement']['jaccard'])} \\\\",
        f"concept footprint covered by bills & {fmt(fidelity['footprint_agreement']['formal_concept_footprint_covered_by_native_events'])} \\\\",
    ]
    table6 = tex_table(
        "Derived formal concepts versus recorded Senate bill coalitions.",
        "tab:senate-fidelity",
        "lr",
        "Quantity & Value",
        fidelity_rows,
        "The formal-concept enumeration uses the aggregate projection with $|T|\\leq3$ and $|H|\\leq10$."
        " Exact agreement requires equality of ordered tail and head sets.",
    )

    mtt_rows = [
        f"{'MCAR' if row['mechanism'] == 'mcar' else 'MNAR-out'} & "
        f"{int(row['completed_masks'])}/{int(row['completed_masks'])} & "
        f"{int(row['positive_theta_masks'])} & {fmt(row['theta_triple_mean'], 4)} & "
        "increasing, same order as directed CN \\\\"
        for _, row in mtt.iterrows()
    ]
    table_a1 = tex_table(
        "Empirical transitive-triple logistic check on primary Senate training projections.",
        "tab:mtt-check",
        "lrrrl",
        "Mask & fits & positive $\\hat\\theta_{tr}$ & mean $\\hat\\theta_{tr}$ & relation",
        mtt_rows,
        "For each split, $y_{ij}$ is regressed on the exact directed transitive-triple change statistic."
        " This checks the sign and ranking relation only.",
    )

    static_rows: list[str] = []
    for model in ("M0", "M1", "M2", "M3", "M4", "M4c"):
        sub = static_metrics.loc[
            (static_metrics["model"] == model)
            & (static_metrics["metric"].isin(["pr_auc", "roc_auc"]))
        ]
        grouped = sub.groupby("metric", as_index=True)["value"].mean()
        static_rows.append(f"{model} & {fmt(grouped['pr_auc'])} & {fmt(grouped['roc_auc'])} \\\\")
    table_a2 = tex_table(
        "Bounded static directed-arc diagnostic for the Senate projection.",
        "tab:static-diagnostic",
        "lrr",
        "MPLE model & PR-AUC & ROC-AUC",
        static_rows,
        "Three arc-first MCAR splits; values are exact conditional tie-score discrimination summaries."
        " This diagnostic does not estimate a temporal or joint coalition model.",
    )

    scope_rows: list[str] = []
    scope_datasets = ("Enron strict custodian core", "MathOverflow reconstructed core")
    for dataset in scope_datasets:
        for mechanism in ("MCAR", "MNAR-out"):
            subset = original_scope.loc[
                (original_scope["dataset"] == dataset)
                & (original_scope["mechanism"] == mechanism)
                & (original_scope["method"] == "M4c::L1g")
            ]
            row = subset.iloc[0]
            short_name = "Enron" if dataset.startswith("Enron") else "MathOverflow"
            scope_rows.append(
                f"{short_name} & {mechanism} & M4c $L_{{1g}}$ & {fmt(row['pr_auc_mean'])}" + r" \\"
            )
    table_a3 = tex_table(
        "Non-political scope checks: strongest reported random-panel native-event PR-AUC.",
        "tab:scope-checks",
        "lllr",
        "Dataset & mask & score & PR-AUC",
        scope_rows,
        "Existing fixed-network event-first benchmarks are retained as scope checks; the Senate is the"
        " political worked application and is analysed in the main text.",
    )

    tables = {
        "table_01_senate_data.tex": table1,
        "table_02_primary_performance.tex": table2,
        "table_03_competitive_contrasts.tex": table3,
        "table_04_sponsor_identification.tex": table4,
        "table_05_cap_sensitivity.tex": table5,
        "table_06_concept_fidelity.tex": table6,
        "table_a1_mtt_check.tex": table_a1,
        "table_a2_static_diagnostic.tex": table_a2,
        "table_a3_scope_checks.tex": table_a3,
    }
    for name, content in tables.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    manifest = {
        "driver": "scripts/71_build_network_science_tables.py",
        "sources": [
            "data/metadata/senate_118_s_bills_audit.json",
            "results/phase2/senate_118_s_bills_primary_*",
            "results/models/senate_118_s_bills_primary_*",
            "results/models/senate_118_s_bills_cap3_sensitivity_*",
            "manuscript/tables/table_03a_primary_native_random_panel_pr_auc.csv",
        ],
        "privacy": "Generated tables contain aggregate counts, metrics, intervals, and no actor identifiers.",
        "tables": sorted(tables),
    }
    (output_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Network Science manuscript tables written: {output_dir}")
    print(f"Tables: {len(tables)}")


if __name__ == "__main__":
    main()
