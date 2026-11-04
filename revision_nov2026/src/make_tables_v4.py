# ruff: noqa: E501
"""Tables of the fourth run (decay ablation, supervised baseline), the training-on-all-bills
analysis for every case, and exact simulation from the dyad-independent models.

Usage: python make_tables_v4.py SUMMARY_V4 SUMMARY_V3 SENS_V3 SIM_P1 TABLES_DIR
"""

import json
import sys

V4 = json.load(open(sys.argv[1]))
V3 = json.load(open(sys.argv[2]))
E = json.load(open(sys.argv[3]))
SIM = json.load(open(sys.argv[4]))
T = sys.argv[5]
MECHS = [("MCAR", "MCAR"), ("MNAR-out", "MNAR-out")]
CASES = [("s118", "118th Senate"), ("s117", "117th Senate"), ("s116", "116th Senate"), ("h118", "118th House")]


def f3(x):
    return f"{x:.3f}".replace("-0.000", "0.000")


def table(path, caption, label, cols, header, rows, note, resize=False):
    lines = [r"\begin{table}[tbp]", r"\centering", r"\small", rf"\caption{{{caption}}}", rf"\label{{{label}}}"]
    if resize:
        lines.append(r"\resizebox{\textwidth}{!}{%")
    lines += [rf"\begin{{tabular}}{{{cols}}}", r"\toprule"] + header + [r"\midrule"]
    lines += [r + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}"]
    if resize:
        lines.append("}")
    lines += [rf"\par\vspace{{2pt}}\footnotesize {note}", r"\end{table}", ""]
    open(f"{T}/{path}", "w").write("\n".join(lines))


# ------------------------------------------------------------ ablation and supervised baseline
NAMES = [
    ("a:M2", "M2"),
    ("a:M3", "M3"),
    ("a:M4", "M4"),
    ("a:M4c", "M4c"),
    ("a:M5", "M5"),
    ("a:M5_deg05", "M5, degree terms at $\\tau=0.5$"),
    ("a:M5_esp05", "M5, shared-partner terms at $\\tau=0.5$"),
    ("S1", "S1"),
    ("a:LR", "logistic regression on local features"),
    ("aa_total", "directed Adamic--Adar"),
    ("sponsor_bills", "initiator bill count"),
]
rows = []
for c, clab in [("s118", "118th Senate"), ("h118", "118th House")]:
    for k, lab in NAMES:
        cells = []
        for m, _ in MECHS:
            o = V4[c][m]
            cells += [f3(o[s][k]) for s in ("random", "perturb", "sub")] + [f3(o["role"][k])]
        rows.append(f"{clab} & {lab} & " + " & ".join(cells))
    rows.append(f"{clab} & chance & 0.500 & 0.500 & 0.500 & {f3(V4[c]['MCAR']['role']['chance'])} & 0.500 & 0.500 & 0.500 & {f3(V4[c]['MNAR-out']['role']['chance'])}")
table(
    "v4_ablation.tex",
    "Degree-term models at the selected decay, separate decays for the degree and shared-partner terms of M5, and a supervised logistic baseline: concordance on the random (R), head-perturbation (H) and substitution (S) sets and top-1 accuracy (A).",
    "tab:ablation",
    "ll" + "r" * 8,
    [r" & & \multicolumn{4}{c}{MCAR} & \multicolumn{4}{c}{MNAR-out} \\", r"Case & score & R & H & S & A & R & H & S & A \\"],
    rows,
    "All degree-term models by MPLE with the decay selected for M5 in each mask unless stated. The logistic regression is fitted to the arcs of the training 2-section on standardized dyadic features, namely directed common neighbours and Adamic--Adar components, reverse arc, out- and in-degrees and their product (computed without the dyad itself), initiator bill count, party and state matching, ideological distance, and the initiator's majority-caucus membership and seniority.",
    resize=True,
)

