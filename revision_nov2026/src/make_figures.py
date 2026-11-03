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
    ("M6 sender-effect conditional $L_{1g}$", v("M6_L1g"), "#7a5195"),
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
ax.text(0.5, 0.94, "random arity-matched panel", ha="center", va="top", fontsize=9)
ax.text(2.5, 0.94, "grammar-preserving sponsor substitution", ha="center", va="top", fontsize=9)
fig.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8)
ax.grid(axis="y", alpha=0.25)
fig.subplots_adjust(bottom=0.09, top=0.88)
for ext in ("pdf", "png"):
    fig.savefig(f"{F}/fig2_senate_primary_pr_auc.{ext}", dpi=300)
print("figure written")
