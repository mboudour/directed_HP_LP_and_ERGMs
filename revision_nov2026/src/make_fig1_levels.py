"""Figure 1: two levels (participation, leadership) x three representations, for two bills of one
sponsor s with co-sponsors {a, b} and {a, c}."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math

from matplotlib.patches import Ellipse, FancyArrowPatch, Polygon

pos = {"s": (0.0, 0.0), "a": (1.0, 0.55), "b": (1.0, -0.55), "c": (-0.15, 1.05)}
pos = {"s": (0.2, 0.0), "a": (1.2, 0.6), "b": (1.3, -0.6), "c": (0.0, 1.2)}
INK, MUTED, A1, A2 = "#1f2933", "#7b8794", "#2f6db5", "#c2552d"


def node(ax, k, xy=None, lab=None, fc="white"):
    x, y = xy or pos[k]
    ax.add_patch(plt.Circle((x, y), 0.13, fc=fc, ec=INK, lw=1.2, zorder=3))
    ax.text(x, y, lab or k, ha="center", va="center", fontsize=10, zorder=4, color=INK)


def edge(ax, u, v, color=INK, lw=1.2, ls="-"):
    (x1, y1), (x2, y2) = pos[u], pos[v]
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=ls, zorder=1)


def arrow(ax, p, q, color=INK, lw=1.3, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, color=color, lw=lw, ls=ls, shrinkA=10, shrinkB=10, zorder=2))


def blob(ax, ks, color):
    xs = [pos[k] for k in ks]
    cx = sum(x for x, _ in xs) / len(xs)
    cy = sum(y for _, y in xs) / len(xs)
    pts = [(cx + 1.35 * (x - cx), cy + 1.35 * (y - cy)) for x, y in xs]
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec=color, alpha=0.18, lw=1.5, joinstyle="round", zorder=0))


fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.6))
titles = [["(a) Hypergraph (participants)", "(b) 2-section (clique graph)", "(c) Incidence network"],
          ["(d) Directed hypergraph (roles)", "(e) Directed 2-section", "(f) Role-labelled incidence network"]]
for r in range(2):
    for c in range(3):
        ax = axes[r, c]
        ax.set_xlim(-0.6, 2.0)
        ax.set_ylim(-1.15, 1.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(titles[r][c], fontsize=10.5, color=INK)
# (a)
ax = axes[0, 0]
blob(ax, ["s", "a", "b"], A1)
blob(ax, ["s", "a", "c"], A2)
for k in pos:
    node(ax, k)
# (b)
ax = axes[0, 1]
for u, v in [("s", "a"), ("s", "b"), ("a", "b"), ("s", "c"), ("a", "c")]:
    edge(ax, u, v)
for k in pos:
    node(ax, k)
# (c) incidence
ax = axes[0, 2]
act = {"s": (0.0, 0.9), "a": (0.0, 0.3), "b": (0.0, -0.3), "c": (0.0, -0.9)}
rec = {"1": (1.4, 0.35), "2": (1.4, -0.35)}
mem = {"1": ["s", "a", "b"], "2": ["s", "a", "c"]}
for rcd, ks in mem.items():
    for k in ks:
        ax.plot([act[k][0], rec[rcd][0]], [act[k][1], rec[rcd][1]], color=A1 if rcd == "1" else A2, lw=1.3, zorder=1)
for k, xy in act.items():
    node(ax, k, xy)
for rcd, (x, y) in rec.items():
    ax.add_patch(plt.Rectangle((x - 0.13, y - 0.13), 0.26, 0.26, fc="white", ec=INK, lw=1.2, zorder=3))
    ax.text(x, y, f"$b_{rcd}$", ha="center", va="center", fontsize=10, zorder=4)
# (d) directed hyperarcs
ax = axes[1, 0]
def ell(ax, u, v, color):
    (x1, y1), (x2, y2) = pos[u], pos[v]
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    ax.add_patch(Ellipse((cx, cy), L + 0.55, 0.5, angle=ang, fc=color, ec=color, alpha=0.2, lw=1.5, zorder=0))
    return cx, cy


cab = ell(ax, "a", "b", A1)
cac = ell(ax, "a", "c", A2)
arrow(ax, pos["s"], (cab[0] - 0.12, cab[1]), A1, 1.8)
arrow(ax, pos["s"], (cac[0] - 0.05, cac[1] - 0.12), A2, 1.8)
for k in pos:
    node(ax, k, fc="#f5e6d3" if k == "s" else "white")
# (e) directed 2-section
ax = axes[1, 1]
for v in ["a", "b", "c"]:
    arrow(ax, pos["s"], pos[v])
for k in pos:
    node(ax, k, fc="#f5e6d3" if k == "s" else "white")
# (f) role-labelled incidence
ax = axes[1, 2]
for rcd, ks in mem.items():
    for k in ks:
        sponsor = k == "s"
        ax.plot([act[k][0], rec[rcd][0]], [act[k][1], rec[rcd][1]], color=A1 if rcd == "1" else A2, lw=2.6 if sponsor else 1.1, ls="-" if sponsor else (0, (3, 2)), zorder=1)
for k, xy in act.items():
    node(ax, k, xy, fc="#f5e6d3" if k == "s" else "white")
for rcd, (x, y) in rec.items():
    ax.add_patch(plt.Rectangle((x - 0.13, y - 0.13), 0.26, 0.26, fc="white", ec=INK, lw=1.2, zorder=3))
    ax.text(x, y, f"$b_{rcd}$", ha="center", va="center", fontsize=10, zorder=4)
fig.text(0.015, 0.73, "Participation", rotation=90, fontsize=11, color=INK, va="center", weight="bold")
fig.text(0.015, 0.27, "Leadership", rotation=90, fontsize=11, color=INK, va="center", weight="bold")
plt.tight_layout(rect=(0.03, 0, 1, 1))
plt.savefig("rev/figures/fig1_levels.pdf")
plt.savefig("check/fig1_levels.png", dpi=110)
