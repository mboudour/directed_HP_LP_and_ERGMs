# ruff: noqa: E501
"""Supplementary table: two-mode ERGM for campaign contributions.

Usage: python make_tables_hm_fec.py SUMMARY_HM_FEC_JSON OUT_TEX
"""

import json
import sys

CYC = [("fec24", "2023--24"), ("fec22", "2021--22")]
SETS = [("random", "R"), ("matched", "P"), ("perturb", "H")]


def main(js, out):
    U = json.load(open(js))
    hdr = "Cycle and mechanism & Set & HM & HM0 & BM & B1 & LR & Co-funding & HM $-$ BM & HM $-$ B1 & co-funding $-$ HM \\\\"
    L = ["{\\scriptsize", "\\begin{longtable}{llrrrrrrlll}",
         "\\caption{Two-mode ERGM for campaign contributions (HM; HM0 without the closure terms), an ERGM of the ties of candidates to batches given their committees fitted by pseudolikelihood with case-control sampling. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets, means over 20 random hidings, and paired differences with 95\\% committee-bootstrap intervals.}\\label{tab:hm-fec} \\\\",
         "\\toprule", hdr, "\\midrule", "\\endfirsthead", "\\toprule", hdr, "\\midrule", "\\endhead"]
    f = lambda x: f"{x[0]:.3f} [{x[1]:.3f}, {x[2]:.3f}]"
    for c, lab in CYC:
        for m in ("MCAR", "MNAR-out"):
            M = U[c][m]
            for i, (s, sl) in enumerate(SETS):
                v, ct = M[s], M[s + "_contrasts"]
                L.append(f"{lab + ', ' + m if i == 0 else ''} & {sl} & {v['HM']:.3f} & {v['HM0']:.3f} & {v['BM']:.3f} & {v['BS1']:.3f} & {v['LR']:.3f} & {v['cofunding']:.3f} & {f(ct['HM - BM'])} & {f(ct['HM - BS1'])} & {f(ct['cofunding - HM'])} \\\\")
            L.append("\\midrule")
    L[-1] = "\\bottomrule"
    L += ["\\end{longtable}", "}"]
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
