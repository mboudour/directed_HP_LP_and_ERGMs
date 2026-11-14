# ruff: noqa: E501
"""Supplementary table: valued ERGM of the weighted undirected 2-section (VM).

Usage: python make_tables_vm.py SUMMARY_VM_JSON OUT_TEX
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]
SETS = [("random", "R"), ("matched", "P"), ("perturb", "H")]


def main(js, out):
    U = json.load(open(js))
    hdr = "Case and mechanism & Set & VM & UM & HM & M5 & VM $-$ UM & HM $-$ VM \\\\"
    L = ["{\\scriptsize", "\\begin{longtable}{llrrrrll}",
         "\\caption{Valued ERGM of the weighted undirected 2-section (VM), a dyad-independent model with a Poisson reference measure and actor sociality, party, state and ideology terms. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets, means over 30 random hidings, with the undirected pairwise ERGM (UM), the two-mode ERGM (HM) and M5, and paired differences with 95\\% sponsor-bootstrap intervals.}\\label{tab:vm} \\\\",
         "\\toprule", hdr, "\\midrule", "\\endfirsthead", "\\toprule", hdr, "\\midrule", "\\endhead"]
    f = lambda x: f"{x[0]:.3f} [{x[1]:.3f}, {x[2]:.3f}]"
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            M = U[c][m]
            for i, (s, sl) in enumerate(SETS):
                v, ct = M[s], M[s + "_contrasts"]
                L.append(f"{lab + ', ' + m if i == 0 else ''} & {sl} & {v['VM']:.3f} & {v['UM']:.3f} & {v['HM']:.3f} & {v['M5']:.3f} & {f(ct['VM - UM'])} & {f(ct['HM - VM'])} \\\\")
            L.append("\\midrule")
    L[-1] = "\\bottomrule"
    L += ["\\end{longtable}", "}"]
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
