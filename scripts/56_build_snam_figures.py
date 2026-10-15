#!/usr/bin/env python3
"""Build aggregate-only figures for the Paper 1 SNAM TeX manuscript."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "manuscript" / "tables"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "manuscript" / "snam" / "figures"

COLORS = {
    "M4c::L1g": "#1f4e79",
    "Directed Adamic-Adar total": "#cc6f00",
    "Reverse-arc mean": "#2c7a4b",
    "M0::L1": "#6b7280",
    "Enron": "#1f4e79",
    "MathOverflow": "#bd5d00",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for PDF and PNG figures.",
    )
    return parser.parse_args()


def save_figure(figure: plt.Figure, output_dir: Path, stem: str) -> None:
    """Write a vector PDF and a high-resolution PNG rendering."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in (("pdf", {}), ("png", {"dpi": 300})):
        figure.savefig(
            output_dir / f"{stem}.{suffix}",
            bbox_inches="tight",
            facecolor="white",
            **kwargs,
        )
    plt.close(figure)


def add_box(
    axis: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str,
    edgecolor: str = "#1f2937",
    textcolor: str = "#111827",
    fontsize: float = 10.0,
) -> None:
    """Place a rounded labelled rectangle in normalized axis coordinates."""
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        linewidth=1.1,
        facecolor=facecolor,
        edgecolor=edgecolor,
        transform=axis.transAxes,
        zorder=2,
    )
    axis.add_patch(patch)
    axis.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        transform=axis.transAxes,
        fontsize=fontsize,
        color=textcolor,
        linespacing=1.28,
        zorder=3,
    )


def add_arrow(
    axis: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    linestyle: str = "solid",
    color: str = "#374151",
) -> None:
    """Draw an explanatory arrow in normalized axis coordinates."""
    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.25,
            linestyle=linestyle,
            color=color,
            transform=axis.transAxes,
            zorder=1,
        )
    )


def build_target_ladder(output_dir: Path) -> None:
    """Render the conceptual target ladder and conditional-score boundary."""
    figure, axis = plt.subplots(figsize=(10.6, 5.8))
    axis.set_axis_off()

    add_box(
        axis,
        (0.04, 0.63),
        0.26,
        0.23,
        "Recorded native event\n$e=(T,H)$\nordered tail and head roles",
        facecolor="#e8f1fb",
        fontsize=10.2,
    )
    add_box(
        axis,
        (0.37, 0.63),
        0.26,
        0.23,
        "Directed footprint\n$\\pi(e)=T\\times H$\ndirected dyads induced by $e$",
        facecolor="#eaf6ee",
        fontsize=10.2,
    )
    add_box(
        axis,
        (0.70, 0.63),
        0.26,
        0.23,
        "Aggregate relation\n$A=\\bigcup_{e\\in\\mathcal{E}}\\pi(e)$\nstatic directed graph",
        facecolor="#fff4df",
        fontsize=10.0,
    )
    add_arrow(axis, (0.30, 0.745), (0.37, 0.745))
    add_arrow(axis, (0.63, 0.745), (0.70, 0.745))
    axis.text(
        0.335,
        0.79,
        "projection",
        transform=axis.transAxes,
        ha="center",
        va="center",
        fontsize=9.0,
        color="#374151",
    )
    axis.text(
        0.665,
        0.79,
        "aggregate",
        transform=axis.transAxes,
        ha="center",
        va="center",
        fontsize=9.0,
        color="#374151",
    )

    add_box(
        axis,
        (0.70, 0.27),
        0.26,
        0.20,
        "Cap-first formal concept\n"
        "$(T,H): T^{\\uparrow}=H,\\ H^{\\downarrow}=T$\n"
        "derived maximal rectangle",
        facecolor="#fff4df",
        fontsize=9.7,
    )
    add_arrow(axis, (0.83, 0.63), (0.83, 0.47), linestyle="dashed")
    axis.text(
        0.845,
        0.545,
        "derive",
        transform=axis.transAxes,
        fontsize=9.0,
        color="#374151",
    )

    add_box(
        axis,
        (0.04, 0.23),
        0.34,
        0.22,
        "Directed local scores and ERGM\n"
        "conditional dyad scores $p_{ij}$\n"
        "computed on an observed graph",
        facecolor="#f3eafa",
        fontsize=10.0,
    )
    add_box(
        axis,
        (0.43, 0.23),
        0.25,
        0.22,
        "Footprint summaries\n"
        "$L_1$, $L_{1g}$, $L_2^{\\mathrm{fac}}$\n"
        "conditional-score constructions",
        facecolor="#f3eafa",
        fontsize=10.0,
    )
    add_arrow(axis, (0.38, 0.34), (0.43, 0.34), color="#5b3b79")
    add_arrow(axis, (0.50, 0.63), (0.50, 0.45), linestyle="dotted", color="#5b3b79")
    axis.text(
        0.515,
        0.53,
        "score\nfootprint",
        transform=axis.transAxes,
        fontsize=8.8,
        color="#5b3b79",
    )

    axis.text(
        0.50,
        0.085,
        "Target boundary: dyadic-footprint support is neither native-event recovery "
        "nor a joint event probability.",
        transform=axis.transAxes,
        ha="center",
        va="center",
        fontsize=10.3,
        color="#7f1d1d",
        fontweight="bold",
    )
    axis.set_title(
        "Fig. 1  Target ladder and conditional-score boundary",
        fontsize=13.0,
        fontweight="bold",
        loc="left",
        pad=12,
    )
    save_figure(figure, output_dir, "Fig1_target_ladder")


