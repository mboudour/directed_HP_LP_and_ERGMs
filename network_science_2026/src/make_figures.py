"""Figure 2 of the manuscript from the 118th Senate summary (aggregate values only).

Usage: python make_figures.py RESULTS_DIR FIGURE_DIR
"""

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R, F = sys.argv[1], sys.argv[2]
S = json.load(open(f"{R}/s118/summary.json"))
S2 = json.load(open(f"{R}/s118_S/summary.json"))
for _m in S["mechs"]:
    for _p in ("random", "sub"):
        S["mechs"][_m]["pr_auc"][_p].update(
            {k: v for k, v in S2["mechs"][_m]["pr_auc"][_p].items() if k.startswith("S")}
        )
cols = [("random", "MCAR"), ("random", "MNAR-out"), ("sub", "MCAR"), ("sub", "MNAR-out")]


def v(key_random, key_sub=None):
    return [
        S["mechs"][m]["pr_auc"][p][key_random if p == "random" or key_sub is None else key_sub]
        for p, m in cols
    ]


series = [
    ("Strongest local reference", v("aa_total", "degprod"), "#174a7c"),
    ("Sponsor activity", v("sponsor_activity"), "#5b8cc0"),
    ("Same-party share", v("party_share"), "#7a7a7a"),
    ("M4c conditional $L_{1g}$", v("M4c_L1g"), "#d97a22"),
    ("M5 political conditional $L_{1g}$", v("M5_L1g"), "#21847e"),
    ("S1 sender–receiver conditional $L_{1g}$", v("S1_L1g"), "#7a5195"),
]
x = np.arange(4)
w = 0.135
fig, ax = plt.subplots(figsize=(10.2, 5.35))
for k, (lab, vals, c) in enumerate(series):
    bars = ax.bar(x + (k - 2.5) * w, vals, w, label=lab, color=c)
    ax.bar_label(
        bars, labels=[f"{h:.3f}" for h in bars.datavalues], padding=2, fontsize=6, rotation=90
    )
ax.set_ylabel("Mean PR-AUC across 30 matched masks")
ax.set_ylim(0.35, 0.95)
ax.set_xticks(x, ["MCAR", "MNAR-out", "MCAR", "MNAR-out"])
ax.axvline(1.5, color="#b5b5b5", linewidth=1)
ax.axhline(0.5, color="#b5b5b5", linewidth=0.8, linestyle=":")
ax.text(0.5, 0.94, "random panel (same number of co-sponsors)", ha="center", va="top", fontsize=9)
ax.text(2.5, 0.94, "sponsor substitution (same participants)", ha="center", va="top", fontsize=9)
fig.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8)
ax.grid(axis="y", alpha=0.25)
fig.subplots_adjust(bottom=0.09, top=0.88)
for ext in ("pdf", "png"):
    fig.savefig(f"{F}/fig2_senate_primary_pr_auc.{ext}", dpi=300)
print("figure written")

# ---------------------------------------------------------------- Figure 3: hyperarcs versus concepts  # noqa: E501
CA = json.load(open(f"{R}/concepts_all.json"))["s118"]["10"]
fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.4))
for ax, title, vals, labels, ylab in [
    (
        axes[0],
        "Hyperarcs and formal concepts",
        [CA["types"], CA["concepts"]],
        ["recorded\nhyperarcs", "formal\nconcepts"],
        "count",
    ),
    (
        axes[1],
        "Arcs in their footprints",
        [CA["type_arcs"], CA["concept_arcs"]],
        ["hyperarc\nfootprint arcs", "concept\nfootprint arcs"],
        "directed arcs",
    ),
]:
    bars = ax.bar([0, 1], vals, color=["#174a7c", "#d97a22"], width=0.62)
    ax.bar_label(bars, labels=[f"{v:,}" for v in vals], padding=3, fontsize=9)
    ax.set_xticks([0, 1], labels)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(ylab)
    ax.set_ylim(0, max(vals) * 1.15)
    ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(f"{F}/fig3_senate_concept_event_fidelity.{ext}", dpi=300)
print("figure 3 written")
