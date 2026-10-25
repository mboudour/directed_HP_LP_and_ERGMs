#!/usr/bin/env python3
"""Render aggregate-only quantitative figures for the Network Science manuscript."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "manuscript" / "network_science" / "figures"

NAVY = "#174a7c"
ORANGE = "#d97a22"
GRAY = "#7a7a7a"
TEAL = "#21847e"


def parse_args() -> argparse.Namespace:
    """Parse output controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    """Resolve a project-relative path."""
    return path if path.is_absolute() else PROJECT_ROOT / path


def local_metric(frame: pd.DataFrame, mechanism: str, score: str) -> float:
    """Extract one PR-AUC aggregate local-score metric."""
    row = frame.loc[
        (frame["mechanism"] == mechanism)
        & (frame["score"] == score)
        & (frame["metric"] == "pr_auc"),
        "mean",
    ]
    if len(row) != 1:
        raise ValueError(f"Missing local metric: {mechanism}/{score}")
    return float(row.iloc[0])


def ergm_metric(frame: pd.DataFrame, panel: str, mechanism: str, model: str) -> float:
    """Extract one geometric conditional ERGM PR-AUC aggregate metric."""
    row = frame.loc[
        (frame["panel"] == panel)
        & (frame["mechanism"] == mechanism)
        & (frame["model"] == model)
        & (frame["score"] == "L1g")
        & (frame["metric"] == "pr_auc"),
        "mean",
    ]
    if len(row) != 1:
        raise ValueError(f"Missing ERGM metric: {panel}/{mechanism}/{model}")
    return float(row.iloc[0])


