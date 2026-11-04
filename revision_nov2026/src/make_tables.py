# ruff: noqa: E501
"""Write the manuscript's LaTeX tables from the summary JSON files.

Usage: python make_tables.py RESULTS_DIR TABLES_DIR
"""

import json
import os
import sys

R, T = sys.argv[1], sys.argv[2]
MECHS = [("MCAR", "MCAR"), ("MNAR-out", "MNAR-out")]
NAMES = {
    "aa_total": "directed Adamic--Adar",
    "aa_oi": "Adamic--Adar, two-paths",
    "cn_total": "CN total",
    "degprod": "degree product",
    "sponsor_activity": "sponsor activity",
    "cosponsor_popularity": "co-sponsor popularity",
    "party_share": "same-party share",
    "reverse": "reverse arc",
    "M0_L1g": "M0 density",
    "M4c_L1g": "M4c structural",
    "M5_L1g": "M5 political",
    "M6_L1g": "M6 sponsor attributes",
    "S0_L1g": "S0 sender--receiver",
    "S1_L1g": "S1 sender--receiver, political",
    "S2_L1g": "S2 = S1 + two-path closure",
    "S3_L1g": "S3 = S1 + all closure",
    "M4c_nomut_L1g": "M4c without mutuality",
}
PANEL = {"random": "random", "sub": "substitution"}


def load(name):
    p = f"{R}/{name}/summary.json"
    return json.load(open(p)) if os.path.exists(p) else None


def _merge(a, b):
    """Recursively merge summary b into a (b supplies sender-receiver model entries)."""
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _merge(a[k], v)
        elif k not in a:
            a[k] = v
    return a


def loadm(name):
    """Original summary merged with the sender-receiver run, when present."""
    a = load(name)
    b = load(name + "_S")
    if a is None:
        return b
    if b is not None:
        _merge(a["mechs"], b["mechs"])
    return a


def f3(x):
    return f"{x:.3f}".replace("-0.000", "0.000")


def pv(p):
    return "$<0.0001$" if p < 1e-4 else f"{p:.4f}"


def ci(c):
    return f"{f3(c[0])} & [{f3(c[1])}, {f3(c[2])}] & {pv(c[3])}"


def table(path, caption, label, cols, header, rows, note, small=True, resize=False):
    lines = [
        r"\begin{table}[tbp]",
        r"\centering",
        r"\small" if small else "",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
    ]
    if resize:
        lines.append(r"\resizebox{\textwidth}{!}{%")
    lines += [rf"\begin{{tabular}}{{{cols}}}", r"\toprule", header + r" \\", r"\midrule"]
    lines += [r + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}"]
    if resize:
        lines.append("}")
    lines += [rf"\par\vspace{{2pt}}\footnotesize {note}", r"\end{table}", ""]
    open(f"{T}/{path}", "w").write("\n".join(line for line in lines if line != ""))


S = loadm("s118")
# ---------------------------------------------------------------- Table 2 primary performance
rows = []
for mech, lab in MECHS:
    M = S["mechs"][mech]
    for p in ["random", "sub"]:
        for k in [
            "aa_total",
            "degprod",
            "sponsor_activity",
            "cosponsor_popularity",
            "party_share",
            "M4c_L1g",
            "M5_L1g",
            "M6_L1g",
            "S0_L1g",
            "S1_L1g",
        ]:
            rows.append(
                f"{lab} & {PANEL[p]} & {NAMES[k]} & {f3(M['pr_auc'][p][k])} & {f3(M['roc_auc'][p][k])}"
            )
table(
    "table_02_primary_performance.tex",
    "118th Senate: mean ranking performance over 30 matched random hidings per mechanism.",
    "tab:senate-performance",
    "lllrr",
    "Mechanism & candidate set & score & PR-AUC & ROC-AUC",
    rows,
    "Local and baseline scores are mean lifts over the candidate footprint computed on the training 2-section. "
    "Sponsor activity is the sponsor's training out-degree; co-sponsor popularity is the mean training in-degree of the head. "
    "ERGM rows use mask-specific MPLE fits and the factorized conditional footprint score $L_{1g}$.",
)

