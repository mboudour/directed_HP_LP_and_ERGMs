# ruff: noqa: E501
"""Table comparing co-participation, computed from the records, with models of the 2-section.

Usage: python make_tables_coal.py SUMMARY_COAL_COSP_JSON OUTDIR
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]


def ci(v):
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


def table(S):
    out = ["\\begin{table}[tbp]", "\\centering", "\\small",
           "\\caption{Co-participation, computed from the observed hypergraph, against the best pairwise models and directed Adamic--Adar. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets, and the difference between co-participation and M5 with 95\\% sponsor-bootstrap intervals. Means over 30 random hidings.}",
           "\\label{tab:records}", "\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{llrrrrrlll}", "\\toprule",
           " & & \\multicolumn{5}{c}{Concordance on R} & \\multicolumn{3}{c}{Co-participation $-$ M5} \\\\",
           "Case & mechanism & co-part. & M5 & S1 & logistic & dir.\\ AA & R & P & H \\\\", "\\midrule"]
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            M = S[c][m]
            r = M["random"]
            d = []
            for s in ("random", "matched", "perturb"):
                mm, lo, hi = M[s + "_contrasts"]["M5 - coparticipation"]
                d.append([-mm, -hi, -lo])
            out.append(f"{lab} & {m} & {r['coparticipation']:.3f} & {r['M5']:.3f} & {r['S1']:.3f} & {r['LR']:.3f} & {r['aa_total']:.3f} & " + " & ".join(ci(v) for v in d) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "}",
            "\\par\\vspace{2pt}\\footnotesize Co-participation is the mean, over all pairs of participants of a candidate, of the number of observed bills in which both participate. Concordance of co-participation on the head-perturbation sets is 0.728 to 0.764 (Supplementary Table~S26).",
            "\\end{table}"]
    return "\n".join(out)


def supp(S):
    out = ["\\begin{table}[tbp]", "\\centering", "\\small",
           "\\caption{Concordance of co-participation and co-support similarity, by candidate set, with the models of the 2-section and directed Adamic--Adar. Means over 30 random hidings.}",
           "\\label{tab:records-full}", "\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{lllrrrrrr}", "\\toprule",
           "Case & mechanism & set & co-participation & co-support & M5 & S1 & logistic & dir.\\ AA \\\\", "\\midrule"]
    for c, lab in CASES:
        for m in ("MCAR", "MNAR-out"):
            for s, sl in (("random", "random"), ("matched", "party-matched"), ("perturb", "head perturbation")):
                r = S[c][m][s]
                lr = f"{r['LR']:.3f}" if "LR" in r else "--"
                out.append(f"{lab} & {m} & {sl} & {r['coparticipation']:.3f} & {r['cosupport']:.3f} & {r['M5']:.3f} & {r['S1']:.3f} & {lr} & {r['aa_total']:.3f} \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "}", "\\par\\vspace{2pt}\\footnotesize The logistic regression was not fitted to the party-matched sets.", "\\end{table}"]
    return "\n".join(out)


if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    open(f"{sys.argv[2]}/coal_records.tex", "w").write(table(S) + "\n")
    open(f"{sys.argv[2]}/coal_records_full.tex", "w").write(supp(S) + "\n")
