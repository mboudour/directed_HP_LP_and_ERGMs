# ruff: noqa: E501
"""Supplementary table: hidden-supporter task with a full ranking (run_member_full.py).

Usage: python make_tables_member_full.py SUMMARY_MEMBER_FULL_JSON OUT_TEX
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]
ROWS = [("HM", "HM (two-mode ERGM)"), ("UM", "UM (undirected pairwise ERGM)"), ("M5", "M5"), ("S1", "S1"), ("LR", "LR"),
        ("coparticipation", "co-participation"), ("hpra", "HPRA"), ("cocitation", "co-citation"), ("weighted_pair", "weighted pair count"), ("indegree", "in-degree"),
        ("NHPD_maxmin", "NHP-D-maxmin+"), ("NHPD_mean", "NHP-D-mean"), ("NHPD_maxmin_r", "NHP-D-maxmin+, random training"), ("NHPD_mean_r", "NHP-D-mean, random training")]


def main(js, out):
    S = json.load(open(js))
    cols = [(c, m) for c, _ in CASES for m in ("MCAR", "MNAR-out")]
    L = ["\\begin{table}[tbp]", "\\centering", "\\scriptsize",
         "\\caption{Hidden-supporter task with a full ranking. Mean reciprocal rank of the hidden co-sponsor against all legislators active in the training data outside the bill (on average 95 to 98 in the Senates, chance about 0.054, and 445 in the House, chance about 0.015), means over ten random hidings per mechanism, and in the last three rows the reciprocal rank of NHP-D-maxmin+ trained as in the main design and on random alternatives, and of HM, when the hidden co-sponsor is one of the nine most active legislators. Random training denotes NHP-D trained on tasks with 19 alternatives drawn at random. The highest value in each column is in bold.}",
         "\\label{tab:member-fullrank}", "\\resizebox{\\textwidth}{!}{%", "\\begin{tabular}{l" + "r" * len(cols) + "}", "\\toprule",
         " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{lab}}}" for _, lab in CASES) + " \\\\",
         "Method & " + " & ".join("MCAR & MNAR-out" for _ in CASES) + " \\\\", "\\midrule"]
    best = {cm: max(v["mrr"] for k, v in S[cm[0]][cm[1]]["full"].items() if k != "contrasts") for cm in cols}
    for k, lab in ROWS:
        cells = []
        for cm in cols:
            v = S[cm[0]][cm[1]]["full"][k]["mrr"]
            cells.append(f"\\textbf{{{v:.3f}}}" if abs(v - best[cm]) < 1e-12 else f"{v:.3f}")
        L.append(f"{lab} & " + " & ".join(cells) + " \\\\")
        if k in ("LR", "indegree"):
            L.append("\\midrule")
    L.append("\\midrule")
    for k, lab in (("NHPD_maxmin", "NHP-D-maxmin+, hidden one of nine most active"), ("NHPD_maxmin_r", "NHP-D-maxmin+, random training, same tasks")):
        L.append(f"{lab} & " + " & ".join(f"{S[c][m]['full'][k]['mrr_top9']:.3f}" for c, m in cols) + " \\\\")
    L.append("HM, same tasks & " + " & ".join(f"{S[c][m]['full']['HM']['mrr_top9']:.3f}" for c, m in cols) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", "}", "\\end{table}"]
    open(out, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