def build_fidelity_figure(output_dir: Path) -> None:
    """Render target-fidelity diagnostics from aggregate-only table inputs."""
    data = pd.read_csv(TABLES_DIR / "table_02_concept_event_fidelity.csv")
    metrics = [
        ("Concept precision (exact tail/head)", "concept_precision"),
        ("Native-type recall (exact tail/head)", "native_type_recall"),
        ("Footprint Jaccard", "footprint_jaccard"),
        ("Native footprint covered by concepts", "native_footprint_covered_by_concepts"),
        (
            "Concept footprint covered by native events",
            "concept_footprint_covered_by_native_events",
        ),
    ]
    figure, axis = plt.subplots(figsize=(10.8, 5.4))
    positions = np.arange(len(metrics))
    width = 0.34
    for offset, (_, row), label, color in zip(
        (-width / 2, width / 2),
        data.iterrows(),
        ("Enron", "MathOverflow"),
        (COLORS["Enron"], COLORS["MathOverflow"]),
        strict=True,
    ):
        values = [float(row[column]) for _, column in metrics]
        bars = axis.barh(
            positions + offset,
            values,
            height=width,
            color=color,
            alpha=0.88,
            label=label,
        )
        for bar, value in zip(bars, values, strict=True):
            x = 0.012 if value == 0 else min(value + 0.015, 1.035)
            axis.text(
                x,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.3f}",
                ha="left",
                va="center",
                fontsize=9.0,
                fontweight="bold" if value == 0 else "normal",
            )
    axis.axvline(0.5, color="#9ca3af", linewidth=0.9, linestyle="--", zorder=0)
    axis.set_xlim(0, 1.10)
    axis.set_yticks(positions, [label for label, _ in metrics], fontsize=9.5)
    axis.invert_yaxis()
    axis.set_xlabel("Proportion", fontsize=10.5)
    axis.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=2,
        frameon=False,
        fontsize=9.5,
    )
    exact_note = "Exact tail/head matches: Enron 0 of 232 concepts; MathOverflow 0 of 207 concepts."
    figure.text(
        0.50,
        0.045,
        exact_note + " Formal concepts are not recovered native events.",
        ha="center",
        va="center",
        fontsize=9.2,
        color="#7f1d1d",
    )
    figure.suptitle(
        "Fig. 2  Formal-concept fidelity: footprint agreement without exact event recovery",
        x=0.08,
        ha="left",
        fontsize=13.0,
        fontweight="bold",
        y=0.985,
    )
    figure.subplots_adjust(bottom=0.25, top=0.86, left=0.31, right=0.96)
    save_figure(figure, output_dir, "Fig2_concept_event_fidelity")


