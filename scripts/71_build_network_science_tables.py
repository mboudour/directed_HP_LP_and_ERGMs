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
NETWORK_SCIENCE_PUBLICATION = PROJECT_ROOT / "results/published/network_science_20261025"
PHASE2_PUBLICATION = PROJECT_ROOT / "results/published/phase2_20261015"
REVIEWER_EXTENSION_PUBLICATION = PHASE2_PUBLICATION / "manuscript_reviewer_extensions"
ROW_END = r"\\"


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
        "\\small\n"
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
    if args.overwrite:
        for stale in output_dir.glob("table_*.tex"):
            stale.unlink()

    audit = json.loads(
        (NETWORK_SCIENCE_PUBLICATION / "records/senate_118_s_bills_audit.json").read_text()
    )
    event = audit["event_construction"]
    primary_heuristic = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_heuristics/metric_summary.csv"
    )
    primary_hard = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_sponsor_substitution/metric_summary.csv"
    )
    party_random = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_same_party_random/metric_summary.csv"
    )
    party_hard = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_same_party_sponsor_substitution/metric_summary.csv"
    )
    sponsor_diagnostics = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_sponsor_substitution_diagnostics/summary.csv"
    )
    recoverability = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_sponsor_substitution_diagnostics"
        / "recoverability_summary.csv"
    )
    primary_ergm = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_ergm_scores/metric_summary.csv"
    )
    political_ergm = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_ergm_m5_scores/metric_summary.csv"
    )
    political_contrasts = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_m5_vs_m4c_paired_uncertainty"
        / "paired_differences.csv"
    )
    competitive = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_competitive_contrasts"
        / "competitive_contrasts.csv"
    )
    primary_role = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_primary_role_assignment/metric_summary_by_arity.csv"
    )
    ergm_role = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_ergm_role_assignment/metric_summary.csv"
    )
    m5_ergm_role = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_m5_ergm_role_assignment/metric_summary.csv"
    )
    fidelity = json.loads(
        (
            NETWORK_SCIENCE_PUBLICATION
            / "phase2/senate_118_s_bills_native_event_fidelity_tail3_head10/summary.json"
        ).read_text()
    )
    static_metrics = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION / "models/senate_118_s_bills_static_arc_ergm/metrics.csv"
    )
    mtt = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_primary_mtt_logistic/mechanism_summary.csv"
    )
    sensitivity = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "models/senate_118_s_bills_cap3_sensitivity_ergm_paired_uncertainty"
        / "paired_differences.csv"
    )
    original_scope = pd.read_csv(
        PROJECT_ROOT / "manuscript/tables/table_03a_primary_native_random_panel_pr_auc.csv"
    )
    scope_fidelity = pd.read_csv(
        PROJECT_ROOT / "manuscript/tables/table_02_concept_event_fidelity.csv"
    )
    scope_hard = pd.read_csv(
        PROJECT_ROOT / "manuscript/tables/table_03b_primary_native_hard_panel_pr_auc.csv"
    )
    scope_ergm = {
        "Enron": pd.read_csv(
            PHASE2_PUBLICATION / "models/enron_native_event_ergm_footprints" / "metric_summary.csv"
        ),
        "MathOverflow": pd.read_csv(
            PHASE2_PUBLICATION
            / "models/mathoverflow_native_event_ergm_footprints"
            / "metric_summary.csv"
        ),
    }
    intermediate_publication = pd.read_csv(
        REVIEWER_EXTENSION_PUBLICATION / "intermediate_ergm_ladder.csv"
    )
    scope_intermediate = {
        "Enron": intermediate_publication.loc[
            intermediate_publication["dataset"] == "enron"
        ].assign(panel="random", score="L1g"),
        "MathOverflow": intermediate_publication.loc[
            intermediate_publication["dataset"] == "mathoverflow"
        ].assign(panel="random", score="L1g"),
    }
    mtt_publication = pd.read_csv(REVIEWER_EXTENSION_PUBLICATION / "mtt_logistic.csv")
    scope_mtt = {
        "Enron": mtt_publication.loc[mtt_publication["dataset"] == "enron"],
        "MathOverflow": mtt_publication.loc[mtt_publication["dataset"] == "mathoverflow"],
    }
    cap_profile = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION / "phase2/senate_118_s_bills_cap_profile/cap_profile.csv"
    )
    concept_gate = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION
        / "phase2/senate_118_s_bills_cap_gate/formal_concept_feasibility.csv"
    )
    mask_summary = pd.read_csv(
        NETWORK_SCIENCE_PUBLICATION / "phase2/senate_118_s_bills_primary_masks/split_summary.csv"
    )
    temporal_diagnostic = pd.read_csv(
        PROJECT_ROOT / "manuscript/tables/table_05_bounded_temporal_diagnostic.csv"
    )

    table1 = tex_table(
        "Senate co-sponsorship record construction and fixed actor universe.",
        "tab:senate-data",
        "p{0.50\\textwidth}p{0.40\\textwidth}",
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

    actor_rows = []
    for policy in audit["actor_policies"]:
        display = (
            "100 persons serving on 1 January 2024"
            if policy["name"] == "reference_date_2024_01_01"
            else "all persons serving during the 118th Congress"
        )
        retention = policy["retained_event_records"] / event["valid_nonempty_head_event_records"]
        actor_rows.append(
            f"{display} & {policy['nodes']:,} & {policy['retained_event_records']:,} & "
            f"{100 * retention:.1f}\% & {policy['static_arcs']:,} " + ROW_END
        )
    table_a1 = tex_table(
        "Actor-universe audit before the primary Senate benchmark.",
        "tab:actor-universe-audit",
        "p{0.40\\textwidth}rrrr",
        "Policy & persons & retained bills & retention & projected arcs",
        actor_rows,
        "The selected policy retains every valid bill with a nonempty original-co-sponsor head and never merges distinct people by Senate seat.",
    )

    cap_rows = []
    concept_counts = dict(zip(concept_gate["head_cap"], concept_gate["concepts"], strict=True))
    for _, row in cap_profile.iterrows():
        cap = int(row["head_cap"])
        cap_rows.append(
            f"{cap} & {100 * row['record_retention']:.1f}\% & {100 * row['type_retention']:.1f}\% & "
            f"{int(row['cap_projection_arcs']):,} & {int(concept_counts[cap]):,} & "
            f"{int(row['sponsor_substitution_eligible_event_types']):,} & "
            f"{int(row['role_assignment_event_types']):,} " + ROW_END
        )
    table_a2 = tex_table(
        "Cap-first Senate target audit across original-co-sponsor head limits.",
        "tab:cap-audit",
        "lrrrrrr",
        "Head cap & bill retention & type retention & arcs & concepts & sponsor swaps & role events",
        cap_rows,
        "All rows use the same 105-person universe. Concepts use the cap-first $|T|\leq3$ enumeration; the primary cap $|H|\leq10$ was selected before the 30-mask study.",
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
        random_m5_pr = metric(political_ergm, "random", mechanism, "M5", "L1g", "pr_auc")
        random_m5_roc = metric(political_ergm, "random", mechanism, "M5", "L1g", "roc_auc")
        random_party_pr = local_metric(party_random, mechanism, "lifted_same_party_mean", "pr_auc")
        random_party_roc = local_metric(
            party_random, mechanism, "lifted_same_party_mean", "roc_auc"
        )
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
        hard_m5_pr = metric(
            political_ergm, "sponsor_substitution", mechanism, "M5", "L1g", "pr_auc"
        )
        hard_m5_roc = metric(
            political_ergm, "sponsor_substitution", mechanism, "M5", "L1g", "roc_auc"
        )
        hard_party_pr = local_metric(party_hard, mechanism, "lifted_same_party_mean", "pr_auc")
        hard_party_roc = local_metric(party_hard, mechanism, "lifted_same_party_mean", "roc_auc")
        performance_rows.extend(
            [
                f"{display} & random & AA-total & {fmt(random_local_pr)} & {fmt(random_local_roc)} "
                + ROW_END,
                f"{display} & random & same-party share & {fmt(random_party_pr)} & {fmt(random_party_roc)} "
                + ROW_END,
                f"{display} & random & M4c conditional & {fmt(random_ergm_pr)} & {fmt(random_ergm_roc)} "
                + ROW_END,
                f"{display} & random & M5 political conditional & {fmt(random_m5_pr)} & {fmt(random_m5_roc)} "
                + ROW_END,
                f"{display} & sponsor substitution & degree product & {fmt(hard_local_pr)} & {fmt(hard_local_roc)} "
                + ROW_END,
                f"{display} & sponsor substitution & same-party share & {fmt(hard_party_pr)} & {fmt(hard_party_roc)} "
                + ROW_END,
                f"{display} & sponsor substitution & M4c conditional & {fmt(hard_ergm_pr)} & {fmt(hard_ergm_roc)} "
                + ROW_END,
                f"{display} & sponsor substitution & M5 political conditional & {fmt(hard_m5_pr)} & {fmt(hard_m5_roc)} "
                + ROW_END,
            ]
        )
    table2 = tex_table(
        "Primary Senate native-event footprint recovery across matched masks.",
        "tab:senate-performance",
        "lllrr",
        "Mask & panel & score & PR-AUC & ROC-AUC",
        performance_rows,
        "Entries are means over 30 matched masks. M5 adds party and state matching and absolute "
        "DW-NOMINATE distance to M4c. ERGM rows use split-specific MPLE estimates and factorized "
        "conditional footprint score $L_{1g}$ rather than a joint coalition probability.",
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

    political_contrast_rows: list[str] = []
    for mechanism, display in (("mcar", "MCAR"), ("mnar_out", "MNAR-out")):
        for panel, panel_display in (
            ("random", "random"),
            ("sponsor_substitution", "sponsor substitution"),
        ):
            subset = political_contrasts.loc[
                (political_contrasts["mechanism"] == mechanism)
                & (political_contrasts["panel"] == panel)
                & (political_contrasts["metric"] == "pr_auc")
                & (political_contrasts["comparison_method"] == "M5::L1g")
                & (political_contrasts["reference_method"] == "M4c::L1g")
            ]
            if len(subset) != 1:
                raise ValueError(f"Expected one political PR-AUC contrast for {mechanism}/{panel}")
            row = subset.iloc[0]
            political_contrast_rows.append(
                f"{display} & {panel_display} & {fmt(row['mean_difference'])} & "
                f"[{fmt(row['bootstrap_ci_low'])}, {fmt(row['bootstrap_ci_high'])}] & "
                f"{row['paired_sign_flip_p_value']:.5f} " + ROW_END
            )
    table3b = tex_table(
        "Matched-mask PR-AUC improvement from political covariates.",
        "tab:political-contrast",
        "llrrr",
        "Mask & panel & M5 minus M4c & 95\\% CI & sign-flip $p$",
        political_contrast_rows,
        "M5 adds party and state matching and absolute DW-NOMINATE distance to the M4c structural"
        " specification. Intervals resample whole masks within the fixed Senate network.",
    )

    role_rows: list[str] = []
    for mechanism in ("mcar", "mnar_out"):
        local_top1 = weighted_role(
            primary_role, mechanism, "lifted_adamic_adar_oi_mean", "top1_accuracy"
        )
        local_mrr = weighted_role(primary_role, mechanism, "lifted_adamic_adar_oi_mean", "mrr")
        model_row = ergm_role.loc[
            (ergm_role["mechanism"] == mechanism) & (ergm_role["score"] == "M4c::L1g")
        ].iloc[0]
        chance_row = ergm_role.loc[
            (ergm_role["mechanism"] == mechanism) & (ergm_role["score"] == "uniform_chance")
        ].iloc[0]
        m5_role_row = m5_ergm_role.loc[
            (m5_ergm_role["mechanism"] == mechanism) & (m5_ergm_role["score"] == "M5::L1g")
        ].iloc[0]
        mechanism_label = "MCAR" if mechanism == "mcar" else "MNAR-out"
        role_rows.append(f"{mechanism_label} & AA-OI & {fmt(local_top1)} & {fmt(local_mrr)} \\\\")
        role_rows.append(
            f"{mechanism_label} & M4c conditional & {fmt(model_row['weighted_top1_accuracy'])} & {fmt(model_row['weighted_mrr'])} \\\\"
        )
        role_rows.append(
            f"{mechanism_label} & uniform chance & {fmt(chance_row['weighted_top1_accuracy'])} & "
            f"{fmt(chance_row['weighted_mrr'])} " + ROW_END
        )
        role_rows.append(
            f"{mechanism_label} & M5 political conditional & "
            f"{fmt(m5_role_row['weighted_top1_accuracy'])} & "
            f"{fmt(m5_role_row['weighted_mrr'])} " + ROW_END
        )
    table4 = tex_table(
        "Sponsor identification with participants and arities held fixed.",
        "tab:senate-role",
        "lrrr",
        "Mask & score & top-1 accuracy & MRR",
        role_rows,
        "Each held-out bill is evaluated against every compatible sponsor/co-sponsor partition."
        " Local rows are event-weighted over observed arities; chance is $1/(|H|+1)$ for top-1."
        " ERGM rows use factorized conditional $L_{1g}$ scores.",
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

    mask_rows = []
    for mechanism, display in (("mcar", "MCAR"), ("mnar_out", "MNAR-out")):
        subset = mask_summary.loc[mask_summary["mechanism"] == mechanism]
        mask_rows.append(
            f"{display} & {len(subset)} & {100 * subset['realized_event_type_mask_rate'].mean():.2f}\% & "
            f"{100 * subset['realized_event_record_mask_rate'].mean():.2f}\% & "
            f"{100 * subset['realized_arc_removal_rate'].mean():.2f}\% & "
            f"{100 * subset['already_observed_footprint_type_fraction'].mean():.2f}\% " + ROW_END
        )
    table_a3 = tex_table(
        "Realised omission and footprint-survival rates across primary Senate masks.",
        "tab:mask-realisation",
        "lrrrrr",
        "Mask & masks & type rate & record rate & arc-removal rate & surviving footprints",
        mask_rows,
        "A surviving footprint means every dyad of a held-out bill type remains induced by at least one distinct observed bill type; it is a representation feature, not target leakage.",
    )

    ladder_rows = []
    for model in ("M0", "M1", "M2", "M3", "M4", "M4c", "M5"):
        ladder_source = political_ergm if model == "M5" else primary_ergm
        values = [
            metric(ladder_source, "random", "mcar", model, "L1g", "pr_auc"),
            metric(ladder_source, "random", "mnar_out", model, "L1g", "pr_auc"),
            metric(ladder_source, "sponsor_substitution", "mcar", model, "L1g", "pr_auc"),
            metric(ladder_source, "sponsor_substitution", "mnar_out", model, "L1g", "pr_auc"),
        ]
        ladder_rows.append(
            f"{model} & {fmt(values[0])} & {fmt(values[1])} & {fmt(values[2])} & {fmt(values[3])} "
            + ROW_END
        )
    table_a4 = tex_table(
        "Full split-specific MPLE ERGM ladder: mean $L_{1g}$ PR-AUC across 30 Senate masks.",
        "tab:ergm-ladder",
        "lrrrr",
        "Model & random MCAR & random MNAR-out & sponsor swap MCAR & sponsor swap MNAR-out",
        ladder_rows,
        "M0 contains edges only; M1 adds mutuality; M2 adds degree terms; M3 adds transitive closure; M4 adds directed shared-partner terms; M4c also adds cyclic triples; M5 adds political covariates. Values are conditional footprint-score rankings, not joint event probabilities.",
    )

    sponsor_pattern_rows: list[str] = []
    sponsor_patterns = (
        "both footprints survive",
        "true bill only survives",
        "substitution only survives",
        "neither footprint survives",
    )
    preference_measures = {
        "M4c::L1g": "M4c_positive_preference",
        "M5::L1g": "M5_positive_preference",
        "party_match": "same_party_positive_preference",
    }
    for mechanism, display in (("mcar", "MCAR"), ("mnar_out", "MNAR-out")):
        for pattern in sponsor_patterns:
            prevalence_row = recoverability.loc[
                (recoverability["mechanism"] == mechanism) & (recoverability["measure"] == pattern)
            ]
            if len(prevalence_row) != 1:
                raise ValueError(f"Expected one recoverability row for {mechanism}/{pattern}")
            preference_cells: list[str] = []
            for score in ("M4c::L1g", "M5::L1g", "party_match"):
                preference_row = sponsor_diagnostics.loc[
                    (sponsor_diagnostics["mechanism"] == mechanism)
                    & (sponsor_diagnostics["recoverability_stratum"] == pattern)
                    & (sponsor_diagnostics["measure"] == preference_measures[score])
                ]
                if len(preference_row) != 1:
                    raise ValueError(
                        f"Expected one sponsor preference row for {mechanism}/{pattern}/{score}"
                    )
                value = preference_row.iloc[0]
                preference_cells.append(
                    f"{fmt(value['mean'])} "
                    f"[{fmt(value['bootstrap_ci_lower'])}, {fmt(value['bootstrap_ci_upper'])}]"
                )
            share = prevalence_row.iloc[0]
            sponsor_pattern_rows.append(
                f"{display} & {pattern.replace('footprints', 'fp.').replace('footprint', 'fp.')} & "
                f"{fmt(share['mean'])} [{fmt(share['bootstrap_ci_lower'])}, "
                f"{fmt(share['bootstrap_ci_upper'])}] & "
                + " & ".join(preference_cells)
                + " "
                + ROW_END
            )
    table_a5b = tex_table(
        "Sponsor-substitution pair recoverability and true-bill preference by score.",
        "tab:sponsor-recoverability",
        "llrrrr",
        "Mask & footprint pattern & pair share & M4c preference & M5 preference & party preference",
        sponsor_pattern_rows,
        "Each preference is the tie-aware probability that the score ranks the held-out true bill above "
        "one valid sponsor substitution; brackets are 95\% mask-bootstrap intervals. The true-bill-only "
        "pattern preserves the true sponsor-to-co-sponsor footprint but removes the substitution's reverse footprint.",
    )
    table_a5b = table_a5b.replace(
        "\\begin{tabular}", "\\resizebox{\\textwidth}{!}{%\n\\begin{tabular}", 1
    ).replace("\\end{tabular}", "\\end{tabular}\n}", 1)

    mtt_rows = [
        f"{'MCAR' if row['mechanism'] == 'mcar' else 'MNAR-out'} & "
        f"{int(row['completed_masks'])}/{int(row['completed_masks'])} & "
        f"{int(row['positive_theta_masks'])} & {fmt(row['theta_triple_mean'], 4)} & "
        "increasing, same order as directed CN \\\\"
        for _, row in mtt.iterrows()
    ]
    table_a5 = tex_table(
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
    table_a6 = tex_table(
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
    table_a7 = tex_table(
        "Non-political scope checks: strongest reported random-panel native-event PR-AUC.",
        "tab:scope-checks",
        "lllr",
        "Dataset & mask & score & PR-AUC",
        scope_rows,
        "Existing fixed-network event-first benchmarks are retained as scope checks; the Senate is the"
        " political worked application and is analysed in the main text.",
    )

    scope_fidelity_rows: list[str] = []
    for _, row in scope_fidelity.iterrows():
        short_name = "Enron" if row["dataset"].startswith("Enron") else "MathOverflow"
        scope_fidelity_rows.append(
            f"{short_name} & {int(row['nodes'])} & {int(row['static_arcs']):,} & "
            f"{int(row['native_event_types']):,} & {int(row['formal_concepts']):,} & "
            f"{int(row['exact_tail_head_matches'])} & {fmt(row['footprint_jaccard'])} " + ROW_END
        )
    table_a8 = tex_table(
        "Non-political target and representation-fidelity audit at common tail/head cap three.",
        "tab:scope-fidelity",
        "lrrrrrr",
        "Core & actors & arcs & types & concepts & exact & footprint $J$",
        scope_fidelity_rows,
        "Exact equality requires identical ordered tail and head sets. Footprint $J$ compares unions of directed arcs and is not event-type recovery.",
    )

    scope_panel_rows: list[str] = []
    scope_panel_specs = (
        ("Random arity-matched", "Directed Adamic-Adar total", "random: AA-total"),
        ("Random arity-matched", "M4c::L1g", "random: M4c $L_{1g}$"),
        ("Reversal/orientation", "Directed Adamic-Adar total", "reversal: AA-total"),
        ("Reversal/orientation", "M4c::L1g", "reversal: M4c $L_{1g}$"),
        ("Role exchange", "Directed Adamic-Adar total", "role exchange: AA-total"),
        ("Role exchange", "M4c::L1g", "role exchange: M4c $L_{1g}$"),
    )
    for panel, method, display in scope_panel_specs:
        values: list[str] = []
        for dataset in scope_datasets:
            source = original_scope if panel == "Random arity-matched" else scope_hard
            for mechanism in ("MCAR", "MNAR-out"):
                subset = source.loc[
                    (source["dataset"] == dataset)
                    & (source["panel"] == panel)
                    & (source["mechanism"] == mechanism)
                    & (source["method"] == method)
                ]
                if len(subset) != 1:
                    raise ValueError(
                        "Expected one scope panel metric for "
                        f"{dataset}/{panel}/{mechanism}/{method}"
                    )
                values.append(fmt(float(subset.iloc[0]["pr_auc_mean"])))
        scope_panel_rows.append(f"{display} & " + " & ".join(values) + " " + ROW_END)
    table_a9 = tex_table(
        "Non-political event-first panel profiles: mean PR-AUC across 30 masks per cell.",
        "tab:scope-panels",
        "lrrrr",
        "Panel and score & Enron M & Enron MN & MO M & MO MN",
        scope_panel_rows,
        "M = MCAR and MN = MNAR-out. Random panels are arity-matched non-event comparisons. Reversal and role-exchange panels contain only valid unseen transformed alternatives and are not pooled with random panels.",
    )

    scope_ladder_rows: list[str] = []
    for model in ("M0", "M1", "M2", "M3", "M4", "M4c"):
        values = [
            metric(
                scope_intermediate[dataset] if model in {"M2", "M4"} else scope_ergm[dataset],
                "random",
                mechanism,
                model,
                "L1g",
                "pr_auc",
            )
            for dataset in ("Enron", "MathOverflow")
            for mechanism in ("mcar", "mnar_out")
        ]
        scope_ladder_rows.append(
            f"{model} & " + " & ".join(fmt(value) for value in values) + " " + ROW_END
        )
    table_a10 = tex_table(
        "Full conditional-score ladder in the non-political event-first scope checks: mean random-panel PR-AUC across 30 masks per cell.",
        "tab:scope-ladder",
        "lrrrr",
        "Model & Enron MCAR & Enron MNAR-out & MathOverflow MCAR & MathOverflow MNAR-out",
        scope_ladder_rows,
        "All entries use split-specific MPLE conditional scores with geometric footprint lifting $L_{1g}$. The table reports rankings on the stated case-control panels, not joint event probabilities.",
    )

    scope_mtt_rows: list[str] = []
    for dataset in ("Enron", "MathOverflow"):
        for mechanism, display in (("mcar", "MCAR"), ("mnar_out", "MNAR-out")):
            row = scope_mtt[dataset].loc[scope_mtt[dataset]["mechanism"] == mechanism].iloc[0]
            scope_mtt_rows.append(
                f"{dataset} & {display} & {int(row['completed_masks'])}/{int(row['completed_masks'])} & "
                f"{int(row['positive_theta_masks'])}/{int(row['completed_masks'])} & "
                f"{fmt(row['theta_triple_mean'], 4)} & "
                f"[{fmt(row['theta_triple_min'], 4)}, {fmt(row['theta_triple_max'], 4)}] " + ROW_END
            )
    table_a11 = tex_table(
        "Cross-source empirical check of the directed transitive-triple conditional dictionary.",
        "tab:scope-mtt",
        "llrrrr",
        r"Core & mask & fits & positive & mean $\hat\theta_{tr}$ & range",
        scope_mtt_rows,
        "Every fit is the restricted split-specific logistic/MPLE check using the exact directed transitive-triple change statistic. Positive coefficients imply that its arc-level conditional score is increasing in directed out--in common neighbours.",
    )

    temporal_rows: list[str] = []
    for _, row in temporal_diagnostic.iterrows():
        source = "Enron" if row["dataset"].startswith("Enron") else "EU-core"
        btergm = "3/5 fit; T2 and T2--H nonfinite" if source == "Enron" else "5/5 fit"
        temporal_rows.append(
            f"{source} & {int(row['nodes'])} & {int(row['panels'])} & {int(row['transitions'])} & "
            f"{row['factorized_lagged_models']} & {btergm} " + ROW_END
        )
    table_a12 = tex_table(
        "Bounded chronological diagnostic status; this is a conditional-score check, not a forecasting experiment.",
        "tab:bounded-temporal",
        "lrrrll",
        "Source & actors & panels & transitions & lagged models & btergm MPLE ladder",
        temporal_rows,
        "Both sources use three frozen panels and two transitions. The btergm branch has 20 temporal bootstrap replicates and no simulation, forecast, TERGM, STERGM, or relational-hyperevent claim.",
    )

    tables = {
        "table_01_senate_data.tex": table1,
        "table_02_primary_performance.tex": table2,
        "table_03_competitive_contrasts.tex": table3,
        "table_03b_political_covariate_contrasts.tex": table3b,
        "table_04_sponsor_identification.tex": table4,
        "table_05_cap_sensitivity.tex": table5,
        "table_06_concept_fidelity.tex": table6,
        "table_a1_actor_universe.tex": table_a1,
        "table_a2_cap_audit.tex": table_a2,
        "table_a3_mask_realisation.tex": table_a3,
        "table_a4_ergm_ladder.tex": table_a4,
        "table_a5b_sponsor_recoverability.tex": table_a5b,
        "table_a5_mtt_check.tex": table_a5,
        "table_a6_static_diagnostic.tex": table_a6,
        "table_a7_scope_checks.tex": table_a7,
        "table_a8_scope_fidelity.tex": table_a8,
        "table_a9_scope_panels.tex": table_a9,
        "table_a10_scope_ladder.tex": table_a10,
        "table_a11_scope_mtt.tex": table_a11,
        "table_a12_bounded_temporal.tex": table_a12,
    }
    for name, content in tables.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    manifest = {
        "driver": "scripts/71_build_network_science_tables.py",
        "sources": [
            "results/published/network_science_20261025/records/senate_118_s_bills_audit.json",
            "results/published/network_science_20261025/phase2/senate_118_s_bills_primary_*",
            "results/published/network_science_20261025/models/senate_118_s_bills_primary_*",
            "results/published/network_science_20261025/models/senate_118_s_bills_cap3_sensitivity_*",
            "manuscript/tables/table_03a_primary_native_random_panel_pr_auc.csv",
            "manuscript/tables/table_02_concept_event_fidelity.csv",
            "manuscript/tables/table_03b_primary_native_hard_panel_pr_auc.csv",
            "results/published/phase2_20261015/models/*_native_event_ergm_footprints/metric_summary.csv",
            "results/published/phase2_20261015/manuscript_reviewer_extensions/intermediate_ergm_ladder.csv",
            "results/published/phase2_20261015/manuscript_reviewer_extensions/mtt_logistic.csv",
            "manuscript/tables/table_05_bounded_temporal_diagnostic.csv",
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