def save_both(fig: plt.Figure, stem: Path) -> None:
    """Save a publication vector figure and a convenient preview raster."""
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Build the two data-driven Senate figure panels."""
    args = parse_args()
    output_dir = resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    publication = PROJECT_ROOT / "results" / "published" / "network_science_20261025"
    heuristic = pd.read_csv(
        publication / "phase2/senate_118_s_bills_primary_heuristics/metric_summary.csv"
    )
    hard = pd.read_csv(
        publication / "phase2/senate_118_s_bills_primary_sponsor_substitution/metric_summary.csv"
    )
    ergm = pd.read_csv(
        publication / "models/senate_118_s_bills_primary_ergm_scores/metric_summary.csv"
    )
    m5 = pd.read_csv(
        publication / "models/senate_118_s_bills_primary_ergm_m5_scores/metric_summary.csv"
    )
    party_random = pd.read_csv(
        publication / "phase2/senate_118_s_bills_primary_same_party_random/metric_summary.csv"
    )
    party_hard = pd.read_csv(
        publication
        / "phase2/senate_118_s_bills_primary_same_party_sponsor_substitution/metric_summary.csv"
    )

    mechanisms = ("mcar", "mnar_out")
    labels = (
        "MCAR\nrandom",
        "MNAR-out\nrandom",
        "MCAR\nsponsor substitution",
        "MNAR-out\nsponsor substitution",
    )
    local_values = [
        local_metric(heuristic, "mcar", "lifted_adamic_adar_total_mean"),
        local_metric(heuristic, "mnar_out", "lifted_adamic_adar_total_mean"),
        local_metric(hard, "mcar", "lifted_degree_product_mean"),
        local_metric(hard, "mnar_out", "lifted_degree_product_mean"),
    ]
    ergm_values = [
        ergm_metric(ergm, "random", mechanisms[0], "M4c"),
        ergm_metric(ergm, "random", mechanisms[1], "M4c"),
        ergm_metric(ergm, "sponsor_substitution", mechanisms[0], "M4c"),
        ergm_metric(ergm, "sponsor_substitution", mechanisms[1], "M4c"),
    ]
    m5_values = [
        ergm_metric(m5, "random", mechanisms[0], "M5"),
        ergm_metric(m5, "random", mechanisms[1], "M5"),
        ergm_metric(m5, "sponsor_substitution", mechanisms[0], "M5"),
        ergm_metric(m5, "sponsor_substitution", mechanisms[1], "M5"),
    ]
    party_values = [
        local_metric(party_random, "mcar", "lifted_same_party_mean"),
        local_metric(party_random, "mnar_out", "lifted_same_party_mean"),
        local_metric(party_hard, "mcar", "lifted_same_party_mean"),
        local_metric(party_hard, "mnar_out", "lifted_same_party_mean"),
    ]
    x = np.arange(len(labels))
    width = 0.19
    fig, ax = plt.subplots(figsize=(10.2, 5.0))
    local_bars = ax.bar(
        x - 1.5 * width, local_values, width, label="Strongest local reference", color=NAVY
    )
    party_bars = ax.bar(x - 0.5 * width, party_values, width, label="Same-party share", color=GRAY)
    ergm_bars = ax.bar(
        x + 0.5 * width, ergm_values, width, label="M4c conditional $L_{1g}$", color=ORANGE
    )
    m5_bars = ax.bar(
        x + 1.5 * width, m5_values, width, label="M5 political conditional $L_{1g}$", color=TEAL
    )
    ax.set_ylabel("Mean PR-AUC across 30 matched masks")
    ax.set_ylim(0.35, 0.90)
    ax.set_xticks(x, labels)
    ax.axvline(1.5, color="#b5b5b5", linewidth=1)
    ax.text(0.5, 0.885, "random arity-matched panel", ha="center", va="top", fontsize=9)
    ax.text(
        2.5, 0.885, "grammar-preserving sponsor substitution", ha="center", va="top", fontsize=9
    )
    ax.legend(frameon=False, loc="lower left", ncol=2, fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    for bars in (local_bars, party_bars, ergm_bars, m5_bars):
        ax.bar_label(
            bars, labels=[f"{height:.3f}" for height in bars.datavalues], padding=2, fontsize=7
        )
    fig.tight_layout()
    save_both(fig, output_dir / "fig2_senate_primary_pr_auc")

    import json

    fidelity_data = json.loads(
        (
            publication
            / "phase2/senate_118_s_bills_native_event_fidelity_tail3_head10/summary.json"
        ).read_text()
    )
    formal_count = fidelity_data["formal_concepts"]["count"]
    event_count = fidelity_data["native_events"]["cap_eligible_event_types"]
    concept_arcs = fidelity_data["footprint_agreement"]["formal_concept_footprint_arcs"]
    event_arcs = fidelity_data["footprint_agreement"]["native_event_cap_footprint_arcs"]
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.25))
    axes[0].bar([0, 1], [event_count, formal_count], color=[NAVY, ORANGE], width=0.62)
    axes[0].set_xticks([0, 1], ["recorded bill\ntypes", "formal\nconcepts"])
    axes[0].set_ylabel("count")
    axes[0].set_title("Ordered group structures")
    for position, value in enumerate([event_count, formal_count]):
        axes[0].text(position, value + 90, f"{value:,}", ha="center", va="bottom", fontsize=9)
    axes[0].set_ylim(0, event_count * 1.12)
    axes[0].grid(axis="y", alpha=0.22)
    axes[1].bar([0, 1], [event_arcs, concept_arcs], color=[NAVY, ORANGE], width=0.62)
    axes[1].set_xticks([0, 1], ["bill\nfootprint arcs", "concept\nfootprint arcs"])
    axes[1].set_ylabel("directed arcs")
    axes[1].set_title("Projected dyadic support")
    for position, value in enumerate([event_arcs, concept_arcs]):
        axes[1].text(position, value + 130, f"{value:,}", ha="center", va="bottom", fontsize=9)
    axes[1].set_ylim(0, event_arcs * 1.12)
    axes[1].grid(axis="y", alpha=0.22)
    fig.tight_layout()
    save_both(fig, output_dir / "fig3_senate_concept_event_fidelity")
    print(f"Network Science quantitative figures written: {output_dir}")


if __name__ == "__main__":
    main()
