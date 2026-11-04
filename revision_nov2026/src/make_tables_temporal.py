# ruff: noqa: E501
"""Tables for the temporal forecasting benchmark and for the statnet two-mode specification.

Usage: python make_tables_temporal.py SUMMARY_TEMPORAL_JSON SUMMARY_HMS_JSON OUTDIR
"""

import json
import sys


def ci(v):
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


def tname(t):
    t = t.replace("edgecov.cv_", "").replace("[[i]]", "")
    return {
        "edges": "edges",
        "memory": "memory (arc in previous quarter)",
        "history": "log history count of the arc",
        "hist_rev": "log history count of the reverse arc",
        "delrecip": "delayed reciprocity",
        "out_lag": "log lagged out-degree of sender",
        "in_lag": "log lagged in-degree of receiver",
        "twopath_lag": "log lagged two-paths",
        "threepath_lag": "log lagged three-paths",
        "cofunding_lag": "lagged co-funding similarity",
        "alignment_lag": "partisan alignment (lagged)",
        "distance_lag": "ideological distance (lagged)",
        "party": "party match",
        "state": "state match",
        "ideology": "ideological distance",
        "same_state": "same state",
        "incumbent": "candidate incumbent",
        "senate": "Senate candidate",
    }.get(t, t)


def main_table(S):
    rows = [
        ("s118", "118th Senate", ["TERGM", "M5", "S1", "HM", "UM", "coparticipation"]),
        ("h118", "118th House", ["TERGM", "M5", "S1", "HM", "UM", "coparticipation"]),
    ]
    out = [
        "\\begin{table}[tbp]",
        "\\centering",
        "\\small",
        "\\caption{Forecasting the last six months. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets for the bills of the last two quarters, with all models trained on the first six quarters, and top-1 accuracy on the role-assignment sets. TERGM: temporal ERGM with lagged and exogenous terms, fitted with \\texttt{btergm}.}",
        "\\label{tab:temporal}",
        "\\begin{tabular}{llrrrr}",
        "\\toprule",
        "Case & Model & R & P & H & Top-1 \\\\",
        "\\midrule",
    ]
    names = {
        "TERGM": "TERGM",
        "M5": "M5",
        "S1": "S1",
        "HM": "HM (two-mode)",
        "UM": "UM (undirected)",
        "coparticipation": "co-participation",
        "sponsor_bills": "most-bills rule",
    }
    for c, lab, ks in rows:
        o = S[c]
        for i, k in enumerate(ks + ["sponsor_bills"]):
            if k == "sponsor_bills":
                cells = ["--", "--", "--", f"{o['role_top1']['sponsor_bills']:.3f}"]
            else:
                t1 = f"{o['role_top1'][k]:.3f}" if k in o["role_top1"] else "--"
                cells = [f"{o[s][k]:.3f}" for s in ("random", "matched", "perturb")] + [t1]
            out.append(f"{lab if i == 0 else ''} & {names[k]} & " + " & ".join(cells) + " \\\\")
        out.append(f" & chance & & & & {o['role_chance']:.3f} \\\\")
        out.append("\\midrule")
    out[-1] = "\\bottomrule"
    out += ["\\end{tabular}", "\\end{table}"]
    return "\n".join(out)


def supp_table(S):
    out = [
        "\\begin{table}[tbp]",
        "\\centering",
        "\\scriptsize",
        "\\caption{Temporal ERGMs: estimates with 95\\% bootstrap intervals over quarters (co-sponsorship: \\texttt{btergm}, 500 replications; contributions: the same estimator, 100 replications), and paired contrasts in the forecast window with sponsor- or committee-bootstrap intervals.}",
        "\\label{tab:temporal-full}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llll}",
        "\\toprule",
        "Case & Term or contrast & Estimate or difference & \\\\",
        "\\midrule",
    ]
    for c, lab in (
        ("s118", "118th Senate"),
        ("h118", "118th House"),
        ("fec24", "Contributions 2023--24"),
        ("fec22", "Contributions 2021--22"),
    ):
        if c not in S:
            continue
        o = S[c]
        first = True
        for row in o.get("tergm_coef", [])[1:]:
            out.append(
                f"{lab if first else ''} & {tname(row[0])} & {float(row[1]):.3f} [{float(row[2]):.3f}, {float(row[3]):.3f}] & \\\\"
            )
            first = False
        for s, sl in (("random", "R"), ("matched", "P"), ("perturb", "H")):
            for k, v in o[s + "_contrasts"].items():
                out.append(
                    f" & {k.replace('coparticipation', 'co-participation').replace('cofunding', 'co-funding').replace('BS1', 'B1')}, {sl} & {ci(v)} & \\\\"
                )
        if "role_contrasts" in o:
            for k, v in o["role_contrasts"].items():
                out.append(
                    f" & {k.replace('sponsor_bills', 'most-bills rule')}, top-1 & {ci(v)} & \\\\"
                )
        out.append("\\midrule")
    out[-1] = "\\bottomrule"
    out += ["\\end{tabular}", "}", "\\end{table}"]
    return "\n".join(out)


def hms_table(H):
    out = [
        "\\begin{table}[tbp]",
        "\\centering",
        "\\small",
        "\\caption{Two-mode ERGM with the standard \\texttt{statnet} bipartite terms (edges, gwb1degree, gwb2degree, cycle(4), b1nodematch for party and state; decays selected by profile pseudolikelihood) against the two-mode ERGM of the main text (HM) and M5. Concordance on the random (R), party-matched (P) and head-perturbation (H) sets, means over 30 masks, and the mean cycle(4) coefficient.}",
        "\\label{tab:hms}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{llrrrrrrrrrr}",
        "\\toprule",
        " & & \\multicolumn{3}{c}{R} & \\multicolumn{3}{c}{P} & \\multicolumn{3}{c}{H} & \\\\",
        "Case & mask & statnet & HM & M5 & statnet & HM & M5 & statnet & HM & M5 & cycle(4) \\\\",
        "\\midrule",
    ]
    labs = {
        "s118": "118th Senate",
        "s117": "117th Senate",
        "s116": "116th Senate",
        "h118": "118th House",
    }
    for key, v in H.items():
        c, m = key.split("_", 1)
        cells = []
        for s in ("random", "matched", "perturb"):
            cells += [f"{v['conc'][s][k]:.3f}" for k in ("HMs", "HM", "M5")]
        out.append(
            f"{labs[c]} & {m} & " + " & ".join(cells) + f" & {v['theta']['cycle4']:.3f} \\\\"
        )
    out += ["\\bottomrule", "\\end{tabular}", "}", "\\end{table}"]
    return "\n".join(out)


if __name__ == "__main__":
    S = json.load(open(sys.argv[1]))
    H = json.load(open(sys.argv[2]))
    d = sys.argv[3]
    open(f"{d}/temporal.tex", "w").write(main_table(S) + "\n")
    open(f"{d}/temporal_full.tex", "w").write(supp_table(S) + "\n")
    open(f"{d}/hms.tex", "w").write(hms_table(H) + "\n")