# ------------------------------------------------------------ sponsor identification against the bill-count rule
rows = []
for c, clab in CASES:
    for m, ml in MECHS:
        o = V4[c][m]
        a = o["role_contrasts"]["S1 - sponsor_bills"]
        b = o["role_contrasts"]["M5 - sponsor_bills"]
        d = o["role_contrasts"]["a:LR - sponsor_bills"]
        rows.append(
            f"{clab} & {ml} & {f3(o['role']['sponsor_bills'])} & {f3(a[0])} [{f3(a[1])}, {f3(a[2])}] & {f3(b[0])} [{f3(b[1])}, {f3(b[2])}] & {f3(d[0])} [{f3(d[1])}, {f3(d[2])}] & "
            f"{f3(o['role_mrr']['S1'])} & {f3(o['role_mrr']['sponsor_bills'])} & {f3(o['role_mrr']['chance'])}"
        )
table(
    "v4_billrule.tex",
    "Sponsor identification relative to the rule that picks the participant with most observed bills: top-1 accuracy of the rule, differences in top-1 accuracy with sponsor-bootstrap intervals, and mean reciprocal rank (MRR).",
    "tab:billrule",
    "llrlllrrr",
    [r" & & rule & \multicolumn{3}{c}{difference from the rule} & \multicolumn{3}{c}{MRR} \\", r"Case & mask & top-1 & S1 & M5 & logistic & S1 & rule & chance \\"],
    rows,
    "Brackets give 95\\% sponsor-bootstrap intervals (fitted models held fixed).",
    resize=True,
)

# ------------------------------------------------------------ training on all bills
rows = []
for c, clab in CASES:
    key = c + "uncap"
    if key not in E:
        continue
    for m, ml in MECHS:
        M, M0 = E[key][m], V3[c][m]
        cells = []
        for s in ("random", "perturb"):
            cells += [f3(M[s][k]["concordance"][0]) for k in ("M5", "S1", "weighted_footprint")]
        cells += [f3(M["role"][k]["top1"][0]) for k in ("M5", "S1", "sponsor_bills")]
        cells.append(f3(M["role"]["chance"]["top1"][0]))
        rows.append(f"{clab} & {ml} & " + " & ".join(cells))
table(
    "v4_uncap.tex",
    "Training on all recorded hyperarcs, including those with more than ten original co-sponsors (which are never hidden): concordance on the random (R) and head-perturbation (H) sets and top-1 accuracy (A).",
    "tab:uncap",
    "ll" + "r" * 10,
    [r" & & \multicolumn{3}{c}{R} & \multicolumn{3}{c}{H} & \multicolumn{4}{c}{A} \\", r"Case & mask & M5 & S1 & weighted & M5 & S1 & weighted & M5 & S1 & bill count & chance \\"],
    rows,
    "Weighted denotes the weighted footprint, the mean number of observed records in which each candidate supporter co-sponsored a bill of the candidate initiator. The training 2-section and the record counts include the bills above the head limit.",
    resize=True,
)

# ------------------------------------------------------------ exact simulation
STATS = [("ttriple", "transitive triples"), ("ctriple", "cyclic triples"), ("mean_esp_otp", "mean two-path partners per arc")]
rows = []
for c, clab in CASES:
    for k, lab in STATS:
        obs = SIM[c]["observed"][k]
        cells = [f"{obs:,.0f}" if obs > 100 else f"{obs:.2f}"]
        for mname in ("S0", "S1", "SI"):
            mu, lo, hi = SIM[c][mname][k]
            fmt = (lambda x: f"{x:,.0f}") if obs > 100 else (lambda x: f"{x:.2f}")
            cells.append(f"{fmt(mu)} [{fmt(lo)}, {fmt(hi)}]")
        rows.append(f"{clab} & {lab} & " + " & ".join(cells))
table(
    "v4_simulation.tex",
    "Exact simulation from the MLE of the dyad-independent models on the complete 2-sections: statistics outside the models' sufficient statistics.",
    "tab:exact-sim",
    "llrlll",
    [r"Case & statistic & observed & S0 & S1 & SI \\"],
    rows,
    "Five hundred networks per model, each dyad drawn independently from its four-state distribution at the MLE with structural zeros. Brackets give central 95\\% ranges. Arcs and mutual dyads are sufficient statistics and are matched in all cases.",
    resize=True,
)
print("v4 tables written")
