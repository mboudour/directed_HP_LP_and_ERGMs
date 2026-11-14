"""Figure 2 (third run): concordance and top-1 gain over chance for selected scores in all cases.

Usage: python make_figures_v3.py SUMMARY_V3_JSON FIGURE_DIR [SUMMARY_GRID_JSON]

With the grid summary, the two-mode ERGM (HM; HR on the role-assignment sets) and the undirected
pairwise ERGM (UM, recognition sets only) are added.
"""

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

S = json.load(open(sys.argv[1]))
F = sys.argv[2]
G = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
CASES = [("s118", "S118"), ("s117", "S117"), ("s116", "S116"), ("h118", "H118")]
MECHS = [("MCAR", "MCAR"), ("MNAR-out", "MNAR")]
SERIES = [
    ("S1", "S1", "#7a5195", "o"),
    ("M5", "M5, selected decay", "#d97a22", "s"),
    ("M5_t05", "M5, decay 0.5", "#e8b07a", "x"),
    ("aa_total", "directed Adamic–Adar", "#174a7c", "^"),
    ("weighted_footprint", "weighted pair count", "#7a7a7a", "D"),
]
if G is not None:
    SERIES += [("HM", "two-mode ERGM (HM; HR for roles)", "#2a9d5c", "P"), ("UM", "undirected pairwise ERGM (UM)", "#c0392b", "v")]
PANELS = [
    ("random", "Random candidates (concordance)"),
    ("matched", "Party-matched candidates (concordance)"),
    ("perturb", "Head perturbation (concordance)"),
    ("role", "Role assignment (top-1 minus chance)"),
]
labels = [f"{c}\n{m}" for _, c in CASES for _, m in MECHS]
x = np.arange(len(labels))
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2), sharex=True)
for ax, (panel, title) in zip(axes.ravel(), PANELS, strict=False):
    for k, (key, lab, col, mk) in enumerate(SERIES):
        if key in ("HM", "UM"):
            if panel == "role":
                if key == "UM":
                    continue
                vals = [G[c][m]["role_top1"]["HR"] - S[c][m]["role"]["chance"]["top1"][0] for c, _ in CASES for m, _ in MECHS]
            else:
                vals = [G[c][m][panel][key] for c, _ in CASES for m, _ in MECHS]
        elif panel == "role":
            vals = [S[c][m]["role"][key]["top1"][0] - S[c][m]["role"]["chance"]["top1"][0] for c, _ in CASES for m, _ in MECHS]
        else:
            vals = [S[c][m][panel][key]["concordance"][0] for c, _ in CASES for m, _ in MECHS]
        ax.plot(x + (k - (len(SERIES) - 1) / 2) * 0.07, vals, mk, color=col, label=lab, markersize=5)
    ax.axhline(0.0 if panel == "role" else 0.5, color="#b5b5b5", linewidth=0.8, linestyle=":")
    for b in (1.5, 3.5, 5.5):
        ax.axvline(b, color="#e0e0e0", linewidth=0.8)
    ax.set_title(title, fontsize=9.5)
    ax.grid(axis="y", alpha=0.25)
    ax.set_xticks(x, labels, fontsize=7.5)
    ax.tick_params(axis="y", labelsize=8)
handles, labs = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labs, frameon=False, loc="upper center", ncol=4 if G is not None else 5, fontsize=8.5)
fig.subplots_adjust(top=0.88 if G is not None else 0.9, hspace=0.3, wspace=0.18, bottom=0.08)
for ext in ("pdf", "png"):
    fig.savefig(f"{F}/fig2_v3_cases.{ext}", dpi=300)
print("figure written")