# ---------------------------------------------------------------- Table 3 competitive contrasts
rows = []
for mech, lab in MECHS:
    C = S["mechs"][mech]["contrasts"]
    rows.append(
        f"{lab} & random & M4c minus directed Adamic--Adar & "
        + ci([-x if i == 0 else x for i, x in enumerate(C["random"]["aa_total - M5_L1g"])])
        if False
        else ""
    )
rows = []
for mech, lab in MECHS:
    C = S["mechs"][mech]["contrasts"]
    for p, a, b, txt in [
        ("random", "aa_total", "M5_L1g", "directed Adamic--Adar minus M5"),
        ("random", "S1_L1g", "M5_L1g", "S1 minus M5"),
        ("random", "aa_total", "S1_L1g", "directed Adamic--Adar minus S1"),
        ("sub", "degprod", "M5_L1g", "degree product minus M5"),
        ("sub", "S1_L1g", "M5_L1g", "S1 minus M5"),
        ("sub", "degprod", "S1_L1g", "degree product minus S1"),
        ("sub", "degprod", "S0_L1g", "degree product minus S0"),
        ("sub", "sponsor_activity", "degprod", "sponsor activity minus degree product"),
    ]:
        rows.append(f"{lab} & {PANEL[p]} & {txt} & " + ci(C[p][f"{a} - {b}"]))
table(
    "table_03_competitive_contrasts.tex",
    "118th Senate: paired PR-AUC contrasts between local scores, nested ERGMs and sender--receiver ERGMs.",
    "tab:senate-contrasts",
    "lllrrr",
    r"Mechanism & candidate set & contrast & difference & 95\% CI & sign-flip $p$",
    rows,
    "Differences are means over 30 matched random hidings; intervals are percentile bootstrap intervals over random hidings "
    "(Monte Carlo precision within the fixed record); $p$-values are two-sided sign-flip tests with 20,000 permutations.", resize=True)

# ---------------------------------------------------------------- Table 3b political contrasts
rows = []
for a, b, txt in [
    ("M4c_L1g", "M0_L1g", "M4c minus M0"),
    ("M5_L1g", "M4c_L1g", "M5 minus M4c"),
    ("M6_L1g", "M5_L1g", "M6 minus M5"),
    ("M4c_nomut_L1g", "M4c_L1g", "M4c without mutuality minus M4c"),
    ("S1_L1g", "S0_L1g", "S1 minus S0"),
    ("S3_L1g", "S1_L1g", "S3 minus S1"),
]:
    for mech, lab in MECHS:
        C = S["mechs"][mech]["contrasts"]
        for p in ["random", "sub"]:
            rows.append(f"{lab} & {PANEL[p]} & {txt} & " + ci(C[p][f"{a} - {b}"]))
table(
    "table_03b_political_covariate_contrasts.tex",
    "118th Senate: paired PR-AUC contrasts along the nested ERGMs.",
    "tab:political-contrast",
    "lllrrr",
    r"Mechanism & candidate set & contrast & difference & 95\% CI & sign-flip $p$",
    rows,
    "M5 adds party and state matching and absolute DW-NOMINATE distance to M4c; M6 adds sponsor-side majority-caucus "
    "and seniority terms; the last contrast removes mutuality alone. Intervals and tests as in the main text.",
resize=True,
)

# ---------------------------------------------------------------- Table 4 role
rows = []
for mech, lab in MECHS:
    M = S["mechs"][mech]
    for k in [
        "aa_oi",
        "degprod",
        "sponsor_activity",
        "cosponsor_popularity",
        "M4c_L1g",
        "M5_L1g",
        "M6_L1g",
        "S0_L1g",
        "S1_L1g",
    ]:
        d = M["role_vs_uniform"][k]["top1"]
        rows.append(
            f"{lab} & {NAMES[k]} & {f3(M['role'][k]['top1'])} & {f3(M['role'][k]['mrr'])} & {f3(d[0])} [{f3(d[1])}, {f3(d[2])}]"
        )
    rows.append(
        f"{lab} & uniform chance & {f3(M['role']['uniform']['top1'])} & {f3(M['role']['uniform']['mrr'])} & "
    )
