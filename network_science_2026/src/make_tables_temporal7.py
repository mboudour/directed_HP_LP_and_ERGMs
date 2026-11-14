# ruff: noqa: E501
"""Supplementary table: forecasting the last quarter (second forecast origin, TARGET_START=7).

Usage: python make_tables_temporal7.py SUMMARY_TEMPORAL7_JSON OUT_TEX
"""

import json
import sys

from make_tables_temporal import ci, tname

COSP = ["TERGM", "M5", "S1", "HM", "UM", "coparticipation"]
FEC = ["TERGM", "BS1", "BM", "LR", "cofunding"]
NAMES = {"TERGM": "TERGM", "M5": "M5", "S1": "S1", "HM": "HM (two-mode)", "UM": "UM (undirected pairwise)", "coparticipation": "co-participation", "BS1": "B1", "BM": "BM", "LR": "LR", "cofunding": "co-funding similarity"}


def rename(k):
    return k.replace("coparticipation", "co-participation").replace("cofunding", "co-funding").replace("BS1", "B1").replace("sponsor_bills", "most-bills rule")


def main(js, out):
    S = json.load(open(js))
    L = ["{\\scriptsize", "\\begin{longtable}{lll}",
         "\\caption{Forecasting the last quarter (second forecast origin), with all models trained on the first seven quarters. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets and top-1 accuracy on the role-assignment sets, paired contrasts with sponsor- or committee-bootstrap intervals, and estimates of the temporal ERGM with 95\\% bootstrap intervals over quarters (100 resamples).}\\label{tab:temporal7} \\\\",
         "\\toprule", "Case & Model, term or contrast & Value \\\\", "\\midrule", "\\endfirsthead", "\\toprule", "Case & Model, term or contrast & Value \\\\", "\\midrule", "\\endhead"]
    for c, lab in (("s118", "118th Senate"), ("h118", "118th House"), ("fec24", "Contributions 2023--24"), ("fec22", "Contributions 2021--22")):
        if c not in S:
            continue
        o = S[c]
        n = o["info"].get("evaluated")
        first = True
        for k in COSP if c[0] in "sh" else FEC:
            cells = ", ".join(f"{sl} {o[s][k]:.3f}" for s, sl in (("random", "R"), ("matched", "P"), ("perturb", "H")))
            if "role_top1" in o and k in o["role_top1"]:
                cells += f", top-1 {o['role_top1'][k]:.3f}"
            L.append(f"{lab + f' ({n} evaluated)' if first else ''} & {NAMES[k]} & {cells} \\\\")
            first = False
        if "role_top1" in o:
            L.append(f" & most-bills rule; chance & top-1 {o['role_top1']['sponsor_bills']:.3f}; {o['role_chance']:.3f} \\\\")
        for s, sl in (("random", "R"), ("matched", "P"), ("perturb", "H")):
            for k, v in o[s + "_contrasts"].items():
                L.append(f" & {rename(k)}, {sl} & {ci(v)} \\\\")
        for k, v in o.get("role_contrasts", {}).items():
            L.append(f" & {rename(k)}, top-1 & {ci(v)} \\\\")
        for row in o.get("tergm_coef", [])[1:]:
            L.append(f" & TERGM: {tname(row[0])} & {float(row[1]):.3f} [{float(row[2]):.3f}, {float(row[3]):.3f}] \\\\")
        L.append("\\midrule")
    L[-1] = "\\bottomrule"
    L += ["\\end{longtable}", "}"]
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