def build_panel_figure(output_dir: Path) -> None:
    """Render primary random and directional hard-panel PR-AUC profiles."""
    random_data = pd.read_csv(TABLES_DIR / "table_03a_primary_native_random_panel_pr_auc.csv")
    hard_data = pd.read_csv(TABLES_DIR / "table_03b_primary_native_hard_panel_pr_auc.csv")
    methods = [
        "M4c::L1g",
        "Directed Adamic-Adar total",
        "Reverse-arc mean",
        "M0::L1",
    ]
    panels = ["Random arity-matched", "Reversal/orientation", "Role exchange"]
    conditions = [
        ("Enron strict custodian core", "MCAR", "Enron: MCAR"),
        ("Enron strict custodian core", "MNAR-out", "Enron: MNAR-out"),
        ("MathOverflow reconstructed core", "MCAR", "MathOverflow: MCAR"),
        ("MathOverflow reconstructed core", "MNAR-out", "MathOverflow: MNAR-out"),
    ]
    figure, axes = plt.subplots(2, 2, figsize=(11.2, 8.2), sharex=True, sharey=True)
    x = np.arange(len(panels))

    for axis, (dataset, mechanism, subtitle) in zip(axes.ravel(), conditions, strict=True):
        current_random = random_data.loc[
            (random_data["dataset"] == dataset) & (random_data["mechanism"] == mechanism)
        ]
        current_hard = hard_data.loc[
            (hard_data["dataset"] == dataset) & (hard_data["mechanism"] == mechanism)
        ]
        for method in methods:
            values: list[float] = []
            for panel in panels:
                source = current_random if panel == "Random arity-matched" else current_hard
                selected = source.loc[
                    (source["panel"] == panel) & (source["method"] == method),
                    "pr_auc_mean",
                ]
                if len(selected) != 1:
                    raise ValueError(
                        f"Expected one value for {dataset}, {mechanism}, {panel}, {method}; "
                        f"found {len(selected)}"
                    )
                values.append(float(selected.iloc[0]))
            linestyle = "--" if method == "M0::L1" else "-"
            marker = "s" if method == "M0::L1" else "o"
            axis.plot(
                x,
                values,
                label=method,
                color=COLORS[method],
                marker=marker,
                markersize=5.8,
                linewidth=2.0,
                linestyle=linestyle,
            )
        axis.axhline(0.5, color="#9ca3af", linewidth=0.9, linestyle=":", zorder=0)
        axis.set_ylim(0.40, 0.91)
        axis.set_xticks(
            x, ["Random\narity-matched", "Reversal /\norientation", "Role\nexchange"], fontsize=8.8
        )
        axis.grid(axis="y", color="#e5e7eb", linewidth=0.8)
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)
        axis.set_title(subtitle, fontsize=10.6, fontweight="bold")

    axes[0, 0].set_ylabel("PR-AUC", fontsize=10.5)
    axes[1, 0].set_ylabel("PR-AUC", fontsize=10.5)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(
        handles,
        labels,
        loc="lower center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.012),
        fontsize=9.3,
    )
    figure.suptitle(
        "Fig. 3  Random-panel footprint discrimination need not transfer to "
        "directional hard panels",
        x=0.08,
        ha="left",
        fontsize=13.0,
        fontweight="bold",
        y=0.985,
    )
    figure.text(
        0.50,
        0.085,
        "Means over 30 fixed masks per dataset and mechanism. The 0.50 line is the "
        "balanced-panel reference; hard panels are selected, role-sensitive subsets and "
        "are not interchangeable with the random panel.",
        ha="center",
        va="center",
        fontsize=8.6,
    )
    figure.subplots_adjust(bottom=0.18, top=0.90, hspace=0.34, wspace=0.15)
    save_figure(figure, output_dir, "Fig3_primary_panel_profiles")


def main() -> None:
    """Build all manuscript figures from aggregate-only input tables."""
    args = parse_args()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.labelcolor": "#111827",
            "text.color": "#111827",
        }
    )
    build_target_ladder(args.output_dir)
    build_fidelity_figure(args.output_dir)
    build_panel_figure(args.output_dir)
    print(f"Wrote 3 PDF/PNG figure pairs to {args.output_dir}")


if __name__ == "__main__":
    main()
