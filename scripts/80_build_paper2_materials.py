#!/usr/bin/env python3
"""Build Paper 2 TeX tables and a sensitivity figure from aggregate-only outputs."""

# ruff: noqa: E501

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = PROJECT_ROOT / "results" / "published" / "paper2_temporal_20261030"
READINESS = PROJECT_ROOT / "data" / "metadata" / "enron_temporal_hyperevent_readiness.json"
TABLE_DIR = PROJECT_ROOT / "manuscript" / "paper2" / "tables"
FIGURE_DIR = PROJECT_ROOT / "manuscript" / "paper2" / "figures"


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a required aggregate-only CSV file."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def latex_escape(value: str) -> str:
    """Escape a short literal label for TeX tabular material."""
    return value.replace("_", "\\_")


def fmt(value: float, digits: int = 3) -> str:
    """Format a compact signed-free decimal for TeX tables."""
    return f"{value:.{digits}f}"


def write(path: Path, contents: str) -> None:
    """Write a generated material file with a terminal newline."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents.rstrip() + "\n", encoding="utf-8")


def build_design_table(
    readiness: dict[str, object], collapsed_metrics: list[dict[str, str]]
) -> None:
    """Render the origin-safe cohort, folds, and footprint-collapse design table."""
    selected = readiness["selected_event_audit"]
    universe = readiness["selected_actor_universe"]
    folds = readiness["rolling_folds"]
    collapse_test = sum(
        int(row["choice_sets"])
        for row in collapsed_metrics
        if row["variant"] == "collapsed_timestamp_footprints_seed_20261030"
        and row["model"] == "DYADIC_HISTORY"
        and row["scope"] == "all"
    )
    fold_rows = "\n".join(
        f"{latex_escape(str(fold['fold']))} & {int(fold['training_events']):,} & {int(fold['test_events']):,} \\\\"
        for fold in folds
    )
    table = rf"""\begin{{table}}[t]
\centering
\caption{{Origin-safe Enron temporal event design. The 50-actor universe is ranked using sender-or-receiver participation strictly before 1 January 2001. The primary source-record representation preserves distinct projected records; the final row is an explicitly labelled representation sensitivity.}}
\label{{tab:design}}
\small
\begin{{tabular}}{{lrr}}
\toprule
Quantity & Primary & Footprint-collapse sensitivity \\
\midrule
Actor universe & {int(universe["core_size"])} & {int(universe["core_size"])} \\
Pre-origin retained events & {int(universe["pre_origin_retained_events"]):,} & --- \\
Events through 2001 & {int(selected["event_records"]):,} & 2,345 \\
Events with $|H|\geq2$ & {int(selected["multi_receiver_events"]):,} & 78 \\
Records in timestamp ties & {int(selected["records_in_timestamp_ties"]):,} & --- \\
Identical time--sender--head records removed & 0 & 2,886 \\
2001 test choice sets & {sum(int(fold["test_events"]) for fold in folds):,} & {collapse_test:,} \\
\bottomrule
\end{{tabular}}

\vspace{{0.6em}}
\begin{{tabular}}{{lrr}}
\toprule
Fold & Training events & Test events \\
\midrule
{fold_rows}
\bottomrule
\end{{tabular}}
\end{{table}}"""
    write(TABLE_DIR / "table_01_design.tex", table)


def build_primary_table(metrics: list[dict[str, str]]) -> None:
    """Render primary sampled-risk-set performance separately by event arity."""
    wanted = [
        row
        for row in metrics
        if row["variant"] == "primary_ascending_seed_20261030"
        and row["scope"] in {"all", "head_size_1", "head_size_ge_2"}
    ]
    model_order = {"DYADIC_HISTORY": 0, "GROUP_AUGMENTED": 1}
    scope_order = {"all": 0, "head_size_1": 1, "head_size_ge_2": 2}
    wanted.sort(key=lambda row: (scope_order[row["scope"]], model_order[row["model"]]))
    labels = {
        "all": "All receiver-set events",
        "head_size_1": "Singleton receiver",
        "head_size_ge_2": "Multiple receivers",
        "DYADIC_HISTORY": "Dyadic history",
        "GROUP_AUGMENTED": "Dyadic + group history",
    }
    rows = "\n".join(
        "{} & {} & {:,} & {} & {} & {} & {} \\\\".format(
            labels[row["scope"]],
            labels[row["model"]],
            int(row["choice_sets"]),
            fmt(float(row["mean_log_score"])),
            fmt(float(row["top1_tie_adjusted"])),
            fmt(float(row["mrr_tie_adjusted"])),
            fmt(float(row["mean_rank"])),
        )
        for row in wanted
    )
    table = rf"""\begin{{table}}[t]
\centering
\caption{{Primary conditional-sender RHEM evaluation, pooled over four expanding 2001 quarters. Every event is ranked only against Eventnet-sampled receiver sets of the same observed size for the observed sender. Metrics are therefore sampled-choice-set discrimination measures, not unconditional event probabilities.}}
\label{{tab:primary-rhem}}
\small
\begin{{tabular}}{{llrrrrr}}
\toprule
Scope & Model & Choice sets & Log score & Top-1 & MRR & Mean rank \\
\midrule
{rows}
\bottomrule
\end{{tabular}}
\end{{table}}"""
    write(TABLE_DIR / "table_02_primary_rhem.tex", table)


def build_sensitivity_table(contrasts: list[dict[str, str]]) -> None:
    """Render the group-versus-dyadic contrast sensitivity table for group events."""
    wanted = [row for row in contrasts if row["scope"] == "head_size_ge_2"]
    order = {
        "primary_ascending_seed_20261030": 0,
        "sampling_seed_20261031": 1,
        "descending_order_seed_20261030": 2,
        "collapsed_timestamp_footprints_seed_20261030": 3,
    }
    labels = {
        "primary_ascending_seed_20261030": "Primary: ascending order, seed 20261030",
        "sampling_seed_20261031": "Control-sampling seed 20261031",
        "descending_order_seed_20261030": "Descending tied-time order",
        "collapsed_timestamp_footprints_seed_20261030": "Collapse identical time--role footprints",
    }
    wanted.sort(key=lambda row: order[row["variant"]])
    rows = "\n".join(
        "{} & {:,} & {:+.3f} & {:+.3f} & {:+.3f} & {:+.3f} \\\\".format(
            labels[row["variant"]],
            int(row["choice_sets"]),
            float(row["delta_mean_log_score"]),
            float(row["delta_top1_tie_adjusted"]),
            float(row["delta_mrr_tie_adjusted"]),
            float(row["delta_mean_rank"]),
        )
        for row in wanted
    )
    table = rf"""\begin{{table}}[t]
