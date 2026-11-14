# ruff: noqa: E501
"""Main-text table of pairwise and higher-order, undirected and directed ERGMs.

Usage: python make_tables_grid.py SUMMARY_GRID_JSON OUTDIR
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]


def ci(v):
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


def table(S):
    out = ["\\begin{table}[tbp]", "\\centering", "\\small",
           "\\caption{Pairwise and higher-order ERGMs. Concordance on the random (R) and head-perturbation (H) sets for the undirected pairwise ERGM (UM), the directed pairwise ERGMs (M5, S1) and the two-mode ERGM (HM); the difference HM $-$ M5 with 95\\% sponsor-bootstrap intervals; and top-1 accuracy of S1 and the role-labelled two-mode ERGM (HR) on the role-assignment sets. Means over 30 random hidings.}",
           "\\label{tab:grid}", "\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{llrrrrrrrrllrr}", "\\toprule",
           " & & \\multicolumn{4}{c}{R} & \\multicolumn{4}{c}{H} & \\multicolumn{2}{c}{HM $-$ M5} & \\multicolumn{2}{c}{Top-1} \\\\",
           "Case & mechanism & UM & M5 & S1 & HM & UM & M5 & S1 & HM & R & H & S1 & HR \\\\", "\\midrule"]
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            M = S[c][m]
            r, h = M["random"], M["perturb"]
            cells = [f"{r[k]:.3f}" for k in ("UM", "M5", "S1", "HM")] + [f"{h[k]:.3f}" for k in ("UM", "M5", "S1", "HM")]
            cells += [ci(M["random_contrasts"]["HM - M5"]), ci(M["perturb_contrasts"]["HM - M5"])]
            cells += [f"{M['role_top1']['S1']:.3f}", f"{M['role_top1']['HR']:.3f}"]
            out.append(f"{lab} & {m} & " + " & ".join(cells) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "}",
            "\\par\\vspace{2pt}\\footnotesize Contrasts on the party-matched sets, contrasts with HM0, co-participation and the logistic regression, and intervals for HR are in Supplementary Table~S27.",
            "\\end{table}"]
    return "\n".join(out)


def supp(S):
    out = ["{\\scriptsize", "\\begin{longtable}{lllll}",
           "\\caption{Pairwise and higher-order ERGMs, paired contrasts with 95\\% sponsor-bootstrap intervals on the random, party-matched and head-perturbation sets, and initiator identification by the role-labelled two-mode ERGM (HR).}\\label{tab:grid-full} \\\\",
           "\\toprule", "Case, mechanism & Contrast & random & party-matched & head perturbation \\\\", "\\midrule", "\\endfirsthead",
           "\\toprule", "Case, mechanism & Contrast & random & party-matched & head perturbation \\\\", "\\midrule", "\\endhead"]
    keys = [("HM - M5", "HM $-$ M5"), ("HM - S1", "HM $-$ S1"), ("HM - HM0", "HM $-$ HM0"), ("HM - coparticipation", "HM $-$ co-participation"), ("M5 - UM", "M5 $-$ UM"), ("HM - UM", "HM $-$ UM"), ("HM - LR", "HM $-$ logistic")]
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            M = S[c][m]
            for i, (k, kl) in enumerate(keys):
                cells = [ci(M[s + "_contrasts"][k]) if k in M[s + "_contrasts"] else "--" for s in ("random", "matched", "perturb")]
                out.append(f"{lab + ', ' + m if i == 0 else ''} & {kl} & " + " & ".join(cells) + " \\\\")
            rc, sc = M["role_contrasts"], M["sub_contrasts"]
            out.append(f" & HR $-$ S1, top-1 & {ci(rc['HR - S1'])} & HR $-$ S1, substitution & {ci(sc['HR - S1'])} \\\\")
            out.append(f" & HR $-$ most-bills rule, top-1 & {ci(rc['HR - sponsor_bills'])} & & \\\\")
            out.append("\\midrule")
    out[-1] = "\\bottomrule"
    out += ["\\end{longtable}", "}"]
    return "\n".join(out)


if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    open(f"{sys.argv[2]}/grid.tex", "w").write(table(S) + "\n")
    open(f"{sys.argv[2]}/grid_full.tex", "w").write(supp(S) + "\n")
