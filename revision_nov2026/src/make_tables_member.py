# ruff: noqa: E501
"""Tables for the hidden-supporter task.

Usage: python make_tables_member.py SUMMARY_MEMBER_JSON OUTDIR
"""

import json
import sys

CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House"), ("fec24", "Contributions 2023--24"), ("fec22", "Contributions 2021--22")]
ROWS = [
    ("HM", "HM (two-mode ERGM)"), ("UM", "UM (undirected ERGM)"), ("M5", "M5"), ("S1", "S1"), ("BM", "BM"), ("BS1", "B1"), ("LR", "LR"),
    ("NHPD_maxmin", "NHP-D-maxmin+"), ("NHPD_mean", "NHP-D-mean"),
    ("coparticipation", "co-participation"), ("hpra", "HPRA"), ("cocitation", "co-citation"),
    ("cofunding", "co-funding similarity"), ("weighted_pair", "weighted pair count"), ("aa_total", "directed Adamic--Adar"), ("path3", "three-paths"), ("indegree", "in-degree"),
]
MECH = [("MCAR", "MCAR"), ("MNAR-out", "MNAR-out")]


def best(S, case, mech, sub):
    return max(v["mrr"] for k, v in S[case][mech][sub].items() if k != "contrasts")


def cell(S, c, m, sub, k):
    v = S[c][m][sub].get(k, {}).get("mrr")
    if v is None:
        return "--"
    t = f"{v:.3f}"
    return f"\\textbf{{{t}}}" if abs(v - best(S, c, m, sub)) < 1e-12 else t


def main_table(S, mech="MCAR", label="tab:member"):
    cases = [c for c in CASES if c[0] in S and mech in S[c[0]]]
    caption = ("Hidden-supporter task. Mean reciprocal rank of the hidden supporter, given the initiator and the other supporters, against all 19 alternatives (All, chance 0.180) and against the 10 alternatives drawn at random only (Random, chance 0.274), bills or batches hidden at random (MCAR), means over ten random hidings for co-sponsorship and five for contributions. The highest value in each column is in bold."
               if mech == "MCAR" else "Hidden-supporter task under the omission of active sponsors' bills or active committees' batches (MNAR-out). Mean reciprocal rank against all 19 alternatives (All) and against the 10 random alternatives only (Random), means over ten random hidings for co-sponsorship and five for contributions. The highest value in each column is in bold.")
    out = ["\\begin{table}[tbp]", "\\centering", "\\small", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\resizebox{\\textwidth}{!}{%",
           "\\begin{tabular}{l" + "rr" * len(cases) + "}", "\\toprule",
           " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{lab}}}" for _, lab in cases) + " \\\\",
           "Method & " + " & ".join("All & Random" for _ in cases) + " \\\\", "\\midrule"]
    for k, lab in ROWS:
        if not any(k in S[c][mech]["all"] for c, _ in cases):
            continue
        out.append(f"{lab} & " + " & ".join(cell(S, c, mech, sub, k) for c, _ in cases for sub in ("all", "random")) + " \\\\")
        if k in ("LR", "NHPD_mean"):
            out.append("\\midrule")
    out += ["\\bottomrule", "\\end{tabular}", "}", "\\end{table}"]
    return "\n".join(out)


def supp_table(S):
    out = ["{\\scriptsize", "\\begin{longtable}{llrrrr}",
           "\\caption{Hidden-supporter task, further measures. Recall@1, Recall@5 and mean rank of the hidden supporter among 20 candidates, and mean reciprocal rank against the 9 most active alternatives only (MRR, hard; chance 0.293), means over random hidings, with the number of evaluated bills or batches per random hiding.}\\label{tab:member-full} \\\\",
           "\\toprule", "Case and mechanism & Method & Recall@1 & Recall@5 & Mean rank & MRR, hard \\\\", "\\midrule", "\\endfirsthead",
           "\\toprule", "Case and mechanism & Method & Recall@1 & Recall@5 & Mean rank & MRR, hard \\\\", "\\midrule", "\\endhead"]
    for c, lab in CASES:
        if c not in S:
            continue
        for m, ml in MECH:
            if m not in S[c]:
                continue
            first = True
            for k, name in ROWS:
                v = S[c][m]["all"].get(k)
                hv = S[c][m]["hard"].get(k)
                if v is None:
                    continue
                head = f"{lab}, {ml} ({S[c][m]['tasks']:,.0f} {'batches' if c.startswith('fec') else 'bills'})" if first else ""
                out.append(f"{head} & {name} & {v['r1']:.3f} & {v['r5']:.3f} & {v['mean_rank']:.2f} & {hv['mrr']:.3f} \\\\")
                first = False
            out.append("\\midrule")
    out[-1] = "\\bottomrule"
    out += ["\\end{longtable}", "}"]
    return "\n".join(out)


def contrast_table(S):
    names = dict(ROWS)
    out = ["{\\scriptsize", "\\begin{longtable}{lll}",
           "\\caption{Hidden-supporter task, paired differences in mean reciprocal rank against all alternatives and against the random alternatives only, with 95\\% sponsor- or committee-bootstrap intervals.}\\label{tab:member-contrasts} \\\\",
           "\\toprule", "Case and mechanism & Contrast & Difference \\\\", "\\midrule", "\\endfirsthead",
           "\\toprule", "Case and mechanism & Contrast & Difference \\\\", "\\midrule", "\\endhead"]
    for c, lab in CASES:
        if c not in S:
            continue
        for m, ml in MECH:
            if m not in S[c]:
                continue
            first = True
            for sub, sl in (("all", "all"), ("random", "random")):
                for key, v in S[c][m][sub]["contrasts"].items():
                    x, y = key.split(" - ")
                    out.append(f"{lab + ', ' + ml if first else ''} & {names[x]} $-$ {names[y]}, {sl} & {v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}] \\\\")
                    first = False
            out.append("\\midrule")
    out[-1] = "\\bottomrule"
    out += ["\\end{longtable}", "}"]
    return "\n".join(out)


if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    d = sys.argv[2]
    open(f"{d}/member.tex", "w").write(main_table(S) + "\n")
    open(f"{d}/member_mnar.tex", "w").write(main_table(S, "MNAR-out", "tab:member-mnar") + "\n")
    open(f"{d}/member_full.tex", "w").write(supp_table(S) + "\n")
    open(f"{d}/member_contrasts.tex", "w").write(contrast_table(S) + "\n")