\centering
\caption{{Sensitivity of the group-augmented minus dyadic-history comparison for multiple-receiver events. Positive log-score, Top-1, and MRR differences favor the group-augmented model; a negative mean-rank difference favors it. The final sensitivity changes the event representation itself, so it is not an uncertainty interval around the primary design.}}
\label{{tab:rhem-sensitivity}}
\small
\begin{{tabular}}{{lrrrrr}}
\toprule
Sensitivity & Choice sets & $\Delta$ log score & $\Delta$ Top-1 & $\Delta$ MRR & $\Delta$ rank \\
\midrule
{rows}
\bottomrule
\end{{tabular}}
\end{{table}}"""
    write(TABLE_DIR / "table_03_rhem_sensitivity.tex", table)


def build_btergm_table() -> None:
    """Render the limited existing temporal-ERGM diagnostic scope without overclaiming it."""
    table = r"""\begin{table}[H]
\centering
\caption{Status of the pre-existing bounded temporal-ERGM diagnostics. These short dyadic panel checks are retained as feasibility information for the temporal-ERGM companion, not as a rival event-level forecast or as coefficient evidence.}
\label{tab:btergm-boundary}
\small
\begin{tabular}{p{0.19\textwidth}rrp{0.53\textwidth}}
\toprule
Dataset & Nodes & Transitions & Diagnostic status \\
\midrule
Enron monthly core & 100 & 2 & 3/5 finite MPLE fits; higher-order specifications are nonfinite, so no substantive ERGM comparison is reported. \\
EU-core 30-day panel & 100 & 2 & 5/5 finite MPLE fits; a dyadic feasibility check only, with no native receiver sets observed. \\
\bottomrule
\end{tabular}
\end{table}"""
    write(TABLE_DIR / "table_04_btergm_boundary.tex", table)


def build_figure(contrasts: list[dict[str, str]]) -> None:
    """Plot the pooled multiple-receiver contrast across all predeclared sensitivities."""
    wanted = [row for row in contrasts if row["scope"] == "head_size_ge_2"]
    order = {
        "primary_ascending_seed_20261030": 0,
        "sampling_seed_20261031": 1,
        "descending_order_seed_20261030": 2,
        "collapsed_timestamp_footprints_seed_20261030": 3,
    }
    labels = ["Primary", "New seed", "Reverse ties", "Collapse records"]
    wanted.sort(key=lambda row: order[row["variant"]])
    log_scores = [float(row["delta_mean_log_score"]) for row in wanted]
    top1 = [float(row["delta_top1_tie_adjusted"]) for row in wanted]
    fig, axes = plt.subplots(1, 2, figsize=(8.7, 3.1), constrained_layout=True)
    colors = ["#1f4e79", "#3f7cac", "#6aa6c9", "#b65c4b"]
    x = list(range(len(wanted)))
    for axis, values, title, fmt_str in (
        (axes[0], log_scores, "Δ conditional log score", "+.2f"),
        (axes[1], top1, "Δ Top-1 accuracy", "+.2f"),
    ):
        bars = axis.bar(x, values, color=colors, width=0.65)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_xticks(x, labels, rotation=25, ha="right")
        axis.set_title(title, fontsize=10)
        axis.set_ylabel("Group-augmented minus dyadic")
        axis.grid(axis="y", alpha=0.25)
        for bar, value in zip(bars, values, strict=True):
            y = value + (0.03 * max(1, max(abs(v) for v in values)))
            if value < 0:
                y = value - (0.05 * max(1, max(abs(v) for v in values)))
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                y,
                format(value, fmt_str),
                ha="center",
                va="bottom" if value >= 0 else "top",
                fontsize=8,
            )
    fig.savefig(FIGURE_DIR / "figure_01_group_contrast_sensitivity.pdf", bbox_inches="tight")
    fig.savefig(
        FIGURE_DIR / "figure_01_group_contrast_sensitivity.png", dpi=220, bbox_inches="tight"
    )
    plt.close(fig)


def main() -> None:
    """Build every source-controlled Paper 2 table and figure."""
    if not PUBLISHED.is_dir() or not READINESS.is_file():
        raise SystemExit("STOP: required Paper 2 aggregate evidence has not been published.")
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    metrics = read_csv(PUBLISHED / "rhem_metrics_pooled.csv")
    contrasts = read_csv(PUBLISHED / "rhem_group_contrasts_pooled.csv")
    build_design_table(readiness, metrics)
    build_primary_table(metrics)
    build_sensitivity_table(contrasts)
    build_btergm_table()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    build_figure(contrasts)
    print("Paper 2 tables and figure complete.")
    print(f"Tables: {TABLE_DIR.relative_to(PROJECT_ROOT)}")
    print(f"Figures: {FIGURE_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