table(
    "table_04_sponsor_identification.tex",
    "118th Senate: identification of the recorded sponsor among all single-initiator assignments of a bill's participants.",
    "tab:senate-role",
    "llrrl",
    r"Mechanism & score & top-1 & MRR & top-1 minus chance [95\% CI]",
    rows,
    "Top-1 and reciprocal rank are expected values under random tie-breaking. Chance is computed bill by bill from the "
    "number of participants. Intervals resample whole random hidings.",
)

# ---------------------------------------------------------------- Ladder
rows = []
for m in ["M0", "M1", "M2", "M3", "M4", "M4c", "M4c_nomut", "M5", "M6", "S0", "S1", "S2", "S3"]:
    k = f"{m}_L1g"
    vals = [S["mechs"][mech]["pr_auc"][p][k] for p in ["random", "sub"] for mech, _ in MECHS]
    rows.append(f"{m.replace('_nomut', ' without mutuality')} & " + " & ".join(f3(v) for v in vals))
table(
    "table_a4_ergm_ladder.tex",
    "118th Senate: mean PR-AUC of the nested MPLE ERGMs ($L_{1g}$).",
    "tab:ergm-ladder",
    "lrrrr",
    "Model & random MCAR & random MNAR-out & substitution MCAR & substitution MNAR-out",
    rows,
    "M0 edges; M1 adds mutuality; M2 adds geometrically weighted out- and in-degree; M3 adds outgoing two-path closure; "
    "M4 adds shared-target and shared-source closure; M4c adds cyclic triples; M5 adds party, state and ideology; M6 adds "
    "majority caucus and seniority of the sponsor. S0 replaces the degree terms of M2 with sender and receiver effects; "
    "S1 adds the political covariates; S2 and S3 add two-path and all three closure terms.",
resize=True,
)

# ---------------------------------------------------------------- Mask realisation (all cases)
rows = []
for name, lab in [
    ("s118", "118th Senate"),
    ("s117", "117th Senate"),
    ("s116", "116th Senate"),
    ("h118", "118th House"),
]:
    X = load(name)
    if not X:
        continue
    for mech, ml in MECHS:
        r = X["mechs"][mech]["realisation"]
        rows.append(
            f"{lab} & {ml} & {100 * r['types_withheld']:.2f}\\% & {100 * r['records_withheld']:.2f}\\% & "
            f"{100 * r['arc_removal']:.2f}\\% & {100 * r['surviving_footprint_share']:.2f}\\%"
        )
table(
    "table_a3_mask_realisation.tex",
    "Realised severity of the two omission mechanisms (means over 30 random hidings).",
    "tab:mask-realisation",
    "llrrrr",
    "Case & mechanism & hyperarc rate & record rate & arc removal & surviving footprints",
    rows,
    "A surviving footprint means every arc of a hidden hyperarc remains in the 2-section through another observed hyperarc; it is a "
    "property of the 2-section, not leakage of the hidden record.",
resize=True,
)

# ---------------------------------------------------------------- Recoverability
rows = []
lab_g = {
    "both": "both survive",
    "true_only": "recorded hyperarc only",
    "sub_only": "substitute only",
    "neither": "neither visible",
}
for mech, ml in MECHS:
    M = S["mechs"][mech]
    for g in ["both", "true_only", "sub_only", "neither"]:
        w = M["strata_win"]
        rows.append(
            f"{ml} & {lab_g[g]} & {f3(M['strata_share'][g])} & "
            + " & ".join(
                f"{f3(w[k][g][0])} [{f3(w[k][g][1])}, {f3(w[k][g][2])}]"
                for k in ["M5_L1g", "S1_L1g", "degprod"]
            )
        )
table(
    "table_a5b_sponsor_recoverability.tex",
    "118th Senate: preference for the hidden bill over its substitute, by survival of the two footprints in the training 2-section.",
    "tab:sponsor-recoverability",
    "llrlll",
    "Mechanism & footprint pattern & share & M5 & S1 & degree product",
    rows,
    "Each entry is the tie-aware probability that the score ranks the hidden recorded hyperarc above its substitute; "
    "brackets are 95\\% bootstrap intervals over random hidings.",
    resize=True,
)

