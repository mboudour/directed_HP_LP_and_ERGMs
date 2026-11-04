# ruff: noqa: E501
"""Counts versus binary: summary of run_counts against the binary pairwise models and HM.

For each case and mechanism, mean concordance over 30 random hidings of M5, S1 and LR with and without
the log co-membership count as an edge covariate (suffix c), and of HM, on the random,
party-matched and head-perturbation sets, with sponsor-bootstrap intervals for the contrasts
HM - M5c, HM - S1c, HM - LRc, M5c - M5, S1c - S1 and LRc - LR. Also writes the LaTeX table.

Usage: python summary_counts.py RESULTS_DIR OUT_JSON OUT_TEX
"""

import json
import os
import pickle
import sys

import numpy as np
from summary_grid import merged
from summary_v3 import cluster_boot, win

CASES = ["s118", "s117", "s116", "h118"]
KEYS = ["M5", "M5c", "S1", "S1c", "LR", "LRc", "HM", "UMc"]
CONTRASTS = [("HM", "M5c"), ("HM", "S1c"), ("HM", "LRc"), ("M5c", "M5"), ("S1c", "S1"), ("LRc", "LR")]
LABS = {"s118": "118th Senate", "s117": "117th Senate", "s116": "116th Senate", "h118": "118th House"}


def load(res, case, mech, rep):
    base = merged(res, case, mech, rep)
    c = pickle.load(open(f"{res}/counts_{case}/{mech}_{rep:02d}.pkl", "rb"))
    out = {}
    for s in ("random", "matched", "perturb"):
        rows = []
        for (p, q, sp), (pc, qc) in zip(base[s], c[s], strict=True):
            assert abs(p["weighted_footprint"] - pc["weighted_footprint"]) < 1e-9
            rows.append(({**p, **pc}, {**q, **qc}, sp))
        out[s] = rows
    return out


def main(res, out_json, out_tex):
    S = {}
    for case in CASES:
        if not all(os.path.exists(f"{res}/counts_{case}/{m}_30.pkl") for m in ("MCAR", "MNAR-out")):
            continue
        S[case] = {}
        for mech in ("MCAR", "MNAR-out"):
            rs = [load(res, case, mech, r) for r in range(1, 31)]
            M = {}
            for s in ("random", "matched", "perturb"):
                keys = [k for k in KEYS if k in rs[0][s][0][0]]
                M[s] = {k: float(np.mean([win(r[s], k).mean() for r in rs])) for k in keys}
                spon = [np.array([p[2] for p in r[s]]) for r in rs]
                M[s + "_contrasts"] = {}
                for x, y in CONTRASTS:
                    if x not in keys or y not in keys:
                        continue
                    vec = [win(r[s], x) - win(r[s], y) for r in rs]
                    M[s + "_contrasts"][f"{x} - {y}"] = [float(np.mean([v.mean() for v in vec])), *cluster_boot(vec, spon)]
            S[case][mech] = M
    json.dump(S, open(out_json, "w"), indent=1)
    t = ["\\begin{table}[tbp]", "\\centering", "\\small",
         "\\caption{Pairwise models with co-membership counts. Concordance of M5, S1 and the logistic regression (LR) without and with the logarithm of the number of training bills shared by the two legislators as an edge covariate (suffix c), and of the two-mode ERGM (HM), on the random (R), party-matched (P) and head-perturbation (H) sets. Means over 30 random hidings; LR without the count covariate was not scored on the party-matched sets.}",
         "\\label{tab:counts}", "\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{ll" + "r" * 21 + "}", "\\toprule",
         " & & \\multicolumn{7}{c}{R} & \\multicolumn{7}{c}{P} & \\multicolumn{7}{c}{H} \\\\",
         "Case & Mechanism" + " & M5 & M5c & S1 & S1c & LR & LRc & HM" * 3 + " \\\\", "\\midrule"]
    for case, o in S.items():
        for i, mech in enumerate(("MCAR", "MNAR-out")):
            cells = [f"{o[mech][s][k]:.3f}" if k in o[mech][s] else "--" for s in ("random", "matched", "perturb") for k in ("M5", "M5c", "S1", "S1c", "LR", "LRc", "HM")]
            t.append(f"{LABS[case] if i == 0 else ''} & {mech} & " + " & ".join(cells) + " \\\\")
    t += ["\\bottomrule", "\\end{tabular}", "}", "\\end{table}"]
    open(out_tex, "w").write("\n".join(t) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
