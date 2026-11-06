# ruff: noqa: E501
"""Supplementary table: two-mode ERGM and directed ERGMs trained on all bills.

Usage: python make_tables_hm_uncap.py SUMMARY_HM_UNCAP_JSON OUT_TEX
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]
SETS = [("random", "R"), ("matched", "P"), ("perturb", "H")]


def main(js, out):
    U = json.load(open(js))
    L = ["{\\scriptsize", "\\begin{longtable}{llrrrrrll}",
         "\\caption{Training on bills of all sizes. Concordance of the two-mode ERGM (HM), M5, S1 and the weighted pair count on the random (R), party-matched (P) and head-perturbation (H) sets when all bills, including those with more than ten original co-sponsors, are used for training, means over 30 random hidings, and paired differences of HM with M5 and S1 with 95\\% sponsor-bootstrap intervals.}\\label{tab:hm-uncap} \\\\",
         "\\toprule", "Case and mechanism & Set & HM & HM0 & M5 & S1 & Weighted & HM $-$ M5 & HM $-$ S1 \\\\", "\\midrule", "\\endfirsthead",
         "\\toprule", "Case and mechanism & Set & HM & HM0 & M5 & S1 & Weighted & HM $-$ M5 & HM $-$ S1 \\\\", "\\midrule", "\\endhead"]
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            M = U[c][m]
            for i, (s, sl) in enumerate(SETS):
                v = M[s]
                ct = M[s + "_contrasts"]
                f = lambda x: f"{x[0]:.3f} [{x[1]:.3f}, {x[2]:.3f}]"
                head = f"{lab}, {m}" if i == 0 else ""
                L.append(f"{head} & {sl} & {v['HM']:.3f} & {v['HM0']:.3f} & {v['M5']:.3f} & {v['S1']:.3f} & {v['weighted_footprint']:.3f} & {f(ct['HM - M5'])} & {f(ct['HM - S1'])} \\\\")
            L.append("\\midrule")
    L[-1] = "\\bottomrule"
    L += ["\\end{longtable}", "}"]
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