# ---------------------------------------------------------------- Bipartisan
rows = []
for mech, ml in MECHS:
    B = S["mechs"][mech]["bipartisan"]
    for p in ["random", "sub"]:
        for lab in ["single_party", "bipartisan"]:
            vals = " & ".join(
                f3(B[p][lab][k])
                for k in ["party_share", "M5_L1g", "S1_L1g", "aa_total", "degprod"]
            )
            c = B[p][lab + "_contrasts"]["M5_L1g - M4c_L1g"]
            c2 = B[p][lab + "_contrasts"]["S1_L1g - S0_L1g"]
            rows.append(
                f"{ml} & {PANEL[p]} & {lab.replace('_', '-')} & {vals} & {f3(c[0])} [{f3(c[1])}, {f3(c[2])}]"
                f" & {f3(c2[0])} [{f3(c2[1])}, {f3(c2[2])}]"
            )
share = S["mechs"]["MCAR"]["bipartisan"]["random"]["share_bipartisan"]
table(
    "table_r3_bipartisan.tex",
    "118th Senate: mean PR-AUC by coalition type. A hidden hyperarc is bipartisan if at least one original co-sponsor belongs to a different caucus from the sponsor.",
    "tab:bipartisan",
    "lllrrrrrll",
    r"Mechanism & candidate set & coalition & party & M5 & S1 & dir.\ AA & deg.\ prod. & M5 minus M4c & S1 minus S0",
    rows,
    f"Independents are assigned to the Democratic caucus. Bipartisan hyperarcs form {100 * share:.1f}\\% of the hidden positives in the MCAR random candidate sets. "
    "PR-AUC is computed within each stratum; negatives keep their pairing with the positive.",
    resize=True,
)

# ---------------------------------------------------------------- co-sponsor limit sensitivity
C3 = loadm("s118cap3")
if C3:
    rows = []
    for mech, ml in MECHS:
        C = C3["mechs"][mech]["contrasts"]
        for p in ["random", "sub"]:
            for a, b, txt in [
                ("M4c_L1g", "M0_L1g", "M4c minus M0"),
                ("M5_L1g", "M4c_L1g", "M5 minus M4c"),
                ("aa_total", "M5_L1g", "directed AA minus M5"),
                ("degprod", "M5_L1g", "degree product minus M5"),
                ("S1_L1g", "M5_L1g", "S1 minus M5"),
                ("aa_total", "S1_L1g", "directed AA minus S1"),
                ("degprod", "S1_L1g", "degree product minus S1"),
            ]:
                if f"{a} - {b}" in C[p]:
                    rows.append(f"{ml} & {PANEL[p]} & {txt} & " + ci(C[p][f"{a} - {b}"]))
    table(
        "table_05_limit_sensitivity.tex",
        "118th Senate, bills with at most three original co-sponsors: paired PR-AUC contrasts.",
        "tab:senate-limit-sensitivity",
        "lllrrr",
        r"Mechanism & candidate set & contrast & difference & 95\% CI & sign-flip $p$",
        rows,
        "Separately constructed target of bills with at most three original co-sponsors, with the same actor universe, seeds and evaluation design (30 random hidings per mechanism).",
    )

# ---------------------------------------------------------------- extras: ttriple + static
E = json.load(open(f"{R}/s118_extras/extras.json"))
rows = [
    f"{ml} & {E['ttriple'][m]['fits']}/30 & {E['ttriple'][m]['positive']} & {E['ttriple'][m]['mean']:.4f} & "
    f"[{E['ttriple'][m]['min']:.4f}, {E['ttriple'][m]['max']:.4f}]"
    for m, ml in MECHS
]
table(
    "table_a5_mtt_check.tex",
    "118th Senate: edges-plus-transitive-triple MPLE on every training 2-section.",
    "tab:mtt-check",
    "lrrrr",
    r"Mechanism & fits & positive $\hat\theta_{tt}$ & mean $\hat\theta_{tt}$ & range",
    rows,
    "The covariate is the transitive-triple change statistic $t^{OI}_{ij}+t^{OO}_{ij}+t^{II}_{ij}$.",
)
rows = [f"{m} & {f3(v['pr_auc'])} & {f3(v['roc_auc'])}" for m, v in E["static"].items()]
table(
    "table_a6_static_diagnostic.tex",
    "118th Senate: arc-level diagnostic on the complete 2-section.",
    "tab:static-diagnostic",
    "lrr",
    "MPLE model & PR-AUC & ROC-AUC",
    rows,
    "Thirty arc-level random hidings, in which 30\\% of arcs are hidden at random and paired with an equal number of random non-arcs; "
    "scores are MPLE conditional tie probabilities on the remaining 2-section.",
)

# ---------------------------------------------------------------- replication data + results
CA = json.load(open(f"{R}/concepts_all.json")) if os.path.exists(f"{R}/concepts_all.json") else {}
rows = []
for name, lab in [
    ("s118", "118th Senate"),
    ("s117", "117th Senate"),
    ("s116", "116th Senate"),
    ("h118", "118th House"),
]:
    X = load(name)
    if not X:
        continue
    m = X["meta"]
    pc = m["party_counts"]
    pstr = "/".join(str(pc.get(p, 0)) for p in ["Democrat", "Independent", "Republican"])
    nb = (
        m["valid_events"]
        + m["dropped"].get("empty_head", 0)
        + m["dropped"].get("outside_universe", 0)
    )
    rows.append(
        f"{lab} & {nb:,} & {m['valid_events']:,} & {m['n']} & {pstr} & {m['majority']} & "
        f"{m['records']:,} ({100 * m['records'] / m['valid_events']:.1f}\\%) & {m['types']:,} & {m['arcs_cap']:,}"
    )
table(
    "table_r1_case_data.tex",
    "Record accounting for the four cases (Bill Status, at most ten original co-sponsors).",
    "tab:case-data",
    "lrrrlrrrr",
    "Case & bills & nonempty heads & actors & D/I/R & majority & eligible bills & hyperarcs & arcs",
    rows,
    "Actors are all persons who served in the chamber during the Congress. Majority counts members of the majority caucus. "
    "Eligible bills have at most ten original co-sponsors; arcs are those of the 2-section of eligible hyperarcs.",
    resize=True,
)

CASES4 = [("s118", "118th S"), ("s117", "117th S"), ("s116", "116th S"), ("h118", "118th H")]
XS = {n: loadm(n) for n, _ in CASES4}


def _c(c):
    return f"{f3(c[0])} ({f3(c[1])}, {f3(c[2])})"


ITEMS = [
    ("M4c minus M0, random", lambda M: M["contrasts"]["random"]["M4c_L1g - M0_L1g"]),
    ("M5 minus M4c, random", lambda M: M["contrasts"]["random"]["M5_L1g - M4c_L1g"]),
    (
        "\\quad single-party bills",
        lambda M: M["bipartisan"]["random"]["single_party_contrasts"]["M5_L1g - M4c_L1g"],
    ),
    (
        "\\quad bipartisan bills",
        lambda M: M["bipartisan"]["random"]["bipartisan_contrasts"]["M5_L1g - M4c_L1g"],
    ),
    ("directed AA minus M5, random", lambda M: M["contrasts"]["random"]["aa_total - M5_L1g"]),
    ("degree product minus M5, substitution", lambda M: M["contrasts"]["sub"]["degprod - M5_L1g"]),
    ("M6 top-1 minus chance", lambda M: M["role_vs_uniform"]["M6_L1g"]["top1"]),
    ("AA two-paths top-1 minus chance", lambda M: M["role_vs_uniform"]["aa_oi"]["top1"]),
    ("S1 minus M5, random", lambda M: M["contrasts"]["random"]["S1_L1g - M5_L1g"]),
    ("directed AA minus S1, random", lambda M: M["contrasts"]["random"]["aa_total - S1_L1g"]),
    ("degree product minus S1, substitution", lambda M: M["contrasts"]["sub"]["degprod - S1_L1g"]),
    ("S1 top-1 minus chance", lambda M: M["role_vs_uniform"]["S1_L1g"]["top1"]),
    (
        "S1 minus S0, bipartisan bills",
        lambda M: M["bipartisan"]["random"]["bipartisan_contrasts"]["S1_L1g - S0_L1g"],
    ),
]


def _cell(fn, X):
    try:
        return _c(fn(X))
    except (KeyError, TypeError):
        return ""

rows = []
for mech, ml in MECHS:
    rows.append(f"\\multicolumn{{5}}{{l}}{{\\textit{{{ml}}}}}")
    for lab, fn in ITEMS:
        rows.append(
            lab
            + " & "
            + " & ".join(_cell(fn, XS[n]["mechs"][mech]) if XS[n] else "" for n, _ in CASES4)
        )
table(
    "table_r2_case_results.tex",
    "Main contrasts in all four cases: mean differences over 30 random hidings with 95\\% bootstrap intervals over random hidings.",
    "tab:case-results",
    "lllll",
    "Contrast & " + " & ".join(lab for _, lab in CASES4),
    rows,
    "PR-AUC differences for the candidate set named; top-1 differences on the role-assignment sets. S = Senate, H = House. "
    "Bipartisan bills have at least one original co-sponsor from a different caucus from the sponsor.",
    resize=True,
)

if CA:
    rows = []
    for name, lab in [
        ("s118", "118th Senate"),
        ("s117", "117th Senate"),
        ("s116", "116th Senate"),
        ("h118", "118th House"),
    ]:
        if name not in CA:
            continue
        for cH in ["10", "15"]:
            a = CA[name].get(cH)
            if a:
                rows.append(
                    f"{lab} & $|H|\\leq{cH}$ & {a['types']:,} & {a['concepts']:,} & {a['exact']} & {a['concept_arcs']:,} & {a['type_arcs']:,} & {a['jaccard']:.3f}"
                )
    table(
        "table_06_concept_fidelity.tex",
        "Formal concepts of the 2-section versus recorded hyperarcs.",
        "tab:senate-fidelity",
        "llrrrrrr",
        "Case & co-sponsor limit & hyperarcs & concepts & exact matches & concept arcs & bill arcs & Jaccard",
        rows,
        "Concepts are enumerated on the 2-section of all bills, including those above the head limit, with at most three senders and at most the stated number of receivers; an exact match requires identical ordered tail and head sets.",
        resize=True,
    )
print("tables written")

# ---------------------------------------------------------------- MPLE simulation check
SIM = f"{R}/mple_sim_s118/simulation_summary.csv"
if os.path.exists(SIM):
    import csv

    rows = []
    SIM2 = f"{R}/gof_sr_s118/simulation_summary.csv"
    recs = list(csv.DictReader(open(SIM)))
    if os.path.exists(SIM2):
        recs += [r for r in csv.DictReader(open(SIM2)) if r["model"] in ("S0", "S1")]
    for r in recs:
        if r["statistic"] in ("edges", "mutual", "ttriple", "ctriple"):
            rows.append(
                f"{r['model']} & {r['statistic'].replace('ttriple', 'transitive triples').replace('ctriple', 'cyclic triples')} & "
                f"{float(r['observed']):,.0f} & {float(r['sim_mean']):,.0f} & "
                f"[{float(r['sim_q025']):,.0f}, {float(r['sim_q975']):,.0f}]"
            )
    table(
        "table_r4_mle.tex",
        "118th Senate: networks simulated from the MPLE fits on the complete 2-section compared with the observed network.",
        "tab:mle",
        "llrrl",
        "Model & statistic & observed & simulated mean & 95\\% range",
        rows,
        "One hundred networks per model simulated with the statnet \\texttt{ergm} package (burn-in 200,000, interval 10,000) from the MPLE coefficients, which for M4c and M5 agree with the Python MPLE to four decimal places. M1 contains arcs and mutual dyads; M2--M5 add geometrically weighted degree terms; S models use sender and receiver effects.",
    )
